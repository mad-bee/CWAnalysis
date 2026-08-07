import csv
from pathlib import Path

from cw_analyser.models import ParseResult
from cw_analyser.morse import MORSE
from cw_analyser.report import write_summary_csv
from cw_analyser.statistics import analyse


def test_summary_has_one_row_per_element(tmp_path: Path):
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["C"] = [[180, 181], [60, 59], [179, 182], [61, 60]]
    session = analyse(ParseResult(values, 2, 0), Path("test.csv"))
    output = write_summary_csv(session, tmp_path / "summary.csv")
    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 4
    assert [row["position"] for row in rows] == ["1", "2", "3", "4"]
    assert [row["element_type"] for row in rows] == ["dah", "dit", "dah", "dit"]

