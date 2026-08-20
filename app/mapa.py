# -*- coding: utf-8 -*-
"""
Mapa de consumo: classifica cada item comprado em domínio, grupo e — para
alimentos — grau de processamento (NOVA, do Guia Alimentar para a População
Brasileira).

Independente de `categorias.py`: aqui a regra olha o TIPO do produto, não a
loja. Isso importa porque muita descrição traz palavra de sabor que engana
("DESINF GOTA LIMPA LIMAO", "SALGADINHO DORITOS QJO NACHO", "SAB NIVEA LEITE").
Por isso as regras de tipo vêm ANTES das de ingrediente, e a primeira que casa
vence.
"""
import re
import unicodedata


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).upper().strip()


# ---------------------------------------------------------------- NOVA
NOVA = {
    1: "In natura ou minimamente processado",
    2: "Ingrediente culinário",
    3: "Processado",
    4: "Ultraprocessado",
    0: "Não se aplica",
}

# ------------------------------------------------------- regras (ordenadas)
# (regex, dominio, grupo, nova)
# dominio: alimentacao | higiene | limpeza | medicamento | pet | outro
R = [
    # ========== 1. NÃO-ALIMENTOS QUE USAM PALAVRA DE COMIDA ==========
    # limpeza da casa — tem que vir antes de tudo que fala em limão, coco, leite
    (r"^(DESINF|DESINFETANTE)|^DETER|^DETERGENTE|^LAVA ROUPA|^LAVA ROUPAS|^L ROUP|"
     r"^PAPEL KITC|^PAPEL TOALHA|^P TOALHA|COALA THE QUEEN|^FILTRO MELITTA|"
     r"^LAVA LOUCA|^AMAC|^AMACIANTE|^ALVEJANTE|^AGUA SANIT|^LIMPADOR|^DESENGORDUR|"
     r"^TIRA MANCHAS|^SABAO EM PO|^SABAO BARRA|\bQBOA\b|\bVANISH\b|\bBOMBRIL\b|"
     r"^LA DE ACO|^ESPONJA|^PANO |^VASSOURA|^RODO |^PA LIXO|^BALDE|^PRENDEDOR|"
     r"^SACO LIXO|^SACO REFORCADO|^SACO FREEZER|^FILME |^FOLHA ALUM|^TOALHA PAP|"
     r"^TOALHA PAPEL|^GUARDANAP|^FOSFORO|^VELA |^PILHA |^LAMPADA|^LAMP |^INCENSO|"
     r"^DIFUSOR|^DESOD SANIT|^DESODORIZ|^INSETIC|\bRAID\b|\bSBP\b|^ALCOOL |"
     r"^KIT LIMPA|^CARVAO|^GARRAFA|^MORDEDOR|^SAPOLIO|^LUSTRA|^CERA ",
     "limpeza", None, 0),

    # medicamentos e insumos de saúde — antes de higiene (pomada, spray, creme)
    (r"DIPIRONA|PARACETAM|IBUPROF|AMOXICIL|OMEPRAZ|DORFLEX|BUSCOPAN|NEOSALDINA|"
     r"\bENGOV\b|KALMENE|RISPERIDONA|\bSELENE\b|HIXIZINE|SORINAN|BIOFENAC|"
     r"MELATONINA|NISTATINA|BACITRACINA|NEOMICINA|DICLOF|DEXAMETASONA|MOMETASONA|"
     r"GRIPINEW|EPOCLER|FIGATIL|GELO-BIO|LORATAD|CETIRIZ|ANADOR|TYLENOL|\bADVIL\b|"
     r"CLONAZEPAM|\bNARIX\b|CARBAMAZ|SERTRALINA|FLUOXETINA|PREDNIS|AZITROMIC|"
     r"CEFALEX|NIMESUL|CIMEGRIPE|\bRESFENOL\b|VITAMINA [ABCDEK]\b|POLIVITAMIN|"
     r"^SERINGA|^GAZE|^CURATIV|BAND ?AID|^TERMOMETRO|^ESPARADRAPO|^SORO FISIOL|"
     r"^BOLSA AGUA QUENTE|^SOL FISIOL|^COLETOR UNIVERSAL|SANFARMA|^OXIDO DE ZINCO",
     "medicamento", None, 0),

    # pet — a palavra do bicho basta; formato de embalagem (sachê) nunca entra
    (r"\bRACAO\b|^ALIM G |^ALIM GATO|^ALIMENTO GATO|^WHI |WHISKAS|FRISKIES|"
     r"MIKCAT|MONELLO|\bBIRBO\b|DOCATS|LEROY GATOS|QUATRO PATAS|SULTAO GATOS|"
     r"PEDIGREE|DENTALIFE|DOG CHOW|CAT CHOW|\bPROPLAN\b|^GRANULADO|^AREIA GATO|"
     r"^AREIA SANIT|AREIA HIG|PIPICAT|PETLETS|PIERINO|\bZECAT\b|SANDBED|"
     r"FIPROLEX|\bCHURU\b|DREAMIES|OVO CODORNA PETRY|\bGATOS?\b|\bCAES\b|"
     r"\bCAO\b|\bCACHORRO\b|\bFELINO\b|ANTIPULG",
     "pet", None, 0),

    # higiene pessoal — antes dos alimentos (SAB ... LEITE, COND ... , CR DENT ...)
    (r"^SAB\b|^SABONETE|^SH\b|^SHAMPOO|^COND\b|^CONDICION|^CR DENT|^CR DENTAL|"
     r"^CR ORAL|^TOALHA UMED|^LENCO UMED|AGABABY|BEBE LIMPINHO|"
     r"^CREME DENT|^GEL D |^ESC D|^ESC DENT|^ESCOVA DENT|^KIT ESC|^ENXAG|"
     r"^CEPACOL|^DES\b|^DESOD|^DESODOR|^DESODAERO|^ABS\b|^ABSORVENTE|^FR BABYSEC|"
     r"^FRALDA|^PAPEL HIG|^PAPEL HIGELITE|^PAPEL HIGIENICO|^ALGODAO|^COTONET|"
     r"^AP GILLETTE|^CARGA GILLETTE|^LAMINA|^ESP BARB|^BALS BARBA|^OLEO PARA BARBA|"
     r"^PERF\b|^PERFM|^PERFUME|^COLONIA|^HIDRAT|^LOC HID|^MASC |^ESM\b|^GLOSS|"
     r"^BATOM|^UNHAS POST|^TALCO|^TINT |^BODY SPLASH|^CR TRAT|^ESCOVA CONDOR|"
     r"\bELSEVE\b|\bSEDA\b|\bPANTENE\b|\bBOZZANO\b|\bMONANGE\b|GIOVANNA BABY|"
     r"^Uomini|^UOMINI|^CBEM SAB|OLEO PAIXAO|^CRM DENT|^CR CLOSEUP|CLOSE ?UP|^ACETONA|^PINCA|^APARELHO BARB|SUPERMAX",
     "higiene", None, 0),

    # vestuário e calçados
    (r"^CALCA\b|^CALCA |CAMISET|^CAMISA|^BERMUDA|^VESTIDO|^BLUSA|^MOLETOM|"
     r"^JAQUETA|^TENIS|^SAPATO|^CHINELO|^SANDALIA|SAND\.|HAVAIANAS|^MEIA |"
     r"^MEIA\b|^CUECA|^CALCINHA|^SUTIA|^BONE|^CASACO|^SHORT|^PIJAMA|^BIQUINI|"
     r"^REGATA|^POLO\b|^CINTO|^KIT \dX1|^BLINK 182|MY CHEMICAL ROMANCE|"
     r"^BRINCO|^COLAR |^PULSEIRA|^RELOGIO|^MOCHILA|^BOLSA\b",
     "vestuario", None, 0),

    # combustível
    (r"^GA GASOLINA|^GC GASOLINA|^ET ETANOL|GASOLINA|\bETANOL\b|\bDIESEL\b|"
     r"^OLEO IPIRANGA|\b20W ?50\b",
     "combustivel", None, 0),

    # casa, cama, mesa e bazar
    (r"^COBERTOR|^TAPETE|^TOALHA DE|^LENCOL|^TRAVESSEIR|^ALMOFADA|^CORTINA|"
     r"^PANELA|^TALHER|^CANECA|^POTE\b|^CAIXA ORG|^CABIDE|^COLA |^PARAFUSO|"
     r"^FERRAMENT|^CADERNO|^CANETA|^PAPEL A4|^CARREGADOR|^CABO USB|^FONE\b|"
     r"^FORM AFRY|^FORMA ",
     "casa", None, 0),

    # ========== 2. BEBIDAS ==========
    (r"^CERV|CERVEJA|^CV |^VINHO|^VH |^VIN |CHOPP|WHISK|VODKA|\bGIN\b|CACHACA|"
     r"ESPUMANTE|LICOR|APEROL|CAMPARI|\bRUM\b|TEQUILA|SIDRA|\bSAQUE\b|\bIPA\b|"
     r"HEINEKEN|BUDW|BRAHMA|\bSKOL\b|\bPOLAR\b|SPATEN|BOHEMIA|EISENBAHN|CARACU|"
     r"BADEN|CORONA|STELLA|AMSTEL|\bPILSEN\b|VELHO BARREIRO|JOTA PE|SANGUE DE BOI|"
     r"ALMADEN|PIEL DE LOBO|\bARBO\b|\bMALBEC\b|\bBONARDA\b|C\.SAUV|\bTANNAT\b|"
     r"\bMERLOT\b|CABERNET|COQUETEL|\bMARULA\b|SMIRNOFF|\bCERPA\b|ESTRELLA GALICIA|"
     r"\bSALVA\b|AZUMA KIRIN|^MS RODEIO|^RODEIO|3MED|^BEATS |LONG NECK|"
     r"^FL TRUFA|^CB CP|^PINK 400",
     "alimentacao", "Bebidas alcoólicas", 3),

    (r"^REFRIG|COCA ?-?COLA|\bCOCA\b|\bPEPSI\b|GUARANA|\bFANTA\b|SPRITE|SCHWEPPES|"
     r"^ENERG|ENERGETIC|RED BULL|\bTNT\b|MONSTER|\bBALY\b|\bH2OH\b|\bTONICA\b|"
     r"SODA LIMONADA|CRYSTAL SABORES",
     "alimentacao", "Refrigerantes e energéticos", 4),

    (r"^AGUA MIN|^AGUA MINERAL|^AG MIN|^AG MINERAL|^AGUA \d|^AGUA 20L|^AGUA\b|"
     r"^CAFE|^CAPPUCCIN|CAPUCCIN|^CHA\b|^CHA |CHIMARRAO|^ERVA MATE|\bERVA\b|"
     r"^SUCO|^SUC |NECTAR|DEL VALLE|\bTANG\b|^REFRESCO|ISOTONIC|GATORADE|POWERADE|"
     r"^BEB LAC|BEBIDA LACTEA|^ACHOC|NESCAU|CHOCOLATTO|^LATTE|^EXPRESSO|^ESPRESSO",
     "alimentacao", "Água, café, chá e sucos", 1),

    # ========== 3. ALIMENTOS ULTRAPROCESSADOS (tipo manda no sabor) ==========
    (r"^SALG|^SALGADIN|^SALGADINHO|CHEETOS|DORITOS|RUFFLES|PRINGLES|FANDANGOS|"
     r"^TORCIDA|TORCIDA JR|BATATA CHIPS|BATATA LAYS|BATATA PALHA|^BALDE BATATA|"
     r"CLUB SOCIAL|\bSNACK\b|\bCHIPS\b",
     "alimentacao", "Ultraprocessados e doces", 4),

    (r"^CHOC|CHOCOLAT|^BOMBOM|^TRUFA|TRUFAO|^BALA\b|^BALAS|^PIRULITO|CHICLE|"
     r"TRIDENT|^HALLS|MENTOS|TIC TAC|KIT ?KAT|OURO BRANCO|SONHO VALSA|\bBIS\b|"
     r"\bLACTA\b|HERSHEY|SNICKERS|STIKADINHO|\bTRENTO\b|5STAR|TALENTO|"
     r"DIAMANTE NEGRO|\bLOLLO\b|\bBATON\b|PRESTIGIO|\bALPINO\b|CHOKITO|^ALFAJOR|"
     r"^FONDANT|^PE DE MOCA|MANTEIGA CACAU|^COCADA|^TORRAO|^PACOCA|^BEIJINHO|"
     r"^BRIGADEIRO|^DOCE |^TRUFAO|^AMOR CARIOCA|^CONF AMOR|^WAFFER|^WAFER|^WAFFLE|^PACOQUINHA|CHOCO STICK|^GOMA |^DC NUTRI|^NUTRI TORR",
     "alimentacao", "Ultraprocessados e doces", 4),

    (r"^BISC|^BISCOIT|^BOLACHA|\bCOOKIE\b|\bOREO\b|ORQUIDEA GERGELIM|^BOLO |"
     r"^BOLINHO|BAUDUCCO|^SUCRILHOS|^BARRA CEREAL|^BARRA PROT|^BARRA WHEY|"
     r"^BARRA DE BANANA|OVOMALTIN|^CEREAL",
     "alimentacao", "Ultraprocessados e doces", 4),

    (r"^EMP\b|^EMPANAD|^STEAK|NUGGET|CHICKEN |ANEIS DE CEBOLA|^LASANHA|^PIZZA|"
     r"^ESFIHA|^NHOQUE|^YAKISSOBA|^FEIJOADA|^KIBE|^HOT DOG|^HAMB|^HAMBURG|"
     r"BATATA CONGELADA|BATATA PRE FRITA|BATATA HASHTAG|DEUTSCHIP|^FILEZINHO SASSAMI|"
     r"^SORVETE|^PICOLE|^ACAI|CUP NOODLES|^NISSIN|^FAGOTTO|^DADINHO TAPIOCA|"
     r"^SALSICHA|^SALSICHAO|^FOLHADO|^MINI COXINHA|^COXINHA|^PASTEL|^MEXICANO|"
     r"^MEDALHAO|^PAO DE QUEIJO|^PAO ALHO|^PAO D ALHO|^PAO DE ALHO|^BROCOLIS P/MICRO|"
     r"^FRICASSE|^ESCONDIDNHO|^ESCONDIDINHO|^STROGONOFF|^MOQUECA|^MISTURA CHINESA|"
     r"MAC.?N ?CHEESE|MACECCHEESE|^HOT BOWLS|^MIST PANQ|^FETTUCCINE|^EMB LOMBO|"
     r"^MIX DE SALGADOS|^MIX DE VEGETAIS|^SOBREMESA|^BISNAGUINHA|NUTRELLA|"
     r"^TORTEI|^CAPELET|^RAVIOLI|EASY CHEF|\bDAUCY\b|^PANQUECA|^FILEZINHO SEARA|AMILANESA",
     "alimentacao", "Ultraprocessados e doces", 4),

    (r"^MAIONESE|^CATCHUP|^KETCHUP|^MOSTARDA|MOLHO|^SHOYU|^BARBECUE|^CALDO|"
     r"^EXTRATO|^PASSATA|^POLPA|^CONSERVA|^PICLES|"
     r"^SOPA|^GELATINA|^PUDIM|^TEMP |^TEMPERO |TEMPERALLE|MERCATTO|BRSPICES|"
     r"PALLATO|^ADOBO|^ALCEBSAL|^MIX PIMENTAS|^SALADA SUPER|^ACAFRAO|^COLORAU|^CANELA|^CRAVO|^COMINHO|^OREGANO|^LOURO|^ALECRIM|^ERVAS FINAS|^GENGIBRE|^PIMENTA|^PIM \b|^SAL DIANA|^CURRY|^COENTRO|^MANJERICAO|^PASSATA|SALSARETTI",
     "alimentacao", "Molhos, temperos e condimentos", 4),

    # ========== 4. LATICÍNIOS E OVOS ==========
    (r"^OVO\b|^OVOS\b|^HF OVO|OVO CAGERI|OVO BRANCO|OVO VM",
     "alimentacao", "Ovos", 1),

    (r"^LEITE COND|LEITE CONDENSADO", "alimentacao", "Laticínios", 4),
    (r"^LEITE\b|^LEITE |LEITE UHT|LEITE L VIDA|LEITE LONGA VIDA",
     "alimentacao", "Laticínios", 1),
    (r"^IOG|IOGURT|^YOPRO|\bDANONE\b|\bYAKULT\b",
     "alimentacao", "Laticínios", 4),
    (r"^QUEIJO|^QJO\b|MUSSAREL|^REQUEIJ|CREAM CHEESE|^RICOTA|^COALHO|POLENGHI|"
     r"^NATA\b|^CHANTIL|^REQ\b|^REQ |^CREM DE LTE|^CREME DE LEITE",
     "alimentacao", "Laticínios", 3),
    (r"^MANTEIG|^MARG\b|^MARGARIN|^CREME DE LEITE",
     "alimentacao", "Gorduras e óleos", 2),

    # ========== 5. PROTEÍNAS ==========
    (r"^LINGUICA|^LING |CALABESA|CALABRESA|^MORTADELA|^PRESUNTO|^SALAME|"
     r"^APRESUNT|PEPPERONI|^PATE |BLANQUET|PEITO DE PERU|^BACON|^FIAMBRE|^MORT",
     "alimentacao", "Carnes processadas e embutidos", 4),

    # sem âncora `^`: o corte raramente abre a descrição ("CONTRA FILE",
    # "POSTA DE SALMAO", "RIPA DE COSTELA", "FILE DE TILAPIA")
    (r"\bCARNE\b|\bCARNES\b|\bBIFE\b|\bBIFES\b|COXAO|\bPATINHO\b|ALCATRA|"
     r"PICANHA|MAMINHA|FRALDINHA|\bCOSTELA\b|COSTELINHA|\bACEM\b|MUSCULO|"
     r"\bFILE\b|\bFRANGO\b|\bPEITO\b|\bCOXA\b|\bCOXAS\b|SOBRECOXA|\bASA\b|"
     r"\bASAS\b|\bPERNIL\b|\bLOMBO\b|\bSUIN[AO]\b|\bBOVIN[AO]\b|\bPORCO\b|"
     r"\bCUPIM\b|\bMOIDA\b|\bMOIDO\b|\bCARRE\b|\bPALETA\b|\bMATAMBRE\b|"
     r"\bFIGADO\b|\bMOELA\b|\bVAZIO\b|ENTRECOT|SPALET|\bTATU\b|\bKING\b|"
     r"\bLAGARTO\b|\bBISTECA\b|\bCHULETA\b|CHARQUE|\bJERKED\b|\bPA BOVINA\b|"
     r"\bMIOLO\b|\bRIPA\b|\bPAILLARD\b|\bTENDER\b|\bMIUDOS\b|DOBRADINHA|"
     r"\bRABADA\b|\bMOCOTO\b|OSSOBUCO|ALMONDEGA|\bDIANTEIRO\b|\bTRASEIRO\b|"
     r"\bTILAPIA\b|\bSALMAO\b|\bMERLUZA\b|\bATUM\b|SARDINH|\bCAMARAO\b|\bCAM \b|"
     r"TENTACULOS|\bPOLVO\b|\bLULA\b|MARISC|MEXILHAO|\bBACALHAU\b|PESCAD|"
     r"\bCORVINA\b|\bANCHOVA\b|\bABADEJO\b|\bPANGA\b|\bPOLACA\b|\bTAINHA\b|"
     r"\bTRAIRA\b|\bPACU\b|\bPOSTA\b|\bPOSTAS\b|\bPED FILE\b|CORACAO BOVINO|"
     r"\bTOUCINHO\b",
     "alimentacao", "Carnes, aves e peixes", 1),

    # ========== 6. FRUTAS ==========
    (r"^HF BANANA|^HF MACA|^HF LARANJA|^HF LIMAO|^HF BERGAMOTA|^HF UVA|^HF PINHAO|"
     r"^BANANA\b|^BANANA |^MACA\b|^LARANJA\b|^LARANJA |^LIMAO SICILIANO|"
     r"^LIMAO TAITI|^BERGAMOTA|^UVA\b|^MANGA\b|^MANGA |^MELANCIA|^MAMAO|^ABACAXI|"
     r"^MORANGO|^PERA\b|^MELAO|^KIWI|^AMEIXA|^PESSEGO|^ABACATE|^GOIABA|^CAQUI|"
     r"^FIGO\b|^COCO\b|^PINHAO",
     "alimentacao", "Frutas", 1),

    # ========== 7. VERDURAS E LEGUMES ==========
    (r"^HF ALFACE|^HF TOMATE|^HF CEBOLA|^HF CENOURA|^HF BETERRABA|^HF REPOLHO|"
     r"^HF PEPINO|^HF ALHO|^HF TEMPERO VERDE|^HF BATATA|"
     r"^ALFACE|^TOMATE|^CEBOLA|^CENOURA|^BETERRABA|^REPOLHO|^PEPINO|^ALHO\b|"
     r"^ALHO |^BROCOLIS|^COUVE|^RUCULA|^AGRIAO|^ABOBOR|^CHUCHU|^VAGEM|^PIMENTAO|"
     r"^SALSA\b|^CEBOLINH|^ESPINAFRE|^BERINJELA|^MILHO VERDE|^ERVILHA|^MORANGA|^ABOBRINHA|^COUVE-?FLOR",
     "alimentacao", "Verduras e legumes", 1),

    # ========== 8. CARBOIDRATOS (raízes, pães, massas) ==========
    (r"^BATATA\b|^BATATA |^AIPIM|^MANDIOCA|^INHAME|^CARA\b|^BATATA DOCE",
     "alimentacao", "Raízes e tubérculos", 1),

    (r"^PAO\b|^PAO |^PAES|CACETINH|^BAGUET|^BRIOCHE|^ROSCA|^CUCA|^PANETONE|"
     r"^TORTA|^CROISSAN|^CHAPINHA|^BOLO DE AIPIM|^MASSINHA DOCE|^SONHO\b",
     "alimentacao", "Pães", 3),

    (r"^MACARRAO|^MASSA |^MASSA\b|ESPAGUETE|ESPAGTNI|RIGATONE|^TALHARIM|"
     r"^PENNE|^PARAFUSO MASSA",
     "alimentacao", "Massas", 3),

    # ========== 9. CEREAIS, GRÃOS E LEGUMINOSAS ==========
    (r"^ARROZ|^FEIJAO|^AVEIA|^LENTILHA|^GRAO DE BICO|^SOJA\b|^QUINOA|^CANJICA|"
     r"^SAGU|^POLENTA|^FUBA|^FARINHA|^TRIGO|^AMIDO|^FERMENT|^MILHO PIP|^PIPOCA|"
     r"^GRANOLA|^CHIA\b|^LINHACA",
     "alimentacao", "Cereais, grãos e leguminosas", 1),

    # ========== 10. GORDURAS, ÓLEOS, AÇÚCAR, SAL ==========
    (r"^OLEO |^OLEO\b|^AZEITE|^AZ \b|^AZ |^BANHA",
     "alimentacao", "Gorduras e óleos", 2),
    (r"^ACUCAR|^SAL\b|^SAL |^VINAGRE|^MEL\b|^ADOCANTE",
     "alimentacao", "Açúcar, sal e vinagre", 2),

    # ========== 11. CONSERVAS ==========
    (r"^AZEITONA|^PALMITO|^SELETA|^MILHO\b|^ERVILHA|^COCO RALADO|^LEITE DE COCO|"
     r"^NUTS|^AMENDOIM|^CASTANHA|^NOZES",
     "alimentacao", "Conservas e oleaginosas", 3),

    # ========== 12. REFEIÇÃO PRONTA ==========
    (r"^COMBO|^LANCHE|^BURGER|SANDUIC|^SAND |^PORCAO|PRATO FEITO|^BUFFET|"
     r"MCLANCHE|BIG MAC|WHOPPER|^ESPETINHO|^REFEICAO|^ALMOCO|^JANTA|BATATA FRITA|"
     r"MILK ?SHAKE|^BAT G|^JALAPENO|^STACKER|^REFRI DRIVE|^CHICKEN DUPLO|"
     r"^KING |^BALDE BATATA|^BATATA GRANDE",
     "alimentacao", "Refeições prontas fora de casa", 4),
]

R = [(re.compile(p), d, g, n) for p, d, g, n in R]


def classificar(desc):
    """-> (dominio, grupo, nova) ; dominio 'outro' quando nada casa."""
    t = norm(desc)
    for rx, dom, grupo, nova in R:
        if rx.search(t):
            return dom, grupo, nova
    return "outro", None, 0


# ----------------------------------------------------- subgrupos de higiene
SUB_HIGIENE = [
    (r"^CR DENT|^CR DENTAL|^CREME DENT|^GEL D |^ESC D|^ESC DENT|^ESCOVA DENT|"
     r"^KIT ESC|^ENXAG|^CEPACOL|FIO DENTAL|^CR ORAL", "Higiene bucal"),
    (r"^PAPEL HIG|^PAPEL HIGELITE|^PAPEL HIGIENICO", "Papel higiênico"),
    (r"^ABS\b|^ABSORVENTE|^FR BABYSEC|^FRALDA", "Absorventes e fraldas"),
    (r"^SH\b|^SHAMPOO|^COND\b|^CONDICION|^MASC TRAT|^CR TRAT|^TINT |\bELSEVE\b|"
     r"\bSEDA\b|\bPANTENE\b", "Cabelo"),
    (r"^AP GILLETTE|^CARGA GILLETTE|^LAMINA|^ESP BARB|^BALS BARBA|OLEO PARA BARBA",
     "Barbear"),
    (r"^PERF\b|^PERFM|^PERFUME|^COLONIA|^ESM\b|^GLOSS|^BATOM|^UNHAS POST|"
     r"^MASC CILIOS|^HIDRAT FAC|^Uomini|OLEO PAIXAO|^BODY SPLASH", "Perfumaria e maquiagem"),
    (r"^SAB\b|^SABONETE|^CBEM SAB|^LOC HID|^HIDRAT|^TALCO|^ALGODAO|^COTONET|"
     r"^ESCOVA CONDOR", "Corpo e pele"),
    (r"^DES\b|^DESOD|^DESODOR|^DESODAERO", "Desodorante"),
]
SUB_HIGIENE = [(re.compile(p), n) for p, n in SUB_HIGIENE]


def sub_higiene(desc):
    t = norm(desc)
    for rx, nome in SUB_HIGIENE:
        if rx.search(t):
            return nome
    return "Outros de higiene"


# ----------------------------------------------------- subgrupos de limpeza
SUB_LIMPEZA = [
    (r"^LAVA ROUPA|^LAVA ROUPAS|^L ROUP|^AMAC|^AMACIANTE|^TIRA MANCHAS|"
     r"^SABAO EM PO|^SABAO BARRA|\bVANISH\b|^ALVEJANTE", "Roupas"),
    (r"^DETER|^DETERGENTE|^LAVA LOUCA|^ESPONJA|^LA DE ACO|\bBOMBRIL\b",
     "Louça"),
    (r"^DESINF|^DESINFETANTE|^AGUA SANIT|^LIMPADOR|^DESENGORDUR|\bQBOA\b|"
     r"^MULTIUSO|^ALCOOL ", "Desinfetante e multiuso"),
    (r"^SACO LIXO|^SACO REFORCADO|^SACO FREEZER|^FILME |^FOLHA ALUM|^TOALHA PAP|"
     r"^TOALHA PAPEL|^GUARDANAP|^PANO ", "Descartáveis"),
    (r"^VASSOURA|^RODO |^PA LIXO|^BALDE|^PRENDEDOR|^KIT LIMPA|^GARRAFA|"
     r"^MORDEDOR", "Utensílios"),
    (r"^FOSFORO|^VELA |^PILHA |^LAMPADA|^LAMP |^CARVAO", "Casa e utilidades"),
    (r"^INCENSO|^DIFUSOR|^DESOD SANIT|^DESODORIZ", "Aromatizantes"),
]
SUB_LIMPEZA = [(re.compile(p), n) for p, n in SUB_LIMPEZA]


def sub_limpeza(desc):
    t = norm(desc)
    for rx, nome in SUB_LIMPEZA:
        if rx.search(t):
            return nome
    return "Outros de limpeza"


# ------------------------------------------------ classes de medicamento
CLASSES_MED = [
    (r"DIPIRONA|PARACETAM|\bDORFLEX\b|ANADOR|TYLENOL|NEOSALDINA",
     "Analgésico e antitérmico", "sem receita"),
    (r"IBUPROF|NIMESUL|DICLOF|BIOFENAC|\bADVIL\b|GELO-BIO",
     "Anti-inflamatório", "sem receita"),
    (r"HIXIZINE|LORATAD|CETIRIZ|SORINAN|\bNARIX\b|DEXAMETASONA|MOMETASONA|"
     r"SOL\.?\s?NASAL|SOLUCAO NASAL|DESLORATAD|PREDNIS|BUDESONIDA|SALBUTAMOL|"
     r"HIDROCORTISONA|BETAMETASONA",
     "Antialérgico e respiratório", "receita simples"),
    (r"RISPERIDONA|CLONAZEPAM|CARBAMAZ|SERTRALINA|FLUOXETINA|KALMENE|MELATONINA|"
     r"DIAZEPAM|ALPRAZOLAM|ESCITALOPRAM|QUETIAPINA|ZOLPIDEM|RIVOTRIL",
     "Sistema nervoso e sono", "receita controlada"),
    (r"NISTATINA|BACITRACINA|NEOMICINA|AMOXICIL|AZITROMIC|CEFALEX",
     "Antibiótico e antifúngico", "receita obrigatória"),
    (r"\bSELENE\b|CICLO 21|DIANE", "Contraceptivo", "receita simples"),
    (r"EPOCLER|FIGATIL|OMEPRAZ|BUSCOPAN|\bENGOV\b", "Fígado e digestão", "sem receita"),
    (r"GRIPINEW|CIMEGRIPE|\bRESFENOL\b", "Gripe e resfriado", "sem receita"),
    (r"VITAMINA|POLIVITAMIN", "Vitaminas e suplementos", "sem receita"),
    (r"^SERINGA|^GAZE|^CURATIV|BAND ?AID|^TERMOMETRO|^ESPARADRAPO|^SORO FISIOL",
     "Material e insumo", "sem receita"),
]
CLASSES_MED = [(re.compile(p), n, r) for p, n, r in CLASSES_MED]


def classe_medicamento(desc):
    t = norm(desc)
    for rx, nome, receita in CLASSES_MED:
        if rx.search(t):
            return nome, receita
    return "Outros medicamentos", "não classificado"


# ------------------------------------------------ agrupamento nutricional
# Os sete grupos que o pedido citou, mais os que faltavam para fechar 100%.
ORDEM_GRUPOS = [
    "Carnes, aves e peixes",
    "Ovos",
    "Carnes processadas e embutidos",
    "Laticínios",
    "Frutas",
    "Verduras e legumes",
    "Cereais, grãos e leguminosas",
    "Raízes e tubérculos",
    "Pães",
    "Massas",
    "Gorduras e óleos",
    "Açúcar, sal e vinagre",
    "Conservas e oleaginosas",
    "Molhos, temperos e condimentos",
    "Ultraprocessados e doces",
    "Refeições prontas fora de casa",
    "Refrigerantes e energéticos",
    "Água, café, chá e sucos",
    "Bebidas alcoólicas",
]

# leitura macro pedida no enunciado
MACRO = {
    "Carnes, aves e peixes": "Proteínas",
    "Ovos": "Proteínas",
    "Carnes processadas e embutidos": "Proteínas",
    "Laticínios": "Proteínas",
    "Frutas": "Frutas",
    "Verduras e legumes": "Verduras e legumes",
    "Cereais, grãos e leguminosas": "Cereais e grãos",
    "Raízes e tubérculos": "Carboidratos",
    "Pães": "Carboidratos",
    "Massas": "Carboidratos",
    "Gorduras e óleos": "Gorduras e temperos",
    "Açúcar, sal e vinagre": "Gorduras e temperos",
    "Conservas e oleaginosas": "Gorduras e temperos",
    "Molhos, temperos e condimentos": "Gorduras e temperos",
    "Ultraprocessados e doces": "Ultraprocessados e doces",
    "Refeições prontas fora de casa": "Ultraprocessados e doces",
    "Refrigerantes e energéticos": "Refrigerantes",
    "Água, café, chá e sucos": "Água, café e sucos",
    "Bebidas alcoólicas": "Bebidas alcoólicas",
}
