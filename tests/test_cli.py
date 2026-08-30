import argparse
import json

from cw_analyser.cli import MAX_INPUT_FILES, _config, build_parser


def test_json_config_is_used_when_cli_option_is_absent(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"plot_type": "strip", "delimiter": ";", "dpi": 120}), encoding="utf-8")
    args = argparse.Namespace(config=config_file, plot_type=None, outlier_method=None, page_size=None,
                              dpi=None, units=None, delimiter=None, hide_points=False,
                              hide_outliers=False, hide_reference_lines=False, fixed_scales=False)
    config = _config(args)
    assert config.plot_type == "strip"
    assert config.delimiter == ";"
    assert config.dpi == 120


def test_cli_accepts_multiple_input_files():
    args = build_parser().parse_args(["first.csv", "second.csv"])
    assert [str(path) for path in args.inputs] == ["first.csv", "second.csv"]
    assert MAX_INPUT_FILES == 100
