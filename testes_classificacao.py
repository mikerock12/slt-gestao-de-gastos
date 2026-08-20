# -*- coding: utf-8 -*-
"""Testa os classificadores contra descrições típicas de nota fiscal."""
import sys

sys.path.insert(0, ".")
from app.categorias import categoria_produto
from app.mapa import classificar

CASOS = [
    # (descrição, domínio esperado, grupo esperado)
    # --- os que o usuário relatou ---
    ("ACHOC PO NESCAU 2.0 SACHE 195G", "alimentacao", "Água, café, chá e sucos"),
    ("ACHOCOLATADO EM PO TODDY 200G", "alimentacao", "Água, café, chá e sucos"),
    ("MOLHO DE TOMATE CAJAMAR SACHE 300G", "alimentacao", "Molhos, temperos e condimentos"),
    ("MOLHO TOMATE CAJAMAR TRAD SACHE 340G", "alimentacao", "Molhos, temperos e condimentos"),
    ("CREME DE LEITE CAJAMAR SACHE 200G", "alimentacao", "Laticínios"),
    ("MAIONESE SACHE 200G", "alimentacao", "Molhos, temperos e condimentos"),
    # --- cortes de carne ---
    ("CONTRA FILE BOVINO KG", "alimentacao", "Carnes, aves e peixes"),
    ("FILE MIGNON BOVINO KG", "alimentacao", "Carnes, aves e peixes"),
    ("BISTECA SUINA KG", "alimentacao", "Carnes, aves e peixes"),
    ("ASA DE FRANGO CONGELADA 1KG", "alimentacao", None),
    ("COXINHA DA ASA FRANGO KG", "alimentacao", None),
    ("POSTA DE SALMAO FRESCO KG", "alimentacao", "Carnes, aves e peixes"),
    ("FILE DE TILAPIA CONGELADO 500G", "alimentacao", None),
    ("LAGARTO BOVINO PECA KG", "alimentacao", "Carnes, aves e peixes"),
    ("PA BOVINA SEM OSSO KG", "alimentacao", "Carnes, aves e peixes"),
    ("CHARQUE DIANTEIRO 500G", "alimentacao", "Carnes, aves e peixes"),
    ("CARNE SECA PONTA DE AGULHA KG", "alimentacao", "Carnes, aves e peixes"),
    ("MIOLO DE ALCATRA KG", "alimentacao", "Carnes, aves e peixes"),
    ("RIPA DE COSTELA BOVINA KG", "alimentacao", "Carnes, aves e peixes"),
    ("TENDER BOVINO DEFUMADO", "alimentacao", None),
    ("PICANHA BOVINA MATURADA KG", "alimentacao", "Carnes, aves e peixes"),
    ("SOBRECOXA DE FRANGO BDJ KG", "alimentacao", None),
    ("PEITO DE FRANGO SEM OSSO KG", "alimentacao", None),
    ("PERNIL SUINO SEM OSSO KG", "alimentacao", "Carnes, aves e peixes"),
    ("MUSCULO BOVINO MOIDO KG", "alimentacao", "Carnes, aves e peixes"),
    ("ACEM BOVINO EM CUBOS KG", "alimentacao", "Carnes, aves e peixes"),
    ("CUPIM BOVINO PECA KG", "alimentacao", "Carnes, aves e peixes"),
    ("FRALDINHA BOVINA KG", "alimentacao", "Carnes, aves e peixes"),
    ("MAMINHA BOVINA KG", "alimentacao", "Carnes, aves e peixes"),
    ("PATINHO BOVINO MOIDO KG", "alimentacao", "Carnes, aves e peixes"),
    ("COSTELA SUINA KG", "alimentacao", "Carnes, aves e peixes"),
    ("PAILLARD DE FRANGO KG", "alimentacao", None),
    ("TILAPIA INTEIRA EVISCERADA KG", "alimentacao", "Carnes, aves e peixes"),
    ("BACALHAU DESSALGADO 400G", "alimentacao", "Carnes, aves e peixes"),
    ("PESCADA BRANCA POSTA KG", "alimentacao", "Carnes, aves e peixes"),
    ("CAMARAO CINZA LIMPO 400G", "alimentacao", "Carnes, aves e peixes"),
    ("COSTELINHA SUINA DEFUMADA KG", "alimentacao", "Carnes, aves e peixes"),
    ("OVOS CAIPIRA C/10", "alimentacao", "Ovos"),
    # --- pet de verdade (não pode quebrar) ---
    ("RACAO WHISKAS SACHE CARNE 85G", "pet", None),
    ("SACHE GATO FRISKIES FRANGO 85G", "pet", None),
    ("PETISCO PARA CAES DENTALIFE", "pet", None),
    ("RACAO GOLDEN GATOS ADULTOS 1KG", "pet", None),
    ("AREIA SANITARIA PARA GATOS 4KG", "pet", None),
    # --- outros que costumam confundir ---
    ("CAFE SOLUVEL SACHE 50G", "alimentacao", "Água, café, chá e sucos"),
    ("SOPA INSTANTANEA SACHE GALINHA", "alimentacao", None),
    ("GOLDEN ALE CERVEJA 473ML", "alimentacao", "Bebidas alcoólicas"),
    ("BISCOITO GOLDEN CREAM 130G", "alimentacao", "Ultraprocessados e doces"),
]


def main():
    erros = 0
    for desc, dom_esp, grupo_esp in CASOS:
        dom, grupo, nova = classificar(desc)
        cat = categoria_produto(desc, None)
        ruim = dom != dom_esp or (grupo_esp and grupo != grupo_esp)
        if ruim:
            erros += 1
            esperado = f"{dom_esp}" + (f" / {grupo_esp}" if grupo_esp else "")
            print(f"  ERRO  {desc}")
            print(f"        obteve  : {dom} / {grupo}   (categoria: {cat})")
            print(f"        esperado: {esperado}")
    print(f"\n{erros} erro(s) em {len(CASOS)} casos")
    return erros


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
