import csv
from pathlib import Path

from cw_analyser.models import ParseResult, ReportConfig
from cw_analyser.morse import MORSE
from cw_analyser.report import write_pdf, write_summary_csv
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


def test_pdf_adds_spacing_pages_and_front_page_sd_percentages(tmp_path: Path):
    from pypdf import PdfReader

    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    spaces = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[58, 60, 62], [174, 180, 186]]
    spaces["A"] = [[55, 60, 65], [170, 180, 190]]
    session = analyse(ParseResult(values, 3, 0, spaces=spaces), Path("markspace.csv"))

    output = write_pdf(session, tmp_path / "report.pdf", ReportConfig(dpi=72))
    text = "\n".join(page.extract_text() or "" for page in PdfReader(output).pages)

    assert "Dit SD (% of mean)" in text
    assert "Dah SD (% of mean)" in text
    assert "Spacing Analysis" in text
    assert "Detailed Character Spacing" in text


def test_mark_only_pdf_omits_spacing_pages(tmp_path: Path):
    from pypdf import PdfReader

    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[60, 61], [180, 183]]
    session = analyse(ParseResult(values, 2, 0), Path("marks.csv"))

    output = write_pdf(session, tmp_path / "report.pdf", ReportConfig(dpi=72))
    text = "\n".join(page.extract_text() or "" for page in PdfReader(output).pages)

    assert "Spacing Analysis" not in text
    assert "Detailed Character Spacing" not in text

