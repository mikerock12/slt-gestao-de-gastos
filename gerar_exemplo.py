# -*- coding: utf-8 -*-
"""Gera um conjunto de dados FICTÍCIO para demonstração.

Serve para o painel e o relatório funcionarem sem que ninguém precise expor as
próprias notas. Nada aqui vem de nota fiscal real: as lojas, as pessoas e as
compras são inventadas; os nomes de produto são genéricos de supermercado.

    python gerar_exemplo.py [pasta de saída]
"""
from __future__ import annotations

import datetime
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.analise import montar
from app.extrair import Item, NotaCompleta, Pagamento
from app.pessoas import Pessoa

SEMENTE = 20260819
INICIO = datetime.date(2026, 1, 5)
DIAS = 182

PESSOAS = [
    Pessoa(nome="Ana", cpf="000.000.000-00", planilhas=["exemplo-ana.xlsx"]),
    Pessoa(nome="Bruno", cpf="111.111.111-11", planilhas=["exemplo-bruno.xlsx"]),
]

LOJAS = [
    ("SUPERMERCADO MODELO LTDA", "11.111.111/0001-11", "AV DAS FLORES, 100, CENTRO", 0.42),
    ("MERCADO DA ESQUINA ME", "22.222.222/0001-22", "RUA DAS ACACIAS, 25, JARDIM", 0.24),
    ("HIPER BOM PRECO SA", "33.333.333/0001-33", "AV BRASIL, 4000, ZONA NORTE", 0.14),
    ("DROGARIA SAUDE LTDA", "44.444.444/0001-44", "RUA CENTRAL, 88, CENTRO", 0.05),
    ("PADARIA PAO QUENTE", "55.555.555/0001-55", "RUA DAS PALMEIRAS, 12", 0.06),
    ("POSTO ESTRADA COMBUSTIVEIS", "66.666.666/0001-66", "BR 101, KM 20", 0.03),
    ("LANCHONETE DA PRACA", "77.777.777/0001-77", "PRACA MATRIZ, 5", 0.04),
    ("PET E CIA COMERCIO", "88.888.888/0001-88", "AV DAS FLORES, 300", 0.02),
]

# (descrição, preço base, unidade, peso na sorteio)
CESTA = [
    ("ARROZ BRANCO TIPO 1 5KG", 24.90, "UN", 3),
    ("FEIJAO PRETO 1KG", 8.49, "UN", 3),
    ("MACARRAO ESPAGUETE 500G", 4.29, "UN", 3),
    ("OLEO DE SOJA 900ML", 7.89, "UN", 2),
    ("ACUCAR REFINADO 1KG", 4.99, "UN", 2),
    ("SAL REFINADO 1KG", 2.49, "UN", 1),
    ("CAFE TORRADO E MOIDO 500G", 18.90, "UN", 3),
    ("LEITE INTEGRAL LONGA VIDA 1L", 5.29, "UN", 5),
    ("QUEIJO MUSSARELA FATIADO 150G", 11.90, "UN", 3),
    ("REQUEIJAO CREMOSO 200G", 8.49, "UN", 2),
    ("IOGURTE NATURAL 170G", 3.29, "UN", 3),
    ("MANTEIGA COM SAL 200G", 12.90, "UN", 2),
    ("OVOS BRANCOS COM 12", 13.99, "UN", 4),
    ("PEITO DE FRANGO KG", 18.90, "KG", 4),
    ("COXAO MOLE BOVINO KG", 44.90, "KG", 3),
    ("COSTELA SUINA KG", 22.90, "KG", 2),
    ("FILE DE TILAPIA KG", 39.90, "KG", 1),
    ("LINGUICA TOSCANA 700G", 19.90, "UN", 2),
    ("BANANA PRATA KG", 6.49, "KG", 4),
    ("MACA GALA KG", 9.90, "KG", 3),
    ("LARANJA PERA KG", 4.99, "KG", 2),
    ("MAMAO FORMOSA KG", 7.90, "KG", 2),
    ("TOMATE LONGA VIDA KG", 8.90, "KG", 3),
    ("CEBOLA BRANCA KG", 5.49, "KG", 3),
    ("BATATA INGLESA KG", 5.99, "KG", 3),
    ("CENOURA KG", 4.49, "KG", 2),
    ("ALFACE CRESPA UN", 3.49, "UN", 2),
    ("BROCOLIS UN", 6.90, "UN", 1),
    ("PAO FRANCES KG", 16.90, "KG", 5),
    ("PAO DE FORMA INTEGRAL 450G", 9.90, "UN", 2),
    ("BOLO DE CENOURA UN", 14.90, "UN", 1),
    ("MOLHO DE TOMATE 340G", 3.49, "UN", 3),
    ("MAIONESE 500G", 12.90, "UN", 2),
    ("CATCHUP 400G", 9.90, "UN", 1),
    ("BISCOITO RECHEADO 130G", 3.99, "UN", 3),
    ("CHOCOLATE AO LEITE 90G", 7.49, "UN", 3),
    ("SALGADINHO DE MILHO 100G", 8.90, "UN", 2),
    ("SORVETE DE CREME 2L", 21.90, "UN", 1),
    ("LASANHA CONGELADA 600G", 22.90, "UN", 1),
    ("NUGGETS DE FRANGO 300G", 14.90, "UN", 2),
    ("REFRIGERANTE COLA 2L", 9.99, "UN", 4),
    ("REFRIGERANTE GUARANA 2L", 8.49, "UN", 2),
    ("SUCO DE UVA INTEGRAL 1L", 15.90, "UN", 1),
    ("AGUA MINERAL SEM GAS 1,5L", 3.29, "UN", 3),
    ("CERVEJA PILSEN LATA 350ML", 3.79, "UN", 4),
    ("VINHO TINTO SECO 750ML", 34.90, "UN", 1),
    ("SABONETE HIDRATANTE 90G", 3.49, "UN", 3),
    ("SHAMPOO 350ML", 18.90, "UN", 1),
    ("CONDICIONADOR 350ML", 19.90, "UN", 1),
    ("CREME DENTAL 90G", 6.49, "UN", 2),
    ("PAPEL HIGIENICO FOLHA DUPLA 12X30M", 26.90, "UN", 2),
    ("DESODORANTE AEROSOL 150ML", 16.90, "UN", 1),
    ("ABSORVENTE COM ABAS 8UN", 8.90, "UN", 1),
    ("DETERGENTE LIQUIDO NEUTRO 500ML", 2.79, "UN", 3),
    ("LAVA ROUPAS LIQUIDO 3L", 29.90, "UN", 1),
    ("AMACIANTE CONCENTRADO 1L", 14.90, "UN", 1),
    ("DESINFETANTE LAVANDA 2L", 9.90, "UN", 1),
    ("SACO PARA LIXO 50L COM 10", 8.49, "UN", 1),
    ("ESPONJA MULTIUSO UN", 2.49, "UN", 1),
    ("DIPIRONA 500MG 10CP", 8.90, "UN", 1),
    ("PARACETAMOL 750MG 20CP", 12.90, "UN", 1),
    ("IBUPROFENO 600MG 20CP", 18.90, "UN", 1),
    ("RACAO PARA GATOS ADULTOS 1KG", 24.90, "UN", 1),
    ("AREIA SANITARIA PARA GATOS 4KG", 19.90, "UN", 1),
    ("GASOLINA COMUM", 100.00, "UN", 1),
    ("COMBO LANCHE COM BATATA", 32.90, "UN", 1),
]

FORMAS = ["Cartão de Débito", "Cartão de Crédito", "Dinheiro", "PIX"]


def escolhe(rnd, opcoes):
    total = sum(p for *_, p in opcoes)
    r = rnd.uniform(0, total)
    acc = 0
    for item in opcoes:
        acc += item[-1]
        if r <= acc:
            return item
    return opcoes[-1]


def gerar(pasta_saida: str):
    rnd = random.Random(SEMENTE)
    notas: list[NotaCompleta] = []
    dono: dict[str, int] = {}
    por_planilha: dict[str, list] = {}
    seq = 0

    for d in range(DIAS):
        data = INICIO + datetime.timedelta(days=d)
        # nem todo dia tem compra; fim de semana rende um pouco mais
        chance = 0.68 if data.weekday() >= 5 else 0.55
        if rnd.random() > chance:
            continue
        for _ in range(rnd.choices([1, 2, 3], weights=[70, 25, 5])[0]):
            seq += 1
            razao, cnpj, endereco, _ = escolhe(rnd, LOJAS)
            pi = 0 if rnd.random() < 0.72 else 1
            pessoa = PESSOAS[pi]

            n = NotaCompleta(chave=f"43{data:%y%m}{seq:038d}"[:44])
            n.emitente = razao
            n.cnpj = cnpj
            n.endereco = endereco
            n.inscricao = "0000000000"
            n.numero = 1000 + seq
            n.serie = 1
            n.data = data.strftime("%d/%m/%Y")
            n.hora = f"{rnd.randint(8, 21):02d}:{rnd.randint(0, 59):02d}:00"
            n.protocolo = f"1432600{seq:06d}"
            n.cpf = pessoa.cpf
            n.consumidor = pessoa.nome.upper()

            for _ in range(rnd.choices([1, 2, 3, 5, 8, 13], weights=[18, 20, 22, 20, 14, 6])[0]):
                desc, base, un, _peso = escolhe(rnd, CESTA)
                preco = round(base * rnd.uniform(0.92, 1.10), 2)
                qtd = round(rnd.uniform(0.2, 1.6), 3) if un == "KG" else rnd.choices(
                    [1, 2, 3, 6], weights=[70, 20, 7, 3])[0]
                n.itens.append(Item(
                    codigo=f"{rnd.randint(10 ** 5, 10 ** 6 - 1)}",
                    descricao=desc, quantidade=qtd, unidade=un,
                    valor_unitario=preco, valor_total=round(preco * qtd, 2)))

            n.valor_total = round(sum(i.valor_total for i in n.itens), 2)
            n.descontos = round(n.valor_total * rnd.choice([0, 0, 0, 0.03, 0.07]), 2)
            liquido = round(n.valor_total - n.descontos, 2)
            n.pagamentos.append(Pagamento(forma=rnd.choice(FORMAS), valor=liquido))
            n.valor_planilha = liquido

            notas.append(n)
            dono[n.chave] = pi
            por_planilha.setdefault(pessoa.planilhas[0], []).append(n)

    for pi, p in enumerate(PESSOAS):
        p.notas = sum(1 for n in notas if dono[n.chave] == pi)

    dados = montar(notas, dono, PESSOAS, True, [],
                   gerado_em=datetime.date.today().isoformat())
    dados["meta"]["exemplo"] = True
    limpo = {k: v for k, v in dados.items() if not k.startswith("_")}

    os.makedirs(pasta_saida, exist_ok=True)
    destino = os.path.join(pasta_saida, "dados.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(limpo, f, ensure_ascii=False, separators=(",", ":"))

    r = limpo["resumo"]
    print(f"conjunto de exemplo: {r['notas']} notas · {r['itens']} itens · "
          f"R$ {r['total']:.2f}")
    print(f"{destino}  ({os.path.getsize(destino) / 1024:.0f} KB)")
    return destino


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else os.path.join("..", "painel", "src", "data")
    gerar(alvo)
