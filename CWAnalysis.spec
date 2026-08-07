a = Analysis(
    ["packaging_entry.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=["matplotlib.backends.backend_agg"],
    hookspath=[],
    hooksconfig={"matplotlib": {"backends": "Agg"}},
    runtime_hooks=[],
    excludes=["tkinter", "IPython", "pytest"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="CWAnalysis",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
