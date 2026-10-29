# SLT — Gestão de Gastos

Aplicação que transforma planilhas exportadas do **Nota Fiscal Gaúcha** em um relatório navegável de consumo.

O programa lê as chaves das notas, consulta os dados públicos disponíveis da NFC-e, organiza os itens e gera um relatório HTML autossuficiente.

![Windows](https://img.shields.io/badge/Windows-10%2F11-informational)
![Python](https://img.shields.io/badge/Python-3.11%2B-informational)

## O que o projeto faz

- importa uma ou mais planilhas XLSX ou arquivos TXT com chaves de acesso avulsas;
- identifica pessoas pelas informações das notas;
- consulta dados públicos de NFC-e;
- usa cache para não repetir consultas;
- extrai loja, data, itens e formas de pagamento;
- classifica produtos por categoria de consumo;
- gera indicadores de alimentação, higiene, limpeza, medicamentos e outros grupos;
- estima carga tributária por categoria;
- cria visualizações 3D e análises navegáveis em um único arquivo HTML.

## Stack

Python 3.11+ · tkinter · openpyxl · requests · lxml · Three.js · GSAP · esbuild · PyInstaller

## Arquitetura

```text
app/
├── planilhas.py   # leitura e validação das planilhas
├── sefaz.py       # consulta + cache
├── extrair.py     # interpretação das páginas
├── pessoas.py     # identificação dos consumidores
├── categorias.py  # classificação comercial
├── mapa.py        # domínios de consumo e alimentação
├── analise.py     # consolidação
├── salvar.py      # CSV/JSON/TXT
├── relatorio.py   # geração do HTML
├── pipeline.py    # orquestração
└── gui.py         # interface desktop

fonte_relatorio/   # front-end Three.js + GSAP
```

## Resultado

O relatório inclui:

- gráfico de gastos diários, semanais ou mensais, com seleção de linhas, navegação por períodos e tabela de valores;
- ranking de estabelecimentos por dias com compra, notas, gasto e ticket médio;
- comparação de marcas por categoria e termo de produto, e ranking de descrições mais frequentes;
- calendário 3D de gastos ao longo do ano;
- categorias de consumo;
- evolução mensal;
- lojas mais utilizadas;
- produtos com variação de preço;
- alimentação por grupo e classificação NOVA;
- medicamentos;
- higiene e limpeza;
- estimativa de impostos;
- explorador de notas e itens.

## Notas avulsas e gráfico

Coloque na pasta de entrada um arquivo `.txt` UTF-8 com uma chave de acesso de 44 dígitos por linha. Pode misturá-lo com planilhas do Nota Fiscal Gaúcha; chaves repetidas são consultadas uma vez. Somente NFC-e com consulta pública na SEFAZ-RS são detalhadas. Arquivos PDF, fotos e XML não são importados por este formato.

No gráfico, cada corpo vai de zero ao total pago no período selecionado; não representa preços de abertura e fechamento de mercado. Linhas mostram valores dos itens classificados no período e o imposto estimado, que já está incluído nos preços. Descontos e acréscimos podem causar diferenças entre a soma dos itens e o total pago. Ração de gato depende de a descrição identificar o animal; demais produtos pet aparecem separadamente. A classificação é aproximada e merece conferência. As etiquetas à direita e a legenda mostram os valores do último período.

### Como interpretar as análises

O ranking de estabelecimentos conta dias distintos com nota em cada nome de loja, e não confirma visitas físicas; várias notas no mesmo dia contam um dia. Nomes agrupados pelo relatório podem reunir filiais. O ticket é o total dividido pelo número de notas.

Em **Compras em detalhe**, escolha uma categoria e informe o produto na descrição. A lista de marcas pode ser editada, separando os nomes por vírgulas. O programa procura palavras inteiras nas descrições, sem acesso a um campo oficial de marca: abreviações ou marcas ausentes não são reconhecidas, e descrições com mais de uma marca procurada ficam fora do ranking. Confira as descrições exibidas antes de tirar conclusões. O ranking de produtos conta linhas e notas por descrição exata, não unidades comparáveis; embalagens e quantidades podem variar. Os valores de itens são anteriores a descontos e acréscimos da nota.

As visualizações 3D são opcionais. O relatório usa as notas consultadas com sucesso; falhas, NF-e sem detalhamento e compras sem nota não aparecem nos gráficos.

## Privacidade

O processamento é local. As planilhas e os relatórios permanecem no computador do usuário.

As consultas externas utilizam somente os endpoints públicos necessários para consultar NFC-e pelas respectivas chaves de acesso.

## Como executar

```bash
pip install openpyxl requests lxml pyinstaller pillow
npm install

python slt.py
```

Para gerar o executável:

```bash
node build_relatorio.mjs
python gerar_icone.py
python build.py
```

## Dados de demonstração

O repositório permite gerar dados fictícios para testar o relatório sem utilizar notas pessoais:

```bash
python gerar_exemplo.py _demo
```

## Ressalvas

- NF-e modelo 55 pode exigir autenticação e não possui o mesmo nível de consulta pública da NFC-e.
- Tributos apresentados são estimativas quando o dado exato não está disponível publicamente.
- A análise de alimentação descreve produtos comprados, não consumo nutricional individual.

## Autor

**Maicon Nunes** — [@mikerock12](https://github.com/mikerock12)
