$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    py -3 -m venv (Join-Path $projectRoot ".venv")
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e "$projectRoot[build]"
& $venvPython -m PyInstaller --clean --noconfirm (Join-Path $projectRoot "CWAnalysis.spec")

Write-Host "Built: $(Join-Path $projectRoot 'dist\CWAnalysis.exe')"
