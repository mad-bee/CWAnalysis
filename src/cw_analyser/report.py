from __future__ import annotations

import csv
import html
import math
import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageTemplate,
                                Paragraph, PageBreak, Spacer, Table, TableStyle)

from .models import ReportConfig, SessionAnalysis
from .plotting import detail_sheet, overview_plot, summary_grid


def write_summary_csv(session: SessionAnalysis, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["character", "pattern", "position", "element_type", "count", "minimum", "maximum",
              "range", "mean", "median", "mode", "variance", "standard_deviation", "mad",
              "percentile_25", "percentile_75", "iqr", "coefficient_of_variation_percent",
              "confidence_interval_low", "confidence_interval_high", "skewness", "kurtosis",
              "outlier_count", "outlier_rate_percent", "character_consistency_score"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for character in session.characters:
            for e in character.elements:
                writer.writerow({
                    "character": e.character, "pattern": e.pattern, "position": e.position,
                    "element_type": e.element_type, "count": e.count, "minimum": _n(e.minimum),
                    "maximum": _n(e.maximum), "range": _n(e.value_range), "mean": _n(e.mean),
                    "median": _n(e.median), "mode": "" if e.mode is None else _n(e.mode),
                    "variance": _n(e.variance), "standard_deviation": _n(e.standard_deviation),
                    "mad": _n(e.mad), "percentile_25": _n(e.percentile_25),
                    "percentile_75": _n(e.percentile_75), "iqr": _n(e.iqr),
                    "coefficient_of_variation_percent": _n(e.coefficient_of_variation),
                    "confidence_interval_low": _n(e.confidence_interval_low),
                    "confidence_interval_high": _n(e.confidence_interval_high),
                    "skewness": _n(e.skewness), "kurtosis": _n(e.kurtosis),
                    "outlier_count": e.outlier_count, "outlier_rate_percent": _n(e.outlier_rate * 100),
                    "character_consistency_score": _n(character.consistency_score),
                })
    return path


def write_error_csv(issues, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["line", "reason", "row"])
        writer.writerows((i.line, i.reason, i.row) for i in issues)
    return path


def write_pdf(session: SessionAnalysis, path: Path, config: ReportConfig) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    page_size = A4 if config.page_size == "A4" else LETTER
    styles = _styles()
    with tempfile.TemporaryDirectory(prefix="cw-report-") as temp_name:
        temp = Path(temp_name)
        overview = overview_plot(session, config, temp / "overview.png")
        summary_paths = [
            ("Letter Timing Summary", "A-Z; each panel reserves four element positions.",
             summary_grid(session.characters, session, config, temp / "summary_letters.png", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 240 * mm),
            ("Number Timing Summary", "0-9; each panel reserves all five element positions.",
             summary_grid(session.characters, session, config, temp / "summary_numbers.png", "0123456789"), 95 * mm),
        ]
        detail_paths = [
            detail_sheet(session.characters, session, config, temp / f"details_{start // 6 + 1}.png", start)
            for start in range(0, len(session.characters), 6)
        ]
        doc = _NumberedDoc(str(path), pagesize=page_size, rightMargin=15 * mm, leftMargin=15 * mm,
                           topMargin=16 * mm, bottomMargin=15 * mm,
                           title="CW Analysis")
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="content")
        doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=_header_footer))
        story = _overview_story(session, overview, styles, config)
        for title, description, plot, image_height in summary_paths:
            story.extend([
                Paragraph(title, styles["Title"]),
                Paragraph(description + " Dah timing is on the left and the linked 3:1 dit scale is on the right.", styles["SubTitle"]),
                Spacer(1, 2 * mm), Image(str(plot), width=174 * mm, height=image_height), PageBreak(),
            ])
        for index, plot in enumerate(detail_paths):
            story.extend([
                Paragraph("Detailed Character Analysis", styles["Title"]),
                Paragraph(f"Source data: {html.escape(str(session.source.resolve()))}", styles["SourcePath"]),
                Spacer(1, 2 * mm), Image(str(plot), width=174 * mm, height=223 * mm),
            ])
            if index != len(detail_paths) - 1:
                story.append(PageBreak())
        story.extend([PageBreak(), *_explanatory_notes(styles, config)])
        doc.build(story)
    return path


def _overview_story(session, overview, styles, config):
    stars = "*" * session.stars + "-" * (5 - session.stars)
    metrics = [
        ["Accepted characters", f"{session.accepted:,}", "Rejected records", f"{session.rejected:,}"],
        ["Median dit", _unit(session.median_dit, config.units), "Median dah", _unit(session.median_dah, config.units)],
        ["Dash/dit ratio", _n(session.dash_dit_ratio), "Estimated speed", f"{session.estimated_wpm:.1f} WPM" if session.estimated_wpm else "N/A"],
        ["Fist quality score", f"{session.overall_score:.1f}%", "Rating", stars],
    ]
    table = Table(metrics, colWidths=[42 * mm, 32 * mm, 42 * mm, 32 * mm])
    table.setStyle(_table_style())
    rejected = ", ".join(f"{reason}: {count}" for reason, count in sorted(session.issue_counts.items())) or "None"
    recommendations = _recommendations(session)
    return [
        Paragraph("CW Analysis", styles["Title"]),
        Paragraph(f"Source data: {html.escape(str(session.source.resolve()))}", styles["SourcePath"]), Spacer(1, 4 * mm),
        table, Spacer(1, 4 * mm), Image(str(overview), width=174 * mm, height=70 * mm),
        Spacer(1, 3 * mm), Paragraph("Rejected input", styles["Heading2"]),
        Paragraph(rejected, styles["BodyText"]), Spacer(1, 3 * mm),
        Paragraph("Recommendations", styles["Heading2"]),
        *[Paragraph(f"- {item}", styles["BodyText"]) for item in recommendations], PageBreak(),
    ]


def _recommendations(session):
    notes = []
    if math.isfinite(session.dash_dit_ratio) and abs(session.dash_dit_ratio - 3) > 0.15:
        notes.append(f"Review dash adjustment: the session ratio is {session.dash_dit_ratio:.2f}:1 versus the 3:1 reference.")
    high_cv = [(c.character, c.average_cv) for c in session.characters if c.average_cv > 12]
    if high_cv:
        text = ", ".join(f"{char} ({cv:.1f}%)" for char, cv in sorted(high_cv, key=lambda x: -x[1])[:5])
        notes.append(f"Prioritise characters with high average variation: {text}.")
    biased = [c.character for c in session.characters if not c.position_notes[0].startswith("No material") and len(c.elements) > 1]
    if biased:
        notes.append("Review position-dependent technique for: " + ", ".join(biased[:12]) + ".")
    return notes or ["Timing is stable against the configured thresholds; continue monitoring across longer sessions."]


def _explanatory_notes(styles, config):
    return [
        Paragraph("How to Read This Report", styles["Title"]),
        Paragraph("Axes and timing reference", styles["Heading2"]),
        Paragraph(
            f"Dah timing uses the red primary Y-axis on the left. Dit timing uses the blue secondary Y-axis on the right. "
            f"The axes are linked at exactly 3:1: a dah at 180 {config.units} is horizontally aligned with a dit at 60 {config.units}. "
            "This permits direct visual comparison without making dits and dahs appear to use the same numerical duration.",
            styles["NotesBody"],
        ),
        Paragraph(
            "The green dashed line marks the session median dit on the right axis and the corresponding ideal 3-times dah duration on the left. "
            "On the overview histograms, the black line is the observed median and the green line is the ideal timing reference.",
            styles["NotesBody"],
        ),
        Paragraph("Box-and-whisker plots", styles["Heading2"]),
        Paragraph("- The coloured box spans the 25th to 75th percentiles, also called the interquartile range (IQR).", styles["NotesBody"]),
        Paragraph("- The black line inside the box is the median for that character and element position.", styles["NotesBody"]),
        Paragraph("- The whiskers extend to the most extreme observations still within 1.5 IQR of the box.", styles["NotesBody"]),
        Paragraph("- Small grey points are individual measurements. Their horizontal jitter only prevents overlap; it has no timing meaning.", styles["NotesBody"]),
        Paragraph("- Orange points are outliers. With the default IQR method they fall below Q1 - 1.5 IQR or above Q3 + 1.5 IQR.", styles["NotesBody"]),
        Spacer(1, 2 * mm),
        Paragraph("Best, Worst and position bias", styles["Heading2"]),
        Paragraph(
            "Best 2 means element position 2 has the lowest coefficient of variation (standard deviation divided by mean) within that character. "
            "Worst 1 means position 1 has the highest coefficient of variation. These labels describe repeatability, not whether the median duration is closest to ideal. "
            "With equal variability, the first tied position is reported.",
            styles["NotesBody"],
        ),
        Paragraph(
            "A material first- or last-element bias is reported when its median differs by at least 5% from other elements of the same type in that character. "
            "For characters containing four or more elements, normalised timing drift is reported when the fitted change reaches 3% per position. "
            "Dahs are divided by three before that drift comparison.",
            styles["NotesBody"],
        ),
        Paragraph(
            "No material position bias detected means none of those practical thresholds was crossed. It does not prove that the positions are statistically identical, "
            "especially when the sample count is small.",
            styles["NotesBody"],
        ),
        Paragraph("Scores and supporting statistics", styles["Heading2"]),
        Paragraph(
            "The character consistency percentage combines average coefficient of variation and outlier rate. The overall fist-quality score also applies a penalty for "
            "departure from the ideal 3:1 median dah/dit ratio. Both are fixed, reproducible coaching indicators rather than calibrated scientific scores.",
            styles["NotesBody"],
        ),
        Paragraph(
            "n is the number of accepted occurrences of the character. Complete per-position values - including mean, median, variance, standard deviation, MAD, quartiles, "
            "IQR, confidence interval, skewness, kurtosis and outlier rate - are exported to CW_Summary.csv beside this PDF.",
            styles["NotesBody"],
        ),
    ]


class _NumberedDoc(BaseDocTemplate):
    pass


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#606A78"))
    canvas.drawString(doc.leftMargin, 8 * mm, "CW Analysis")
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _styles():
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#173A5E")
    styles["Title"].fontSize = 18
    styles["Title"].leading = 21
    styles.add(ParagraphStyle("SubTitle", parent=styles["Normal"], alignment=TA_CENTER,
                              textColor=colors.HexColor("#536273"), fontSize=9, leading=12))
    styles.add(ParagraphStyle("SourcePath", parent=styles["Normal"], alignment=TA_CENTER,
                              textColor=colors.HexColor("#536273"), fontSize=7.5, leading=10,
                              wordWrap="CJK"))
    styles.add(ParagraphStyle("SmallBody", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(ParagraphStyle("NotesBody", parent=styles["BodyText"], fontSize=9, leading=12,
                              spaceAfter=3))
    return styles


def _table_style(header=False, font_size=8):
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#243342")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BAC3CC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173A5E")),
                     ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    else:
        commands += [("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold")]
    return TableStyle(commands)


def _n(value):
    return "" if value is None or not math.isfinite(float(value)) else f"{float(value):.4f}".rstrip("0").rstrip(".")


def _unit(value, units):
    return f"{_n(value)} {units}" if math.isfinite(value) else "N/A"
