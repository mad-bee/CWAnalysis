from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(slots=True)
class Issue:
    line: int
    reason: str
    row: str = ""


@dataclass(slots=True)
class ParseResult:
    values: dict[str, list[list[float]]]
    accepted: int
    rejected: int
    issues: list[Issue] = field(default_factory=list)
    issue_counts: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class ElementStats:
    character: str
    pattern: str
    position: int
    element_type: Literal["dit", "dah"]
    count: int
    minimum: float
    maximum: float
    value_range: float
    mean: float
    median: float
    mode: float | None
    variance: float
    standard_deviation: float
    mad: float
    percentile_25: float
    percentile_75: float
    iqr: float
    coefficient_of_variation: float
    confidence_interval_low: float
    confidence_interval_high: float
    skewness: float
    kurtosis: float
    outlier_count: int
    outlier_rate: float
    values: list[float] = field(repr=False)
    outlier_mask: list[bool] = field(repr=False)


@dataclass(slots=True)
class CharacterAnalysis:
    character: str
    pattern: str
    sample_count: int
    elements: list[ElementStats]
    average_cv: float
    best_element: int
    worst_element: int
    consistency_score: float
    position_notes: list[str]


@dataclass(slots=True)
class SessionAnalysis:
    source: Path
    accepted: int
    rejected: int
    issue_counts: dict[str, int]
    characters: list[CharacterAnalysis]
    median_dit: float
    median_dah: float
    dash_dit_ratio: float
    estimated_wpm: float | None
    overall_score: float
    stars: int


@dataclass(slots=True)
class ReportConfig:
    plot_type: Literal["box", "violin", "strip", "histogram"] = "box"
    show_outliers: bool = True
    show_points: bool = True
    show_reference_lines: bool = True
    fixed_scales: bool = False
    page_size: Literal["A4", "LETTER"] = "A4"
    dpi: int = 160
    units: str = "ms"
    delimiter: str = ","
    outlier_method: Literal["iqr", "modified-z"] = "iqr"
    colours: dict[str, str] = field(default_factory=lambda: {
        "dit": "#2878B5", "dah": "#D64541", "median": "#111111",
        "ideal": "#2A9D4B", "outlier": "#F28E2B", "point": "#303030",
    })

