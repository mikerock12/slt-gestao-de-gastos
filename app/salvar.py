# -*- coding: utf-8 -*-
"""Gravação dos arquivos: uma nota por .txt, o HTML original, os CSVs e o JSON."""
from __future__ import annotations

import csv
import datetime
import json
import os
import re
import shutil
import unicodedata

from .categorias import CARGA

LARGURA = 92


def slug(s: str, n: int = 34) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s[:n] or "sem-nome"


def brl(v) -> str:
    if v is None:
        return "-"
    return ("R$ " + format(v, ",.2f")).replace(",", "X").replace(".", ",").replace("X", ".")


def _n(v, casas=2) -> str:
    return format(v or 0, f".{casas}f").replace(".", ",")


def _linha(c="-", n=LARGURA) -> str:
    return c * n


def render_nota(reg, pessoa_nome: str) -> str:
    n = reg["nota"]
    L, A = [], None
    A = L.append

    trib = {}
    for i in reg["itens"]:
        c = i["categoria"]
        v, t = trib.get(c, (0.0, 0.0))
        trib[c] = (round(v + i["vl_total"], 2), round(t + i["imposto_est"], 2))
    aliq = reg["imposto"] / n.valor_total if n.valor_total else 0

    A(_linha("="))
    A("NOTA FISCAL DE CONSUMIDOR ELETRONICA (NFC-e)")
    A(_linha("="))
    A("Chave de acesso : %s" % " ".join(n.chave[i:i + 4] for i in range(0, 44, 4)))
    A("Consulta SEFAZ  : https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx?chaveNFe=%s" % n.chave)
    A("Numero / Serie  : %s / %s" % (n.numero, n.serie))
    A("Data e hora     : %s %s" % (n.data, n.hora))
    A("Protocolo       : %s" % n.protocolo)
    A("Tipo de emissao : %s" % n.emissao_tipo)
    A("")
    A(_linha()); A("EMITENTE"); A(_linha())
    A("Razao social    : %s" % n.emitente)
    A("CNPJ            : %s" % n.cnpj)
    A("Inscr. Estadual : %s" % n.inscricao)
    A("Endereco        : %s" % n.endereco)
    A("Categoria       : %s" % reg["cat_loja"])
    A("")
    A(_linha()); A("CONSUMIDOR"); A(_linha())
    A("CPF             : %s" % (n.cpf or "-"))
    A("Nome            : %s" % (n.consumidor or "-"))
    A("Titular na base : %s" % pessoa_nome)
    A("")
    A(_linha()); A("PRODUTOS / SERVICOS"); A(_linha())
    A("%-3s %-20s %-42s %9s %-4s %10s %10s"
      % ("#", "Codigo", "Descricao", "Qtd", "Un", "Vl Unit", "Vl Total"))
    A(_linha())
    for k, it in enumerate(reg["itens"], 1):
        q = ("%g" % it["qtd"]) if it["qtd"] is not None else "-"
        A("%-3d %-20s %-42s %9s %-4s %10s %10s"
          % (k, (it["cod"] or "")[:20], it["desc"][:42], q, (it["un"] or "")[:4],
             _n(it["vl_unit"]), _n(it["vl_total"])))
    A(_linha())
    A("%-61s %16s" % ("Quantidade total de itens:", len(reg["itens"])))
    A("%-61s %16s" % ("Valor total dos produtos:", brl(n.valor_total)))
    A("%-61s %16s" % ("Descontos:", brl(n.descontos)))
    if reg["acrescimos"]:
        A("%-61s %16s" % ("Acrescimos / taxa de entrega:", brl(reg["acrescimos"])))
    A("%-61s %16s" % ("VALOR DA NOTA:", brl(reg["valor_nota"])))
    A("")
    A(_linha()); A("PAGAMENTO"); A(_linha())
    for p in n.pagamentos:
        A("%-61s %16s" % (p.forma, brl(p.valor)))
    if reg["troco"]:
        A("%-61s %16s" % ("Troco:", brl(reg["troco"])))
    A("")
    A(_linha()); A("TRIBUTOS (ESTIMATIVA)"); A(_linha())
    A("A consulta publica da SEFAZ-RS nao divulga os valores de tributos da nota.")
    A("Os valores abaixo sao ESTIMADOS a partir da carga tributaria media por")
    A("categoria de produto (ICMS-RS + PIS/COFINS + IPI), criterio da Lei 12.741/2012.")
    A("")
    A("%-42s %10s %10s %12s" % ("Categoria", "Valor", "Aliq.est", "Imposto est."))
    A(_linha())
    for cat, (v, t) in sorted(trib.items(), key=lambda x: -x[1][0]):
        A("%-42s %10s %9.1f%% %12s" % (cat[:42], _n(v), 100 * CARGA[cat], _n(t)))
    A(_linha())
    A("%-42s %10s %9.1f%% %12s"
      % ("TOTAL ESTIMADO DE TRIBUTOS", _n(n.valor_total), 100 * aliq, _n(reg["imposto"])))
    A("")
    A(_linha("="))
    A("Fonte: consulta publica NFC-e - Secretaria da Fazenda do RS")
    A("Gerado por SLT - Gestao de Gastos")
    A(_linha("="))
    return "\n".join(L)


def gravar(dados, cache_html: dict[str, str], pasta_saida: str, progresso=None):
    """Escreve tudo em <pasta_saida>/Notas."""
    base = os.path.join(pasta_saida, "Notas")
    dir_html = os.path.join(base, "_HTML_ORIGINAL_SEFAZ")
    dir_dados = os.path.join(base, "_DADOS")
    for d in (base, dir_html, dir_dados):
        os.makedirs(d, exist_ok=True)

    registros = dados["_registros"]
    nomes = dados["pessoasNomes"]
    total = len(registros)

    for k, reg in enumerate(registros, 1):
        n = reg["nota"]
        mes = n.data_iso[:7]
        pasta_mes = os.path.join(base, mes)
        os.makedirs(pasta_mes, exist_ok=True)
        nome = "%s_%s_%s_%s_%s.txt" % (
            n.data_iso, n.hora.replace(":", ""), slug(reg["loja"], 30),
            _n(reg["valor_nota"]), n.chave[-8:])
        with open(os.path.join(pasta_mes, nome), "w", encoding="utf-8") as f:
            f.write(render_nota(reg, nomes[reg["pessoa"]]))
        origem = cache_html.get(n.chave)
        if origem and os.path.exists(origem):
            shutil.copyfile(origem, os.path.join(dir_html, n.chave + ".html"))
        if progresso and k % 20 == 0:
            progresso(k, total)

    # ------------------------------------------------------------------ CSVs
    with open(os.path.join(dir_dados, "notas.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "hora", "titular", "loja", "razao_social", "cnpj",
                    "categoria_loja", "numero", "qtd_itens", "valor_produtos",
                    "descontos", "acrescimos", "valor_nota", "imposto_estimado",
                    "aliquota_efetiva_%", "forma_pagamento", "chave"])
        for reg in registros:
            n = reg["nota"]
            aliq = 100 * reg["imposto"] / n.valor_total if n.valor_total else 0
            w.writerow([n.data_iso, n.hora, nomes[reg["pessoa"]], reg["loja"],
                        n.emitente, n.cnpj, reg["cat_loja"], n.numero,
                        len(reg["itens"]), _n(n.valor_total), _n(n.descontos),
                        _n(reg["acrescimos"]), _n(reg["valor_nota"]),
                        _n(reg["imposto"]), _n(aliq, 1),
                        " + ".join(p.forma for p in n.pagamentos) or "-", n.chave])

    with open(os.path.join(dir_dados, "itens.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "hora", "titular", "loja", "categoria_loja", "codigo",
                    "descricao", "categoria_produto", "dominio_consumo",
                    "grupo_alimentar", "grau_processamento_nova", "quantidade",
                    "unidade", "valor_unitario", "valor_total", "imposto_estimado",
                    "chave"])
        for reg in registros:
            n = reg["nota"]
            for it in reg["itens"]:
                w.writerow([n.data_iso, n.hora, nomes[reg["pessoa"]], reg["loja"],
                            reg["cat_loja"], it["cod"], it["desc"], it["categoria"],
                            it["dominio"], it["grupo"] or "", it["nova"] or "",
                            _n(it["qtd"] or 0, 3), it["un"], _n(it["vl_unit"]),
                            _n(it["vl_total"]), _n(it["imposto_est"]), n.chave])

    # ------------------------------------------------------------------ JSON
    completo = []
    for reg in registros:
        n = reg["nota"]
        completo.append({
            "chave": n.chave, "pessoa": nomes[reg["pessoa"]], "loja": reg["loja"],
            "emitente": n.emitente, "cnpj": n.cnpj, "ie": n.inscricao,
            "endereco": n.endereco, "cat_loja": reg["cat_loja"],
            "numero": n.numero, "serie": n.serie, "data": n.data, "hora": n.hora,
            "data_iso": n.data_iso, "protocolo": n.protocolo,
            "emissao_tipo": n.emissao_tipo, "cpf": n.cpf, "consumidor": n.consumidor,
            "valor_total": n.valor_total, "descontos": n.descontos,
            "acrescimos": reg["acrescimos"], "valor_nota": reg["valor_nota"],
            "troco": reg["troco"], "imposto_est": reg["imposto"],
            "pagamentos": [{"forma": p.forma, "valor": p.valor} for p in n.pagamentos],
            "itens": reg["itens"],
        })
    with open(os.path.join(dir_dados, "notas_completas.json"), "w",
              encoding="utf-8") as f:
        json.dump(completo, f, ensure_ascii=False, indent=1)

    return base


def gravar_nao_classificados(dados, pasta_saida: str):
    """Lista o que caiu em 'Outros' — é assim que lacunas de regra aparecem.

    Sem este arquivo, um produto mal classificado some no meio do total e só é
    percebido por acaso, olhando um gráfico.
    """
    linhas = []
    for reg in dados["_registros"]:
        for it in reg["itens"]:
            if it["categoria"] == "Outros" or it["dominio"] == "outro":
                linhas.append((reg["nota"].data_iso, reg["loja"], it["desc"],
                               it["categoria"], it["dominio"], it["vl_total"]))
    if not linhas:
        return None
    linhas.sort(key=lambda x: -x[5])
    caminho = os.path.join(pasta_saida, "Notas", "_DADOS",
                           "itens_nao_classificados.csv")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "loja", "descricao", "categoria", "dominio_consumo",
                    "valor"])
        for data, loja, desc, cat, dom, val in linhas:
            w.writerow([data, loja, desc, cat, dom, _n(val)])
    return caminho


def gravar_pendentes(notas_m55, pasta_saida: str):
    """As NF-e modelo 55, que não têm consulta pública."""
    if not notas_m55:
        return None
    caminho = os.path.join(pasta_saida, "Notas", "_DADOS",
                           "nfe_modelo55_sem_consulta_publica.csv")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["data", "origem", "razao_social", "numero", "valor", "chave",
                    "observacao"])
        for n in sorted(notas_m55, key=lambda x: x.emissao):
            w.writerow([n.emissao, n.origem, n.razao, n.numero, _n(n.valor),
                        n.chave,
                        "NF-e modelo 55: a consulta completa exige login gov.br"])
    return caminho


def gravar_falhas(falhas, pasta_saida: str):
    if not falhas:
        return None
    caminho = os.path.join(pasta_saida, "Notas", "_DADOS", "chaves_com_falha.csv")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["chave", "origem", "razao_social", "emissao", "valor"])
        for n in falhas:
            w.writerow([n.chave, n.origem, n.razao, n.emissao, _n(n.valor)])
    return caminho


LEIA_ME = """\
================================================================================
{titulo}
Notas fiscais de {inicio} a {fim}
Gerado por SLT - Gestao de Gastos em {gerado}
================================================================================

O QUE TEM AQUI
--------------------------------------------------------------------------------
As chaves de acesso das planilhas do programa Nota Fiscal Gaucha foram
consultadas uma a uma na SEFAZ-RS, em

    https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx?chaveNFe=<CHAVE>

e, em cada consulta, foi acionado o botao "Avancar" para abrir a Consulta
Completa da NFC-e. O conteudo de cada nota foi extraido e salvo aqui.

    {chaves} chaves nas planilhas
    {baixadas} NFC-e (modelo 65) baixadas
    {m55} NF-e (modelo 55) sem consulta publica
    {falhas} chave(s) com falha de download
    {itens} itens de produto extraidos


ESTRUTURA DAS PASTAS
--------------------------------------------------------------------------------
AAAA-MM/
    Uma pasta por mes, um arquivo .txt por nota, com a nota completa: emitente,
    CNPJ, endereco, numero, serie, data, hora, protocolo, CPF do consumidor,
    todos os produtos com codigo, quantidade, valor unitario e total, descontos,
    acrescimos, formas de pagamento, troco e a estimativa de tributos.

_HTML_ORIGINAL_SEFAZ/
    A pagina HTML original devolvida pela SEFAZ para cada chave, sem alteracao.

_DADOS/
    notas.csv ............ uma linha por nota
    itens.csv ............ uma linha por produto, ja classificado
    notas_completas.json . tudo em JSON, com os itens aninhados
    nfe_modelo55_sem_consulta_publica.csv
    chaves_com_falha.csv . so existe se alguma chave nao pode ser baixada


SOBRE OS TRIBUTOS
--------------------------------------------------------------------------------
IMPORTANTE: a consulta publica da NFC-e da SEFAZ-RS NAO divulga os valores de
tributos da nota. O campo "Valor aproximado dos tributos" da Lei 12.741/2012
existe no XML original, mas nao aparece na visualizacao publica, e a versao em
abas (com ICMS, PIS e COFINS item a item) exige login gov.br.

Por isso os valores de imposto sao ESTIMADOS: a cada item foi aplicada a carga
tributaria media da sua categoria (ICMS-RS + PIS/COFINS + IPI), o mesmo criterio
que os supermercados usam para imprimir o total de tributos no rodape do cupom.
E uma estimativa de ordem de grandeza, nao o valor exato recolhido.


SOBRE A CLASSIFICACAO DE CONSUMO
--------------------------------------------------------------------------------
Cada item foi classificado pelo TIPO do produto lido na descricao, nao pela loja
onde foi comprado - porque a descricao engana muito ("DESINF GOTA LIMPA LIMAO"
nao e fruta, "SAB NIVEA LEITE" nao e laticinio). Os grupos alimentares e o grau
de processamento seguem o Guia Alimentar para a Populacao Brasileira
(classificacao NOVA).

A leitura nutricional e do produto COMPRADO, nao do que foi efetivamente comido.
Nada aqui mede porcao, caloria ou nutriente, e nao substitui orientacao
profissional.

================================================================================
"""


def gravar_leia_me(dados, pasta_saida, chaves, baixadas, falhas):
    r = dados["resumo"]
    m = dados["meta"]
    txt = LEIA_ME.format(
        titulo=m["titulo"], inicio=m["inicio"], fim=m["fim"],
        gerado=datetime.date.fromisoformat(m["geradoEm"]).strftime("%d/%m/%Y"),
        chaves=chaves, baixadas=baixadas, m55=r["m55Notas"], falhas=falhas,
        itens=r["itens"])
    caminho = os.path.join(pasta_saida, "Notas", "LEIA-ME.txt")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(txt)
    return caminho
