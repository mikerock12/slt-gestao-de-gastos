/* Todos os painéis de análise do relatório. */
import {
  D, IB, el, brl, brlCurto, pct, n0, n1, n2, dataCurta, dataDia, mesLongo,
  corPorRank, COR_NOVA, card, barra, leader, tabela, tr, abas, desc,
} from "./util.js";
import { rosca } from "./rosca.js";

const R = D.resumo, A = D.alimentacao, H = D.higiene, M = D.medicamentos;
const SEMANAS = D.meta.dias / 7;
const grupo = (nome) => A.grupos.find((g) => g.nome === nome) || { total: 0, itens: 0, kg: 0, litros: 0 };
const macro = (nome) => A.macro.find((m) => m.nome === nome) || { total: 0, share: 0, itens: 0 };

/* ------------------------------------------------------------- faixa KPI */
export function faixaKpis() {
  const box = el("div", { class: "kpis" });
  box.append(el("div", { class: "kpi hero" }, [
    el("span", { class: "eyebrow", text: "Total gasto no período" }),
    el("div", { class: "v", text: brl(R.totalGeral) }),
    el("span", { class: "legenda n", style: { display: "block", textAlign: "left" },
      text: R.m55Notas
        ? `${brl(R.total)} em ${R.notas} NFC-e detalhadas + ${brl(R.m55Total)} em ${R.m55Notas} NF-e sem detalhe público`
        : `${R.notas} notas fiscais detalhadas` }),
  ]));
  const kpi = (r, v, n) => el("div", { class: "kpi" }, [
    el("span", { class: "eyebrow", text: r }),
    el("div", { class: "v", text: v }),
    el("span", { class: "legenda n", style: { display: "block", textAlign: "left" }, text: n }),
  ]);
  box.append(
    kpi("Por mês", brlCurto(R.mediaMes), `média de ${n1(D.meta.dias / 30.44)} meses`),
    kpi("Por semana", brlCurto(R.mediaSemana), `${D.semanas.length} semanas com compra`),
    kpi("Notas / itens", `${n0(R.notas)} / ${n0(R.itens)}`, `${n0(R.produtosDistintos)} produtos distintos`),
    kpi("Ticket médio", brl(R.ticket), `${brl(R.valorItem)} por item`),
    kpi("Descontos obtidos", brlCurto(R.descontos), `${pct(R.descontoShare)} do valor cheio`),
    kpi("Impostos (estimativa)", brlCurto(R.imposto), `≈ ${pct(R.aliqMedia)} do valor dos produtos`),
  );
  return box;
}

/* ---------------------------------------------------------- mapa geral */
export function mapaConsumo() {
  const dom = D.dominioResumo;
  const total = dom.reduce((a, d) => a + d.total, 0) || 1;
  const DESTINO = {
    alimentacao: "#alimentacao", higiene: "#higiene", limpeza: "#higiene",
    medicamento: "#medicamentos",
  };
  const RESUMO = {
    alimentacao: `${pct(A.ultraShareMedio)} ultraprocessado`,
    higiene: `${H.higieneItens} itens`, limpeza: `${H.limpezaItens} itens`,
    medicamento: `${M.itens} itens`, pet: "ração e cuidados",
    vestuario: "roupa e calçado", combustivel: "abastecimentos",
    casa: "cama, mesa e bazar", outro: "não classificado",
  };

  const faixa = el("div", { class: "pilha", style: { height: "34px" } });
  dom.forEach((d, i) => faixa.append(el("a", {
    href: DESTINO[d.id] || "#categorias",
    title: `${d.nome}: ${brl(d.total)} (${pct(d.share)})`,
    style: { width: `${d.share}%`, background: corPorRank(i, dom.length), display: "block" },
  })));
  const legenda = el("div", { class: "chips", style: { marginTop: "16px" } },
    dom.map((d, i) => el("span", { class: "legenda", style: { display: "inline-flex", alignItems: "center", gap: "6px" } }, [
      el("i", { style: { width: "10px", height: "10px", borderRadius: "2px", background: corPorRank(i, dom.length), display: "inline-block" } }),
      `${d.nome} ${pct(d.share)}`,
    ])));

  const cartoes = el("div", { class: "grade", style: { gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))" } },
    dom.filter((d) => d.id !== "outro").map((d, i) => el("a", {
      href: DESTINO[d.id] || "#categorias",
      class: "card", style: { textDecoration: "none", color: "inherit", padding: "16px" },
    }, [
      el("div", { style: { display: "flex", alignItems: "center", gap: "8px" } }, [
        el("i", { style: { width: "10px", height: "10px", borderRadius: "2px", background: corPorRank(i, dom.length), display: "inline-block" } }),
        el("span", { class: "eyebrow", text: d.nome }),
      ]),
      el("div", { class: "mono", style: { fontSize: "21px", fontWeight: "600", marginTop: "8px" }, text: brl(d.total) }),
      el("div", { class: "legenda", text: `${pct(d.share)} · ${RESUMO[d.id] || ""}` }),
      el("div", { class: "legenda", text: `${brl(d.total / SEMANAS)} por semana` }),
    ])));

  const cesta = [
    ["Gasto total", brl(R.total / SEMANAS)],
    ["Comida e bebida", brl(A.total / SEMANAS)],
    ["— disso, álcool", `${n1(A.litros.alcoolPorSemana)} L`],
    ["— disso, refrigerante", `${n1(A.litros.refriPorSemana)} L`],
    ["Fruta e verdura", `${n1((A.kg.frutas + A.kg.verduras) / SEMANAS)} kg`],
    ["Carne e peixe", `${n1(A.kg.carnesPorSemana)} kg`],
    ["Higiene e limpeza", brl((H.higieneTotal + H.limpezaTotal) / SEMANAS)],
    ["Medicamentos", brl(M.total / SEMANAS)],
    ["Imposto estimado", brl(R.imposto / SEMANAS)],
    ["Notas emitidas", n1(R.notas / SEMANAS)],
  ];
  const gradeCesta = el("div", { class: "grade g2", style: { gap: "6px 34px" } },
    cesta.map(([r, v]) => leader(r, v)));

  return el("div", { class: "grade" }, [
    card("Tudo que a casa consumiu, em uma faixa",
      `${brl(total)} em ${n0(R.itens)} itens`, [faixa, legenda]),
    cartoes,
    card("A cesta de uma semana média",
      `tudo dividido pelas ${n1(SEMANAS)} semanas do período`, [gradeCesta]),
  ]);
}

/* -------------------------------------------------------- alimentação */
export function painelAlimentacao() {
  const alcool = grupo("Bebidas alcoólicas");
  const nova = (() => {
    const g = (n) => A.nova.find((x) => x.n === n) || { total: 0 };
    return {
      real: g(1).total + g(2).total,
      proc: g(3).total - alcool.total,
      ultra: g(4).total,
    };
  })();

  const resumoTopo = el("div", { class: "kpis" }, [
    ["Gasto com comida e bebida", brl(A.total), `${pct((100 * A.total) / R.valorProdutos)} de tudo`],
    ["Comida de verdade", pct(A.qualidadeMedia), "do que é comprado para comer"],
    ["Ultraprocessados", pct(A.ultraShareMedio), "da mesma base"],
    ["Álcool", brl(alcool.total), `${n1(A.litros.alcool)} L no período`],
  ].map(([r, v, n]) => el("div", { class: "kpi" }, [
    el("span", { class: "eyebrow", text: r }),
    el("div", { class: "v", text: v }),
    el("span", { class: "legenda", style: { display: "block" }, text: n }),
  ])));

  const conteudo = el("div", { class: "grade" });
  const painel = el("div", { class: "grade" }, [
    resumoTopo,
    abas([["panorama", "Panorama"], ["grupos", "Grupos alimentares"],
          ["semanas", "Semana a semana"], ["dias", "Dia a dia"]],
         "panorama", (id) => render(id)),
    conteudo,
  ]);

  function render(aba) {
    conteudo.innerHTML = "";
    if (aba === "panorama") conteudo.append(...panorama());
    else if (aba === "grupos") conteudo.append(gruposAlim());
    else if (aba === "semanas") conteudo.append(...semanasAlim());
    else conteudo.append(diasAlim());
  }

  function panorama() {
    const fatiasMacro = A.macro.map((m, i) => ({
      nome: m.nome, valor: m.total, cor: corPorRank(i, A.macro.length),
      nota: `${m.itens} itens`,
    }));
    const fatiasNova = [
      { nome: "Comida de verdade", valor: nova.real, cor: COR_NOVA.real, nota: "NOVA 1 e 2" },
      { nome: "Processado", valor: nova.proc, cor: COR_NOVA.proc, nota: "NOVA 3" },
      { nome: "Ultraprocessado", valor: nova.ultra, cor: COR_NOVA.ultra, nota: "NOVA 4" },
    ];

    const roscas = el("div", { class: "grade g2" }, [
      card("Para onde vai o dinheiro da comida", brl(A.total),
        [rosca(fatiasMacro, { centroRotulo: "Alimentação", centroValor: brl(A.total) })]),
      card("Qualidade do que entra em casa", "sem contar bebida alcoólica", [
        rosca(fatiasNova, { centroRotulo: "Comida", centroValor: brl(A.totalSemAlcool) }),
        el("p", { class: "legenda", style: { marginTop: "16px" }, text:
          "Classificação NOVA, do Guia Alimentar para a População Brasileira. " +
          "“Comida de verdade” reúne o que é in natura ou minimamente processado " +
          "(carne, ovo, arroz, fruta, leite) mais os ingredientes de cozinha (óleo, " +
          "sal, açúcar). Ultraprocessado é o que vem pronto de fábrica: salgadinho, " +
          "refrigerante, congelado, biscoito, molho pronto." }),
      ]),
    ]);

    const fresco = card("Quanto chega de comida fresca", null, [
      el("div", { class: "leaders" }, [
        leader("Frutas", `${n2(A.kg.frutas)} kg`, `${n2(A.kg.frutasPorSemana)}/sem`),
        leader("Verduras e legumes", `${n2(A.kg.verduras)} kg`, `${n2(A.kg.verdurasPorSemana)}/sem`),
        leader("Carnes e peixes", `${n2(A.kg.carnes)} kg`, `${n2(A.kg.carnesPorSemana)}/sem`),
      ]),
      el("p", { class: "legenda", style: { marginTop: "16px" }, text:
        "Só o que foi vendido a quilo entra nesta conta. A OMS recomenda 400 g de " +
        "frutas e hortaliças por pessoa por dia — para duas pessoas seriam cerca de " +
        "5,6 kg por semana." }),
    ]);

    const liquidos = card("Litros que entraram", null, [
      el("div", { class: "leaders" }, [
        leader("Bebida alcoólica", `${n1(A.litros.alcool)} L`, `${n1(A.litros.alcoolPorSemana)}/sem`),
        leader("Refrigerante e energético", `${n1(A.litros.refri)} L`, `${n1(A.litros.refriPorSemana)}/sem`),
        leader("Água, café, chá e suco", `${n1(A.litros.agua)} L`, `${n1(A.litros.agua / SEMANAS)}/sem`),
      ]),
      el("p", { class: "legenda", style: { marginTop: "16px" }, text:
        `Volume lido da embalagem na descrição da nota. ${A.litros.itensSemVolume} dos ` +
        `${A.litros.itensBebida} itens de bebida não traziam o volume, então os totais ` +
        "reais são um pouco maiores." }),
    ]);

    const freq = card("Frequência", null, [
      el("div", { class: "leaders" }, [
        leader("Dias com bebida alcoólica", n0(A.diasComAlcool), `de ${A.diasComAlimento} com comida`),
        leader("Dias com fruta ou verdura", n0(A.diasComFrutaOuVerdura), `de ${A.diasComAlimento}`),
        leader("Itens de alimentação", n0(A.itens), "no período"),
      ]),
      el("p", { class: "legenda", style: { marginTop: "16px" }, text:
        `Em ${pct((100 * A.diasComAlcool) / (A.diasComAlimento || 1))} dos dias em que se ` +
        "comprou comida também se comprou bebida alcoólica. Fruta ou verdura apareceu em " +
        `${pct((100 * A.diasComFrutaOuVerdura) / (A.diasComAlimento || 1))}.` }),
    ]);

    const frutasVerduras = grupo("Frutas").total + grupo("Verduras e legumes").total;
    const obs = [
      ["O álcool é o maior item da mesa",
       `${brl(alcool.total)} — ${pct((100 * alcool.total) / (A.total || 1))} de tudo que se gasta com comida e bebida. São ${n1(A.litros.alcool)} litros, cerca de ${n1(A.litros.alcoolPorSemana)} L por semana.`,
       "alerta", alcool.total / (A.total || 1) > 0.15],
      ["Ultraprocessado domina a comida do dia a dia",
       `Tirando a bebida alcoólica, ${pct(A.ultraShareMedio)} do gasto com comida vai para produto pronto de fábrica, contra ${pct(A.qualidadeMedia)} de comida de verdade. O Guia Alimentar recomenda o inverso: a base deve ser in natura e minimamente processada.`,
       "alerta", A.ultraShareMedio > A.qualidadeMedia],
      ["A base da alimentação é comida de verdade",
       `${pct(A.qualidadeMedia)} do gasto com comida é in natura ou minimamente processado, contra ${pct(A.ultraShareMedio)} de ultraprocessado. É exatamente o que o Guia Alimentar recomenda.`,
       "bom", A.qualidadeMedia >= A.ultraShareMedio],
      ["Fruta e verdura são o ponto mais fraco",
       `Juntas somam ${brl(frutasVerduras)} no período — ${pct((100 * frutasVerduras) / (A.total || 1))} do gasto alimentar. Em quilo dá ${n2(A.kg.frutas + A.kg.verduras)} kg, ou ${n2((A.kg.frutas + A.kg.verduras) / SEMANAS)} kg por semana.`,
       "alerta", (100 * frutasVerduras) / (A.total || 1) < 6],
      ["A proteína está bem servida",
       `Carnes, ovos e laticínios somam ${brl(macro("Proteínas").total)}, ${pct(macro("Proteínas").share)} do gasto alimentar, com ${n2(A.kg.carnes)} kg de carne e peixe comprados a quilo.`,
       "bom", macro("Proteínas").share > 10],
      ["Refrigerante entra com frequência",
       `${n1(A.litros.refri)} litros no período, ${n1(A.litros.refriPorSemana)} L por semana, ${brl(grupo("Refrigerantes e energéticos").total)} no total.`,
       "alerta", A.litros.refri > 40],
      ["Molho e tempero pesam mais do que parece",
       `${brl(grupo("Molhos, temperos e condimentos").total)} em maionese, catchup, molho pronto e temperos. Quase tudo é ultraprocessado.`,
       "atencao", grupo("Molhos, temperos e condimentos").total > 200],
    ].filter(([, , , mostra]) => mostra);

    const caixaObs = card("O que os números estão dizendo", null, [
      el("div", { class: "obs" }, obs.map(([t, d, tom]) =>
        el("div", { class: tom === "bom" ? "" : tom }, [
          el("h4", { text: t }), el("p", { text: d }),
        ]))),
    ]);

    return [roscas, el("div", { class: "grade g3" }, [fresco, liquidos, freq]), caixaObs];
  }

  function gruposAlim() {
    const ordenados = [...A.grupos].sort((a, b) => b.total - a.total);
    const max = ordenados[0] ? ordenados[0].total : 1;
    const detalhe = card("Escolha um grupo", null, [
      el("p", { class: "dim", style: { padding: "24px 0", textAlign: "center", fontSize: "14px" },
        text: "Clique numa barra ao lado para ver os produtos daquele grupo." }),
    ]);

    const mostra = (g) => {
      detalhe.innerHTML = "";
      detalhe.append(el("div", { class: "cardtitle" }, [
        el("span", { class: "t", text: `Dentro de ${g.nome.toLowerCase()}` }),
      ]));
      detalhe.append(el("div", { class: "chips", style: { marginBottom: "14px" } }, [
        el("span", { class: "mono", style: { fontSize: "18px", fontWeight: "600", color: "var(--mate)" }, text: brl(g.total) }),
        el("span", { class: "legenda", text: `${g.itens} itens` }),
        g.kg > 0 ? el("span", { class: "legenda", text: `${n2(g.kg)} kg` }) : null,
        g.litros > 0 ? el("span", { class: "legenda", text: `${n1(g.litros)} L` }) : null,
        el("span", { class: "legenda", text: `grupo: ${g.macro}` }),
      ]));
      const lista = el("div", { class: "leaders" });
      (A.topPorGrupo[g.nome] || []).forEach((p) =>
        lista.append(leader(p.desc, brl(p.total), `${p.vezes}×`)));
      detalhe.append(lista);
    };

    const barras = el("div", { class: "barras" },
      ordenados.map((g) => barra({
        nome: g.nome, sub: `${g.itens} itens`, valor: g.total, max,
        extra: pct(g.share), onClick: () => mostra(g),
      })));

    return el("div", { class: "grade g21" }, [
      card("Todos os grupos alimentares", "clique para ver os produtos", [barras]),
      el("div", { class: "grade" }, [
        detalhe,
        card("Leitura macro", "os grupos pedidos, mais o resto", [
          tabela([{ t: "Grupo" }, { t: "Itens", n: 1 }, { t: "Gasto", n: 1 }, { t: "Fatia", n: 1 }],
            A.macro.map((m) => tr([m.nome, { v: m.itens, n: 1, dim: 1 },
              { v: brl(m.total), n: 1 }, { v: pct(m.share), n: 1 }]))),
        ]),
      ]),
    ]);
  }

  function semanasAlim() {
    const semanas = A.semanas.filter((s) => s.semAlcool >= 40);
    const linhas = semanas.map((s) => {
      const base = s.semAlcool || 1;
      const p = (v) => `${(100 * v) / base}%`;
      const pior = A.piorSemana && A.piorSemana.i === s.i;
      const melhor = A.melhorSemana && A.melhorSemana.i === s.i;
      return el("div", {
        style: { display: "grid", gridTemplateColumns: "62px minmax(0,1fr) 54px",
                 alignItems: "center", gap: "10px" },
        title: `${dataCurta(s.ini)} a ${dataCurta(s.fim)} — ${pct(s.qualidade)} comida de verdade`,
      }, [
        el("span", { class: "legenda", text: dataCurta(s.ini) }),
        el("span", { class: "pilha" }, [
          el("span", { style: { width: p(s.nova1 + s.nova2), background: COR_NOVA.real } }),
          el("span", { style: { width: p(s.nova3), background: COR_NOVA.proc } }),
          el("span", { style: { width: p(s.nova4), background: COR_NOVA.ultra } }),
        ]),
        el("span", { class: "mono", style: { fontSize: "12.5px", textAlign: "right",
          color: melhor ? COR_NOVA.real : pior ? COR_NOVA.ultra : "inherit" }, text: pct(s.qualidade) }),
      ]);
    });

    const legenda = el("div", { class: "chips", style: { marginTop: "16px" } },
      [["Comida de verdade", COR_NOVA.real], ["Processado", COR_NOVA.proc],
       ["Ultraprocessado", COR_NOVA.ultra]].map(([n, c]) =>
        el("span", { class: "legenda", style: { display: "inline-flex", alignItems: "center", gap: "6px" } }, [
          el("i", { style: { width: "10px", height: "10px", borderRadius: "2px", background: c, display: "inline-block" } }), n,
        ])));

    const cartoesExtremos = [A.piorSemana, A.melhorSemana].filter(Boolean).map((s, k) =>
      card(k === 0 ? "A semana menos nutritiva" : "A semana mais nutritiva",
        `${dataCurta(s.ini)} a ${dataCurta(s.fim)}`, [
        el("div", { class: "chips", style: { marginBottom: "14px", alignItems: "baseline" } }, [
          el("span", { class: "mono", style: { fontSize: "28px", fontWeight: "600",
            color: k === 0 ? COR_NOVA.ultra : COR_NOVA.real }, text: pct(s.qualidade) }),
          el("span", { class: "legenda", text: "comida de verdade" }),
          el("span", { class: "legenda", text: `${pct(s.ultraShare)} ultraprocessado` }),
        ]),
        tabela([{ t: "Grupo" }, { t: "Gasto", n: 1 }],
          [["Proteínas", s.proteinas], ["Frutas", s.frutas], ["Verduras e legumes", s.verduras],
           ["Cereais e grãos", s.cereais], ["Carboidratos", s.carboidratos],
           ["Ultraprocessados e doces", s.ultra], ["Refrigerantes", s.refri],
           ["Bebidas alcoólicas", s.alcool]].map(([n, v]) =>
            tr([{ v: n, dim: v === 0 }, { v: v > 0 ? brl(v) : "—", n: 1, dim: v === 0 }]))),
        el("p", { class: "legenda", style: { marginTop: "12px" }, text: k === 0
          ? `${s.frutas === 0 && s.verduras === 0 ? "Nenhuma fruta e nenhuma verdura na semana inteira. " : ""}Dos ${brl(s.semAlcool)} gastos em comida, ${brl(s.nova4)} foram para produto ultraprocessado.`
          : `A semana com mais comida fresca do período: ${brl(s.nova1 + s.nova2)} de um total de ${brl(s.semAlcool)} em alimentos.` }),
      ]));

    const tabelaMeses = card("Mês a mês", "qualidade e composição", [
      tabela([{ t: "Mês" }, { t: "Comida de verdade", n: 1 }, { t: "Ultra", n: 1 },
              { t: "Frutas+verduras", n: 1 }, { t: "Álcool", n: 1 }, { t: "Total", n: 1 }],
        A.meses.map((m) => tr([
          mesLongo(`${m.mes}-01`),
          { v: pct(m.qualidade), n: 1 }, { v: pct(m.ultraShare), n: 1 },
          { v: brl(m.frutas + m.verduras), n: 1, dim: 1 },
          { v: brl(m.alcool), n: 1, dim: 1 }, { v: brl(m.total), n: 1 },
        ]))),
    ]);

    return [
      card("Quanto de cada semana foi comida de verdade",
        "barra cheia = 100% do gasto alimentar da semana, sem álcool",
        [el("div", { class: "grade", style: { gap: "6px" } }, linhas), legenda]),
      el("div", { class: "grade g2" }, cartoesExtremos),
      tabelaMeses,
    ];
  }

  function diasAlim() {
    const max = Math.max(...A.dias.map((d) => d.total), 1);
    const linhas = A.dias.map((d) => {
      const w = (v) => `${(100 * v) / max}%`;
      const outros = Math.max(0, d.total - d.real - d.ultra - d.alcool);
      return el("div", {
        style: { display: "grid", gridTemplateColumns: "58px minmax(0,1fr) 74px",
                 alignItems: "center", gap: "10px" },
        title: `${dataDia(d.data)} — ${brl(d.total)} em ${d.itens} itens`,
      }, [
        el("span", { class: "legenda", text: dataDia(d.data) }),
        el("span", { class: "pilha", style: { height: "12px" } }, [
          el("span", { style: { width: w(d.real), background: COR_NOVA.real } }),
          el("span", { style: { width: w(outros), background: COR_NOVA.proc } }),
          el("span", { style: { width: w(d.ultra), background: COR_NOVA.ultra } }),
          el("span", { style: { width: w(d.alcool), background: "#7a5c8f" } }),
        ]),
        el("span", { class: "mono", style: { fontSize: "11.5px", textAlign: "right" }, text: brl(d.total) }),
      ]);
    });
    const legenda = el("div", { class: "chips", style: { marginTop: "16px" } },
      [["Comida de verdade", COR_NOVA.real], ["Processado", COR_NOVA.proc],
       ["Ultraprocessado", COR_NOVA.ultra], ["Bebida alcoólica", "#7a5c8f"]].map(([n, c]) =>
        el("span", { class: "legenda", style: { display: "inline-flex", alignItems: "center", gap: "6px" } }, [
          el("i", { style: { width: "10px", height: "10px", borderRadius: "2px", background: c, display: "inline-block" } }), n,
        ])));
    return card("O que se comprou de comida, dia a dia",
      `${A.dias.length} dias com compra de alimento`,
      [el("div", { class: "grade", style: { gap: "4px" } }, linhas), legenda,
       el("p", { class: "legenda", style: { marginTop: "12px" }, text:
         "A largura da barra é o gasto do dia em relação ao maior dia do período. " +
         "Para ver a nota inteira, use o calendário 3D no topo da página." })]);
  }

  render("panorama");
  return painel;
}

/* -------------------------------------------------- higiene e limpeza */
export function painelHigiene() {
  const total = H.higieneTotal + H.limpezaTotal;
  const meses = D.meses.map((m) => ({
    curto: m.curto,
    higiene: (H.mesHigiene.find((x) => x.mes === m.mes) || {}).total || 0,
    limpeza: (H.mesLimpeza.find((x) => x.mes === m.mes) || {}).total || 0,
  }));
  const maxMes = Math.max(...meses.map((m) => m.higiene + m.limpeza), 1);

  const topo = el("div", { class: "kpis" }, [
    ["Higiene pessoal", brl(H.higieneTotal), `${H.higieneItens} itens`],
    ["Limpeza da casa", brl(H.limpezaTotal), `${H.limpezaItens} itens`],
    ["Somados", brl(total), `${pct((100 * total) / R.valorProdutos)} de tudo`],
    ["Por mês", brl(total / (D.meta.dias / 30.44)), "média do período"],
  ].map(([r, v, n]) => el("div", { class: "kpi" }, [
    el("span", { class: "eyebrow", text: r }),
    el("div", { class: "v", text: v }),
    el("span", { class: "legenda", style: { display: "block" }, text: n }),
  ])));

  const conteudo = el("div", { class: "grade" });
  function render(aba) {
    conteudo.innerHTML = "";
    if (aba === "recorrencia") { conteudo.append(...recorrencia()); return; }
    const eh = aba === "higiene";
    const sub = eh ? H.subHigiene : H.subLimpeza;
    const top = eh ? H.topHigiene : H.topLimpeza;
    const val = eh ? H.higieneTotal : H.limpezaTotal;
    conteudo.append(
      el("div", { class: "grade g2" }, [
        card(eh ? "Higiene pessoal por tipo" : "Limpeza da casa por tipo", brl(val),
          [rosca(sub.map((s, i) => ({ nome: s.nome, valor: s.total,
            cor: corPorRank(i, sub.length), nota: `${s.itens} itens` })),
            { centroRotulo: eh ? "Higiene" : "Limpeza", centroValor: brl(val) })]),
        card("Os produtos que mais pesaram", null,
          [el("div", { class: "leaders" }, top.map((p) => leader(p.desc, brl(p.total))))]),
      ]),
      el("div", { class: "grade g21" }, [
        card("Mês a mês", "higiene e limpeza empilhados", [
          el("div", { class: "colunas", style: { height: "180px", paddingTop: "24px" } },
            meses.map((m) => el("div", { class: "col",
              title: `${m.curto}: higiene ${brl(m.higiene)} · limpeza ${brl(m.limpeza)}` }, [
              el("span", { class: "v", text: n0(m.higiene + m.limpeza) }),
              el("i", { style: { height: `${(100 * m.limpeza) / maxMes}%`, background: "var(--plum)" } }),
              el("i", { style: { height: `${(100 * m.higiene) / maxMes}%`, borderRadius: "0" } }),
            ]))),
          el("div", { class: "eixo-x" }, meses.map((m) => el("span", { class: "legenda", text: m.curto }))),
          el("div", { class: "chips", style: { marginTop: "14px" } },
            [["Higiene pessoal", "var(--mate)"], ["Limpeza da casa", "var(--plum)"]].map(([n, c]) =>
              el("span", { class: "legenda", style: { display: "inline-flex", alignItems: "center", gap: "6px" } }, [
                el("i", { style: { width: "10px", height: "10px", borderRadius: "2px", background: c, display: "inline-block" } }), n,
              ]))),
        ]),
        card("Detalhe por tipo", "valor e número de itens", [
          tabela([{ t: "Tipo" }, { t: "Itens", n: 1 }, { t: "Gasto", n: 1 }, { t: "Fatia", n: 1 }],
            sub.map((s) => tr([s.nome, { v: s.itens, n: 1, dim: 1 },
              { v: brl(s.total), n: 1 }, { v: pct(s.share), n: 1 }]))),
        ]),
      ]),
    );
  }

  function recorrencia() {
    if (!H.essenciais.length) {
      return [card("De quanto em quanto tempo", null, [
        el("p", { class: "dim", style: { padding: "20px 0", textAlign: "center", fontSize: "14px" },
          text: "Ainda não há compras repetidas suficientes para medir o intervalo de reposição." })])];
    }
    const max = Math.max(...H.essenciais.map((e) => e.intervaloMedio));
    const barras = el("div", { class: "barras" }, H.essenciais.map((e) => barra({
      nome: e.nome, sub: e.area, valor: e.intervaloMedio, max,
      texto: `${n1(e.intervaloMedio)} dias`, extra: `${e.compras}×`,
      alt: e.area === "Limpeza",
    })));
    return [
      card("De quanto em quanto tempo cada essencial é reposto",
        "intervalo médio entre compras", [barras,
        el("p", { class: "legenda", style: { marginTop: "16px" }, text:
          "Quanto menor a barra, mais rápido o produto acaba. O número à direita é " +
          "quantas vezes ele foi comprado no período." })]),
      card("Tabela completa", null, [
        tabela([{ t: "Produto" }, { t: "Área" }, { t: "Compras", n: 1 },
                { t: "Intervalo", n: 1 }, { t: "Última", n: 1 }, { t: "Gasto", n: 1 }],
          H.essenciais.map((e) => tr([e.nome, { v: e.area, dim: 1 },
            { v: e.compras, n: 1, dim: 1 }, { v: `${n1(e.intervaloMedio)} d`, n: 1 },
            { v: dataDia(e.ultimo), n: 1, dim: 1 }, { v: brl(e.total), n: 1 }]))),
      ]),
    ];
  }

  const painel = el("div", { class: "grade" }, [
    topo,
    abas([["higiene", "Higiene pessoal"], ["limpeza", "Limpeza da casa"],
          ["recorrencia", "De quanto em quanto tempo"]], "higiene", render),
    conteudo,
  ]);
  render("higiene");
  return painel;
}

/* ------------------------------------------------------- medicamentos */
export function painelMedicamentos() {
  if (!M.itens) {
    return card("Medicamentos", null, [
      el("p", { class: "dim", style: { padding: "22px 0", textAlign: "center", fontSize: "14px" },
        text: "Nenhum medicamento identificado nas notas do período." })]);
  }
  const CORES = {
    "sem receita": "#35a87a", "receita simples": "#a678c8",
    "receita obrigatória": "#d4614c", "receita controlada": "#d4614c",
    "não classificado": "#78837c",
  };
  const porReceita = new Map();
  for (const c of M.classes) {
    const a = porReceita.get(c.receita) || { total: 0, itens: 0 };
    a.total += c.total; a.itens += c.itens;
    porReceita.set(c.receita, a);
  }
  const maxMes = Math.max(...M.porMes.map((m) => m.total), 1);
  const meses = D.meses.map((m) => ({
    curto: m.curto,
    total: (M.porMes.find((x) => x.mes === m.mes) || {}).total || 0,
    itens: (M.porMes.find((x) => x.mes === m.mes) || {}).itens || 0,
  }));
  const controlados = M.classes.filter((c) => c.receita === "receita controlada");
  const semReceita = M.classes.filter((c) => c.receita === "sem receita");

  const topo = el("div", { class: "kpis" }, [
    ["Gasto com medicamento", brl(M.total), `${M.itens} itens no período`],
    ["Por mês", brl(M.gastoMensal), "média do período"],
    ["Dias com compra", n0(M.diasComCompra), `de ${R.diasComCompra} dias com compra`],
    ["Fatia do orçamento", pct((100 * M.total) / R.valorProdutos), "de tudo que passou pelo caixa"],
  ].map(([r, v, n]) => el("div", { class: "kpi" }, [
    el("span", { class: "eyebrow", text: r }),
    el("div", { class: "v", text: v }),
    el("span", { class: "legenda", style: { display: "block" }, text: n }),
  ])));

  const obs = [
    ["Farmácia é uma despesa pequena e espaçada",
     `${brl(M.total)} no período inteiro, ${pct((100 * M.total) / R.valorProdutos)} do orçamento — cerca de ${brl(M.gastoMensal)} por mês, com compra em apenas ${M.diasComCompra} dias.`, "bom"],
    controlados.length ? ["Uso contínuo na conta",
     `Receita controlada — ${controlados.map((c) => c.nome.toLowerCase()).join(" e ")} — soma ${brl(controlados.reduce((a, c) => a + c.total, 0))}, ${pct((100 * controlados.reduce((a, c) => a + c.total, 0)) / M.total)} do total. A maior classe isolada é ${M.classes[0].nome.toLowerCase()}, com ${brl(M.classes[0].total)}.`, "atencao"] : null,
    semReceita.length ? ["Remédio sem receita aparece pouco",
     `${semReceita.reduce((a, c) => a + c.itens, 0)} itens sem exigência de receita, ${brl(semReceita.reduce((a, c) => a + c.total, 0))} no total. Não há indício de automedicação frequente na base.`, "bom"] : null,
    M.shareForaFarmacia > 50 ? ["Quase tudo foi comprado fora da farmácia",
     `${pct(M.shareForaFarmacia)} do valor saiu de mercado, não de drogaria — só ${brl(M.emFarmacia)} em farmácia de fato. Vale conferir preço: drogaria costuma ter genérico e programa de desconto que o mercado não oferece.`, "atencao"] : null,
  ].filter(Boolean);

  return el("div", { class: "grade" }, [
    topo,
    el("div", { class: "grade g2" }, [
      card("Para que serve o que se compra", brl(M.total), [
        rosca(M.classes.map((c, i) => ({ nome: c.nome, valor: c.total,
          cor: corPorRank(i, M.classes.length), nota: `${c.itens} ${c.itens > 1 ? "itens" : "item"}` })),
          { centroRotulo: "Medicamentos", centroValor: brl(M.total) }),
      ]),
      el("div", { class: "grade" }, [
        card("Exigência de receita", null, [
          el("div", { class: "barras" }, [...porReceita.entries()]
            .sort((a, b) => b[1].total - a[1].total)
            .map(([r, a]) => el("div", { class: "barra" }, [
              el("span", { class: "nome" }, [r, el("small", { text: `${a.itens} itens` })]),
              el("span", { class: "trilha" }, [el("i", {
                style: { width: `${(100 * a.total) / M.total}%`, background: CORES[r] || "#78837c" } })]),
              el("span", { class: "val", text: brl(a.total) }),
            ]))),
          el("p", { class: "legenda", style: { marginTop: "16px" }, text:
            "A classificação vem do princípio ativo lido na descrição da nota. Serve para " +
            "dar panorama do consumo, não substitui a orientação de médico ou farmacêutico." }),
        ]),
        card("Mês a mês", "gasto com farmácia", [
          el("div", { class: "colunas", style: { height: "110px", paddingTop: "22px" } },
            meses.map((m) => el("div", { class: "col", title: `${m.curto}: ${brl(m.total)} em ${m.itens} itens` }, [
              m.total > 0 ? el("span", { class: "v", text: n0(m.total) }) : null,
              el("i", { style: { height: `${Math.max(0.8, (100 * m.total) / maxMes)}%` } }),
            ]))),
          el("div", { class: "eixo-x" }, meses.map((m) => el("span", { class: "legenda", text: m.curto }))),
        ]),
      ]),
    ]),
    card("Tudo que foi comprado, em ordem", `${M.itens} itens`, [
      tabela([{ t: "Data" }, { t: "Medicamento" }, { t: "Classe" }, { t: "Receita" },
              { t: "Onde" }, { t: "Valor", n: 1 }],
        M.linha.map((l) => tr([
          { v: dataDia(l.data), n: 1, dim: 1 }, l.desc, { v: l.classe, dim: 1 },
          el("span", { class: "pill", style: { color: CORES[l.receita] || "#78837c",
            background: `${CORES[l.receita] || "#78837c"}1f` }, text: l.receita }),
          { v: l.loja, dim: 1 }, { v: brl(l.valor), n: 1 },
        ]))),
    ]),
    card("O que dá para ler nisso", null, [
      el("div", { class: "obs" }, obs.map(([t, d, tom]) =>
        el("div", { class: tom === "bom" ? "" : tom }, [el("h4", { text: t }), el("p", { text: d })]))),
    ]),
  ]);
}
