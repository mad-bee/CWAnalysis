"""Regenerate the four README plot examples from the 500-letter sample."""

from __future__ import annotations

from pathlib import Path

from cw_analyser.models import ReportConfig
from cw_analyser.parser import parse_csv
from cw_analyser.plotting import character_plot
from cw_analyser.statistics import analyse


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "examples" / "sample_500_letters.csv"
    output = root / "docs" / "images"
    output.mkdir(parents=True, exist_ok=True)
    session = analyse(parse_csv(source), source)
    character = next(item for item in session.characters if item.character == "C")
    for plot_type in ("box", "violin", "strip", "histogram"):
        config = ReportConfig(plot_type=plot_type, dpi=140)
        character_plot(character, session, config, output / f"plot-{plot_type}.png")
        print(f"Wrote plot-{plot_type}.png")


if __name__ == "__main__":
    main()
