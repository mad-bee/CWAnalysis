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
.\.venv\Scripts\python.exe -m cw_analyser input.csv --plot-type histogram
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
   .\.venv\Scripts\python.exe -m cw_analyser examples\sample.csv
   ```

   When it finishes, open `output\pdf\CW_Analysis.pdf` to see the report.

### Windows: analyse your own files

Put a CSV file in the project folder and replace `input.csv` with its filename:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser input.csv
```

If the filename or path contains spaces, enclose it in quotation marks:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser "C:\Users\YourName\Documents\CW recordings\session 1.csv"
```

List several files to combine all their measurements into one report:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser session1.csv session2.csv session3.csv -o combined-results
```

Add `--fixed-scales` when all character plots should share one scale for direct comparison:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser input.csv --fixed-scales
```

The command has three main parts:

- `.\.venv\Scripts\python.exe` runs the private Python installation created during setup.
- `-m cw_analyser` starts CWAnalysis.
- Everything after that identifies the CSV files and any options.

### Windows: run it again later

There is no need to reinstall anything. Open PowerShell in the extracted `CWAnalysis` folder and run:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser input.csv
```

Show every available option with:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser --help
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
python -m cw_analyser examples/sample.csv
```

For later runs, return to the project folder, run `source .venv/bin/activate`, and then use `python -m cw_analyser input.csv`.

## Build the Windows executable

To build the executable from source:

```powershell
.\build_windows.ps1
```

The build script creates `dist\CWAnalysis.exe` using PyInstaller. A Windows build must be produced on Windows; executables for other operating systems must be built on those operating systems.

## Examples and outputs

Run the small included example from Python:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser examples\sample.csv
```

A deterministic 500-letter example is also included:

```powershell
.\.venv\Scripts\python.exe -m cw_analyser examples\sample_500_letters.csv -o output\example_500
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
- recorder exports headed `Character,mark1,space1,mark2,space2,...`. The analyser uses the mark columns and ignores space and unused trailing columns.

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
