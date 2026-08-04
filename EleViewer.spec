# -*- mode: python ; coding: utf-8 -*-
# EleViewer.spec — legacy PyInstaller build spec retained for reference only.
# The active release workflow now packages EleViewer with Nuitka + Inno Setup.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icons/', 'icons'), ('getting_started/', 'getting_started')],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtSvg',
        'markdown',
        'docx',
        'openpyxl',
        'pptx',
        'pyttsx3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'tensorflow', 'scikit-learn', 'pandas', 'numpy'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EleViewer',
    icon='icons/eleviewer.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX disabled — causes decompression errors on some machines
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
