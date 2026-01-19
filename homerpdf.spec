# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Hospital PDF Manager.
Build with: pyinstaller homerpdf.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Determine if we're on macOS
is_macos = sys.platform == "darwin"

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("files", "files"),  # Include PDF templates
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],  # binaries and zipfiles go in COLLECT for onedir
    a.datas,
    [],
    name="Hospital PDF Manager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    icon=None,  # Can add icon file here: "icon.ico"
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT for onedir mode (directory with dependencies)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Hospital PDF Manager",
)

# For macOS, create an app bundle
if is_macos:
    app = BUNDLE(
        exe,
        name="Hospital PDF Manager.app",
        icon=None,  # Can add icon file here: "icon.icns"
        bundle_identifier="com.homerpdf.app",
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSHighResolutionCapable": "True",
        },
    )
