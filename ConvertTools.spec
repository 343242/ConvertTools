# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

ROOT = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=[],
    datas=[],
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Test & dev
        'pytest', 'pluggy', 'iniconfig', 'packaging', 'pygments',
        # Unnecessary stdlib
        'unittest', 'xmlrunner', 'doctest', 'pydoc',
        'difflib', 'inspect', 'ast', 'dis', 'ctypes.test',
        # Unused Qt modules
        'PySide6.QtNetwork', 'PySide6.QtSql', 'PySide6.QtTest',
        'PySide6.QtXml', 'PySide6.QtBluetooth', 'PySide6.QtNfc',
        'PySide6.QtPositioning', 'PySide6.QtLocation',
        'PySide6.QtSensors', 'PySide6.QtSerialPort',
        'PySide6.QtWebEngine', 'PySide6.QtWebSockets',
        'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
        'PySide6.QtCharts', 'PySide6.QtDataVisualization',
        'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets',
        'PySide6.Qt3D', 'PySide6.QtDesigner',
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
    upx=True,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='ConvertTools',
)
