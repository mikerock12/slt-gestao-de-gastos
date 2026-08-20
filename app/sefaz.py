# -*- coding: utf-8 -*-
"""Consulta pública da NFC-e na SEFAZ-RS.

O caminho é o mesmo que uma pessoa faria no navegador:

  1. abrir  https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx?chaveNFe=<CHAVE>
  2. clicar em "Avançar"

A página do passo 1 é só um invólucro com um iframe; o formulário de verdade
mora em /ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_1.asp e envia um POST para o _2.asp.
É esse POST que devolve a Consulta Completa da NFC-e.

NF-e modelo 55 não tem consulta pública: o portal DFe da SVRS exige login
gov.br. Essas notas entram no total pelo valor da planilha, sem itens.
"""
from __future__ import annotations

import os
import random
import time

import requests

BASE = "https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/"
FORM = BASE + "SAT-WEB-NFE-NFC_1.asp"
ENVIO = BASE + "SAT-WEB-NFE-NFC_2.asp"
PUBLICA = "https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx?chaveNFe="

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class ConsultaError(Exception):
    pass


def nova_sessao() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }
    )
    return s


def _ok(html: str) -> bool:
    return "CONSULTA DA NFC-e" in html and "respostaWS" in html


def baixar_uma(sessao: requests.Session, chave: str, timeout: int = 90) -> str:
    """Devolve o HTML da Consulta Completa. Levanta ConsultaError se não vier."""
    r1 = sessao.get(FORM + "?chaveNFe=" + chave, timeout=timeout)
    r1.raise_for_status()
    r2 = sessao.post(
        ENVIO,
        data={"HML": "false", "chaveNFe": chave, "Action": "Avançar"},
        headers={
            "Referer": r1.url,
            "Origin": "https://www.sefaz.rs.gov.br",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=timeout,
    )
    r2.raise_for_status()
    html = r2.content.decode("iso-8859-1")
    if not _ok(html):
        raise ConsultaError("a página devolvida não é a consulta da NFC-e")
    return html


def baixar(
    chaves: list[str],
    pasta_cache: str,
    progresso=None,
    cancelado=None,
    pausa=(0.8, 1.6),
    tentativas: int = 4,
) -> dict[str, str]:
    """Baixa todas as chaves, reaproveitando o que já está em cache.

    `progresso(feitas, total, chave, estado)` é chamado a cada nota;
    `cancelado()` devolvendo True interrompe.
    Retorna {chave: caminho do html} apenas das que deram certo.
    """
    os.makedirs(pasta_cache, exist_ok=True)
    sessao = nova_sessao()
    resultado: dict[str, str] = {}
    total = len(chaves)

    for i, chave in enumerate(chaves, 1):
        if cancelado and cancelado():
            break

        destino = os.path.join(pasta_cache, chave + ".html")
        if os.path.exists(destino) and os.path.getsize(destino) > 5000:
            resultado[chave] = destino
            if progresso:
                progresso(i, total, chave, "cache")
            continue

        estado = "erro"
        for tentativa in range(tentativas):
            if cancelado and cancelado():
                break
            try:
                html = baixar_uma(sessao, chave)
                with open(destino, "w", encoding="utf-8") as f:
                    f.write(html)
                resultado[chave] = destino
                estado = "baixada"
                break
            except Exception:
                if tentativa == tentativas - 1:
                    estado = "falhou"
                else:
                    time.sleep(3 * (tentativa + 1))
                    sessao = nova_sessao()

        if progresso:
            progresso(i, total, chave, estado)
        # respiro entre requisições, para não martelar o servidor da SEFAZ
        time.sleep(random.uniform(*pausa))

    return resultado
