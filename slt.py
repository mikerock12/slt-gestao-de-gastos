# -*- coding: utf-8 -*-
"""SLT — Gestão de Gastos.

Sem argumentos, abre a janela. Com argumentos, roda pela linha de comando:

    slt.py <pasta com as planilhas> [pasta de saída]
"""
from __future__ import annotations

import os
import sys


def main():
    if len(sys.argv) > 1:
        from app.pipeline import executar

        entrada = os.path.abspath(sys.argv[1])
        saida = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else \
            os.path.join(entrada, "Gestao de Gastos")

        def passo(fase, feito, total):
            if fase == "baixando" and (feito % 10 == 0 or feito == total):
                print(f"  {fase}: {feito}/{total}", flush=True)

        r = executar(entrada, saida, aviso=lambda t: print(t, flush=True), passo=passo)
        if not r.ok:
            print("\nERRO: " + r.erro, file=sys.stderr)
            return 1
        print(f"\nRelatório: {r.relatorio}")
        print(f"Notas:     {r.pasta_notas}")
        return 0

    from app.gui import main as janela
    janela()
    return 0


if __name__ == "__main__":
    sys.exit(main())
