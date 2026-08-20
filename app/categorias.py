# -*- coding: utf-8 -*-
import json, os, re, unicodedata


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', s).upper().strip()


# ---------- categoria de produto ----------
REGRAS = [
 # SACHE, GOLDEN e PETISCO saíram daqui de propósito: sachê é formato de
 # embalagem e Golden é nome de marca em vários ramos. Com eles, achocolatado
 # em sachê, molho de tomate em sachê, café em sachê e cerveja Golden Ale
 # viravam "Pet". Produto para animal quase sempre traz RACAO ou a palavra do
 # bicho na descrição, então nada de verdade se perde.
 ('Pet', r'\bRACAO\b|GRANULADO HIG|AREIA HIG|\bMIAU\b|MONELLO|\bBIRBO\b|WHISKAS|PEDIGREE|\bCOBASI\b|\bGATOS?\b|\bCAES\b|\bCAO\b|\bCACHORRO\b|ANTIPULG|\bFELINO\b|AREIA SANIT|GRANULADO SANIT|MIKCAT|PETLETS|PIPICAT|\bZECAT\b|\bPIERINO\b|DENTALIFE|DOG CHOW|CAT CHOW|\bPROPLAN\b|\bFRISKIES\b|\bDOCATS\b|SANDBED|FIPROLEX|\bCHURU\b|DREAMIES|LEROY GATOS|QUATRO PATAS|SULTAO GATOS'),
 ('Bebidas alcoolicas', r'\bCERV|CERVEJA|\bVINHO\b|CHOPP|WHISK|VODKA|\bGIN\b|CACHACA|ESPUMANTE|LICOR|APEROL|CAMPARI|\bRUM\b|TEQUILA|SIDRA|SAKE|\bIPA\b|HEINEKEN|BUDW|BRAHMA|SKOL|POLAR|SPATEN|BOHEMIA|EISENBAHN|CARACU|BADEN|CORONA|STELLA|AMSTEL|\bPILSEN\b|VELHO BARREIRO|JOTA PE|SANGUE DE BOI|\bWINE\b|\bLAGER\b|\bWEISS\b|\bPURO MALTE\b|^VH |^VIN |\bSAQUE\b|\bMALBEC\b|\bBONARDA\b|C\.SAUV|\bTANNAT\b|\bMERLOT\b|\bCHARDONN|\bDRINK\b|\bCAIPIR|COQUETEL|\bMARULA\b'),
 ('Refrigerantes e energeticos', r'REFRIG|COCA COLA|\bPEPSI\b|GUARANA|FANTA|SPRITE|SCHWEPPES|ENERGETIC|RED BULL|\bTNT\b|MONSTER|BALY|\bTONICA\b|\bBAREE\b|\bCOCA\b|\bSUC \b|\bH2OH\b|AGUA SABORIZ|\bTUBAINA\b'),
 ('Aguas, sucos, cha e cafe', r'\bAGUA\b|\bAG \b|AG MIN|AGUA MIN|\bSUCO\b|NECTAR|\bCHA\b|\bCAFE\b|CAPUCCIN|ISOTONIC|GATORADE|POWERADE|\bMATE\b|CHIMARRAO|\bERVA\b|\bDEL VALLE\b|\bTANG\b|\bREFRESCO\b'),
 # Saídas de emergência: o TIPO do produto tem que ganhar da palavra de sabor.
 # Sem elas, "MOLHO DE TOMATE" vira tomate, "DESINF LIMPA LIMAO" vira limão,
 # "SALGADINHO QJO NACHO" vira queijo — e cada um leva junto a alíquota errada.
 ('Mercearia e basicos', r'^MOLHO|MOLHO DE TOM|MOLHO TOM|^EXTRATO|^PASSATA|^POLPA|^CATCHUP|^KETCHUP|^MAIONESE|^MOSTARDA|^CONSERVA|^SELETA|^AZEITONA|^PALMITO|^PICLES'),
 ('Doces, snacks e biscoitos', r'BATATA CHIPS|BATATA PALHA|BATATA LAYS|BATATA STIKS|RUFFLES|PRINGLES|^SALGADIN|^SALG |CHEETOS|DORITOS|^TORCIDA|FANDANGOS|CLUB SOCIAL|\bSNACK\b'),
 ('Congelados e industrializados', r'PAO DE ALHO|PAO D ALHO|PAO ALHO|PAO DE QUEIJO|BATATA CONGELADA|BATATA PRE FRITA|BATATA HASHTAG|ANEIS DE CEBOLA'),
 ('Limpeza e utilidades domesticas', r'^DESINF|^DETER|^LIMPADOR|^DESENGORD|^LAVA ROUP|^L ROUP|^AMAC|^AGUA SANIT|^ALVEJANTE|^TIRA MANCHAS|^SABAO EM PO|^MULTIUSO|^LUSTRA'),
 ('Congelados e industrializados', r'CONGELAD|\bCONG\b|EMPANAD|\bEMP\b|\bSTEAK\b|NUGGET|ANEIS DE CEBOLA|LASANHA|\bPIZZA\b|\bESFIHA\b|NHOQUE|BATATA CONG|DEUTSCHIP|\bSEARA\b|\bSADIA\b|EXCELSIOR|PERDIGAO|\bAURORA\b|SORVETE|PICOLE|\bACAI\b|\bNISSIN\b|CUP NOODLES|\bFAGOTTO\b|\bTORTEI\b|\bCAPELET|\bRAVIOLI\b'),
 ('Carnes, aves e peixes', r'\bCARNE\b|\bCARNES\b|\bBIFE\b|\bBIFES\b|COXAO|PATINHO|ALCATRA|PICANHA|MAMINHA|FRALDINHA|COSTELA|\bACEM\b|MUSCULO|\bFILE\b|\bFRANGO\b|\bPEITO\b|\bCOXA\b|\bCOXAS\b|SOBRECOXA|\bASA\b|\bASAS\b|LINGUICA|SALSICH|\bBACON\b|\bPERNIL\b|\bLOMBO\b|\bSUIN[AO]\b|\bBOVIN[AO]\b|\bPORCO\b|\bBOI\b|HAMBURG|\bPEIXE\b|TILAPIA|SALMAO|MERLUZA|\bATUM\b|SARDINH|CAMARAO|\bCUPIM\b|MOIDA|\bMOIDO\b|CHURRASC|\bCARRE\b|COSTELINHA|TOUCINHO|\bPALETA\b|\bMATAMBRE\b|\bFIGADO\b|\bMOELA\b|\bVAZIO\b|ENTRECOT|SPALET|\bLING\b|CALABESA|CALABRESA|\bCAM \b|CAMARO|TENTACULOS|\bPOLVO\b|\bLULA\b|\bMARISC|\bMAMINH|\bGRILL\b|\bBDJ\b|\bDEFUMAD|SASSAMI|\bFILEZINHO\b|COXINHA|CORACAO BOVINO|\bLAGARTO\b|\bBISTECA\b|\bCHULETA\b|CHARQUE|\bJERKED\b|\bPA BOVINA\b|\bMIOLO\b|\bRIPA\b|\bPAILLARD\b|\bTENDER\b|\bMIUDOS\b|DOBRADINHA|\bRABADA\b|\bMOCOTO\b|OSSOBUCO|ALMONDEGA|\bDIANTEIRO\b|\bTRASEIRO\b|\bBACALHAU\b|PESCAD|\bCORVINA\b|\bANCHOVA\b|\bABADEJO\b|\bPANGA\b|\bPOLACA\b|\bTAINHA\b|\bTRAIRA\b|\bPACU\b|MEXILHAO|\bPOSTA\b|\bPOSTAS\b'),
 ('Frios e embutidos', r'MORTADELA|PRESUNTO|SALAME|APRESUNT|PEPPERONI|\bPATE\b|BLANQUET|PEITO DE PERU'),
 ('Laticinios e ovos', r'\bLEITE\b|\bQUEIJO\b|MUSSAREL|REQUEIJ|IOGURT|MANTEIG|MARGARIN|CREME DE LEITE|LEITE COND|\bNATA\b|\bOVO\b|\bOVOS\b|RICOTA|COALHO|\bDANONE\b|\bYAKULT\b|\bNINHO\b|\bCHANTIL|\bIOG\b|\bQJO\b|\bGOUDA\b|\bBATAVO\b|\bGREGO\b|CREAM CHEESE|POLENGHI'),
 ('Hortifruti', r'^HF |\bBANANA\b|\bMACA\b|\bLARANJA\b|\bLIMAO\b|\bLIMA\b|\bTOMATE\b|\bCEBOLA\b|\bALHO\b|ALFACE|\bCENOURA\b|\bMAMAO\b|MELANCIA|ABACAXI|\bUVA\b|\bMANGA\b|\bPERA\b|\bMELAO\b|MORANGO|ABOBOR|\bPEPINO\b|REPOLHO|BROCOLI|\bCOUVE\b|BETERRAB|\bCHUCHU\b|\bVAGEM\b|TEMPERO VERDE|\bSALSA\b|\bRUCULA\b|\bAGRIAO\b|BERGAMOTA|\bKIWI\b|AMEIXA|PESSEGO|CEBOLINH|PIMENTAO|MANDIOCA|\bAIPIM\b|\bINHAME\b|ABACATE|\bBATATA\b'),
 ('Padaria e confeitaria', r'\bPAO\b|\bPAES\b|CACETINH|\bBOLO\b|\bTORTA\b|CROISSAN|\bCUCA\b|\bROSCA\b|BAGUET|BRIOCHE|PANETONE|CONFEIT|\bSONHO\b(?!.*VALSA)'),
 ('Mercearia e basicos', r'\bARROZ\b|\bFEIJAO\b|MACARRAO|\bMASSA\b|FARINHA|ACUCAR|\bSAL\b|\bOLEO\b|AZEITE|VINAGRE|\bMOLHO\b|EXTRATO |TEMPERALLE|\bTEMPERO|\bPIMENTA\b|OREGANO|CANELA|\bCRAVO\b|COMINHO|COLORAU|\bKNORR\b|\bAVEIA\b|POLENTA|\bFUBA\b|\bAMIDO\b|FERMENT|\bTRIGO\b|LENTILHA|GRAO DE BICO|\bSOJA\b|\bMILHO\b|ERVILHA|SELETA|PALMITO|AZEITONA|KETCHUP|MOSTARDA|MAIONESE|\bSHOYU\b|BARBECUE|CANJICA|\bSAGU\b|\bMEL\b|GELATINA|\bPUDIM\b|LEITE DE COCO|COCO RALADO|\bCALDO\b|\bSOPA\b|CATCHUP|\bTEMP \b|\bADOBO\b|\bAZ \b|CAPPUCCIN|\bSALADA\b|\bPIM \b|MERCATTO|BEB LAC|MIX PIMENTAS|BRSPICES|\bACHOC\b|NESCAU|TAPIOCA|\bDADINHO\b|\bHARUS\b'),
 ('Doces, snacks e biscoitos', r'CHOCOLAT|BOMBOM|TRUFA|TRUFAO|\bBALA\b|\bBALAS\b|\bDOCE\b|PIRULITO|CHICLE|BISCOIT|BOLACHA|\bWAFER\b|\bCOOKIE\b|SALGADIN|\bCHIPS\b|RUFFLES|DORITOS|PRINGLES|AMENDOIM|CASTANHA|\bNOZES\b|PIPOCA|COCADA|TORRAO|PACOCA|BRIGADEIRO|\bHALLS\b|MENTOS|TIC TAC|KITKAT|OURO BRANCO|SONHO VALSA|\bBIS\b|\bLACTA\b|\bNESTLE\b|\bGAROTO\b|CEREAL|BARRA DE|SUCRILHOS|\bPACOQUINHA\b|\bCHOC\b|WAFFER|\bWAFFLE\b|CHEETOS|BEIJINHO|5STAR|SNICKERS|STIKADINHO|\bTRENTO\b|HERSHEY|\bBISC\b|\bOREO\b|\bDORITO|\bFANDANGOS\b|\bTORCIDA\b|\bMMS\b|\bTALENTO\b|\bDIAMANTE NEGRO\b|\bLOLLO\b|\bBATON\b|\bPRESTIGIO\b|\bALPINO\b|\bCHOKITO\b|\bORQUIDEA\b|BARRA PROT|OVOMALTIN|\bKIT KAT\b|\bBISNAGUINHA\b|NUTRELLA'),
 ('Higiene e beleza', r'\bSAB\b|SABONET|SHAMPOO|\bSH\b|CONDICION|\bCOND\b|CREME DENTAL|\bCR\b|\bDENTAL\b|ESCOVA DENT|\bENXAG\b|CEPACOL|DESODOR|\bDES\b|\bABSORV\b|\bFRALDA\b|PAPEL HIG|\bLENCO\b|BARBEAR|\bBARBA\b|GILLETTE|\bLAMINA\b|HIDRATANT|PERFUME|COLONIA|\bBATOM\b|ESMALTE|MAQUIAG|\bDOVE\b|\bNIVEA\b|REXONA|\bCLEAR\b|\bSEDA\b|PANTENE|ELSEVE|BOZZANO|CLOSEUP|COLGATE|ORAL-?B|ALGODAO|COTONET|PROTETOR SOLAR|\bTALCO\b|TINTURA|\bCOLOR\b|\bCREME\b|\bGEL\b|\bBALS\b|\bPERF\b|PERFUM|\bEDT\b|\bEDP\b|\bMASC\b|CILIOS|HIDRAT|BODY SPLASH|\bABS\b|BABYSEC|\bFR \b|\bSABONETE\b|\bGARNIER\b|\bEUDORA\b|\bAVON\b|\bNATURA\b|\bVULT\b|\bRUBY ROSE\b|\bDESOD\b|\bAXE\b|\bMONANGE\b|\bGIOVANNA BABY\b|\bESCOVA\b|\bFIO DENTAL\b|\bENXAGUANTE\b|ABSORVENTE|\bMILI\b|UNHAS POST|\bRICCA\b|\bTINT \b|KIT ESC DENT|SLIM SOFT|\bPERFM\b|\bAMAKHA\b|\bESM \b|COLORAMA'),
 ('Limpeza e utilidades domesticas', r'\bDETERG\b|\bSABAO\b|\bOMO\b|AMACIANT|\bDOWNY\b|COMFORT|AGUA SANIT|\bQBOA\b|CANDIDA|DESINFET|\bPINHO\b|\bVEJA\b|LIMPADOR|MULTIUSO|ALVEJANT|ESPONJA|BOMBRIL|SACO LIXO|\bPANO\b|VASSOURA|\bRODO\b|\bBALDE\b|PAPEL TOALHA|GUARDANAP|ALUMINIO|FILME PVC|FOSFORO|\bVELA\b|\bPILHA\b|LAMPADA|INSETIC|\bRAID\b|\bSBP\b|INCENSO|DESODORIZ|LUSTRA|\bCERA\b|\bAMONIA\b|SAPOLIO|\bSACO\b|LAVA ROUP|\bL ROUP\b|\bDETER\b|BRILHANTE|AQUAFAST|\bCOALA\b|\bVANISH\b|TIRA MANCHAS|\bFILME\b|FOLHA ALUM|PRENDEDOR|\bCARVAO\b|\bYPE\b|\bBRILHANTE\b|\bT.CARINHO\b|\bALCOOL\b|\bWYDA\b|\bJANE\b|\bCONDOR\b|\bLIMPA\b|DESENGORDUR|PA LIXO|BETTANIN|\bJEITOS\b|\bGARRAFA\b|SPORT FITNESS|\bLAMP\b|\bLED\b|\bPHILIPS\b|\bMORDEDOR\b|\bBUBA\b'),
 ('Farmacia e medicamentos', r'\bCPR?\b|\bCOMP\b|DIPIRONA|PARACETAM|IBUPROF|AMOXICIL|OMEPRAZ|DORFLEX|BUSCOPAN|NEOSALDINA|ENGOV|KALMENE|VITAMIN|POMADA|XAROPE|\bSORO\b|\bGAZE\b|CURATIV|BAND ?AID|SERINGA|TERMOMETRO|ALCOOL 70|ANADOR|TYLENOL|\bADVIL\b|LORATAD|CETIRIZ|\bMG\b|RISPERIDONA|\bSELENE\b|HIXIZINE|SORINAN|BIOFENAC|MELATONINA|NISTATINA|\bCPR\b|\bCP\b|\bPOM\b|\bNEO QUI\b|\bMG/ML\b|\bMG/G\b|\bDROPS\b|\bGOTAS\b|BACITRACINA|NEOMICINA|\bDICLOF\b|DIETILAMONIO'),
 ('Combustivel', r'GASOLINA|\bETANOL\b|ALCOOL COMUM|\bDIESEL\b|\bGNV\b|COMBUSTIV'),
 ('Refeicoes fora de casa', r'\bCOMBO\b|\bLANCHE\b|\bBURGER\b|SANDUIC|\bPORCAO\b|PRATO FEITO|\bBUFFET\b|MCLANCHE|BIG MAC|WHOPPER|\bPASTEL\b|ESPETINHO|REFEICAO|\bALMOCO\b|\bJANTA\b|BATATA FRITA|\bMILK ?SHAKE\b'),
 ('Vestuario e calcados', r'CAMISET|CAMISA|\bCALCA\b|BERMUDA|VESTIDO|\bBLUSA\b|MOLETOM|JAQUETA|\bTENIS\b|SAPATO|CHINELO|SANDALIA|\bMEIA\b|\bCUECA\b|CALCINHA|\bSUTIA\b|\bBONE\b|CASACO|\bSHORT\b|PIJAMA|BIQUINI|REGATA|\bPOLO\b|HAVAIANAS|\bSAND\.|\bCHINELO\b|\bTOP MAX\b'),
 ('Casa, bazar e eletro', r'PANELA|TALHER|\bPRATO\b|\bCOPO\b|CANECA|TOALHA|LENCOL|TRAVESSEIR|COBERTOR|ALMOFADA|CORTINA|TAPETE|CABIDE|\bPOTE\b|CAIXA ORG|FERRAMENT|PARAFUSO|\bFITA\b|\bCOLA\b|CADERNO|CANETA|PAPEL A4|CARREGADOR|CABO USB|\bFONE\b|BRINCO|\bCOLAR\b|PULSEIRA|RELOGIO|MOCHILA|\bTESOURA\b|\bCHAVE\b|\bFORMA\b|\bFORM \b|LIMPA TELA|\bAFRY\b'),
]
REGRAS = [(n, re.compile(p)) for n, p in REGRAS]

# Carga tributaria total estimada por categoria (ICMS RS + PIS/COFINS + IPI).
# Medias publicadas pelo IBPT para efeito da Lei 12.741/2012 ("De Olho no Imposto").
CARGA = {
 'Bebidas alcoolicas': 0.560,
 'Refrigerantes e energeticos': 0.370,
 'Aguas, sucos, cha e cafe': 0.230,
 'Carnes, aves e peixes': 0.130,
 'Frios e embutidos': 0.280,
 'Laticinios e ovos': 0.160,
 'Hortifruti': 0.080,
 'Padaria e confeitaria': 0.170,
 'Mercearia e basicos': 0.190,
 'Congelados e industrializados': 0.300,
 'Doces, snacks e biscoitos': 0.330,
 'Higiene e beleza': 0.380,
 'Limpeza e utilidades domesticas': 0.350,
 'Pet': 0.360,
 'Farmacia e medicamentos': 0.300,
 'Combustivel': 0.450,
 'Refeicoes fora de casa': 0.250,
 'Vestuario e calcados': 0.340,
 'Casa, bazar e eletro': 0.400,
 'Servicos': 0.200,
 'Outros': 0.300,
}


def categoria_produto(desc, cat_loja=None):
    d = norm(desc)
    if cat_loja == 'Combustivel':
        return 'Combustivel'
    if cat_loja == 'Farmacia':
        for nome, rx in REGRAS:
            if nome in ('Higiene e beleza', 'Farmacia e medicamentos') and rx.search(d):
                return nome
        return 'Farmacia e medicamentos'
    if cat_loja in ('Restaurante / fast-food', 'Padaria / lancheria'):
        return 'Refeicoes fora de casa'
    if cat_loja == 'Pet shop':
        return 'Pet'
    if cat_loja == 'Vestuario':
        return 'Vestuario e calcados'
    for nome, rx in REGRAS:
        if rx.search(d):
            return nome
    return 'Outros'


# ---------- categoria de estabelecimento ----------
# ---------- ramo do estabelecimento ----------
# Só palavras genéricas: a razão social quase sempre traz o ramo no nome
# ("SUPERMERCADO X LTDA", "DROGARIA Y"). Nada de marca específica — o programa
# tem que funcionar para o comércio de qualquer cidade.
LOJAS = [
 (r'FARMACIA|DROGARIA|DROGA |DROGASIL|PANVEL|MEDICAMENTOS?\b', 'Farmacia'),
 (r'\bPET\b|PETSHOP|PET SHOP|AGROPECUARIA|VETERINARI', 'Pet shop'),
 (r'COMBUSTIVE|\bPOSTO\b|AUTO POSTO', 'Combustivel'),
 (r'CONFEC|VESTUARIO|MODAS?\b|BOUTIQUE|CALCADOS?\b', 'Vestuario'),
 (r'MAGAZINE|DEPARTAMENTO|VAREJO S\.?A', 'Loja de departamento'),
 (r'PERFUMARIA|COSMETICOS', 'Perfumaria'),
 (r'RESTAURANTE|LANCHONETE|PIZZARIA|PASTEL|CHURRASCARIA|BAR E |'
 r'ALIMENTACAO E BEBIDAS|FAST FOOD|SNACK', 'Restaurante / fast-food'),
 (r'SUPERMERCAD|HIPERMERCAD|ATACAD|ATACAREJO|SUPER |COMERCIO DE ALIMENTOS|'
 r'GENEROS ALIMENT', 'Supermercado'),
 (r'MERCADO|MERCEARIA|MINIMERCADO|CONVENIENCIA|EMPORIO|PADARIA|'
 r'PANIFICADORA', 'Mercado de bairro / conveniencia'),
 (r'OFICINA|\bAUTO\b|MECANICA|CAR SERVICE|PNEUS?\b', 'Servicos automotivos'),
 (r'SOFTWARE|TELECOM|INTERNET|PLATAFORMA|TECNOLOGIA|DIGITA', 'Servicos digitais'),
 (r'GRAFIC|IMPRESS|COPIADORA', 'Servicos graficos'),
 (r'ELETRICA|CONSTRU|MATERIAIS|FERRAGEM|HIDRAULIC', 'Material de construcao'),
]
LOJAS = [(re.compile(p), c) for p, c in LOJAS]


def categoria_loja(nome):
    _, ramo = _local(nome)
    if ramo:
        return ramo
    n = norm(nome)
    for rx, c in LOJAS:
        if rx.search(n):
            return c
    return 'Outros'


# ---------- nome curto e legível da loja ----------
# A razão social vem cheia de ruído jurídico ("COM DE GENEROS ALIMENT LTDA
# FILIAL 22"). Aqui ela é limpa para caber num gráfico, sem lista de marcas.
_RUIDO = re.compile(
    r'\b(LTDA|ME|EPP|EIRELI|S\.?\s?A\.?|CIA|COMPANHIA|'
    r'COM|COMERCIO|COMERCIAL|COML|IND|INDS|INDUSTRIA|INDUSTRIAL|'
    r'DISTRIB|DISTRIBUIDORA|ATAC|ATACADO|ATACADISTA|PRODS|PRODUTOS|'
    r'IMPORTADORA|EXPORTADORA|REPRESENTACOES|PARTICIPACOES|'
    r'EMPREENDIMENTOS|FILIAL|MATRIZ|UNIDADE)\b\.?', re.I)
_MIUDAS = {'de', 'da', 'do', 'das', 'dos', 'e'}

# Apelidos e ramos definidos pelo usuário, carregados de um lojas.json opcional
# na pasta das planilhas. Serve para dar nome curto às lojas do seu bairro sem
# que ninguém precise mexer no código — nem publicar onde faz compras.
_LOCAIS: list = []


def carregar_lojas_locais(caminho):
    """lojas.json = [{"quando": "regex", "apelido": "...", "ramo": "..."}, ...]"""
    global _LOCAIS
    _LOCAIS = []
    if not caminho or not os.path.exists(caminho):
        return 0
    try:
        with open(caminho, encoding='utf-8') as f:
            bruto = json.load(f)
    except (OSError, ValueError):
        return 0
    for regra in bruto if isinstance(bruto, list) else []:
        try:
            rx = re.compile(regra['quando'], re.I)
        except (KeyError, re.error):
            continue
        _LOCAIS.append((rx, regra.get('apelido'), regra.get('ramo')))
    return len(_LOCAIS)


def _local(nome):
    n = norm(nome)
    for rx, ap, ramo in _LOCAIS:
        if rx.search(n):
            return ap, ramo
    return None, None


def apelido(nome, limite=26):
    """'COM DE GENEROS ALIMENT MODELO LTDA' -> 'Generos Aliment Modelo'."""
    ap, _ = _local(nome)
    if ap:
        return ap

    # marca onde o ruído saiu, para poder descartar o conectivo que ficou
    # órfão do lado ("PADARIA COMERCIO DE PAES" -> "Padaria Paes")
    t = _RUIDO.sub(' · ', norm(nome))
    t = re.sub(r'[^A-Z0-9&·\s\-]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()

    palavras = t.split()
    limpas = []
    for k, w in enumerate(palavras):
        if w == '·':
            continue
        if w.lower() in _MIUDAS:
            antes_sumiu = k == 0 or palavras[k - 1] == '·'
            depois_sumiu = k + 1 >= len(palavras) or palavras[k + 1] == '·'
            if antes_sumiu or depois_sumiu:
                continue
        limpas.append(w)
    palavras = limpas or [norm(nome)]

    curto, tamanho = [], 0
    for p in palavras:
        if curto and tamanho + 1 + len(p) > limite:
            break
        curto.append(p)
        tamanho += (1 if len(curto) > 1 else 0) + len(p)
    # não terminar em "de", "e", "da"…
    while len(curto) > 1 and curto[-1].lower() in _MIUDAS:
        curto.pop()

    return ' '.join(w.lower() if w.lower() in _MIUDAS else w.capitalize()
                    for w in (curto or palavras[:1] or [norm(nome)]))
