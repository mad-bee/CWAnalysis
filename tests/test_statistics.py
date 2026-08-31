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
    assert math.isclose(session.dit_standard_deviation_percent, 0.0)
    assert math.isclose(session.dah_standard_deviation_percent, 0.0)


def test_spacing_analysis_separates_intra_and_inter_character_spaces():
    values = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    spaces = {char: [[] for _ in pattern] for char, pattern in MORSE.items()}
    values["A"] = [[60, 62], [180, 186]]
    spaces["A"] = [[55, 65], [170, 190]]
    session = analyse(ParseResult(values, 2, 0, spaces=spaces), Path("test.csv"))

    assert len(session.spacing) == 1
    assert [item.space_type for item in session.spacing[0].spaces] == ["intra-character", "inter-character"]
    assert session.median_intra_character_space == 60
    assert session.median_inter_character_space == 180
    assert session.spacing[0].spaces[0].coefficient_of_variation > 0

