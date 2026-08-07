from pathlib import Path

from cw_analyser.parser import parse_csv


def test_parser_accepts_header_and_valid_rows(tmp_path: Path):
    source = tmp_path / "input.csv"
    source.write_text("Character,Element1,Element2\nA,60,180\nC,180,60,181,59\n", encoding="utf-8")
    result = parse_csv(source)
    assert result.accepted == 2
    assert result.rejected == 0
    assert result.values["A"] == [[60.0], [180.0]]


def test_parser_reports_bad_rows_without_stopping(tmp_path: Path):
    source = tmp_path / "input.csv"
    source.write_text("?,60\nA,60\nA,x,180\nA,-1,180\n\nA,61,183\n", encoding="utf-8")
    result = parse_csv(source)
    assert result.accepted == 1
    assert result.rejected == 5
    assert result.issue_counts == {
        "unknown character": 1,
        "wrong element count": 1,
        "invalid number": 1,
        "non-positive or non-finite timing": 1,
        "empty record": 1,
    }

