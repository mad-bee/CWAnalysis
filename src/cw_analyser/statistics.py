from __future__ import annotations

import math
import statistics as st
from pathlib import Path

import numpy as np

from .models import CharacterAnalysis, ElementStats, ParseResult, SessionAnalysis
from .morse import MORSE, element_name


def analyse(parse: ParseResult, source: str | Path, outlier_method: str = "iqr", units: str = "ms") -> SessionAnalysis:
    characters: list[CharacterAnalysis] = []
    all_dits: list[float] = []
    all_dahs: list[float] = []
    for char in MORSE:
        columns = parse.values[char]
        if not columns or not columns[0]:
            continue
        elements = [
            calculate_element(char, MORSE[char], position + 1, symbol, columns[position], outlier_method)
            for position, symbol in enumerate(MORSE[char])
        ]
        for element in elements:
            (all_dits if element.element_type == "dit" else all_dahs).extend(element.values)
        cvs = [abs(e.coefficient_of_variation) for e in elements if math.isfinite(e.coefficient_of_variation)]
        best = min(range(len(elements)), key=lambda i: elements[i].coefficient_of_variation)
        worst = max(range(len(elements)), key=lambda i: elements[i].coefficient_of_variation)
        average_cv = st.fmean(cvs) if cvs else 0.0
        consistency = _clamp(100.0 - average_cv * 2.5 - 100 * st.fmean(e.outlier_rate for e in elements))
        notes = position_bias_notes(elements)
        characters.append(CharacterAnalysis(
            char, MORSE[char], len(columns[0]), elements, average_cv,
            best + 1, worst + 1, consistency, notes,
        ))

    median_dit = float(np.median(all_dits)) if all_dits else math.nan
    median_dah = float(np.median(all_dahs)) if all_dahs else math.nan
    ratio = median_dah / median_dit if all_dits and all_dahs and median_dit else math.nan
    estimated_wpm = 1200.0 / median_dit if units.lower() in {"ms", "millisecond", "milliseconds"} and median_dit else None
    all_elements = [e for c in characters for e in c.elements]
    avg_cv = st.fmean(abs(e.coefficient_of_variation) for e in all_elements) if all_elements else 100.0
    outlier_rate = sum(e.outlier_count for e in all_elements) / max(1, sum(e.count for e in all_elements))
    ratio_penalty = min(35.0, abs(ratio - 3.0) * 18.0) if math.isfinite(ratio) else 35.0
    score = _clamp(100.0 - avg_cv * 1.6 - ratio_penalty - outlier_rate * 100.0)
    stars = max(0, min(5, round(score / 20)))
    return SessionAnalysis(source, parse.accepted, parse.rejected, parse.issue_counts, characters,
                           median_dit, median_dah, ratio, estimated_wpm, score, stars)


def calculate_element(char: str, pattern: str, position: int, symbol: str,
                      values: list[float], method: str = "iqr") -> ElementStats:
    array = np.asarray(values, dtype=float)
    count = len(array)
    mean = float(np.mean(array))
    median = float(np.median(array))
    p25, p75 = (float(x) for x in np.percentile(array, [25, 75]))
    iqr = p75 - p25
    variance = float(np.var(array, ddof=1)) if count > 1 else 0.0
    sd = math.sqrt(variance)
    mad = float(np.median(np.abs(array - median)))
    mode = _unique_mode(values)
    cv = sd / mean * 100.0 if mean else math.nan
    margin = 1.96 * sd / math.sqrt(count) if count > 1 else 0.0
    centered = array - mean
    skewness = float(np.mean(centered ** 3) / (np.std(array) ** 3)) if count > 2 and np.std(array) else 0.0
    kurtosis = float(np.mean(centered ** 4) / (np.var(array) ** 2) - 3.0) if count > 3 and np.var(array) else 0.0
    mask = _outlier_mask(array, p25, p75, iqr, median, mad, method)
    outlier_count = int(np.count_nonzero(mask))
    return ElementStats(
        char, pattern, position, element_name(symbol), count, float(np.min(array)), float(np.max(array)),
        float(np.ptp(array)), mean, median, mode, variance, sd, mad, p25, p75, iqr, cv,
        mean - margin, mean + margin, skewness, kurtosis, outlier_count, outlier_count / count,
        list(map(float, array)), list(map(bool, mask)),
    )


def _unique_mode(values: list[float]) -> float | None:
    modes = st.multimode(values)
    return float(modes[0]) if len(modes) == 1 and values.count(modes[0]) > 1 else None


def _outlier_mask(array: np.ndarray, p25: float, p75: float, iqr: float,
                  median: float, mad: float, method: str) -> np.ndarray:
    if method == "modified-z":
        if mad == 0:
            return np.zeros(len(array), dtype=bool)
        return np.abs(0.6745 * (array - median) / mad) > 3.5
    return (array < p25 - 1.5 * iqr) | (array > p75 + 1.5 * iqr)


def position_bias_notes(elements: list[ElementStats]) -> list[str]:
    if len(elements) < 2:
        return ["Single-element character; position bias is not applicable."]
    notes: list[str] = []
    first, last = elements[0], elements[-1]
    comparable = [e for e in elements[1:] if e.element_type == first.element_type]
    if comparable:
        reference = st.fmean(e.median for e in comparable)
        delta = (first.median / reference - 1) * 100 if reference else 0
        if abs(delta) >= 5:
            notes.append(f"First {first.element_type} is {abs(delta):.1f}% {'longer' if delta > 0 else 'shorter'} than later matching elements.")
    comparable = [e for e in elements[:-1] if e.element_type == last.element_type]
    if comparable:
        reference = st.fmean(e.median for e in comparable)
        delta = (last.median / reference - 1) * 100 if reference else 0
        if abs(delta) >= 5:
            notes.append(f"Last {last.element_type} is {abs(delta):.1f}% {'lengthened' if delta > 0 else 'shortened'}.")
    if len(elements) >= 4:
        medians = np.asarray([e.median / (3 if e.element_type == "dah" else 1) for e in elements])
        slope = float(np.polyfit(np.arange(len(medians)), medians, 1)[0])
        base = float(np.mean(medians))
        drift = slope / base * 100 if base else 0
        if abs(drift) >= 3:
            notes.append(f"Normalised element timing drifts {abs(drift):.1f}% per position {'upward' if drift > 0 else 'downward'}.")
    return notes or ["No material position bias detected at the 5% threshold."]


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))
