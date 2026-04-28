# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

import PySide6
import shiboken6

block_cipher = None

ROOT = os.path.abspath('.')
PYSIDE_DIR = Path(PySide6.__file__).resolve().parent
SHIBOKEN_DIR = Path(shiboken6.__file__).resolve().parent
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
SYSTEM_ICU_DLL_PREFIXES = ('icu',)


def _is_system_icu_binary(binary_toc_entry):
    dest_name = Path(binary_toc_entry[0]).name.lower()
    src_name = Path(binary_toc_entry[1]).name.lower()
    return (
        dest_name.startswith(SYSTEM_ICU_DLL_PREFIXES)
        and dest_name.endswith('.dll')
    ) or (
        src_name.startswith(SYSTEM_ICU_DLL_PREFIXES)
        and src_name.endswith('.dll')
    )


extra_binaries = [
    (str(PYSIDE_DIR / dll_name), 'PySide6')
    for dll_name in MSVC_RUNTIME_DLLS
    if (PYSIDE_DIR / dll_name).exists()
]
# Co-locate shiboken6 DLL with PySide6 so Windows can resolve
# the transitive dependency: QtWidgets.pyd -> pyside6.abi3.dll -> shiboken6.abi3.dll
extra_binaries += [
    (str(SHIBOKEN_DIR / 'shiboken6.abi3.dll'), 'PySide6'),
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

# Qt6Core on Windows can use the OS ICU DLLs from System32. PyInstaller may
# accidentally collect Anaconda's ICU forwarder DLLs from PATH, and those break
# PySide6 import at startup when they shadow the OS copies.
a.binaries = [entry for entry in a.binaries if not _is_system_icu_binary(entry)]

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
