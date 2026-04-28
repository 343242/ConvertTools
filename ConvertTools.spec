# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

import PySide6

block_cipher = None

ROOT = os.path.abspath('.')
PYSIDE_DIR = Path(PySide6.__file__).resolve().parent
MSVC_RUNTIME_DLLS = [
    'concrt140.dll',
    'msvcp140.dll',
    'msvcp140_1.dll',
    'msvcp140_2.dll',
    'msvcp140_codecvt_ids.dll',
    'vccorlib140.dll',
    'vcomp140.dll',
    'vcruntime140.dll',
    'vcruntime140_1.dll',
]
extra_binaries = [
    (str(PYSIDE_DIR / dll_name), 'PySide6')
    for dll_name in MSVC_RUNTIME_DLLS
    if (PYSIDE_DIR / dll_name).exists()
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=extra_binaries,
    datas=[],
    hiddenimports=[
        'psd_tools',
        'psd_tools.api',
        'psd_tools.constants',
        'psd_tools.psd',
        'psd_tools.decoder',
        'psd_tools.reader',
        'psd_tools.composite',
        'srcgen',
        'enum',
        'attr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Test & dev
        'pytest', 'pluggy', 'iniconfig', 'packaging', 'pygments',
        # Optional tooling
        'xmlrunner', 'ctypes.test',
    ],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ConvertTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='ConvertTools',
)
