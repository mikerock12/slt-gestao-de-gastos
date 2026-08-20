/* Painéis de gasto: ritmo, pessoas, lojas, categorias, preços, impostos,
   extremos e o explorador das notas. */
import {
  D, IB, el, brl, brlCurto, pct, n0, n1, n2, dataCurta, dataDia, mesLongo,
  diaParaISO, corPorRank, card, barra, leader, tabela, tr, abas,
} from "./util.js";

const R = D.resumo;

/* ------------------------------------------------------------- ritmo */
export function painelRitmo() {
  const meses = D.meses;
  const pessoas = D.pessoasNomes;
  let quem = -1;   // -1 = todos

  const valorDe = (m) => (quem < 0 ? m.total : m[`p${quem}`] || 0);

  const grafico = el("div", { class: "colunas", style: { height: "220px", paddingTop: "26px" } });
  const eixo = el("div", { class: "eixo-x" }, meses.map((m) => el("span", { class: "legenda", text: m.curto })));
  const rodape = el("div", { style: { marginTop: "18px", borderTop: "1px solid var(--rule)", paddingTop: "14px" } });

  function desenha() {
    const max = Math.max(...meses.map(valorDe), 1);
    grafico.innerHTML = "";
    meses.forEach((m) => {
      const v = valorDe(m);
      const col = el("div", { class: "col" }, [
        el("span", { class: "v", text: brlCurto(v) }),
        el("i", { style: { height: `${Math.max(0.8, (100 * v) / max)}%` } }),
      ]);
      col.addEventListener("mouseenter", () => detalhe(m));
      col.addEventListener("mouseleave", () => detalhe(null));
      grafico.append(col);
    });
    detalhe(null);
  }
  function detalhe(m) {
    rodape.innerHTML = "";
    if (!m) {
      rodape.append(el("p", { class: "legenda", text: "passe o cursor sobre um mês para ver o detalhe" }));
      return;
    }
    rodape.append(el("div", { class: "chips", style: { alignItems: "baseline" } }, [
      el("span", { style: { fontFamily: "var(--serif)", fontSize: "18px", fontWeight: "600" }, text: m.label }),
      el("span", { class: "legenda", text: `${m.notas} notas` }),
      el("span", { class: "legenda", text: `${m.itens} itens` }),
      el("span", { class: "legenda", text: `ticket ${brl(m.ticket)}` }),
      el("span", { class: "legenda", text: `${m.diasCompra} dias com compra` }),
    ]));
  }

  const filtros = el("div", { class: "chips", style: { marginBottom: "18px" } });
  const opcoes = [[-1, pessoas.length > 1 ? "Todos" : pessoas[0]]]
    .concat(pessoas.length > 1 ? pessoas.map((p, i) => [i, p]) : []);
  const botoes = opcoes.map(([id, rot]) => el("button", {
    class: "aba", "aria-pressed": id === quem,
    onclick: () => {
      quem = id;
      botoes.forEach((b, i) => b.setAttribute("aria-pressed", opcoes[i][0] === id));
      desenha();
    },
  }, [rot]));
  botoes.forEach((b) => filtros.append(b));

  /* --------- semanal --------- */
  const sem = D.semanas;
  const maxSem = Math.max(...sem.map((s) => s.total), 1);
  const ordenadas = [...sem].sort((a, b) => a.total - b.total);
  const mediana = ordenadas.length % 2
    ? ordenadas[(ordenadas.length - 1) / 2].total
    : (ordenadas[ordenadas.length / 2 - 1].total + ordenadas[ordenadas.length / 2].total) / 2;

  const W = 900, Hh = 190, pad = 8;
  const x = (i) => pad + (i * (W - 2 * pad)) / Math.max(1, sem.length - 1);
  const y = (v) => Hh - 12 - ((Hh - 26) * v) / (maxSem * 1.08);
  const linha = sem.map((s, i) => `${i ? "L" : "M"}${x(i).toFixed(1)} ${y(s.total).toFixed(1)}`).join(" ");
  const area = `${linha} L${x(sem.length - 1).toFixed(1)} ${Hh - 12} L${x(0).toFixed(1)} ${Hh - 12} Z`;

  const svgSem = el("div", {
    html: `<svg viewBox="0 0 ${W} ${Hh}" preserveAspectRatio="none" role="img"
      aria-label="Gasto semanal" style="width:100%;height:190px;overflow:visible">
      <defs><linearGradient id="gsem" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#35a87a" stop-opacity=".34"/>
        <stop offset="100%" stop-color="#35a87a" stop-opacity="0"/></linearGradient></defs>
      <line x1="0" y1="${y(mediana)}" x2="${W}" y2="${y(mediana)}" stroke="#3a423a"
        stroke-width="1" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>
      <path d="${area}" fill="url(#gsem)"/>
      <path d="${linha}" fill="none" stroke="#35a87a" stroke-width="2" stroke-linejoin="round"
        stroke-linecap="round" vector-effect="non-scaling-stroke"/>
      <circle id="ptSem" r="4" fill="#35a87a" stroke="#0e100e" stroke-width="2" opacity="0"/>
    </svg>`,
  });
  const infoSem = el("p", { class: "legenda", style: { marginTop: "12px" },
    text: "passe o cursor sobre o gráfico" });
  const svgEl = svgSem.querySelector("svg");
  svgEl.addEventListener("mousemove", (ev) => {
    const r = svgEl.getBoundingClientRect();
    let i = Math.round((((ev.clientX - r.left) / r.width) * W - pad) / ((W - 2 * pad) / Math.max(1, sem.length - 1)));
    i = Math.max(0, Math.min(sem.length - 1, i));
    const s = sem[i];
    const pt = svgEl.querySelector("#ptSem");
    pt.setAttribute("cx", x(i));
    pt.setAttribute("cy", y(s.total));
    pt.setAttribute("opacity", "1");
    infoSem.innerHTML = "";
    infoSem.append(el("span", { class: "mono", style: { color: "var(--mate)" }, text: brl(s.total) }),
      ` · ${dataCurta(s.ini)} a ${dataCurta(s.fim)} · ${s.notas} notas · ${n0(s.itens)} itens`);
  });
  svgEl.addEventListener("mouseleave", () => {
    svgEl.querySelector("#ptSem").setAttribute("opacity", "0");
    infoSem.textContent = "passe o cursor sobre o gráfico";
  });

  desenha();
  return el("div", { class: "grade" }, [
    card("Gasto por mês", `${brl(R.total)} no período`, [filtros, grafico, eixo, rodape]),
    card("Gasto por semana", `${sem.length} semanas · mediana ${brl(mediana)}`, [svgSem, infoSem]),
  ]);
}

/* ----------------------------------------------------------- pessoas */
export function painelPessoas() {
  const linhas = D.pessoas.map((p) => tr([
    el("strong", { text: p.nome }),
    { v: p.cpf, dim: 1 }, { v: p.notas, n: 1 }, { v: p.itens, n: 1 },
    { v: brl(p.total), n: 1 }, { v: brl(p.ticket), n: 1 },
    { v: pct(p.share), n: 1 }, { v: brl(p.imposto), n: 1, dim: 1 },
  ]));
  if (D.pessoas.length > 1) {
    linhas.push(tr([{ v: "Família", dim: 1 }, { v: "", dim: 1 },
      { v: R.notas, n: 1, dim: 1 }, { v: R.itens, n: 1, dim: 1 },
      { v: brl(R.total), n: 1, dim: 1 }, { v: brl(R.ticket), n: 1, dim: 1 },
      { v: "100,0%", n: 1, dim: 1 }, { v: brl(R.imposto), n: 1, dim: 1 }]));
  }
  return card(null, null, [tabela(
    [{ t: "Titular" }, { t: "CPF" }, { t: "Notas", n: 1 }, { t: "Itens", n: 1 },
     { t: "Total", n: 1 }, { t: "Ticket médio", n: 1 }, { t: "% do total", n: 1 },
     { t: "Imposto est.", n: 1 }], linhas)]);
}

/* ------------------------------------------------------------- lojas */
export function painelLojas() {
  const topo = D.lojas.slice(0, 14);
  const resto = D.lojas.slice(14);
  const somaResto = resto.reduce((a, l) => a + l.total, 0);
  const max = topo[0] ? topo[0].total : 1;

  const detalhe = card("Por tipo de estabelecimento", null, [
    el("div", { class: "barras" }, D.catLoja.map((c) => barra({
      nome: c.nome, sub: `${c.notas}×`, valor: c.total,
      max: D.catLoja[0].total, extra: pct(c.share),
    }))),
  ]);

  const mostra = (l) => {
    detalhe.innerHTML = "";
    detalhe.append(el("div", { class: "cardtitle" }, [el("span", { class: "t", text: "Detalhe da loja" })]));
    detalhe.append(el("h4", { style: { fontSize: "19px" }, text: l.nome }));
    detalhe.append(el("p", { class: "legenda", text: l.razao }));
    detalhe.append(el("div", { class: "grade g2", style: { marginTop: "16px", gap: "10px 20px" } },
      [["Gasto total", brl(l.total)], ["Notas", n0(l.notas)], ["Itens", n0(l.itens)],
       ["Ticket médio", brl(l.ticket)], ["Imposto est.", brl(l.imposto)],
       ["% do total", pct(l.share)]].map(([r, v]) => el("div", {}, [
        el("div", { class: "eyebrow", text: r }),
        el("div", { class: "mono", style: { fontSize: "15px", fontWeight: "600", marginTop: "2px" }, text: v }),
      ]))));
  };

  const barras = el("div", { class: "barras" }, [
    ...topo.map((l) => barra({
      nome: l.nome, sub: `${l.notas}×`, valor: l.total, max, extra: pct(l.share),
      onClick: () => mostra(l),
    })),
    resto.length ? el("div", { style: { opacity: .55 } },
      [barra({ nome: `outros ${resto.length} estabelecimentos`, valor: somaResto, max })]) : null,
  ]);

  const menos = card("Onde menos se comprou", "uma ou duas visitas", [
    tabela([{ t: "Loja" }, { t: "Visitas", n: 1 }, { t: "Total", n: 1 }],
      D.lojas.slice(-8).reverse().map((l) =>
        tr([l.nome, { v: l.notas, n: 1, dim: 1 }, { v: brl(l.total), n: 1 }]))),
  ]);

  return el("div", { class: "grade g21" }, [
    card("Onde mais se comprou", "clique para ver o detalhe", [barras]),
    el("div", { class: "grade" }, [detalhe, menos]),
  ]);
}

/* -------------------------------------------------------- categorias */
export function painelCategorias() {
  let modo = "valor";
  const barras = el("div", { class: "barras" });
  function desenha() {
    const cats = [...D.categorias].sort((a, b) =>
      modo === "valor" ? b.total - a.total : b.itens - a.itens);
    const max = Math.max(...cats.map((c) => (modo === "valor" ? c.total : c.itens)), 1);
    barras.innerHTML = "";
    cats.forEach((c) => barras.append(barra({
      nome: c.nome, sub: modo === "valor" ? `${c.itens} itens` : null,
      valor: modo === "valor" ? c.total : c.itens, max,
      texto: modo === "valor" ? brl(c.total) : String(c.itens),
      extra: modo === "valor" ? pct(c.share) : null,
    })));
  }
  desenha();

  return el("div", { class: "grade g21" }, [
    card("Gasto por categoria de produto", null, [
      abas([["valor", "Por valor"], ["itens", "Por nº de itens"]], "valor",
        (id) => { modo = id; desenha(); }),
      el("div", { style: { height: "18px" } }),
      barras,
    ]),
    el("div", { class: "grade" }, [
      card("Comprados mais vezes", "nº de notas", [
        el("div", { class: "leaders" }, D.produtosFreq.slice(0, 12).map((p) =>
          leader(p.desc, `${p.vezes}×`, brl(p.total)))),
      ]),
      card("Onde mais foi dinheiro", "R$ somados no período", [
        el("div", { class: "leaders" }, D.produtosValor.slice(0, 12).map((p) =>
          leader(p.desc, brl(p.total), `${p.vezes}×`))),
      ]),
    ]),
  ]);
}

/* ------------------------------------------------------------ preços */
export function painelPrecos() {
  if (!D.precoSubiu.length && !D.precoCaiu.length) {
    return card("Variação de preço", null, [
      el("p", { class: "dim", style: { padding: "22px 0", textAlign: "center", fontSize: "14px" },
        text: "Ainda não há produtos comprados vezes suficientes, com intervalo grande o " +
              "bastante, para medir variação de preço." })]);
  }
  const cab = [{ t: "Produto" }, { t: "De", n: 1 }, { t: "Para", n: 1 }, { t: "Var.", n: 1 }];
  const linha = (v, sobe) => {
    const faixa = v.max - v.min;
    const a = faixa > 0 ? ((v.p0 - v.min) / faixa) * 100 : 50;
    const b = faixa > 0 ? ((v.p1 - v.min) / faixa) * 100 : 50;
    return tr([
      el("div", {}, [
        el("div", { text: v.desc }),
        el("div", { class: "legenda", text: `${v.vezes} compras · ${dataCurta(v.de)} → ${dataCurta(v.ate)}` }),
        el("span", { class: "pilha", title: `variou entre ${n2(v.min)} e ${n2(v.max)}`,
          style: { height: "3px", maxWidth: "220px", marginTop: "6px", borderRadius: "999px" } }, [
          el("span", { style: { marginLeft: `${Math.min(a, b)}%`, width: `${Math.max(3, Math.abs(b - a))}%`,
            background: sobe ? "var(--ember)" : "var(--mate)", borderRadius: "999px" } }),
        ]),
      ]),
      { v: n2(v.p0), n: 1, dim: 1 }, { v: n2(v.p1), n: 1 },
      el("span", { class: `pill ${sobe ? "up" : "down"}`,
        text: `${sobe ? "▲ +" : "▼ "}${n1(v.var)}%` }),
    ]);
  };
  return el("div", { class: "grade g2" }, [
    card("▲ Subiram", "1ª vs. última compra",
      [tabela(cab, D.precoSubiu.map((v) => linha(v, true)))]),
    card("▼ Caíram", "1ª vs. última compra",
      [tabela(cab, D.precoCaiu.map((v) => linha(v, false)))]),
  ]);
}

/* ---------------------------------------------------------- impostos */
export function painelImpostos() {
  const cats = [...D.categorias].sort((a, b) => b.imposto - a.imposto).slice(0, 14);
  const max = cats[0] ? cats[0].imposto : 1;
  return el("div", { class: "grade" }, [
    el("div", { class: "nota-lateral plum" }, [
      el("strong", { text: "Por que é estimativa. " }),
      el("span", { text:
        "A consulta pública da NFC-e da SEFAZ-RS não publica os valores de tributo da " +
        "nota — o campo da Lei 12.741/2012 existe no XML, mas não aparece na tela " +
        "pública, e a versão em abas com ICMS/PIS/COFINS item a item exige login gov.br. " +
        "Os números abaixo aplicam a cada item a carga tributária média da sua categoria " +
        "(ICMS-RS + PIS/COFINS + IPI), nas faixas do IBPT — o mesmo critério que o " +
        "supermercado usa para imprimir o total de tributos no rodapé do cupom. É ordem " +
        "de grandeza, não o valor exato recolhido." }),
    ]),
    el("div", { class: "grade g21" }, [
      card("Imposto estimado por categoria", "alíquota média aplicada", [
        el("div", { class: "barras" }, cats.map((c) => barra({
          nome: c.nome, sub: `${n1(c.aliq)}%`, valor: c.imposto, max }))),
      ]),
      card("Carga efetiva por loja", "quanto da conta virou imposto", [
        tabela([{ t: "Loja" }, { t: "Gasto", n: 1 }, { t: "Imposto", n: 1 }, { t: "Carga", n: 1 }],
          D.impostoLoja.map((l) => tr([l.loja, { v: brl(l.total), n: 1, dim: 1 },
            { v: brl(l.imposto), n: 1 }, { v: pct(l.aliq), n: 1 }]))),
      ]),
    ]),
  ]);
}

/* ---------------------------------------------------------- extremos */
export function painelExtremos() {
  const maxHora = Math.max(...D.horas.map((h) => h.notas), 1);
  const horas = Array.from({ length: 17 }, (_, k) => {
    const h = k + 7;
    const x = D.horas.find((v) => v.hora === h);
    return { h, notas: x ? x.notas : 0 };
  });
  const maxDow = Math.max(...D.dow.map((d) => d.media), 1);

  const tabelaDias = (lista, campo, rotulo) => tabela(
    [{ t: "Data" }, { t: "Dia" }, { t: rotulo, n: 1 }, { t: "Total", n: 1 }],
    lista.map((d) => tr([
      { v: dataDia(d.data), n: 1 },
      el("div", {}, [el("div", { class: "dim", text: d.dow }),
        el("div", { class: "legenda", text: d.lojas.join(", ") })]),
      { v: d[campo], n: 1, dim: 1 },
      el("strong", { class: "mono", text: brl(d.total) }),
    ])));

  return el("div", { class: "grade" }, [
    el("div", { class: "grade g2" }, [
      card("Dias mais caros", null, [tabelaDias(D.diaTop, "notas", "Notas")]),
      card("Dias mais baratos", null, [tabelaDias(D.diaBottom, "itens", "Itens")]),
    ]),
    el("div", { class: "grade g2" }, [
      card("Dia da semana", "média por dia com compra", [
        el("div", { class: "barras" }, D.dow.map((d) => barra({
          nome: d.nome, sub: `${d.notas} notas`, valor: d.media, max: maxDow }))),
      ]),
      card("Hora da compra", "nº de notas", [
        el("div", { style: { display: "flex", alignItems: "flex-end", gap: "3px", height: "110px" } },
          horas.map((x) => el("span", { title: `${x.h}h — ${x.notas} notas`,
            style: { flex: "1", background: "var(--mate)", borderRadius: "3px 3px 0 0",
                     opacity: ".88", height: `${Math.max(1.5, (100 * x.notas) / maxHora)}%` } }))),
        el("div", { style: { display: "flex", gap: "3px", borderTop: "1px solid var(--rule)",
          marginTop: "4px", paddingTop: "5px" } },
          horas.map((x) => el("span", { class: "legenda",
            style: { flex: "1", textAlign: "center", fontSize: "9.5px" },
            text: x.h % 2 === 1 ? String(x.h) : "" }))),
      ]),
    ]),
    el("div", { class: "grade g2" }, [
      card("Maiores notas do período", null, [
        tabela([{ t: "Data" }, { t: "Loja" }, { t: "Itens", n: 1 }, { t: "Valor", n: 1 }],
          D.maioresNotas.map((n) => tr([
            { v: `${dataDia(n.data)} ${n.hora.slice(0, 5)}`, n: 1 },
            el("div", {}, [el("div", { text: n.loja }), el("div", { class: "legenda", text: n.pessoa })]),
            { v: n.itens, n: 1, dim: 1 },
            el("strong", { class: "mono", text: brl(n.valor) }),
          ]))),
      ]),
      el("div", { class: "grade" }, [
        card("Itens mais caros de uma só vez", null, [
          tabela([{ t: "Produto" }, { t: "Valor", n: 1 }],
            D.maioresItens.slice(0, 8).map((i) => tr([
              el("div", {}, [el("div", { text: i.desc }),
                el("div", { class: "legenda", text: `${dataDia(i.data)} · ${i.loja}` })]),
              el("strong", { class: "mono", text: brl(i.valor) }),
            ]))),
        ]),
        card("Como se pagou", null, [
          el("div", { class: "barras" }, D.pagamento.map((p) => barra({
            nome: p.forma, sub: `${p.notas} notas`, valor: p.total,
            max: D.pagamento[0].total, alt: /não informada/i.test(p.forma) }))),
        ]),
      ]),
    ]),
  ]);
}

/* -------------------------------------------------------- explorador */
export function painelNotas() {
  const PAGINA = 30;
  let busca = "", quem = null, ramo = null, ordem = "valor", limite = PAGINA;

  const ramoDaLoja = new Map(D.lojas.map((l) => [l.nome, l.categoria]));
  const linhas = () => {
    const q = busca.trim().toLowerCase();
    const out = D.notasBrutas.map((n, i) => ({
      i, dia: n[0], hora: n[1], loja: n[2], pessoa: n[3], valor: n[4],
      itens: n[5], imposto: n[6],
      nomeLoja: D.nomesLojas[n[2]],
      ramo: ramoDaLoja.get(D.nomesLojas[n[2]]) || "—",
    })).filter((r) =>
      (quem === null || r.pessoa === quem) &&
      (!ramo || r.ramo === ramo) &&
      (!q || r.nomeLoja.toLowerCase().includes(q)));
    out.sort((a, b) => ordem === "valor" ? b.valor - a.valor
      : ordem === "itens" ? b.itens - a.itens
      : (b.dia - a.dia) || (b.hora - a.hora));
    return out;
  };

  const resumo = el("div", { class: "kpis", style: { marginBottom: "16px" } });
  const corpo = el("div");
  const maisBtn = el("button", { class: "aba", style: { width: "100%", marginTop: "14px" },
    onclick: () => { limite += PAGINA * 2; desenha(); } });

  function desenha() {
    const ls = linhas();
    const soma = ls.reduce((a, r) => a + r.valor, 0);
    resumo.innerHTML = "";
    [["Notas", n0(ls.length)], ["Total", brl(soma)],
     ["Itens", n0(ls.reduce((a, r) => a + r.itens, 0))],
     ["Imposto est.", brl(ls.reduce((a, r) => a + r.imposto, 0))]]
      .forEach(([r, v]) => resumo.append(el("div", { class: "kpi" }, [
        el("span", { class: "eyebrow", text: r }),
        el("div", { class: "v", style: { fontSize: "16px" }, text: v }),
      ])));

    corpo.innerHTML = "";
    if (!ls.length) {
      corpo.append(el("p", { class: "dim", style: { padding: "26px 0", textAlign: "center", fontSize: "14px" },
        text: "Nenhuma nota corresponde a esses filtros." }));
      maisBtn.classList.add("oculto");
      return;
    }
    corpo.append(tabela(
      [{ t: "Data" }, { t: "Loja" }, { t: "Titular" }, { t: "Itens", n: 1 },
       { t: "Imposto est.", n: 1 }, { t: "Valor", n: 1 }],
      ls.slice(0, limite).map((r) => tr([
        { v: `${dataDia(diaParaISO(r.dia))} ${String(r.hora).padStart(2, "0")}h`, n: 1 },
        el("div", {}, [el("div", { text: r.nomeLoja }), el("div", { class: "legenda", text: r.ramo })]),
        { v: D.pessoasNomes[r.pessoa], dim: 1 },
        { v: r.itens, n: 1, dim: 1 }, { v: brl(r.imposto), n: 1, dim: 1 },
        el("strong", { class: "mono", text: brl(r.valor) }),
      ]))));
    if (limite < ls.length) {
      maisBtn.classList.remove("oculto");
      maisBtn.textContent = `mostrar mais (${n0(ls.length - limite)} restantes)`;
    } else maisBtn.classList.add("oculto");
  }

  const campo = el("input", { type: "search", placeholder: "Buscar loja…",
    "aria-label": "Buscar por nome da loja",
    oninput: (e) => { busca = e.target.value; limite = PAGINA; desenha(); } });

  const ordemBtns = abas([["data", "↓ Data"], ["valor", "↓ Valor"], ["itens", "↓ Itens"]],
    "valor", (id) => { ordem = id; desenha(); });

  const filtros = el("div", { class: "chips", style: { marginTop: "10px" } });
  if (D.pessoasNomes.length > 1) {
    D.pessoasNomes.forEach((p, i) => filtros.append(el("button", {
      class: "chip", "aria-pressed": false,
      onclick: (e) => {
        quem = quem === i ? null : i;
        limite = PAGINA;
        filtros.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
        if (quem !== null) e.currentTarget.setAttribute("aria-pressed", "true");
        desenha();
      },
    }, [p])));
    filtros.append(el("span", { class: "legenda", style: { alignSelf: "center" }, text: "|" }));
  }
  D.catLoja.forEach((c) => filtros.append(el("button", {
    class: "chip", "aria-pressed": false,
    onclick: (e) => {
      const era = ramo === c.nome;
      ramo = era ? null : c.nome;
      limite = PAGINA;
      [...filtros.querySelectorAll("button")].slice(D.pessoasNomes.length > 1 ? D.pessoasNomes.length : 0)
        .forEach((b) => b.setAttribute("aria-pressed", "false"));
      if (!era) e.currentTarget.setAttribute("aria-pressed", "true");
      desenha();
    },
  }, [c.nome])));

  desenha();
  return card(`Todas as ${n0(R.notas)} notas`, "filtre, ordene, busque", [
    el("div", { style: { display: "flex", flexWrap: "wrap", gap: "8px", alignItems: "center" } },
      [campo, ordemBtns]),
    filtros,
    el("div", { style: { height: "16px" } }),
    resumo, corpo, maisBtn,
  ]);
}
