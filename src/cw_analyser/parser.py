from __future__ import annotations

import csv
from pathlib import Path

from .models import Issue, ParseResult
from .morse import MORSE

MAX_RECORDED_ISSUES = 1000


def parse_csv(path: Path, delimiter: str = ",") -> ParseResult:
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    issues: list[Issue] = []
    counts: dict[str, int] = {}
    accepted = rejected = 0
    alternating_mark_space = False

    def reject(line: int, reason: str, row: list[str]) -> None:
        nonlocal rejected
        rejected += 1
        counts[reason] = counts.get(reason, 0) + 1
        if len(issues) < MAX_RECORDED_ISSUES:
            issues.append(Issue(line, reason, delimiter.join(row)[:300]))

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter=delimiter)
        for line, row in enumerate(reader, start=1):
            if not row or not any(cell.strip() for cell in row):
                reject(line, "empty record", row)
                continue
            char = row[0].strip().upper()
            if line == 1 and char in {"CHARACTER", "CHAR", "LETTER"}:
                headings = [cell.strip().lower() for cell in row[1:]]
                alternating_mark_space = bool(headings) and headings[0].startswith("mark")
                continue
            if char not in MORSE:
                reject(line, "unknown character", row)
                continue
            expected = len(MORSE[char])
            cells = [cell.strip() for cell in row[1:]]
            if alternating_mark_space:
                # Recorder exports use mark1,space1,mark2,space2,... .  Only
                # mark durations describe the keyed Morse elements; inter-mark
                # spaces and unused trailing columns are intentionally ignored.
                cells = cells[0 : expected * 2 : 2]
            if len(cells) != expected or any(cell == "" for cell in cells):
                reject(line, "wrong element count", row)
                continue
            try:
                timings = [float(cell) for cell in cells]
            except ValueError:
                reject(line, "invalid number", row)
                continue
            if any(not _finite_positive(value) for value in timings):
                reject(line, "non-positive or non-finite timing", row)
                continue
            for position, timing in enumerate(timings):
                values[char][position].append(timing)
            accepted += 1

    return ParseResult(values, accepted, rejected, issues, counts)


def _finite_positive(value: float) -> bool:
    return value > 0 and value != float("inf") and value != float("-inf") and value == value
