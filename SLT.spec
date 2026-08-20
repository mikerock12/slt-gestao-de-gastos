# -*- mode: python ; coding: utf-8 -*-
"""Empacotamento do SLT — Gestão de Gastos.

    python -m PyInstaller --noconfirm SLT.spec

Gera um único .exe em dist/. Os recursos do relatório (Three.js, GSAP, CSS e o
molde do HTML) viajam dentro do executável e são lidos de sys._MEIPASS.
"""

import os

AQUI = os.path.abspath(os.path.dirname(SPEC))
NOME = "SLT - Gestão de Gastos"

a = Analysis(
    ["slt.py"],
    pathex=[AQUI],
    binaries=[],
    datas=[("recursos", "recursos")],
    # slt.py importa app.* dentro das funções, para a janela abrir rápido.
    # O PyInstaller não enxerga import tardio, então os módulos vão nomeados.
    hiddenimports=[
        "lxml.etree", "lxml._elementpath",
        "app", "app.analise", "app.categorias", "app.extrair", "app.gui",
        "app.mapa", "app.pessoas", "app.pipeline", "app.planilhas",
        "app.relatorio", "app.salvar", "app.sefaz",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # nada disso é usado e só engordaria o executável.
        # CUIDADO: o PyInstaller casa exclusão por prefixo de nome. "pip" na
        # lista derrubava junto o nosso app.pipeline, e o .exe abria com
        # "No module named 'app.pipeline'". Por isso "pip" e "test" ficaram
        # de fora — o ganho de tamanho não paga o risco.
        "PIL", "numpy", "pandas", "matplotlib", "scipy", "pytest",
        "setuptools", "unittest", "pydoc", "sqlite3",
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
