# -*- coding: utf-8 -*-
"""Gera o executável do zero.

    python build.py

Faz, em ordem:
  1. o ícone
  2. o bundle JS do relatório (Three.js + GSAP + o código), via esbuild
  3. copia CSS e molde HTML para recursos/
  4. chama o PyInstaller

Precisa de Node instalado só para o passo 2. O .exe resultante não precisa de
nada: nem Python, nem Node, nem internet (fora a consulta à SEFAZ, claro).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def passo(n, texto):
    print(f"\n[{n}] {texto}", flush=True)


def roda(cmd, **kw):
    print("    $ " + " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=AQUI, **kw)
    if r.returncode != 0:
        sys.exit(f"falhou: {' '.join(cmd)}")


def main():
    os.chdir(AQUI)

    passo(1, "ícone")
    roda([sys.executable, "gerar_icone.py"])

    passo(2, "bundle do relatório (esbuild)")
    if not os.path.isdir(os.path.join(AQUI, "node_modules")):
        roda(["npm.cmd" if os.name == "nt" else "npm", "install"], shell=os.name == "nt")
    roda(["node", "build_relatorio.mjs"], shell=os.name == "nt")

    passo(3, "CSS e molde HTML")
    destino = os.path.join(AQUI, "recursos", "relatorio")
    os.makedirs(destino, exist_ok=True)
    for nome in ("estilo.css", "base.html"):
        shutil.copyfile(os.path.join(AQUI, "fonte_relatorio", nome),
                        os.path.join(destino, nome))
        print(f"    {nome}")

    passo(4, "PyInstaller")
    roda([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "SLT.spec"])

    exe = os.path.join(AQUI, "dist", "SLT - Gestão de Gastos.exe")
    if os.path.exists(exe):
        print(f"\nPronto: {exe}  ({os.path.getsize(exe) / 1048576:.1f} MB)")
    else:
        sys.exit("o executável não apareceu em dist/")


if __name__ == "__main__":
    main()
