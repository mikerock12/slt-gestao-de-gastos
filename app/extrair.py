# -*- coding: utf-8 -*-
"""Extração dos dados de uma página de Consulta Completa da NFC-e."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import lxml.html


def _limpa(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def _num(s):
    if s is None:
        return None
    t = _limpa(s).replace("R$", "").strip()
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


@dataclass
class Item:
    codigo: str
    descricao: str
    quantidade: float | None
    unidade: str
    valor_unitario: float | None
    valor_total: float | None


@dataclass
class Pagamento:
    forma: str
    valor: float


@dataclass
class NotaCompleta:
    chave: str
    emitente: str = ""
    cnpj: str = ""
    inscricao: str = ""
    endereco: str = ""
    numero: int | None = None
    serie: int | None = None
    data: str = ""
    hora: str = ""
    protocolo: str = ""
    emissao_tipo: str = "Normal"
    cpf: str = ""
    consumidor: str = ""
    itens: list[Item] = field(default_factory=list)
    valor_total: float = 0.0
    descontos: float = 0.0
    pagamentos: list[Pagamento] = field(default_factory=list)

    @property
    def valor_pago(self) -> float:
        return round(sum(p.valor for p in self.pagamentos), 2)

    @property
    def data_iso(self) -> str:
        if not self.data:
            return ""
        d, m, a = self.data.split("/")
        return f"{a}-{m}-{d}"


def ler(caminho: str, chave: str) -> NotaCompleta:
    with open(caminho, encoding="utf-8") as f:
        html = f.read()

    doc = lxml.html.fromstring(html)
    for ruim in doc.xpath("//script|//style"):
        ruim.getparent().remove(ruim)
    txt = _limpa(doc.text_content())

    n = NotaCompleta(chave=chave)

    cab = doc.xpath('//td[contains(@class,"NFCCabecalho_SubTitulo")]')
    n.emitente = _limpa(cab[0].text_content()) if cab else ""

    # o endereço fica nas células de classe exata NFCCabecalho_SubTitulo1
    sub1 = [_limpa(e.text_content()) for e in doc.xpath('//td[@class="NFCCabecalho_SubTitulo1"]')]
    n.endereco = " | ".join(x for x in sub1 if x and not x.startswith("CNPJ:"))

    def busca(padrao, grupo=1):
        m = re.search(padrao, txt)
        return m.group(grupo) if m else ""

    n.cnpj = busca(r"CNPJ:\s*([\d./-]{14,20})")
    n.inscricao = busca(r"Inscri\S+o Estadual:\s*(\d+)")
    num = busca(r"NFC-e n\S+:\s*(\d+)")
    n.numero = int(num) if num else None
    ser = busca(r"S\S+rie:\s*(\d+)")
    n.serie = int(ser) if ser else None
    m = re.search(r"Data de Emiss\S+o:\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2}:\d{2})", txt)
    if m:
        n.data, n.hora = m.group(1), m.group(2)
    n.protocolo = busca(r"Protocolo de Autoriza\S+o:\s*(\d+)")
    n.emissao_tipo = "Contingência" if "Conting" in txt else "Normal"

    m = re.search(r"CPF:\s*([\d.\-]{11,14})\s*-?\s*([A-ZÀ-Ü\s]+?)(?:C\S+digo|Descri|$)", txt)
    if m:
        n.cpf = m.group(1)
        n.consumidor = _limpa(m.group(2))
    else:
        n.cpf = busca(r"CPF:\s*([\d.\-]{11,14})")

    for tr in doc.xpath('//tr[starts-with(@id,"Item")]'):
        tds = [_limpa(td.text_content()) for td in tr.xpath("./td")]
        if len(tds) < 6:
            continue
        n.itens.append(
            Item(
                codigo=tds[0],
                descricao=tds[1],
                quantidade=_num(tds[2]),
                unidade=tds[3],
                valor_unitario=_num(tds[4]),
                valor_total=_num(tds[5]),
            )
        )

    n.valor_total = _num(busca(r"Valor total R\$\s*([\d.,]+)")) or 0.0
    n.descontos = _num(busca(r"Valor descontos R\$\s*([\d.,]+)")) or 0.0

    cabecalho_pag = doc.xpath('//td[normalize-space(text())="FORMA PAGAMENTO"]')
    if cabecalho_pag:
        tr = cabecalho_pag[0].getparent()
        for prox in tr.itersiblings("tr"):
            tds = [_limpa(td.text_content()) for td in prox.xpath("./td")]
            if len(tds) < 2:
                break
            v = _num(tds[1])
            if v is None:
                break
            n.pagamentos.append(Pagamento(forma=tds[0] or "Não informada", valor=v))

    return n
