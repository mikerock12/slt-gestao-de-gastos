# -*- mode: python ; coding: utf-8 -*-
"""Empacotamento do SLT — Gestão de Gastos.

    python -m PyInstaller --noconfirm SLT.spec

Gera um único .exe em dist/. Os recursos do relatório (Three.js, GSAP, CSS e o
molde do HTML) viajam dentro do executável e são lidos de sys._MEIPASS.
"""

NOME = "SLT - Gestão de Gastos"

a = Analysis(
    ["slt.py"],
    pathex=[],
    binaries=[],
    datas=[("recursos", "recursos")],
    hiddenimports=["lxml.etree", "lxml._elementpath"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # nada disso é usado e só engordaria o executável
        "PIL", "numpy", "pandas", "matplotlib", "scipy", "pytest",
        "setuptools", "pip", "test", "unittest", "pydoc",
        "tkinter.test", "sqlite3", "email.test",
    ],
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
    name=NOME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="recursos/slt.ico",
    version="versao.txt",
)
