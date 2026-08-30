from pathlib import Path

import matplotlib.pyplot as plt

from cw_analyser.models import ParseResult, ReportConfig
from cw_analyser.morse import MORSE
from cw_analyser.plotting import _draw_character_axis, _special_dah_values
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


def test_character_axes_use_individual_limits_by_default():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[50, 60], [150, 180]]
    values["T"] = [[300, 360]]
    session = analyse(ParseResult(values, 4, 0), Path("test.csv"))
    config = ReportConfig()
    fig, (axis_a, axis_t) = plt.subplots(1, 2)

    _draw_character_axis(axis_a, session.characters[0], session, config, detail=True)
    _draw_character_axis(axis_t, session.characters[1], session, config, detail=True)
    assert axis_a.get_ylim() != axis_t.get_ylim()
    plt.close(fig)


def test_fixed_character_axes_share_optimised_session_limits():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[50, 60], [150, 180]]
    values["T"] = [[300, 360]]
    session = analyse(ParseResult(values, 4, 0), Path("test.csv"))
    config = ReportConfig(fixed_scales=True)
    fig, (axis_a, axis_t) = plt.subplots(1, 2)

    _draw_character_axis(axis_a, session.characters[0], session, config, detail=True)
    _draw_character_axis(axis_t, session.characters[1], session, config, detail=True)
    fig.canvas.draw()

    assert axis_a.get_ylim() == axis_t.get_ylim()
    assert axis_a.get_ylim() == (139.5, 370.5)
    assert axis_a.child_axes[0].get_ylim() == (46.5, 123.5)
    plt.close(fig)


def test_special_dah_populations_use_last_dah_and_each_adjacent_pair():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["M"] = [[101], [102]]
    values["W"] = [[50], [201], [202]]
    values["O"] = [[301], [302], [303]]
    session = analyse(ParseResult(values, 3, 0), Path("test.csv"))
    last_dahs, first_pair_dahs = _special_dah_values(session)
    assert last_dahs == [102.0, 303.0, 202.0]
    assert first_pair_dahs == [101.0, 301.0, 302.0, 201.0]
