# -*- coding: utf-8 -*-
"""Leitura das planilhas do programa Nota Fiscal Gaúcha.

O arquivo exportado pelo site tem sempre o mesmo molde: a linha 1 traz o título,
a linha 2 o cabeçalho e daí em diante uma nota por linha. A coluna que interessa
é a "Chave de Acesso" — 44 dígitos, às vezes com espaços no meio.

Cada planilha é tratada como uma pessoa. O nome sai do arquivo e, depois que as
notas são baixadas, é confirmado pelo nome do consumidor que consta na nota.
"""
from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field

import openpyxl

CABECALHOS = {
    "munic": "municipio",
    "razao social": "razao",
    "emissao": "emissao",
    "numero": "numero",
    "tipodoc.": "tipo",
    "tipodoc": "tipo",
    "chave de acesso": "chave",
    "valor": "valor",
    "data registro": "registro",
    "tipo operacao": "operacao",
    "situacao docto": "situacao",
}


def _norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


@dataclass
class Nota:
    chave: str
    origem: str            # nome do arquivo de onde veio
    razao: str = ""
    emissao: str = ""
    numero: str = ""
    tipo: str = ""
    valor: float = 0.0
    municipio: str = ""
    situacao: str = ""

    @property
    def modelo(self) -> str:
        """55 = NF-e comum, 65 = NFC-e (cupom)."""
        return self.chave[20:22]


@dataclass
class Planilha:
    caminho: str
    rotulo: str                       # nome provável da pessoa
    notas: list[Nota] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


def _valor(txt) -> float:
    if txt is None:
        return 0.0
    if isinstance(txt, (int, float)):
        return float(txt)
    t = re.sub(r"[^\d,.-]", "", str(txt))
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return 0.0


def _rotulo_do_arquivo(caminho: str) -> str:
    """'Nota Fiscal Gaúcha Maria.xlsx' -> 'Maria'."""
    nome = os.path.splitext(os.path.basename(caminho))[0]
    limpo = re.sub(r"(?i)nota\s*fiscal\s*ga[úu]cha", "", nome)
    limpo = re.sub(r"(?i)\b(nfg|notas?|planilha|relatorio|relatório)\b", "", limpo)
    limpo = re.sub(r"[_\-–]+", " ", limpo)
    limpo = re.sub(r"\s+", " ", limpo).strip(" .-")
    return limpo.title() if limpo else nome.strip().title()


def _digitos(v) -> str:
    return re.sub(r"\D", "", str(v or ""))


def valida_chave(chave: str) -> bool:
    """44 dígitos e dígito verificador (módulo 11) correto."""
    if len(chave) != 44 or not chave.isdigit():
        return False
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    for i, d in enumerate(reversed(chave[:43])):
        soma += int(d) * pesos[i % 8]
    resto = soma % 11
    dv = 0 if resto < 2 else 11 - resto
    return dv == int(chave[43])


def ler(caminho: str) -> Planilha:
    """Lê uma planilha e devolve as notas encontradas."""
    p = Planilha(caminho=caminho, rotulo=_rotulo_do_arquivo(caminho))

    wb = openpyxl.load_workbook(caminho, data_only=True, read_only=True)
    try:
        ws = wb.worksheets[0]
        linhas = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()

    # acha a linha de cabeçalho procurando "chave de acesso"
    idx_cab = None
    for i, linha in enumerate(linhas[:15]):
        celulas = [_norm(c) for c in linha]
        if any("chave de acesso" in c for c in celulas):
            idx_cab = i
            break
    if idx_cab is None:
        p.avisos.append(
            "não encontrei a coluna \"Chave de Acesso\" — o arquivo parece não ser "
            "uma planilha do Nota Fiscal Gaúcha"
        )
        return p

    cab = [_norm(c) for c in linhas[idx_cab]]
    col = {}
    for j, c in enumerate(cab):
        for chave_cab, campo in CABECALHOS.items():
            if c == chave_cab or (chave_cab in c and campo not in col):
                col[campo] = j
    if "chave" not in col:
        p.avisos.append("coluna de chave de acesso não localizada")
        return p

    vistas: set[str] = set()
    invalidas = 0
    for linha in linhas[idx_cab + 1:]:
        if col["chave"] >= len(linha):
            continue
        chave = _digitos(linha[col["chave"]])
        if not chave:
            continue
        if not valida_chave(chave):
            invalidas += 1
            continue
        if chave in vistas:
            continue
        vistas.add(chave)

        def cel(campo, padrao=""):
            j = col.get(campo)
            if j is None or j >= len(linha):
                return padrao
            v = linha[j]
            return padrao if v is None else str(v).strip()

        p.notas.append(
            Nota(
                chave=chave,
                origem=os.path.basename(caminho),
                razao=cel("razao"),
                emissao=cel("emissao"),
                numero=cel("numero"),
                tipo=cel("tipo"),
                valor=_valor(linha[col["valor"]] if "valor" in col and col["valor"] < len(linha) else None),
                municipio=cel("municipio"),
                situacao=cel("situacao"),
            )
        )

    if invalidas:
        p.avisos.append(f"{invalidas} linha(s) com chave inválida foram ignoradas")
    if not p.notas:
        p.avisos.append("nenhuma chave de acesso válida encontrada")
    return p


def ler_pasta(pasta: str) -> list[Planilha]:
    """Lê todas as planilhas .xlsx/.xlsm de uma pasta (ignora temporários do Excel)."""
    achadas = []
    for nome in sorted(os.listdir(pasta)):
        if nome.startswith("~$"):
            continue
        if not nome.lower().endswith((".xlsx", ".xlsm")):
            continue
        achadas.append(ler(os.path.join(pasta, nome)))
    return achadas
