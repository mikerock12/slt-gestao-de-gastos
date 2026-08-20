# -*- coding: utf-8 -*-
"""Consolida as notas extraídas no conjunto de dados que alimenta o relatório.

Funciona com uma pessoa ou com várias. Tudo que é "por pessoa" sai de uma lista,
nunca de nomes fixos.
"""
from __future__ import annotations

import collections
import datetime
import re
import statistics

from .categorias import CARGA, apelido, categoria_loja, categoria_produto
from .mapa import (MACRO, NOVA, ORDEM_GRUPOS, classe_medicamento, classificar,
                   sub_higiene, sub_limpeza)

MES_CURTO = ["jan", "fev", "mar", "abr", "mai", "jun",
             "jul", "ago", "set", "out", "nov", "dez"]
MES_LONGO = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
DIA_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

ACENTO = {
    "Bebidas alcoolicas": "Bebidas alcoólicas",
    "Refrigerantes e energeticos": "Refrigerantes e energéticos",
    "Aguas, sucos, cha e cafe": "Águas, sucos, chá e café",
    "Laticinios e ovos": "Laticínios e ovos",
    "Mercearia e basicos": "Mercearia e básicos",
    "Limpeza e utilidades domesticas": "Limpeza e utilidades domésticas",
    "Farmacia e medicamentos": "Farmácia e medicamentos",
    "Combustivel": "Combustível",
    "Refeicoes fora de casa": "Refeições fora de casa",
    "Vestuario e calcados": "Vestuário e calçados",
    "Vestuario": "Vestuário",
    "Farmacia": "Farmácia",
    "Mercado de bairro / conveniencia": "Mercado de bairro / conveniência",
    "Servicos automotivos": "Serviços automotivos",
    "Servicos digitais": "Serviços digitais",
    "Servicos graficos": "Serviços gráficos",
    "Material de construcao": "Material de construção",
}
ac = lambda s: ACENTO.get(s, s)

DOMINIOS = ["alimentacao", "higiene", "limpeza", "medicamento", "pet",
            "vestuario", "combustivel", "casa", "outro"]
DOM_NOME = {
    "alimentacao": "Alimentação", "higiene": "Higiene pessoal",
    "limpeza": "Limpeza da casa", "medicamento": "Medicamentos",
    "pet": "Pet", "vestuario": "Vestuário", "combustivel": "Combustível",
    "casa": "Casa e bazar", "outro": "Outros",
}


# ------------------------------------------------------------------ volumes
def litros_da_descricao(desc: str, qtd: float) -> float:
    """Volume da embalagem x quantidade. 0 quando não dá para saber.

    Três armadilhas reais nas descrições:
      "GF 2 5L"  -> 2,5 L   (o separador decimal virou espaço)
      "15LT"     -> 1,5 L   (o separador decimal sumiu)
      "20L"      -> 20 L    (galão de água, esse é literal)
    """
    t = (desc or "").upper().replace(",", ".")
    t = re.sub(r"(\d)\s+(\d)\s*(L|LT)\b", r"\1.\2\3", t)

    m = re.search(r"(\d+(?:\.\d+)?)\s*ML\b", t)
    if m:
        v = float(m.group(1)) / 1000
    else:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:L|LT|LTS|LITRO)\b", t)
        if not m:
            return 0.0
        v = float(m.group(1))
        if v >= 15 and v % 10 == 5:
            v /= 10
    if v <= 0 or v > 25:
        return 0.0
    pk = re.search(r"\bC\s*/?\s*(\d{1,2})\b|\bC(\d{1,2})\b|\bPACK\s*(\d{1,2})\b", t)
    if pk and ("FARDO" in t or "PACK" in t):
        n = int(next(g for g in pk.groups() if g))
        if 2 <= n <= 24:
            v *= n
    return v * (qtd or 1)


# ------------------------------------------------------------------- helper
def _idx(lista, mapa, v):
    if v not in mapa:
        mapa[v] = len(lista)
        lista.append(v)
    return mapa[v]


def montar(notas_completas, dono_por_chave, pessoas, e_familia,
           notas_m55, gerado_em=None):
    """`notas_completas`: [NotaCompleta] já extraídas
    `dono_por_chave`: {chave: índice da pessoa}
    `pessoas`: [Pessoa]
    `notas_m55`: [planilhas.Nota] das NF-e sem consulta pública
    """
    N = sorted(notas_completas, key=lambda n: (n.data_iso, n.hora))
    if not N:
        raise ValueError("nenhuma nota foi extraída")

    gerado_em = gerado_em or datetime.date.today().isoformat()
    D0 = datetime.date.fromisoformat(N[0].data_iso)
    D1 = datetime.date.fromisoformat(N[-1].data_iso)
    DIAS = (D1 - D0).days + 1
    DOW_INI = D0.weekday()
    NSEM = (DIAS - 1 + DOW_INI) // 7 + 1
    SEMANAS_FLOAT = DIAS / 7

    dia_de = lambda iso: (datetime.date.fromisoformat(iso) - D0).days
    semana_de = lambda dia: (dia + DOW_INI) // 7

    def datas_da_semana(s):
        ini = D0 + datetime.timedelta(days=s * 7 - DOW_INI)
        return (str(max(ini, D0)),
                str(min(ini + datetime.timedelta(days=6), D1)))

    nomes_pessoas = [p.nome for p in pessoas]

    # ---------------------------------------------------------- enriquecimento
    registros = []   # uma linha por nota
    detalhe = []     # uma linha por item
    for n in N:
        cat_loja = categoria_loja(n.emitente)
        loja = apelido(n.emitente)
        dono = dono_por_chave.get(n.chave, 0)
        liquido = round(n.valor_total - n.descontos, 2)
        valor_nota = liquido
        acrescimos = 0.0
        # a planilha registra o valor final; a diferença é taxa de entrega
        planilha = getattr(n, "valor_planilha", None)
        if planilha:
            valor_nota = planilha
            acrescimos = round(valor_nota - liquido, 2)
            if abs(acrescimos) < 0.02:
                acrescimos = 0.0
        troco = round(n.valor_pago - valor_nota, 2) if n.pagamentos else 0.0
        if troco < 0.02:
            troco = 0.0

        itens = []
        imposto = 0.0
        for it in n.itens:
            cat = categoria_produto(it.descricao, cat_loja)
            dom, grupo, nova = classificar(it.descricao)
            v = it.valor_total or 0.0
            t = round(v * CARGA[cat], 2)
            imposto += t
            itens.append({
                "cod": it.codigo, "desc": it.descricao, "qtd": it.quantidade,
                "un": (it.unidade or "").upper(), "vl_unit": it.valor_unitario,
                "vl_total": v, "categoria": cat, "imposto_est": t,
                "dominio": dom, "grupo": grupo, "nova": nova,
            })
            detalhe.append({
                "dia": dia_de(n.data_iso), "dom": dom, "grupo": grupo, "nova": nova,
                "desc": it.descricao, "valor": v, "qtd": it.quantidade or 0,
                "un": (it.unidade or "").upper(), "loja": loja,
                "pessoa": dono, "cat": cat,
            })

        registros.append({
            "nota": n, "loja": loja, "cat_loja": cat_loja, "pessoa": dono,
            "dia": dia_de(n.data_iso), "hora": int(n.hora[:2]) if n.hora else 0,
            "valor_nota": valor_nota, "acrescimos": acrescimos, "troco": troco,
            "imposto": round(imposto, 2), "itens": itens,
        })

    total = round(sum(r["valor_nota"] for r in registros), 2)
    total_produtos = round(sum(r["nota"].valor_total for r in registros), 2)
    total_itens = sum(len(r["itens"]) for r in registros)
    imposto_total = round(sum(r["imposto"] for r in registros), 2)

    # ------------------------------------------------------------------ índices
    cat_tot = collections.Counter()
    for r in registros:
        for i in r["itens"]:
            cat_tot[i["categoria"]] += i["vl_total"]
    cats = [c for c, _ in cat_tot.most_common()]
    cati = {c: i for i, c in enumerate(cats)}

    loja_tot = collections.Counter()
    for r in registros:
        loja_tot[r["loja"]] += r["valor_nota"]
    lojas = [l for l, _ in loja_tot.most_common()]
    lojai = {l: i for i, l in enumerate(lojas)}

    descs, desci, uns, uni = [], {}, [], {}
    grupos_alim = list(ORDEM_GRUPOS)
    grupoi = {g: i for i, g in enumerate(grupos_alim)}

    notas_brutas, itens_brutos = [], []
    for r in registros:
        li = lojai[r["loja"]]
        # o índice da nota vai junto de cada item: sem ele, duas compras na
        # mesma loja no mesmo dia se misturam na hora de listar os produtos
        ni = len(notas_brutas)
        notas_brutas.append([r["dia"], r["hora"], li, r["pessoa"],
                             r["valor_nota"], len(r["itens"]), r["imposto"]])
        for i in r["itens"]:
            itens_brutos.append([
                r["dia"], cati[i["categoria"]], li, r["pessoa"],
                round(i["vl_total"], 2), i["imposto_est"],
                _idx(descs, desci, i["desc"]),
                DOMINIOS.index(i["dominio"]),
                grupoi[i["grupo"]] if i["grupo"] else -1,
                i["nova"], round(i["qtd"] or 0, 3),
                _idx(uns, uni, i["un"]),
                ni,
            ])

    # ------------------------------------------------------------------ séries
    def agrega(chave_fn, campos=("valor_nota", "imposto")):
        m = collections.defaultdict(lambda: collections.Counter())
        for r in registros:
            k = chave_fn(r)
            m[k]["notas"] += 1
            m[k]["itens"] += len(r["itens"])
            for c in campos:
                m[k][c] += r[c]
        return m

    por_mes = agrega(lambda r: str(D0 + datetime.timedelta(days=r["dia"]))[:7])
    meses = []
    for k in sorted(por_mes):
        v = por_mes[k]
        mm = int(k[5:]) - 1
        linha = {
            "mes": k, "label": f"{MES_LONGO[mm]}/{k[:4]}", "curto": MES_CURTO[mm],
            "notas": int(v["notas"]), "total": round(v["valor_nota"], 2),
            "itens": int(v["itens"]), "imposto": round(v["imposto"], 2),
            "ticket": round(v["valor_nota"] / v["notas"], 2),
            "diasCompra": len({r["dia"] for r in registros
                               if str(D0 + datetime.timedelta(days=r["dia"]))[:7] == k}),
        }
        for pi, nome in enumerate(nomes_pessoas):
            linha[f"p{pi}"] = round(
                sum(r["valor_nota"] for r in registros
                    if r["pessoa"] == pi
                    and str(D0 + datetime.timedelta(days=r["dia"]))[:7] == k), 2)
        meses.append(linha)

    por_sem = agrega(lambda r: semana_de(r["dia"]))
    semanas = []
    for s in range(NSEM):
        v = por_sem.get(s)
        if not v:
            continue
        ini, fim = datas_da_semana(s)
        semanas.append({"i": s, "ini": ini, "fim": fim,
                        "total": round(v["valor_nota"], 2),
                        "notas": int(v["notas"]), "itens": int(v["itens"])})

    por_dia = agrega(lambda r: r["dia"])
    dias_lista = []
    for k in sorted(por_dia):
        v = por_dia[k]
        data = str(D0 + datetime.timedelta(days=k))
        dias_lista.append({
            "data": data, "dia": k,
            "dow": DIA_SEMANA[(D0 + datetime.timedelta(days=k)).weekday()],
            "notas": int(v["notas"]), "total": round(v["valor_nota"], 2),
            "itens": int(v["itens"]),
            "lojas": sorted({r["loja"] for r in registros if r["dia"] == k}),
        })
    dias_ord = sorted(dias_lista, key=lambda d: -d["total"])

    dow = collections.defaultdict(lambda: {"notas": 0, "total": 0.0, "dias": set()})
    for r in registros:
        d = D0 + datetime.timedelta(days=r["dia"])
        k = DIA_SEMANA[d.weekday()]
        dow[k]["notas"] += 1
        dow[k]["total"] += r["valor_nota"]
        dow[k]["dias"].add(r["dia"])
    dow_lista = [{"nome": k, "notas": v["notas"], "total": round(v["total"], 2),
                  "dias": len(v["dias"]),
                  "media": round(v["total"] / len(v["dias"]), 2)}
                 for k, v in sorted(dow.items(), key=lambda x: DIA_SEMANA.index(x[0]))]

    horas = collections.defaultdict(lambda: {"notas": 0, "total": 0.0})
    for r in registros:
        horas[r["hora"]]["notas"] += 1
        horas[r["hora"]]["total"] += r["valor_nota"]
    horas_lista = [{"hora": h, "notas": v["notas"], "total": round(v["total"], 2)}
                   for h, v in sorted(horas.items())]

    # ----------------------------------------------------------------- lojas
    lojas_info = []
    for l in lojas:
        rs = [r for r in registros if r["loja"] == l]
        t = round(sum(r["valor_nota"] for r in rs), 2)
        lojas_info.append({
            "nome": l, "razao": rs[0]["nota"].emitente,
            "categoria": ac(rs[0]["cat_loja"]), "notas": len(rs), "total": t,
            "itens": sum(len(r["itens"]) for r in rs),
            "imposto": round(sum(r["imposto"] for r in rs), 2),
            "ticket": round(t / len(rs), 2),
            "share": round(100 * t / total, 1) if total else 0,
        })

    cl = collections.defaultdict(lambda: {"notas": 0, "total": 0.0, "imposto": 0.0})
    for r in registros:
        k = ac(r["cat_loja"])
        cl[k]["notas"] += 1
        cl[k]["total"] += r["valor_nota"]
        cl[k]["imposto"] += r["imposto"]
    cat_loja_lista = sorted(
        ({"nome": k, "notas": v["notas"], "total": round(v["total"], 2),
          "imposto": round(v["imposto"], 2),
          "share": round(100 * v["total"] / total, 1) if total else 0}
         for k, v in cl.items()), key=lambda x: -x["total"])

    # ------------------------------------------------------------ categorias
    cat_info = []
    soma_itens = sum(i["vl_total"] for r in registros for i in r["itens"]) or 1
    for c in cats:
        its = [i for r in registros for i in r["itens"] if i["categoria"] == c]
        t = round(sum(i["vl_total"] for i in its), 2)
        cat_info.append({
            "nome": ac(c), "total": t, "itens": len(its),
            "imposto": round(sum(i["imposto_est"] for i in its), 2),
            "aliq": round(100 * CARGA[c], 1),
            "share": round(100 * t / soma_itens, 1),
        })

    # -------------------------------------------------------------- produtos
    prod = collections.defaultdict(
        lambda: {"n": 0, "qtd": 0.0, "total": 0.0, "cat": "", "un": "", "precos": []})
    for r in registros:
        for i in r["itens"]:
            p = prod[i["desc"].strip()]
            p["n"] += 1
            p["qtd"] += i["qtd"] or 0
            p["total"] += i["vl_total"]
            p["cat"] = ac(i["categoria"])
            p["un"] = i["un"]
            p["precos"].append((str(D0 + datetime.timedelta(days=r["dia"])), i["vl_unit"]))

    prod_freq = sorted(
        ({"desc": k, "vezes": v["n"], "qtd": round(v["qtd"], 3), "un": v["un"],
          "total": round(v["total"], 2), "categoria": v["cat"]}
         for k, v in prod.items() if v["n"] >= 3), key=lambda x: -x["vezes"])[:24]
    prod_valor = sorted(
        ({"desc": k, "vezes": v["n"], "qtd": round(v["qtd"], 3), "un": v["un"],
          "total": round(v["total"], 2), "categoria": v["cat"]}
         for k, v in prod.items()), key=lambda x: -x["total"])[:24]

    # --------------------------------------------------------- preço no tempo
    variacao = []
    for k, v in prod.items():
        ps = sorted(v["precos"])
        datas = sorted({d for d, _ in ps})
        if len(datas) < 3:
            continue
        dini = datetime.date.fromisoformat(datas[0])
        dfim = datetime.date.fromisoformat(datas[-1])
        if (dfim - dini).days < 45:
            continue
        prim = [p for d, p in ps if d in datas[:2] and p]
        ult = [p for d, p in ps if d in datas[-2:] and p]
        if not prim or not ult:
            continue
        p0, p1 = statistics.mean(prim), statistics.mean(ult)
        if p0 < 1.0:
            continue
        todos = [p for _, p in ps if p]
        variacao.append({
            "desc": k, "categoria": v["cat"], "un": v["un"], "vezes": v["n"],
            "p0": round(p0, 2), "p1": round(p1, 2),
            "var": round(100 * (p1 - p0) / p0, 1),
            "de": datas[0], "ate": datas[-1], "dias": (dfim - dini).days,
            "min": round(min(todos), 2), "max": round(max(todos), 2),
        })
    variacao.sort(key=lambda x: -x["var"])
    subiu = [v for v in variacao if v["var"] >= 1][:12]
    caiu = [v for v in variacao if v["var"] < 0][-12:][::-1]

    # -------------------------------------------------------------- pagamento
    pag = collections.defaultdict(lambda: {"notas": 0, "total": 0.0})
    for r in registros:
        for p in r["nota"].pagamentos:
            forma = p.forma or "Não informada"
            pag[forma]["notas"] += 1
            pag[forma]["total"] += p.valor
    pagamento = sorted(({"forma": k, "notas": v["notas"], "total": round(v["total"], 2)}
                        for k, v in pag.items()), key=lambda x: -x["total"])

    # ------------------------------------------------------------- extremos
    ord_notas = sorted(registros, key=lambda r: -r["valor_nota"])
    maiores_notas = [{
        "data": str(D0 + datetime.timedelta(days=r["dia"])),
        "hora": r["nota"].hora, "loja": r["loja"],
        "pessoa": nomes_pessoas[r["pessoa"]],
        "valor": r["valor_nota"], "itens": len(r["itens"])} for r in ord_notas[:10]]

    todos_itens = sorted(
        ((i, r) for r in registros for i in r["itens"]),
        key=lambda x: -x[0]["vl_total"])
    maiores_itens = [{
        "desc": i["desc"], "valor": round(i["vl_total"], 2),
        "data": str(D0 + datetime.timedelta(days=r["dia"])),
        "loja": r["loja"], "categoria": ac(i["categoria"])}
        for i, r in todos_itens[:10]]

    imposto_loja = sorted(
        ({"loja": l["nome"], "imposto": l["imposto"], "total": l["total"],
          "aliq": round(100 * l["imposto"] / l["total"], 1) if l["total"] else 0}
         for l in lojas_info), key=lambda x: -x["imposto"])[:14]

    # ---------------------------------------------------------- alimentação
    AL = [d for d in detalhe if d["dom"] == "alimentacao"]
    alimentacao = _bloco_alimentacao(AL, D0, DIAS, NSEM, semana_de, datas_da_semana,
                                     grupos_alim)

    # ------------------------------------------------------ higiene e limpeza
    higiene = _bloco_higiene(detalhe, D0)

    # ------------------------------------------------------------ remédios
    medicamentos = _bloco_medicamentos(detalhe, D0, DIAS)

    # ------------------------------------------------------------- domínios
    dom_val = collections.Counter()
    dom_it = collections.Counter()
    for d in detalhe:
        dom_val[d["dom"]] += d["valor"]
        dom_it[d["dom"]] += 1
    tot_dom = sum(dom_val.values()) or 1
    dominio_resumo = sorted(
        ({"id": k, "nome": DOM_NOME[k], "total": round(v, 2), "itens": dom_it[k],
          "share": round(100 * v / tot_dom, 1)} for k, v in dom_val.items()),
        key=lambda x: -x["total"])

    # ------------------------------------------------------------ pessoas
    pessoas_info = []
    for pi, p in enumerate(pessoas):
        rs = [r for r in registros if r["pessoa"] == pi]
        t = round(sum(r["valor_nota"] for r in rs), 2)
        pessoas_info.append({
            "nome": p.nome, "cpf": p.cpf_mascarado,
            "notas": len(rs), "itens": sum(len(r["itens"]) for r in rs),
            "total": t, "imposto": round(sum(r["imposto"] for r in rs), 2),
            "ticket": round(t / len(rs), 2) if rs else 0,
            "share": round(100 * t / total, 1) if total else 0,
        })

    total_m55 = round(sum(n.valor for n in notas_m55), 2)
    m55_por_loja = collections.defaultdict(lambda: {"notas": 0, "total": 0.0})
    for n in notas_m55:
        m55_por_loja[n.razao]["notas"] += 1
        m55_por_loja[n.razao]["total"] += n.valor
    m55 = sorted(({"razao": k, "notas": v["notas"], "total": round(v["total"], 2)}
                  for k, v in m55_por_loja.items()), key=lambda x: -x["total"])

    descontos = round(sum(r["nota"].descontos for r in registros), 2)
    dias_com_compra = len({r["dia"] for r in registros})

    return {
        "meta": {
            "inicio": str(D0), "fim": str(D1), "dias": DIAS, "semanas": NSEM,
            "dowInicio": DOW_INI, "geradoEm": gerado_em,
            "familia": e_familia,
            "titulo": " e ".join(nomes_pessoas) if e_familia else nomes_pessoas[0],
            "municipio": collections.Counter(
                n.municipio for n in notas_m55).most_common(1)[0][0] if notas_m55 else "",
        },
        "resumo": {
            "total": total, "totalGeral": round(total + total_m55, 2),
            "m55Total": total_m55, "m55Notas": len(notas_m55),
            "notas": len(registros), "itens": total_itens,
            "produtosDistintos": len(prod),
            "ticket": round(total / len(registros), 2),
            "valorItem": round(soma_itens / total_itens, 2) if total_itens else 0,
            "mediaDia": round(total / DIAS, 2),
            "mediaSemana": round(total / SEMANAS_FLOAT, 2),
            "mediaMes": round(total / (DIAS / 30.44), 2),
            "diasComCompra": dias_com_compra,
            "descontos": descontos,
            "descontoShare": round(100 * descontos / (total_produtos or 1), 1),
            "imposto": imposto_total,
            "aliqMedia": round(100 * imposto_total / (total_produtos or 1), 1),
            "valorProdutos": total_produtos,
            "lojasDistintas": len(lojas),
            "cnpjs": len({r["nota"].cnpj for r in registros}),
            "semanasFloat": round(SEMANAS_FLOAT, 1),
        },
        "pessoas": pessoas_info,
        "categorias": cat_info,
        "lojas": lojas_info,
        "catLoja": cat_loja_lista,
        "meses": meses,
        "semanas": semanas,
        "dow": dow_lista,
        "horas": horas_lista,
        "produtosFreq": prod_freq,
        "produtosValor": prod_valor,
        "precoSubiu": subiu,
        "precoCaiu": caiu,
        "precoMeta": {
            "amostra": len(variacao),
            "media": round(statistics.mean([v["var"] for v in variacao]), 1) if variacao else 0,
            "mediana": round(statistics.median([v["var"] for v in variacao]), 1) if variacao else 0,
        },
        "pagamento": pagamento,
        "diaTop": dias_ord[:10],
        "diaBottom": dias_ord[-10:][::-1],
        "diaStats": {
            "media": round(statistics.mean([d["total"] for d in dias_lista]), 2),
            "mediana": round(statistics.median([d["total"] for d in dias_lista]), 2),
        },
        "maioresNotas": maiores_notas,
        "maioresItens": maiores_itens,
        "impostoLoja": imposto_loja,
        "m55": m55,
        "nomesCategorias": [ac(c) for c in cats],
        "nomesLojas": lojas,
        "pessoasNomes": nomes_pessoas,
        "descricoes": descs,
        "unidades": uns,
        "gruposAlim": grupos_alim,
        "dominios": DOMINIOS,
        "dominioNomes": [DOM_NOME[d] for d in DOMINIOS],
        "macroDeGrupo": [MACRO[g] for g in grupos_alim],
        "novaNomes": {str(k): v for k, v in NOVA.items()},
        "notasBrutas": notas_brutas,
        "itensBrutos": itens_brutos,
        "alimentacao": alimentacao,
        "higiene": higiene,
        "medicamentos": medicamentos,
        "dominioResumo": dominio_resumo,
        "_registros": registros,   # uso interno (gravação dos arquivos)
    }


# =========================================================== blocos temáticos
def _bloco_alimentacao(AL, D0, DIAS, NSEM, semana_de, datas_da_semana, grupos_alim):
    total = round(sum(d["valor"] for d in AL), 2)
    sem_alcool = [d for d in AL if d["grupo"] != "Bebidas alcoólicas"]
    total_sa = round(sum(d["valor"] for d in sem_alcool), 2) or 1

    g_val, g_it, g_kg, g_l = (collections.Counter() for _ in range(4))
    macro_val, macro_it = collections.Counter(), collections.Counter()
    nova_val, nova_it, nova_sa = (collections.Counter() for _ in range(3))
    for d in AL:
        g_val[d["grupo"]] += d["valor"]
        g_it[d["grupo"]] += 1
        if d["un"] in ("KG", "KGS"):
            g_kg[d["grupo"]] += d["qtd"]
        L = litros_da_descricao(d["desc"], d["qtd"])
        if L:
            g_l[d["grupo"]] += L
        macro_val[MACRO[d["grupo"]]] += d["valor"]
        macro_it[MACRO[d["grupo"]]] += 1
        nova_val[d["nova"]] += d["valor"]
        nova_it[d["nova"]] += 1
    for d in sem_alcool:
        nova_sa[d["nova"]] += d["valor"]

    GRUPOS_BEBIDA = ("Bebidas alcoólicas", "Refrigerantes e energéticos",
                     "Água, café, chá e sucos")
    bebidas = [d for d in AL if d["grupo"] in GRUPOS_BEBIDA]
    sem_volume = sum(1 for d in bebidas if not litros_da_descricao(d["desc"], d["qtd"]))

    # semana a semana (NOVA sempre sem álcool, para bater com a base)
    sem = collections.defaultdict(lambda: collections.Counter())
    sem_itens = collections.Counter()
    for d in AL:
        s = semana_de(d["dia"])
        w = sem[s]
        w["total"] += d["valor"]
        w[MACRO[d["grupo"]]] += d["valor"]
        if d["grupo"] != "Bebidas alcoólicas":
            w["semAlcool"] += d["valor"]
            w["nova%d" % d["nova"]] += d["valor"]
        sem_itens[s] += 1

    semanas = []
    for s in range(NSEM):
        w = sem.get(s)
        if not w:
            continue
        base = w["semAlcool"]
        ini, fim = datas_da_semana(s)
        semanas.append({
            "i": s, "ini": ini, "fim": fim,
            "total": round(w["total"], 2), "semAlcool": round(base, 2),
            "itens": sem_itens[s],
            "nova1": round(w["nova1"], 2), "nova2": round(w["nova2"], 2),
            "nova3": round(w["nova3"], 2), "nova4": round(w["nova4"], 2),
            "qualidade": round(100 * (w["nova1"] + w["nova2"]) / base, 1) if base else 0,
            "ultraShare": round(100 * w["nova4"] / base, 1) if base else 0,
            "alcool": round(w["Bebidas alcoólicas"], 2),
            "refri": round(w["Refrigerantes"], 2),
            "frutas": round(w["Frutas"], 2),
            "verduras": round(w["Verduras e legumes"], 2),
            "proteinas": round(w["Proteínas"], 2),
            "carboidratos": round(w["Carboidratos"], 2),
            "cereais": round(w["Cereais e grãos"], 2),
            "ultra": round(w["Ultraprocessados e doces"], 2),
        })

    com_base = [s for s in semanas if s["semAlcool"] >= 40]
    pior = min(com_base, key=lambda s: s["qualidade"]) if com_base else None
    melhor = max(com_base, key=lambda s: s["qualidade"]) if com_base else None

    mes = collections.defaultdict(lambda: collections.Counter())
    for d in AL:
        k = str(D0 + datetime.timedelta(days=d["dia"]))[:7]
        w = mes[k]
        w["total"] += d["valor"]
        w[MACRO[d["grupo"]]] += d["valor"]
        if d["grupo"] != "Bebidas alcoólicas":
            w["semAlcool"] += d["valor"]
            w["nova%d" % d["nova"]] += d["valor"]
    meses = []
    for k in sorted(mes):
        w = mes[k]
        base = w["semAlcool"]
        meses.append({
            "mes": k, "total": round(w["total"], 2), "semAlcool": round(base, 2),
            "qualidade": round(100 * (w["nova1"] + w["nova2"]) / base, 1) if base else 0,
            "ultraShare": round(100 * w["nova4"] / base, 1) if base else 0,
            "alcool": round(w["Bebidas alcoólicas"], 2),
            "frutas": round(w["Frutas"], 2),
            "verduras": round(w["Verduras e legumes"], 2),
            "proteinas": round(w["Proteínas"], 2),
            "ultra": round(w["Ultraprocessados e doces"], 2),
            "refri": round(w["Refrigerantes"], 2),
        })

    dia = collections.defaultdict(lambda: collections.Counter())
    for d in AL:
        w = dia[d["dia"]]
        w["total"] += d["valor"]
        w["itens"] += 1
        w[MACRO[d["grupo"]]] += d["valor"]
        if d["nova"] == 4:
            w["ultra"] += d["valor"]
        if d["nova"] in (1, 2):
            w["real"] += d["valor"]
    dias = [{
        "dia": k, "data": str(D0 + datetime.timedelta(days=k)),
        "total": round(v["total"], 2), "itens": int(v["itens"]),
        "real": round(v["real"], 2), "ultra": round(v["ultra"], 2),
        "alcool": round(v["Bebidas alcoólicas"], 2),
        "frutas": round(v["Frutas"], 2),
        "verduras": round(v["Verduras e legumes"], 2),
        "proteinas": round(v["Proteínas"], 2)} for k, v in sorted(dia.items())]

    top = {}
    for g in grupos_alim:
        c, q = collections.Counter(), collections.Counter()
        for d in AL:
            if d["grupo"] == g:
                c[d["desc"]] += d["valor"]
                q[d["desc"]] += 1
        if c:
            top[g] = [{"desc": k, "total": round(v, 2), "vezes": q[k]}
                      for k, v in c.most_common(8)]

    semanas_float = DIAS / 7
    return {
        "total": total, "totalSemAlcool": total_sa, "itens": len(AL),
        "grupos": [{"nome": g, "macro": MACRO[g], "total": round(g_val[g], 2),
                    "itens": g_it[g], "kg": round(g_kg[g], 2),
                    "litros": round(g_l[g], 1),
                    "share": round(100 * g_val[g] / (total or 1), 1)}
                   for g in grupos_alim if g_val[g] > 0],
        "macro": [{"nome": k, "total": round(v, 2), "itens": macro_it[k],
                   "share": round(100 * v / (total or 1), 1)}
                  for k, v in macro_val.most_common()],
        "nova": [{"n": k, "nome": NOVA[k], "total": round(nova_val[k], 2),
                  "itens": nova_it[k],
                  "share": round(100 * nova_val[k] / (total or 1), 1),
                  "shareSemAlcool": round(100 * nova_sa[k] / total_sa, 1)}
                 for k in (1, 2, 3, 4)],
        "semanas": semanas, "meses": meses, "dias": dias, "topPorGrupo": top,
        "qualidadeMedia": round(100 * (nova_sa[1] + nova_sa[2]) / total_sa, 1),
        "ultraShareMedio": round(100 * nova_sa[4] / total_sa, 1),
        "piorSemana": pior, "melhorSemana": melhor,
        "kg": {"frutas": round(g_kg["Frutas"], 2),
               "verduras": round(g_kg["Verduras e legumes"], 2),
               "carnes": round(g_kg["Carnes, aves e peixes"], 2),
               "frutasPorSemana": round(g_kg["Frutas"] / semanas_float, 2),
               "verdurasPorSemana": round(g_kg["Verduras e legumes"] / semanas_float, 2),
               "carnesPorSemana": round(g_kg["Carnes, aves e peixes"] / semanas_float, 2)},
        "litros": {"alcool": round(g_l["Bebidas alcoólicas"], 1),
                   "refri": round(g_l["Refrigerantes e energéticos"], 1),
                   "agua": round(g_l["Água, café, chá e sucos"], 1),
                   "alcoolPorSemana": round(g_l["Bebidas alcoólicas"] / semanas_float, 2),
                   "refriPorSemana": round(g_l["Refrigerantes e energéticos"] / semanas_float, 2),
                   "itensBebida": len(bebidas), "itensSemVolume": sem_volume},
        "diasComAlcool": len({d["dia"] for d in AL if d["grupo"] == "Bebidas alcoólicas"}),
        "diasComFrutaOuVerdura": len({d["dia"] for d in AL
                                      if d["grupo"] in ("Frutas", "Verduras e legumes")}),
        "diasComAlimento": len({d["dia"] for d in AL}),
    }


def _agrupa_sub(lista, fn):
    val, it, un = collections.Counter(), collections.Counter(), collections.Counter()
    for d in lista:
        k = fn(d["desc"])
        val[k] += d["valor"]
        it[k] += 1
        un[k] += d["qtd"] if d["un"] in ("UN", "UNID", "") else 1
    tot = sum(val.values()) or 1
    return sorted(({"nome": k, "total": round(v, 2), "itens": it[k],
                    "unidades": round(un[k], 1),
                    "share": round(100 * v / tot, 1)} for k, v in val.items()),
                  key=lambda x: -x["total"])


def _por_mes(lista, D0):
    m = collections.defaultdict(lambda: collections.Counter())
    for d in lista:
        k = str(D0 + datetime.timedelta(days=d["dia"]))[:7]
        m[k]["total"] += d["valor"]
        m[k]["itens"] += 1
    return [{"mes": k, "total": round(v["total"], 2), "itens": int(v["itens"])}
            for k, v in sorted(m.items())]


ESSENCIAIS = [
    ("Papel higiênico", "higiene", r"PAPEL HIG"),
    ("Sabonete", "higiene", r"^SAB\b|^SABONETE|^CBEM SAB"),
    ("Creme dental", "higiene", r"^CR DENT|^CREME DENT|^CRM DENT|^GEL D |^CR ORAL|^CR CLOSEUP"),
    ("Shampoo e condicionador", "higiene", r"^SH\b|^SHAMPOO|^COND\b|^CONDICION"),
    ("Desodorante", "higiene", r"^DES\b|^DESOD|^DESODAERO"),
    ("Absorvente", "higiene", r"^ABS\b|^ABSORVENTE"),
    ("Lava-roupas", "limpeza", r"^LAVA ROUPA|^L ROUP"),
    ("Amaciante", "limpeza", r"^AMAC"),
    ("Detergente de louça", "limpeza", r"^DETER"),
    ("Desinfetante", "limpeza", r"^DESINF"),
    ("Saco de lixo", "limpeza", r"^SACO LIXO|^SACO REFORCADO"),
    ("Esponja", "limpeza", r"^ESPONJA|^LA DE ACO"),
]


def _bloco_higiene(detalhe, D0):
    HI = [d for d in detalhe if d["dom"] == "higiene"]
    LI = [d for d in detalhe if d["dom"] == "limpeza"]

    essenciais = []
    for nome, area, padrao in ESSENCIAIS:
        base = HI if area == "higiene" else LI
        rx = re.compile(padrao)
        casos = [d for d in base if rx.search(d["desc"].upper())]
        dias = sorted({d["dia"] for d in casos})
        if len(dias) < 2:
            continue
        gaps = [b - a for a, b in zip(dias, dias[1:])]
        essenciais.append({
            "nome": nome, "area": "Higiene" if area == "higiene" else "Limpeza",
            "compras": len(dias),
            "intervaloMedio": round(statistics.mean(gaps), 1),
            "ultimo": str(D0 + datetime.timedelta(days=dias[-1])),
            "total": round(sum(d["valor"] for d in casos), 2),
            "unidades": round(sum(d["qtd"] for d in casos), 1),
        })
    essenciais.sort(key=lambda x: x["intervaloMedio"])

    def top(lista):
        c = collections.Counter()
        for d in lista:
            c[d["desc"]] += d["valor"]
        return [{"desc": k, "total": round(v, 2)} for k, v in c.most_common(12)]

    return {
        "higieneTotal": round(sum(d["valor"] for d in HI), 2), "higieneItens": len(HI),
        "limpezaTotal": round(sum(d["valor"] for d in LI), 2), "limpezaItens": len(LI),
        "subHigiene": _agrupa_sub(HI, sub_higiene),
        "subLimpeza": _agrupa_sub(LI, sub_limpeza),
        "mesHigiene": _por_mes(HI, D0), "mesLimpeza": _por_mes(LI, D0),
        "essenciais": essenciais,
        "topHigiene": top(HI), "topLimpeza": top(LI),
    }


def _bloco_medicamentos(detalhe, D0, DIAS):
    ME = [d for d in detalhe if d["dom"] == "medicamento"]
    val, it, rec = collections.Counter(), collections.Counter(), {}
    for d in ME:
        nome, receita = classe_medicamento(d["desc"])
        val[nome] += d["valor"]
        it[nome] += 1
        rec[nome] = receita
    tot = sum(val.values())

    linha = sorted(({
        "data": str(D0 + datetime.timedelta(days=d["dia"])),
        "desc": d["desc"], "classe": classe_medicamento(d["desc"])[0],
        "receita": classe_medicamento(d["desc"])[1],
        "valor": round(d["valor"], 2), "loja": d["loja"]} for d in ME),
        key=lambda x: x["data"])

    por_loja = collections.Counter()
    for d in ME:
        por_loja[d["loja"]] += d["valor"]
    farmacia = round(sum(v for k, v in por_loja.items()
                         if re.search(r"(?i)farm|droga|drogaria|panvel|medicament", k)), 2)

    return {
        "total": round(tot, 2), "itens": len(ME),
        "classes": sorted(({"nome": k, "receita": rec[k], "total": round(v, 2),
                            "itens": it[k],
                            "share": round(100 * v / tot, 1) if tot else 0}
                           for k, v in val.items()), key=lambda x: -x["total"]),
        "linha": linha, "porMes": _por_mes(ME, D0),
        "diasComCompra": len({d["dia"] for d in ME}),
        "gastoMensal": round(tot / (DIAS / 30.44), 2) if DIAS else 0,
        "emFarmacia": farmacia,
        "foraFarmacia": round(tot - farmacia, 2),
        "shareForaFarmacia": round(100 * (tot - farmacia) / tot, 1) if tot else 0,
    }
