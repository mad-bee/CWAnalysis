from pathlib import Path

import matplotlib.pyplot as plt

from cw_analyser.models import ParseResult, ReportConfig
from cw_analyser.morse import MORSE
from cw_analyser.plotting import _draw_character_axis
from cw_analyser.statistics import analyse


def test_secondary_axis_is_exactly_one_third_of_primary():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[60, 61], [180, 183]]
    session = analyse(ParseResult(values, 2, 0), Path("test.csv"))
    fig, axis = plt.subplots()
    _draw_character_axis(axis, session.characters[0], session, ReportConfig(), detail=True)
    fig.canvas.draw()
    secondary = axis.child_axes[0]
    assert secondary.get_ylim()[0] == axis.get_ylim()[0] / 3
    assert secondary.get_ylim()[1] == axis.get_ylim()[1] / 3
    plt.close(fig)


def test_summary_axis_reserves_four_positions_for_short_character():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["E"] = [[60, 61]]
    session = analyse(ParseResult(values, 2, 0), Path("test.csv"))
    fig, axis = plt.subplots()
    _draw_character_axis(axis, session.characters[0], session, ReportConfig(), detail=False, fixed_positions=4)
    assert axis.get_xlim() == (0.5, 4.5)
    assert list(axis.get_xticks()) == [1, 2, 3, 4]
    plt.close(fig)
