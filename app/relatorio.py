# -*- coding: utf-8 -*-
"""Monta o relatório HTML5 — um arquivo só, que abre com dois cliques.

Three.js, GSAP, o CSS e os dados vão todos dentro do arquivo. Não depende de
servidor, de internet nem de nada instalado: basta um navegador.
"""
from __future__ import annotations

import json
import os
import sys

RECURSOS = ("recursos", "relatorio")


def _base_recursos() -> str:
    """Funciona tanto rodando do código quanto de dentro do .exe (PyInstaller)."""
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(sys._MEIPASS, *RECURSOS)
    aqui = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(aqui, *RECURSOS)


def _ler(nome: str) -> str:
    caminho = os.path.join(_base_recursos(), nome)
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def gerar(dados: dict, pasta_saida: str, nome_arquivo: str = "Relatorio.html") -> str:
    base = _ler("base.html")
    css = _ler("estilo.css")
    app = _ler("app.bundle.js")

    meta = dados["meta"]
    titulo = f"Gestão de Gastos — {meta['titulo']}"
    descricao = (
        f"Análise de {dados['resumo']['notas']} notas fiscais de "
        f"{meta['inicio']} a {meta['fim']}."
    )

    # </script> dentro do JSON encerraria o bloco antes da hora
    js_dados = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    js_dados = js_dados.replace("</", "<\\/")

    html = (base
            .replace("{{TITULO}}", titulo)
            .replace("{{DESCRICAO}}", descricao)
            .replace("{{CSS}}", css)
            .replace("{{DADOS}}", js_dados)
            .replace("{{APP}}", app))

    caminho = os.path.join(pasta_saida, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho
