# CWAnalysis

Python 3 application that validates recorded CW timing CSV files, analyses every element position independently, and creates a printable PDF plus machine-readable statistics.

One or more CSV recordings can be supplied in the same command. Their accepted measurements are combined into a single analysis and report; a maximum of 100 input files is supported per run. The character-record count is not capped at 5,000: files are parsed as streams, and the retained measurements are limited only by available memory.

## Features

- Complete International Morse lookup for A-Z and 0-9.
- Streaming CSV ingestion: records are validated one at a time, so large inputs do not need a second in-memory copy.
- Per-character and per-position descriptive statistics, 95% confidence intervals, skewness, excess kurtosis, MAD, CV, and outlier counts.
- IQR or modified Z-score outlier detection.
- Linked dual-axis plots: dah timing uses the primary left axis and dit timing uses the secondary right axis, fixed at an exact 3:1 scale. Character plots use individually optimised ranges by default; optional fixed scales use one data-fitted range across the session for direct comparison. Plots retain reproducible jitter, coloured element types, outliers, medians, and ideal timing references.
- First-page histograms for all dits, all dahs, the final dah in each letter, and the first dah of every adjacent dah pair.
- Separate visual summary pages for A-Z and 0-9. Letter panels reserve four element positions; number panels reserve five. Missing characters remain visible as labelled `No samples` panels. Detailed report pages contain six plots each.
- Character consistency, position-bias observations, estimated WPM for millisecond input, and a transparent heuristic fist-quality score.
- Separate intra-character and inter-character spacing pages for PCWFistCheck mark-space exports. Detailed plots use linked axes at the ideal 3:1 inter/intra ratio; existing element-timing plots remain unchanged.
- Front-page dit and dah standard deviation percentages for a quick view of overall mark consistency.
- A4 or Letter PDF report, summary CSV, and rejected-row CSV.
- Box, violin, strip, and compact histogram/rug plot modes.

The quality and consistency scores are heuristic coaching indicators, not calibrated scientific or medical measures. A report generated without timestamps does not include trend analysis or session duration; the current CSV format has no time field.

## Plot examples

All plots analyse each element position separately. Dah timing uses the red left axis, dit timing uses the blue right axis, and the axes are linked at the ideal 3:1 ratio. The examples below show the same character C data in each available mode.

| Box (`--plot-type box`) | Violin (`--plot-type violin`) |
| --- | --- |
| ![Box-and-whisker plot](docs/images/plot-box.png) | ![Violin plot](docs/images/plot-violin.png) |
| **Strip (`--plot-type strip`)** | **Histogram (`--plot-type histogram`)** |
| ![Strip plot](docs/images/plot-strip.png) | ![Per-position histogram](docs/images/plot-histogram.png) |

- **Box:** median, quartiles, 1.5-IQR whiskers, individual measurements, and orange outliers.
- **Violin:** a smoothed view of each position's distribution, with measurements and outliers overlaid.
- **Strip:** every measurement shown directly with stable horizontal jitter to reduce overlap.
- **Histogram:** compact mirrored frequency bars for each element position, with measurements and outliers overlaid.

Select a mode with either the executable or Python command:

```powershell
.\CWAnalysis.exe input.csv --plot-type violin
.\.venv\Scripts\cw-analyser.exe input.csv --plot-type histogram
```

The documentation images can be regenerated with:

```powershell
.\.venv\Scripts\python.exe tools\generate_readme_plots.py
```

## Full example report

View the complete report generated from the included 500-letter demonstration session:

- [CW Analysis full example PDF](docs/examples/CW_Analysis_Example.pdf)
- [500-letter source CSV](examples/sample_500_letters.csv)

The example includes the session overview, A-Z and 0-9 summary pages, detailed per-character plots, position-bias observations, and the explanatory notes appendix.

## CW sending practice text

[The Quixotic Jazz Expedition](examples/The%20Quixotic%20Jazz%20Expedition.pdf) is a four-page story provided as practice copy for sending CW. It contains a varied mix of words and at least 100 occurrences of every letter from A to Z, giving users repeated practice with both common and less frequently encountered characters. Send it at a comfortable speed, record the session, and analyse the resulting timing CSV with CWAnalysis to track consistency and identify characters or element positions that need more practice.

The PDF is source material to send, not an input file for CWAnalysis; the analyser accepts the recorded CSV produced during the practice session.

The diamond symbols (`◆`) mark breaks in the practice text. Because PCWFistCheck limits the number of characters in a recording, stop at each diamond and export the mark-space data from PCWFistCheck before continuing with the next section. CWAnalysis can combine the exported CSV files into a single analysis.

## What the files and folders are for

If you only want to analyse your own recordings, you do not need to understand or edit the Python source files. The files you are most likely to use are:

| File or folder | Purpose |
| --- | --- |
| `CWAnalysis.exe` | The ready-to-run Windows program supplied on the GitHub Releases page. It is not stored in the source download. |
| `config.example.json` | An optional example configuration. Copy it to a new file such as `config.json`, change the settings you want, and select it with `--config config.json`. The original example can then remain unchanged for reference. |
| `examples/sample.csv` | A small input recording for checking that the installation works. |
| `examples/sample_500_letters.csv` | A larger, repeatable example used to demonstrate a full report. |
| `examples/The Quixotic Jazz Expedition.pdf` | Practice text to send as CW. This PDF is reading material, not analyser input. |
| `README.md` | This guide. GitHub displays it on the project home page. |
| `output/` | The default results folder created when the analyser runs. It contains the PDF report and summary/error CSV files. |

The remaining files are mainly for developers or people building the program themselves:

| File or folder | Purpose |
| --- | --- |
| `pyproject.toml` | Defines the Python project, required packages, version, test settings, and the `cw-analyser` command. `pip install -e .` reads this file. |
| `build_windows.ps1` | PowerShell script that installs the build tools and creates the Windows executable. |
| `CWAnalysis.spec` | PyInstaller recipe used by `build_windows.ps1` to package the program as `CWAnalysis.exe`. |
| `packaging_entry.py` | Small starting point used only by the packaged Windows executable. |
| `src/cw_analyser/` | The program's Python source code. `cli.py` handles commands and options; `parser.py` reads CSV input; `statistics.py` calculates results; `plotting.py` creates charts; `report.py` creates PDF and CSV output; `morse.py` contains Morse patterns; `models.py` defines shared data structures; `__main__.py` supports running the package with Python; and `__init__.py` marks the folder as a Python package. |
| `tests/` | Automated checks. `test_cli.py`, `test_parser.py`, `test_statistics.py`, `test_plotting.py`, and `test_export.py` cover the corresponding commands, input, calculations, charts, and output files. |
| `tools/` | Developer utilities: `generate_example.py` recreates the large example dataset and `generate_readme_plots.py` recreates the four plot images. |
| `docs/` | Documentation assets. `docs/images/` contains the README plot images and `docs/examples/CW_Analysis_Example.pdf` is the linked example report. |
| `.venv/` | A private Python environment created during source setup. It is generated on your computer and should not be copied or edited manually. |
| `build/` and `dist/` | Temporary build files and the finished executable created by `build_windows.ps1`. |

### Using the JSON configuration file

JSON is a plain-text format for saving settings. Using it is optional: without `--config`, CWAnalysis uses its built-in defaults and any options entered on the command line.

To make your own configuration on Windows, copy the example and then open the new file in Notepad:

```powershell
Copy-Item config.example.json config.json
notepad config.json
```

Run the analyser with that file:

```powershell
.\CWAnalysis.exe input.csv --config config.json
```

For the Python installation, use:

```powershell
.\.venv\Scripts\cw-analyser.exe input.csv --config config.json
```

The settings in `config.example.json` are:

| Setting | What it controls |
| --- | --- |
| `plot_type` | Chart style: `box`, `violin`, `strip`, or `histogram`. |
| `show_outliers` | Shows specially identified unusual measurements when `true`. |
| `show_points` | Shows the individual measurements behind each distribution when `true`. |
| `show_reference_lines` | Shows the green ideal-timing reference lines when `true`. |
| `fixed_scales` | Uses shared timing scales across character plots when `true`, making direct comparisons easier. |
| `page_size` | PDF paper size: `A4` or `LETTER`. |
| `dpi` | Resolution of plot images in the PDF. Higher values are sharper but take more time and memory. The accepted range is 72 to 600. |
| `units` | Text displayed beside timing values, normally `ms` or `ticks`. This changes the label only; it does not convert the measurements. |
| `delimiter` | Character separating fields in the input, normally `,`. Use `;` for a semicolon-separated file. |
| `outlier_method` | Method used to identify unusual values: `iqr` or `modified-z`. |
| `colours` | Plot colours written as hexadecimal RGB values. `dit`, `dah`, `median`, `ideal`, `outlier`, and `point` can be changed independently. |

JSON requires double quotation marks, commas between entries, and lowercase `true` or `false`. Do not place a comma after the final entry in an object. If the same setting appears both in the JSON file and on the command line, the command-line option takes precedence.

## Run the standalone Windows executable

Windows users can run `CWAnalysis.exe` without installing Python. [Download the latest Windows executable](https://github.com/mad-bee/CWAnalysis/releases/latest/download/CWAnalysis.exe) and run:

```powershell
.\CWAnalysis.exe input.csv
```

Combine multiple recordings by listing them before any options:

```powershell
.\CWAnalysis.exe session1.csv session2.csv session3.csv -o combined-results
```

For example, to analyse a file with comparable fixed scales and choose a different output folder:

```powershell
.\CWAnalysis.exe C:\path\to\input.csv --fixed-scales -o C:\path\to\results
```

Show every available option with:

```powershell
.\CWAnalysis.exe --help
```

Windows may show a SmartScreen warning because community builds are not code-signed.

## Run from Python source

These instructions assume no previous Python experience. Setup is required only once; after that, use the shorter steps under **Run it again later**.

### Windows: first-time setup

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/). In the Windows installer, select **Add python.exe to PATH** before choosing **Install Now**.
2. Download this project from GitHub using **Code > Download ZIP**, then extract the ZIP to a folder such as `C:\Users\YourName\Documents\CWAnalysis`.
3. Open that folder in File Explorer. Click the address bar, type `powershell`, and press Enter. A PowerShell window opens in the correct project folder.
4. Check that Python is available:

   ```powershell
   py -3 --version
   ```

   A version such as `Python 3.12.4` confirms that Python is ready.

5. Create a private Python environment for CWAnalysis:

   ```powershell
   py -3 -m venv .venv
   ```

   This creates a hidden `.venv` folder inside the project. It keeps CWAnalysis and its supporting packages separate from other Python programs.

6. Install CWAnalysis and its required packages:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -e .
   ```

   The downloads may take several minutes. Wait until the command completes and the PowerShell prompt returns.

7. Confirm the installation by analysing the included small example:

   ```powershell
   .\.venv\Scripts\cw-analyser.exe examples\sample.csv
   ```

   When it finishes, open `output\pdf\CW_Analysis.pdf` to see the report.

### Windows: analyse your own files

Put a CSV file in the project folder and replace `input.csv` with its filename:

```powershell
.\.venv\Scripts\cw-analyser.exe input.csv
```

If the filename or path contains spaces, enclose it in quotation marks:

```powershell
.\.venv\Scripts\cw-analyser.exe "C:\Users\YourName\Documents\CW recordings\session 1.csv"
```

List several files to combine all their measurements into one report:

```powershell
.\.venv\Scripts\cw-analyser.exe session1.csv session2.csv session3.csv -o combined-results
```

Add `--fixed-scales` when all character plots should share one scale for direct comparison:

```powershell
.\.venv\Scripts\cw-analyser.exe input.csv --fixed-scales
```

The command has two main parts:

- `.\.venv\Scripts\cw-analyser.exe` starts CWAnalysis using the private Python installation created during setup. The command uses a hyphen because Python command names cannot contain underscores.
- Everything after it identifies the CSV files and any options. The underlying Python package is named `cw_analyser`, using the underscore required for Python imports.

The former `cw-analyse` command remains available as a compatibility alias, but new instructions and scripts should use `cw-analyser`.

### Windows: run it again later

There is no need to reinstall anything. Open PowerShell in the extracted `CWAnalysis` folder and run:

```powershell
.\.venv\Scripts\cw-analyser.exe input.csv
```

Show every available option with:

```powershell
.\.venv\Scripts\cw-analyser.exe --help
```

If `py` is not recognised during first-time setup, close and reopen PowerShell after installing Python. If it still does not work, replace `py -3` in the setup commands with `python`:

```powershell
python --version
python -m venv .venv
```

### macOS or Linux

Open a terminal in the extracted project folder, then run:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cw-analyser examples/sample.csv
```

For later runs, return to the project folder, run `source .venv/bin/activate`, and then use `cw-analyser input.csv`.

## Build the Windows executable

To build the executable from source:

```powershell
.\build_windows.ps1
```

The build script creates `dist\CWAnalysis.exe` using PyInstaller. A Windows build must be produced on Windows; executables for other operating systems must be built on those operating systems.

## Examples and outputs

Run the small included example from Python:

```powershell
.\.venv\Scripts\cw-analyser.exe examples\sample.csv
```

A deterministic 500-letter example is also included:

```powershell
.\.venv\Scripts\cw-analyser.exe examples\sample_500_letters.csv -o output\example_500
```

Unless `-o` or `--output-dir` is supplied, both the EXE and Python version write beneath `output` in the current directory:

```text
output/
  CW_Errors.csv
  CW_Summary.csv
  pdf/CW_Analysis.pdf
```

The first row may be a `Character,...` header. Two layouts are accepted:

- compact rows containing one finite positive timing for each mark in the character's Morse pattern; and
- recorder exports headed `Character,mark1,space1,mark2,space2,...`. The analyser uses mark columns for element timing and valid space columns for spacing analysis; unused trailing columns are ignored.

Invalid rows are skipped and included in `CW_Errors.csv`; up to 1,000 detailed error rows are retained while all rejection counts remain accurate.
For multi-file analyses, `CW_Errors.csv` includes the source filename for every retained rejected row.

Useful options:

```text
--units ms|ticks
--delimiter ";"
--plot-type box|violin|strip|histogram
--outlier-method iqr|modified-z
--page-size A4|LETTER
--dpi 72..600
--hide-points --hide-outliers --hide-reference-lines
--fixed-scales
--config config.json
```

By default, each character plot uses its own optimised timing range. Add `--fixed-scales` to either the EXE or Python command to use one shared, data-fitted range across every character plot. `config.example.json` contains all configuration keys and the full colour scheme. Explicit command-line values take precedence over values read from the JSON configuration file.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Notes on scale

The analyser retains accepted timing measurements because plots and exact quantiles require the observations. At 100,000 typical characters this remains comfortably below the 500 MB target. CSV parsing itself is streaming; malformed rows never terminate the run.

Fist score starts at 100 and applies penalties for aggregate CV, departure from a 3:1 median dash/dit ratio, and outlier frequency. Character consistency similarly combines average CV and outlier rate. Fixed formulas make repeated runs reproducible, and plot jitter uses a fixed random seed.
