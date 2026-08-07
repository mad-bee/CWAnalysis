import math
from pathlib import Path

from cw_analyser.models import ParseResult
from cw_analyser.morse import MORSE
from cw_analyser.statistics import analyse, calculate_element


def test_element_statistics_and_iqr_outlier():
    element = calculate_element("E", ".", 1, ".", [58, 59, 60, 61, 62, 120])
    assert element.count == 6
    assert element.minimum == 58
    assert element.maximum == 120
    assert element.outlier_count == 1
    assert math.isclose(element.median, 60.5)
    assert element.confidence_interval_low < element.mean < element.confidence_interval_high


def test_session_ratio_wpm_and_character_positions():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[60, 60, 60], [180, 180, 180]]
    parsed = ParseResult(values, 3, 0)
    session = analyse(parsed, Path("test.csv"))
    assert session.median_dit == 60
    assert session.median_dah == 180
    assert session.dash_dit_ratio == 3
    assert session.estimated_wpm == 20
    assert session.characters[0].elements[0].position == 1
    assert session.characters[0].elements[1].position == 2

