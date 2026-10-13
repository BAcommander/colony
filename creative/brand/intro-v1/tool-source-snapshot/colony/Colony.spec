# -*- mode: python ; coding: utf-8 -*-
#
# Colony - PyInstaller spec (single-file, windowed)
#
# Build from the repo root:  python -m PyInstaller --noconfirm --clean colony/Colony.spec
# (colony/build.bat does exactly that). Output: dist/Colony.exe
#
# Onefile is fine here: Colony is an internal tool, not an MSIX package
# (the main app's spec explains why that one has to be onedir).
import os
from PyInstaller.utils.hooks import collect_data_files

ROOT = os.path.dirname(SPECPATH)

a = Analysis(
    [os.path.join(SPECPATH, 'gui.py')],
    pathex=[ROOT],
    binaries=[],
    # the bundled ffmpeg binary: imageio-ffmpeg ships it as package data
    datas=collect_data_files('imageio_ffmpeg') + [(os.path.join(SPECPATH, 'assets'), 'colony/assets')],
    hiddenimports=[],
    excludes=['cv2', 'numpy', 'webview', 'pythonnet', 'clr_loader'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Colony',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)
