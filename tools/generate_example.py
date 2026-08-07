"""Generate the deterministic 500-letter demonstration session."""

from __future__ import annotations

import csv
import random
from pathlib import Path

from cw_analyser.morse import MORSE


def main() -> None:
    rng = random.Random(890)
    output = Path(__file__).resolve().parents[1] / "examples" / "sample_500_letters.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Character", "Element1", "Element2", "Element3", "Element4"])
        for record in range(500):
            character = rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            timings = []
            for position, symbol in enumerate(MORSE[character]):
                base = 60.0 if symbol == "." else 180.0
                # Deliberate, visible technique signatures for demonstration.
                if character == "C" and position == 3 and symbol == ".":
                    base *= 0.88
                if character == "G" and symbol == "-":
                    base *= 1.08
                if character == "L" and position == len(MORSE[character]) - 1:
                    base *= 0.90
                if character == "Q" and position > 0:
                    base *= 1.0 + position * 0.025
                timing = rng.gauss(base, 2.4 if symbol == "." else 6.0)
                if rng.random() < 0.008:
                    timing *= rng.choice((0.72, 1.32))
                timings.append(f"{timing:.1f}")
            writer.writerow([character, *timings])
    print(f"Wrote {output} (500 records)")


if __name__ == "__main__":
    main()

