from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import ReportConfig
from .parser import parse_csv
from .report import write_error_csv, write_pdf, write_summary_csv
from .statistics import analyse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyse Morse element timing per character position.")
    parser.add_argument("input", type=Path, help="CSV input file")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--delimiter")
    parser.add_argument("--units")
    parser.add_argument("--plot-type", choices=["box", "violin", "strip", "histogram"])
    parser.add_argument("--outlier-method", choices=["iqr", "modified-z"])
    parser.add_argument("--page-size", choices=["A4", "LETTER"])
    parser.add_argument("--dpi", type=int)
    parser.add_argument("--hide-points", action="store_true")
    parser.add_argument("--hide-outliers", action="store_true")
    parser.add_argument("--hide-reference-lines", action="store_true")
    parser.add_argument("--config", type=Path, help="Optional JSON configuration file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.input.is_file():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 2
    try:
        config = _config(args)
        parsed = parse_csv(args.input, config.delimiter)
        if not parsed.accepted:
            print("error: no valid records were found", file=sys.stderr)
            if parsed.issues:
                write_error_csv(parsed.issues, args.output_dir / "CW_Errors.csv")
            return 1
        session = analyse(parsed, args.input, config.outlier_method, config.units)
        pdf = write_pdf(session, args.output_dir / "pdf" / "CW_Analysis.pdf", config)
        summary = write_summary_csv(session, args.output_dir / "CW_Summary.csv")
        errors = write_error_csv(parsed.issues, args.output_dir / "CW_Errors.csv")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Analysed {session.accepted:,} characters; rejected {session.rejected:,} records.")
    print(f"PDF: {pdf}")
    print(f"Summary: {summary}")
    print(f"Errors: {errors}")
    return 0


def _config(args) -> ReportConfig:
    values = {}
    if args.config:
        with args.config.open("r", encoding="utf-8") as stream:
            values = json.load(stream)
        allowed = set(ReportConfig.__dataclass_fields__)
        unknown = set(values) - allowed
        if unknown:
            raise ValueError("unknown configuration keys: " + ", ".join(sorted(unknown)))
    cli = {key: value for key, value in {
        "plot_type": args.plot_type, "outlier_method": args.outlier_method, "page_size": args.page_size,
        "dpi": args.dpi, "units": args.units, "delimiter": args.delimiter,
    }.items() if value is not None}
    if args.hide_points:
        cli["show_points"] = False
    if args.hide_outliers:
        cli["show_outliers"] = False
    if args.hide_reference_lines:
        cli["show_reference_lines"] = False
    values.update(cli)
    candidate = ReportConfig(**values)
    if len(candidate.delimiter) != 1:
        raise ValueError("delimiter must be one character")
    if candidate.dpi < 72 or candidate.dpi > 600:
        raise ValueError("dpi must be between 72 and 600")
    return candidate
