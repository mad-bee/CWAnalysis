# CWAnalysis

Python 3 application that validates recorded CW timing CSV files, analyses every element position independently, and creates a printable PDF plus machine-readable statistics.

## Features

- Complete International Morse lookup for A-Z and 0-9.
- Streaming CSV ingestion: records are validated one at a time, so large inputs do not need a second in-memory copy.
- Per-character and per-position descriptive statistics, 95% confidence intervals, skewness, excess kurtosis, MAD, CV, and outlier counts.
- IQR or modified Z-score outlier detection.
- Linked dual-axis plots: dah timing uses the primary left axis and dit timing uses the secondary right axis, fixed at an exact 3:1 scale. Plots retain reproducible jitter, coloured element types, outliers, medians, and ideal timing references.
- Separate visual summary pages for A-Z and 0-9. Letter panels reserve four element positions; number panels reserve five. Missing characters remain visible as labelled `No samples` panels. Detailed report pages contain six plots each.
- Character consistency, position-bias observations, estimated WPM for millisecond input, and a transparent heuristic fist-quality score.
- A4 or Letter PDF report, summary CSV, and rejected-row CSV.
- Box, violin, strip, and compact histogram/rug plot modes.

The quality and consistency scores are heuristic coaching indicators, not calibrated scientific or medical measures. A report generated without timestamps does not include trend analysis or session duration; the current CSV format has no time field.

## Install

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -e ".[test]"
```

Python 3.10 or later is required.

## Run

```powershell
.venv\Scripts\cw-analyse examples\sample.csv
```

A deterministic 500-letter example is also included:

```powershell
.venv\Scripts\cw-analyse examples\sample_500_letters.csv -o output\example_500
```

Outputs:

```text
output/
  CW_Errors.csv
  CW_Summary.csv
  pdf/CW_Analysis.pdf
```

The first row may be a `Character,...` header. All later rows must contain exactly the number of finite positive timing values defined by that character's Morse pattern. Invalid rows are skipped and included in `CW_Errors.csv`; up to 1,000 detailed error rows are retained while all rejection counts remain accurate.

Useful options:

```text
--units ms|ticks
--delimiter ";"
--plot-type box|violin|strip|histogram
--outlier-method iqr|modified-z
--page-size A4|LETTER
--dpi 72..600
--hide-points --hide-outliers --hide-reference-lines
--config config.json
```

See all options with `cw-analyse --help`. `config.example.json` contains the full colour scheme. Explicit command-line values take precedence over values read from the JSON configuration file.

## Tests

```powershell
.venv\Scripts\python -m pytest
```

## Notes on scale

The analyser retains accepted timing measurements because plots and exact quantiles require the observations. At 100,000 typical characters this remains comfortably below the 500 MB target. CSV parsing itself is streaming; malformed rows never terminate the run.

Fist score starts at 100 and applies penalties for aggregate CV, departure from a 3:1 median dash/dit ratio, and outlier frequency. Character consistency similarly combines average CV and outlier rate. Fixed formulas make repeated runs reproducible, and plot jitter uses a fixed random seed.
