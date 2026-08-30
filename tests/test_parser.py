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


def test_parser_accepts_alternating_mark_space_export(tmp_path: Path):
    source = tmp_path / "markspace.csv"
    source.write_text(
        "Character, mark1, space1, mark2, space2, mark3, space3, mark4, space4,\n"
        "e,37,190\n"
        "a,42,8,136,117\n"
        "l,43,21,131,36,40,45,39,118\n",
        encoding="utf-8",
    )

    result = parse_csv(source)

    assert result.accepted == 3
    assert result.rejected == 0
    assert result.values["E"] == [[37.0]]
    assert result.values["A"] == [[42.0], [136.0]]
    assert result.values["L"] == [[43.0], [131.0], [40.0], [39.0]]
