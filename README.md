# SLT — Gestão de Gastos

Aplicação que transforma planilhas exportadas do **Nota Fiscal Gaúcha** em um relatório navegável de consumo.

O programa lê as chaves das notas, consulta os dados públicos disponíveis da NFC-e, organiza os itens e gera um relatório HTML autossuficiente.

![Windows](https://img.shields.io/badge/Windows-10%2F11-informational)
![Python](https://img.shields.io/badge/Python-3.11%2B-informational)

## O que o projeto faz

- importa uma ou mais planilhas XLSX;
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
