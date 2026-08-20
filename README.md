# SLT — Gestão de Gastos

Transforma a planilha do **Nota Fiscal Gaúcha** num relatório completo do que
você consome — com cenas 3D navegáveis, análise nutricional e estimativa de
impostos. Tudo roda no seu computador; nada é enviado para lugar nenhum.

Você baixa a planilha do site, aponta a pasta no programa e pronto.

![Windows](https://img.shields.io/badge/Windows-10%2F11-0e100e?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-35a87a?style=flat-square)
![Licença](https://img.shields.io/badge/licença-MIT-35a87a?style=flat-square)

---

## Como obter o seu relatório

### 1. Baixe a planilha no site do Nota Fiscal Gaúcha

1. Entre em <https://nfg.sefaz.rs.gov.br> e faça login (CPF e senha, ou gov.br).
2. No menu, vá em **Documentos Fiscais → Consultar Documentos Fiscais**
   (em algumas versões do site: *Minhas Notas* ou *Consultas → Documentos*).
3. Escolha o período. Para o ano todo, coloque de **01/01** até hoje.
4. Clique em **Consultar** e depois no botão de **exportar para Excel**
   (ícone de planilha, ou "Baixar XLSX").

O arquivo vem com um nome tipo `Nota Fiscal Gaúcha.xlsx`. Ele tem uma linha por
nota e uma coluna **Chave de Acesso** — é dela que o programa parte.

> **Renomeie o arquivo com o nome da pessoa**, por exemplo
> `Nota Fiscal Gaúcha Maria.xlsx`. O programa usa isso como primeiro palpite do
> nome; depois confirma pelo nome que consta na própria nota.

### 2. Junte as planilhas numa pasta

Crie uma pasta qualquer — `C:\Meus Gastos`, por exemplo — e coloque as planilhas
dentro. **Uma planilha por pessoa.**

```
C:\Meus Gastos\
  Nota Fiscal Gaúcha Maria.xlsx
  Nota Fiscal Gaúcha João.xlsx      ← opcional, se quiser o relatório da família
```

### 3. Abra o programa e clique em Analisar

Baixe o **SLT - Gestão de Gastos.exe** na
[página de versões](../../releases) e execute. Aponte a pasta e clique em
**Analisar**.

Na primeira vez, consultar a SEFAZ leva cerca de **1,5 segundo por nota** —
umas oito minutos para 300 notas. O programa faz uma pausa entre as consultas de
propósito, para não sobrecarregar o servidor público. Nas próximas execuções o
que já foi baixado é reaproveitado e o resultado sai em segundos.

### 4. Abra o Relatorio.html

Quando terminar, o programa oferece abrir o relatório. É um arquivo só, que
funciona offline e você pode mandar por e-mail ou guardar num pendrive.

---

## Uma pessoa ou a família toda

O programa descobre sozinho quem é quem: o CPF e o nome saem das próprias notas
consultadas — a NFC-e traz `CPF: 000.000.000-00 - FULANO DE TAL`.

| Planilhas na pasta | O que acontece |
| --- | --- |
| Uma, com um CPF | Relatório individual, no nome da pessoa. O título fica *"O mapa do que você consome"*. |
| Duas ou mais, CPFs diferentes | Modo família: soma tudo, cada pessoa vira um membro e aparece a comparação de quem gastou o quê. |
| Duas com o **mesmo** CPF | Viram uma pessoa só, com as notas juntadas. |

Chave repetida em mais de uma planilha é contada uma vez só.

---

## O que o relatório mostra

**Calendário 3D do ano.** Uma coluna por dia: eixo largo = as semanas, eixo curto
= segunda a domingo, altura e cor = quanto se gastou. Clicar numa coluna leva a
câmera até ela e abre a nota daquele dia, com loja, horário e cada produto.

**Torres por categoria.** Uma torre por categoria de produto, fatiada pelos
meses. Clicar entra na categoria: evolução mensal, produtos que mais pesaram,
onde se compra.

**Mapa do consumo.** Para onde o dinheiro vai por área da vida — alimentação,
higiene, limpeza, medicamento, pet, vestuário, combustível, casa — e a cesta de
uma semana média.

**Alimentação.** Grupos alimentares, grau de processamento pela classificação
**NOVA** do Guia Alimentar para a População Brasileira, qual semana foi a menos
nutritiva, quilos de comida fresca, litros de bebida, e o dia a dia.

**Higiene e limpeza.** Composição por tipo e de quanto em quanto tempo cada
essencial é reposto: papel higiênico, sabonete, creme dental, lava-roupas.

**Medicamentos.** Classe terapêutica, exigência de receita, linha do tempo.

**E o resto.** Ritmo mensal e semanal, lojas, preços que subiram e caíram,
impostos estimados, dias extremos e um explorador de todas as notas com busca,
filtro e ordenação.

---

## Ver funcionando, sem usar suas notas

Há um conjunto de dados **fictício** no repositório para você ver o resultado
antes de rodar com as suas notas:

```bash
python gerar_exemplo.py _demo          # gera dados inventados
python -c "import json,sys; sys.path.insert(0,'.'); from app import relatorio; relatorio.gerar(json.load(open('_demo/dados.json',encoding='utf-8')),'_demo')"
```

Abra `_demo/Relatorio.html`. As pessoas, as lojas e as compras são inventadas.

---

## Como os dados são obtidos

Para cada chave de acesso da planilha, o programa faz o mesmo caminho que uma
pessoa faria no navegador:

1. abre `https://www.sefaz.rs.gov.br/NFE/NFE-NFC.aspx?chaveNFe=<CHAVE>`
2. aciona o botão **Avançar**

A página do passo 1 é um invólucro com iframe; o formulário de verdade fica em
`/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_1.asp` e envia um POST para o `_2.asp`. É
esse POST que devolve a *Consulta Completa da NFC-e*, com emitente, CNPJ,
endereço, número, série, data, hora, protocolo, CPF do consumidor, todos os
produtos e as formas de pagamento.

### O que não dá para baixar

Chaves de **NF-e modelo 55** (nota fiscal comum, não cupom) não têm consulta
pública: o portal DFe da SVRS exige login pela conta gov.br. Elas entram no total
pelo valor da planilha, sem detalhe de itens, e ficam listadas num CSV à parte.

---

## O que sai na pasta

```
Relatorio.html          o relatório inteiro num arquivo só
Notas/
  2026-01/ … 2026-12/   uma pasta por mês, um .txt por nota, com a nota completa
  _HTML_ORIGINAL_SEFAZ/ a página original da SEFAZ para cada chave, sem alteração
  _DADOS/
    notas.csv                    uma linha por nota
    itens.csv                    uma linha por produto, já classificado
    notas_completas.json         tudo em JSON, itens aninhados
    itens_nao_classificados.csv  o que caiu em "Outros"
    nfe_modelo55_sem_consulta_publica.csv
    chaves_com_falha.csv         só existe se alguma chave não baixou
  LEIA-ME.txt
.cache_sefaz/           as páginas baixadas, para não repetir a consulta
```

---

## Duas ressalvas importantes

### Os tributos são estimativa

A consulta pública da NFC-e **não divulga** os valores de tributo da nota. O
campo da Lei 12.741/2012 existe no XML original, mas não aparece na tela
pública, e a versão em abas com ICMS/PIS/COFINS item a item exige login gov.br.

Por isso o programa **estima**: aplica a cada item a carga tributária média da
sua categoria (ICMS-RS + PIS/COFINS + IPI), nas faixas divulgadas pelo IBPT — o
mesmo critério que o supermercado usa para imprimir o total de tributos no
rodapé do cupom. É ordem de grandeza, não o valor exato recolhido.

### Gasto não é quantidade

Fruta e verdura são baratas por quilo; bebida alcoólica é cara. Ler só o dinheiro
distorce a leitura nutricional. Por isso os **quilos** (do que é vendido a quilo)
e os **litros** (lidos do volume na descrição) aparecem sempre ao lado do valor.

E a classificação nutricional é do produto **comprado**, não do que foi
efetivamente comido. Nada aqui mede porção, caloria ou nutriente, e não
substitui orientação profissional.

---

## Como a classificação funciona

Cada item é classificado pelo **tipo do produto** lido na descrição, não pela
loja onde foi comprado. Isso importa porque a descrição da nota engana muito:

| Descrição na nota | O que parece | O que é |
| --- | --- | --- |
| `DESINF GOTA LIMPA LIMAO 2L` | fruta | desinfetante |
| `SAB NIVEA LEITE 85G` | laticínio | sabonete |
| `SALGADINHO DORITOS QJO NACHO` | queijo | salgadinho |
| `ACHOC PO NESCAU SACHE 195G` | ração (sachê!) | achocolatado |
| `AG MINERAL NATURALE C/GAS` | combustível | água mineral |

As regras de **tipo** vêm antes das de **ingrediente**, e a primeira que casa
vence. Há um arquivo de testes com casos reais:

```bash
python testes_classificacao.py
```

### Dando nome às suas lojas

O programa limpa a razão social automaticamente
(`COM DE GENEROS ALIMENT MODELO LTDA` → `Generos Aliment Modelo`). Se quiser
nomes melhores, crie um `lojas.json` na pasta das planilhas:

```json
[
  { "quando": "MODELO",     "apelido": "Mercado do Zé", "ramo": "Supermercado" },
  { "quando": "SILVA LTDA", "apelido": "Padaria da Esquina" }
]
```

`quando` é uma expressão regular testada contra a razão social. Esse arquivo
fica só no seu computador.

---

## Compilar do código

Precisa de **Python 3.11+** e **Node 18+** (o Node só para empacotar o JavaScript
do relatório).

```bash
pip install openpyxl requests lxml pyinstaller pillow
npm install

node build_relatorio.mjs     # empacota Three.js + GSAP + o app num arquivo só
python gerar_icone.py        # desenha o ícone
python build.py              # gera dist/SLT - Gestão de Gastos.exe
```

Sem compilar, dá para rodar direto:

```bash
python slt.py                          # abre a janela
python slt.py "C:\Meus Gastos"         # linha de comando
```

---

## Como está organizado

```
app/
  planilhas.py   lê os .xlsx e valida as chaves de acesso
  sefaz.py       consulta a SEFAZ-RS (com cache e pausa entre requisições)
  extrair.py     interpreta a página da Consulta Completa
  pessoas.py     descobre quem é quem pelo CPF das notas
  categorias.py  categoria comercial + carga tributária estimada
  mapa.py        domínio de consumo, grupo alimentar e classificação NOVA
  analise.py     consolida tudo no conjunto que alimenta o relatório
  salvar.py      escreve os .txt, os CSVs e o JSON
  relatorio.py   monta o HTML final
  pipeline.py    orquestra do zero ao relatório
  gui.py         a janela (tkinter)
fonte_relatorio/ o front-end do relatório (Three.js + GSAP, JavaScript puro)
recursos/        ícone e o molde do HTML
```

**Feito com:** Python · tkinter · Three.js · GSAP · esbuild · PyInstaller

---

## Licença

MIT — veja [LICENSE](LICENSE).

Este projeto não tem vínculo com a Secretaria da Fazenda do RS nem com o
programa Nota Fiscal Gaúcha. Usa apenas a consulta pública de NFC-e, do mesmo
jeito que qualquer pessoa faria pelo navegador.
