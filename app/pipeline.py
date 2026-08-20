# -*- coding: utf-8 -*-
"""O trabalho todo, do zero ao relatório aberto no navegador."""
from __future__ import annotations

import datetime
import json
import os
import traceback
from dataclasses import dataclass, field

from . import extrair, pessoas as mod_pessoas, planilhas, relatorio, salvar, sefaz
from .analise import montar


@dataclass
class Resultado:
    ok: bool = False
    erro: str = ""
    pasta_saida: str = ""
    relatorio: str = ""
    pasta_notas: str = ""
    chaves: int = 0
    baixadas: int = 0
    falhas: int = 0
    m55: int = 0
    itens: int = 0
    pessoas: list = field(default_factory=list)
    familia: bool = False
    avisos: list[str] = field(default_factory=list)


class Cancelado(Exception):
    pass


def executar(pasta_entrada: str, pasta_saida: str, aviso=None, cancelado=None,
             passo=None) -> Resultado:
    """`aviso(texto)` para mensagens, `passo(fase, feito, total)` para a barra."""
    r = Resultado(pasta_saida=pasta_saida)
    diz = aviso or (lambda *_: None)
    marca = passo or (lambda *_: None)
    parar = cancelado or (lambda: False)

    try:
        if not os.path.isdir(pasta_entrada):
            r.erro = ("A pasta escolhida não existe mais:\n\n"
                      f"{pasta_entrada}\n\n"
                      "Escolha de novo a pasta onde estão as planilhas.")
            return r
        os.makedirs(pasta_saida, exist_ok=True)

        # ------------------------------------------------ 1. ler as planilhas
        diz("Lendo as planilhas…")
        marca("planilhas", 0, 1)
        arquivos = planilhas.ler_pasta(pasta_entrada)
        if not arquivos:
            r.erro = ("Nenhuma planilha .xlsx encontrada na pasta escolhida.\n\n"
                      "Coloque ali o arquivo que você baixa do site do Nota Fiscal "
                      "Gaúcha (um por pessoa) e tente de novo.")
            return r

        com_notas = [p for p in arquivos if p.notas]
        for p in arquivos:
            for a in p.avisos:
                r.avisos.append(f"{os.path.basename(p.caminho)}: {a}")
        if not com_notas:
            r.erro = ("As planilhas foram abertas, mas nenhuma chave de acesso "
                      "válida foi encontrada.\n\nConfira se o arquivo é mesmo o "
                      "export do Nota Fiscal Gaúcha, com a coluna "
                      "\"Chave de Acesso\".")
            return r

        todas = [n for p in com_notas for n in p.notas]
        # chave repetida em mais de uma planilha fica com a primeira
        vistas, unicas = set(), []
        for n in todas:
            if n.chave in vistas:
                continue
            vistas.add(n.chave)
            unicas.append(n)

        nfce = [n for n in unicas if n.modelo == "65"]
        m55 = [n for n in unicas if n.modelo != "65"]
        r.chaves = len(unicas)
        r.m55 = len(m55)
        marca("planilhas", 1, 1)
        diz(f"{len(com_notas)} planilha(s), {len(unicas)} chaves — "
            f"{len(nfce)} NFC-e e {len(m55)} NF-e sem consulta pública.")

        if not nfce:
            r.erro = ("Todas as chaves das planilhas são NF-e modelo 55, que não "
                      "têm consulta pública (o portal exige login gov.br).\n\n"
                      "Não há o que detalhar.")
            return r

        # ------------------------------------------------ 2. baixar da SEFAZ
        cache = os.path.join(pasta_saida, ".cache_sefaz")
        diz(f"Consultando a SEFAZ-RS — {len(nfce)} notas. "
            "Isso leva alguns minutos na primeira vez.")

        def p_baixa(feitas, total, chave, estado):
            marca("baixando", feitas, total)
            if parar():
                raise Cancelado()

        baixadas = sefaz.baixar(
            [n.chave for n in nfce], cache,
            progresso=p_baixa, cancelado=parar)
        if parar():
            raise Cancelado()

        falhas = [n for n in nfce if n.chave not in baixadas]
        r.baixadas = len(baixadas)
        r.falhas = len(falhas)
        if falhas:
            diz(f"{len(falhas)} nota(s) não puderam ser baixadas. "
                "Elas ficam listadas em chaves_com_falha.csv.")
        if not baixadas:
            r.erro = ("Não foi possível baixar nenhuma nota da SEFAZ-RS.\n\n"
                      "Verifique a conexão com a internet e tente de novo — "
                      "o que já tiver sido baixado é reaproveitado.")
            return r

        # ------------------------------------------------ 3. extrair
        diz("Lendo o conteúdo das notas…")
        por_chave = {n.chave: n for n in nfce}
        dono_por_chave: dict[str, int] = {}
        por_planilha: dict[str, list] = {}
        extraidas = []
        total_ex = len(baixadas)
        for k, (chave, caminho) in enumerate(baixadas.items(), 1):
            if parar():
                raise Cancelado()
            try:
                nc = extrair.ler(caminho, chave)
            except Exception:
                r.avisos.append(f"nota {chave[-8:]}: não consegui interpretar a página")
                continue
            if not nc.data or not nc.itens:
                r.avisos.append(f"nota {chave[-8:]}: página sem itens, ignorada")
                continue
            origem = por_chave[chave].origem
            nc.valor_planilha = por_chave[chave].valor or None
            por_planilha.setdefault(origem, []).append(nc)
            extraidas.append(nc)
            if k % 25 == 0:
                marca("lendo", k, total_ex)
        marca("lendo", total_ex, total_ex)

        if not extraidas:
            r.erro = "As páginas foram baixadas, mas nenhuma pôde ser interpretada."
            return r

        # ------------------------------------------------ 4. quem é quem
        lista_pessoas, familia = mod_pessoas.identificar(por_planilha)
        indice = {}
        for i, p in enumerate(lista_pessoas):
            for rot in p.planilhas:
                indice[rot] = i
        for chave, nc in ((n.chave, n) for n in extraidas):
            dono_por_chave[chave] = indice.get(por_chave[chave].origem, 0)

        r.pessoas = [p.nome for p in lista_pessoas]
        r.familia = familia
        diz("Identificado: " + mod_pessoas.titulo_do_conjunto(lista_pessoas)
            + (" (família)" if familia else ""))

        # ------------------------------------------------ 5. analisar
        diz("Analisando e classificando os produtos…")
        marca("analise", 0, 1)
        dados = montar(extraidas, dono_por_chave, lista_pessoas, familia, m55)
        r.itens = dados["resumo"]["itens"]
        marca("analise", 1, 1)

        # ------------------------------------------------ 6. gravar
        diz("Gravando as notas em disco…")
        r.pasta_notas = salvar.gravar(
            dados, baixadas, pasta_saida,
            progresso=lambda f, t: marca("gravando", f, t))
        salvar.gravar_pendentes(m55, pasta_saida)
        salvar.gravar_nao_classificados(dados, pasta_saida)
        salvar.gravar_falhas(falhas, pasta_saida)
        salvar.gravar_leia_me(dados, pasta_saida, r.chaves, r.baixadas, r.falhas)

        # ------------------------------------------------ 7. relatório
        diz("Montando o relatório…")
        marca("relatorio", 0, 1)
        limpo = {k: v for k, v in dados.items() if not k.startswith("_")}
        with open(os.path.join(pasta_saida, "Notas", "_DADOS", "dados_relatorio.json"),
                  "w", encoding="utf-8") as f:
            json.dump(limpo, f, ensure_ascii=False, separators=(",", ":"))
        r.relatorio = relatorio.gerar(limpo, pasta_saida)
        marca("relatorio", 1, 1)

        r.ok = True
        diz("Pronto.")
        return r

    except Cancelado:
        r.erro = "Cancelado. O que já foi baixado fica guardado para a próxima vez."
        return r
    except Exception as e:
        r.erro = f"{type(e).__name__}: {e}\n\n{traceback.format_exc(limit=4)}"
        return r
