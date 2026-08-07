from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path

_mpl_config = Path(tempfile.gettempdir()) / "cw-analysis-matplotlib"
_mpl_config.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_config))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .models import CharacterAnalysis, ReportConfig, SessionAnalysis


def character_plot(character: CharacterAnalysis, session: SessionAnalysis,
                   config: ReportConfig, output: Path) -> Path:
    """Write a standalone full character plot with linked 3:1 axes."""
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots(figsize=(8.0, 4.4))
    _draw_character_axis(axis, character, session, config, detail=True)
    fig.suptitle(
        f"Character {character.character}   Pattern {character.pattern}   Samples {character.sample_count}",
        fontsize=13, fontweight="bold",
    )
    fig.subplots_adjust(left=0.10, right=0.90, top=0.86, bottom=0.18)
    fig.savefig(output, dpi=config.dpi, facecolor="white")
    plt.close(fig)
    return output


def overview_plot(session: SessionAnalysis, config: ReportConfig, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.8))
    all_dits = [v for c in session.characters for e in c.elements if e.element_type == "dit" for v in e.values]
    all_dahs = [v for c in session.characters for e in c.elements if e.element_type == "dah" for v in e.values]
    last_dahs, first_pair_dahs = _special_dah_values(session)
    panels = (
        (axes[0, 0], all_dits, "All dits", "dit", session.median_dit),
        (axes[0, 1], all_dahs, "All dahs", "dah", session.median_dit * 3),
        (axes[1, 0], last_dahs, "Last dah in a letter", "dah", session.median_dit * 3),
        (axes[1, 1], first_pair_dahs, "First dah in adjacent dah pair", "dah", session.median_dit * 3),
    )
    for axis, values, title, kind, ideal in panels:
        _draw_overview_histogram(axis, values, title, kind, ideal, session, config)
    fig.suptitle("Overall element distributions", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96), h_pad=1.5, w_pad=1.2)
    fig.savefig(output, dpi=config.dpi, facecolor="white")
    plt.close(fig)
    return output


def _special_dah_values(session: SessionAnalysis) -> tuple[list[float], list[float]]:
    """Return final-dah values and first-dah values from adjacent pairs for A-Z."""
    last_dahs: list[float] = []
    first_pair_dahs: list[float] = []
    for character in session.characters:
        if not character.character.isalpha():
            continue
        dah_positions = [index for index, symbol in enumerate(character.pattern) if symbol == "-"]
        if dah_positions:
            last_dahs.extend(character.elements[dah_positions[-1]].values)
        for index in range(len(character.pattern) - 1):
            if character.pattern[index:index + 2] == "--":
                first_pair_dahs.extend(character.elements[index].values)
    return last_dahs, first_pair_dahs


def _draw_overview_histogram(axis, values: list[float], title: str, kind: str, ideal: float,
                             session: SessionAnalysis, config: ReportConfig) -> None:
    if values:
        axis.hist(values, bins="auto", color=config.colours[kind], alpha=0.8, edgecolor="white")
        median = float(np.median(values))
        axis.axvline(median, color=config.colours["median"], linewidth=1.3, label=f"Median {median:.2f}")
        if config.show_reference_lines and math.isfinite(ideal):
            axis.axvline(ideal, color=config.colours["ideal"], linestyle="--", label=f"Ideal {ideal:.2f}")
        axis.legend(fontsize=6, frameon=False)
        title = f"{title} (n={len(values):,})"
    else:
        axis.text(0.5, 0.5, "No matching measurements", transform=axis.transAxes,
                  ha="center", va="center", fontsize=8, color="#7B8794")
    axis.set_title(title, fontsize=9)
    axis.set_xlabel(config.units, fontsize=7)
    axis.set_ylabel("Measurements", fontsize=7)
    axis.tick_params(labelsize=7)
    axis.grid(axis="y", alpha=0.25)


def summary_grid(characters: list[CharacterAnalysis], session: SessionAnalysis,
                 config: ReportConfig, output: Path, labels: str) -> Path:
    """Write a category overview, retaining labelled slots with no samples."""
    output.parent.mkdir(parents=True, exist_ok=True)
    by_label = {character.character: character for character in characters}
    is_numbers = labels == "0123456789"
    rows = 2 if is_numbers else 6
    fixed_positions = 5 if is_numbers else 4
    fig_height = 6.0 if is_numbers else 15.2
    fig, axes = plt.subplots(rows, 5, figsize=(11.0, fig_height), squeeze=False)
    for axis, label in zip(axes.flat, labels):
        character = by_label.get(label)
        if character is None:
            _draw_empty_summary_axis(axis, label, fixed_positions)
        else:
            _draw_character_axis(axis, character, session, config, detail=False, fixed_positions=fixed_positions)
    for axis in list(axes.flat)[len(labels):]:
        axis.axis("off")
    fig.subplots_adjust(left=0.055, right=0.945, top=0.96 if is_numbers else 0.985,
                        bottom=0.08 if is_numbers else 0.035, hspace=0.62 if is_numbers else 0.70,
                        wspace=0.60)
    fig.savefig(output, dpi=config.dpi, facecolor="white")
    plt.close(fig)
    return output


def detail_sheet(characters: list[CharacterAnalysis], session: SessionAnalysis,
                 config: ReportConfig, output: Path, start: int = 0) -> Path:
    """Write a report sheet containing six readable character plots."""
    output.parent.mkdir(parents=True, exist_ok=True)
    selected = characters[start:start + 6]
    fig, axes = plt.subplots(3, 2, figsize=(8.1, 10.4), squeeze=False)
    for axis, character in zip(axes.flat, selected):
        _draw_character_axis(axis, character, session, config, detail=True)
        axis.set_title(
            f"{character.character}  {character.pattern}  n={character.sample_count}  consistency={character.consistency_score:.1f}%",
            fontsize=9, fontweight="bold", pad=5,
        )
        note = character.position_notes[0]
        if len(note) > 68:
            note = note[:65] + "..."
        axis.text(0.0, -0.29, f"Best {character.best_element} | Worst {character.worst_element} | {note}",
                  transform=axis.transAxes, fontsize=5.7, color="#425466", va="top")
    for axis in list(axes.flat)[len(selected):]:
        axis.axis("off")
    fig.subplots_adjust(left=0.085, right=0.915, top=0.985, bottom=0.055, hspace=0.64, wspace=0.38)
    fig.savefig(output, dpi=config.dpi, facecolor="white")
    plt.close(fig)
    return output


def _draw_character_axis(axis, character: CharacterAnalysis, session: SessionAnalysis,
                         config: ReportConfig, detail: bool, fixed_positions: int | None = None) -> None:
    """Plot dahs on the primary scale and dits transformed by exactly x3.

    The right secondary axis applies the inverse transform, so a value at 180 on
    the left aligns exactly with 60 on the right.
    """
    rng = np.random.default_rng(0)
    for element in character.elements:
        values = np.asarray(element.values, dtype=float)
        plotted = values if element.element_type == "dah" else values * 3.0
        _draw_element(axis, element.position, plotted, np.asarray(element.outlier_mask),
                      element.element_type, config, rng, detail)

    all_values = [v if e.element_type == "dah" else v * 3.0
                  for e in character.elements for v in e.values]
    _set_limits(axis, all_values)
    if config.show_reference_lines and math.isfinite(session.median_dit):
        axis.axhline(session.median_dit * 3.0, color=config.colours["ideal"], linestyle="--",
                    linewidth=0.9 if detail else 0.55, zorder=1)
    positions = np.arange(1, len(character.elements) + 1)
    if detail:
        axis.set_xticks(positions, [f"{i} {symbol}" for i, symbol in enumerate(character.pattern, 1)])
        axis.set_xlabel("Element position", fontsize=7)
        axis.set_ylabel(f"Dah ({config.units})", color=config.colours["dah"], fontsize=7)
        secondary = axis.secondary_yaxis("right", functions=(lambda value: value / 3.0, lambda value: value * 3.0))
        secondary.set_ylabel(f"Dit ({config.units})", color=config.colours["dit"], fontsize=7)
        secondary.tick_params(axis="y", labelsize=6, colors=config.colours["dit"])
        axis.tick_params(axis="both", labelsize=6)
    else:
        axis.set_title(f"{character.character}  {character.pattern}", fontsize=7, fontweight="bold", pad=2)
        displayed_positions = fixed_positions or len(character.elements)
        axis.set_xlim(0.5, displayed_positions + 0.5)
        axis.set_xticks(np.arange(1, displayed_positions + 1))
        axis.set_xticklabels([])
        axis.tick_params(axis="both", labelsize=4, length=1.5, pad=1)
        secondary = axis.secondary_yaxis("right", functions=(lambda value: value / 3.0, lambda value: value * 3.0))
        secondary.tick_params(axis="y", labelsize=4, length=1.5, pad=1, colors=config.colours["dit"])
    axis.tick_params(axis="y", colors=config.colours["dah"])
    axis.grid(axis="y", color="#D7DCE2", linewidth=0.45, alpha=0.8)
    axis.set_axisbelow(True)


def _draw_element(axis, position: int, values: np.ndarray, mask: np.ndarray, kind: str,
                  config: ReportConfig, rng, detail: bool) -> None:
    colour = config.colours[kind]
    non_outliers = values[~mask]
    outliers = values[mask]
    width = 0.48 if detail else 0.56
    if config.plot_type == "violin" and len(values) >= 2 and np.ptp(values) > 0:
        violin = axis.violinplot(values, positions=[position], widths=width, showextrema=False)
        for body in violin["bodies"]:
            body.set_facecolor(colour)
            body.set_edgecolor(colour)
            body.set_alpha(0.35)
    elif config.plot_type == "histogram":
        bins = min(8, max(3, round(math.sqrt(len(values)))))
        counts, edges = np.histogram(values, bins=bins)
        centres = (edges[:-1] + edges[1:]) / 2.0
        half_widths = counts / max(1, counts.max()) * width / 2.0
        heights = np.diff(edges) * 0.82
        axis.barh(centres, half_widths * 2.0, height=heights, left=position - half_widths,
                  color=colour, edgecolor=colour, linewidth=0.5, alpha=0.38, zorder=2)
    elif config.plot_type == "strip":
        pass
    else:
        axis.boxplot(values, positions=[position], widths=width, patch_artist=True, showfliers=False,
                     boxprops={"facecolor": colour, "alpha": 0.38, "edgecolor": colour, "linewidth": 0.7},
                     medianprops={"color": config.colours["median"], "linewidth": 1.0},
                     whiskerprops={"color": colour, "linewidth": 0.7},
                     capprops={"color": colour, "linewidth": 0.7})
    if config.show_points and detail:
        jitter = rng.uniform(-0.14, 0.14, len(non_outliers))
        axis.scatter(position + jitter, non_outliers, s=5, color=config.colours["point"], alpha=0.28,
                     linewidths=0, zorder=3)
    if config.show_outliers and len(outliers):
        jitter = rng.uniform(-0.12, 0.12, len(outliers))
        axis.scatter(position + jitter, outliers, s=12 if detail else 5, color=config.colours["outlier"],
                     edgecolors="white", linewidths=0.25, zorder=4)


def _set_limits(axis, values: list[float]) -> None:
    if not values:
        return
    low, high = min(values), max(values)
    pad = max((high - low) * 0.12, abs(high) * 0.025, 1e-6)
    axis.set_ylim(max(0, low - pad), high + pad)


def _draw_empty_summary_axis(axis, label: str, positions: int) -> None:
    axis.set_title(label, fontsize=7, fontweight="bold", pad=2)
    axis.set_xlim(0.5, positions + 0.5)
    axis.set_ylim(0, 1)
    axis.set_xticks(np.arange(1, positions + 1))
    axis.set_xticklabels([])
    axis.set_yticks([])
    axis.text(0.5, 0.5, "No samples", transform=axis.transAxes, ha="center", va="center",
              fontsize=6, color="#7B8794")
    axis.grid(axis="x", color="#E5E9ED", linewidth=0.4)
