# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

ROOT = os.path.abspath('.')
pyside_datas, pyside_binaries, pyside_hiddenimports = collect_all('PySide6')
shiboken_datas, shiboken_binaries, shiboken_hiddenimports = collect_all('shiboken6')

a = Analysis(
    ['main.py'],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=pyside_binaries + shiboken_binaries,
    datas=pyside_datas + shiboken_datas,
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageEnhance',
        'PIL.ImageFilter',
        'PIL.ImageOps',
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
    ] + pyside_hiddenimports + shiboken_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Test & dev
        'pytest', 'pluggy', 'iniconfig', 'packaging', 'pygments',
        # Optional tooling
        'xmlrunner', 'ctypes.test',
        # Misc unused
        'tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas',
        'IPython', 'jupyter', 'notebook',
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
