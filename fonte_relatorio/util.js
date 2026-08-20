/* Formatação, helpers de DOM e a paleta. */

export const D = window.__SLT_DADOS__;

/* itensBrutos:
   [dia, cat, loja, pessoa, valor, imposto, desc, dom, grupo, nova, qtd, un, nota] */
export const IB = {
  dia: 0, cat: 1, loja: 2, pessoa: 3, valor: 4, imposto: 5,
  desc: 6, dom: 7, grupo: 8, nova: 9, qtd: 10, un: 11, nota: 12,
};

const fmt = (min, max) =>
  new Intl.NumberFormat("pt-BR", { minimumFractionDigits: min, maximumFractionDigits: max });
const f0 = fmt(0, 0), f1 = fmt(1, 1), f2 = fmt(2, 2);

export const brl = (v) => `R$ ${f2.format(v || 0)}`;
export const brlCurto = (v) => (v >= 1000 ? `R$ ${f1.format(v / 1000)} mil` : `R$ ${f0.format(v || 0)}`);
export const n0 = (v) => f0.format(v || 0);
export const n1 = (v) => f1.format(v || 0);
export const n2 = (v) => f2.format(v || 0);
export const pct = (v) => `${f1.format(v || 0)}%`;

const MES_CURTO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const MES_LONGO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
  "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
export const DIA_SEMANA = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"];

export const dataCurta = (iso) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;
export const dataDia = (iso) => `${iso.slice(8, 10)} ${MES_CURTO[+iso.slice(5, 7) - 1]}`;
export const mesLongo = (iso) => MES_LONGO[+iso.slice(5, 7) - 1];
export const dataLonga = (iso) => `${+iso.slice(8, 10)} de ${MES_LONGO[+iso.slice(5, 7) - 1]}`;

const INICIO = new Date(`${D.meta.inicio}T12:00:00`);
export const diaParaISO = (d) => new Date(INICIO.getTime() + d * 86400000).toISOString().slice(0, 10);
export const diaDaSemana = (d) => DIA_SEMANA[new Date(INICIO.getTime() + d * 86400000).getDay()];

export const desc = (it) => D.descricoes[it[IB.desc]];
export const unidade = (it) => D.unidades[it[IB.un]] || "";

/* Rampa de uma matiz só: a cor codifica magnitude/posição, nunca identidade —
   o nome sempre acompanha. */
export const RAMPA = ["#6ee7b0", "#4ec397", "#41b489", "#37a67c", "#2f9770",
  "#288964", "#227b59", "#1c6d4e", "#175f44", "#12523a"];
export const corPorRank = (i, total) =>
  RAMPA[Math.round((total <= 1 ? 0 : i / (total - 1)) * (RAMPA.length - 1))];

/* Escala ordinal de processamento (NOVA). Validada para daltonismo. */
export const COR_NOVA = { real: "#35a87a", proc: "#a678c8", ultra: "#d4614c" };

/* --------------------------------------------------------------- DOM */
export function el(tag, attrs = {}, filhos = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (k === "text") e.textContent = v;
    else if (k === "style" && typeof v === "object") Object.assign(e.style, v);
    else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : String(v));
  }
  for (const f of [].concat(filhos)) {
    if (f === null || f === undefined || f === false) continue;
    e.append(typeof f === "string" || typeof f === "number" ? String(f) : f);
  }
  return e;
}

export const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function card(titulo, nota, corpo, classe = "") {
  const c = el("div", { class: `card ${classe}` });
  if (titulo || nota) {
    c.append(el("div", { class: "cardtitle" }, [
      titulo ? el("span", { class: "t", text: titulo }) : null,
      nota ? el("span", { class: "eyebrow", text: nota }) : null,
    ]));
  }
  for (const f of [].concat(corpo)) if (f) c.append(f);
  return c;
}

export function secao(id, titulo, marca, prosa) {
  const s = el("section", { id });
  const h = el("div", { class: "sechead" }, [
    el("div", { class: "linha" }, [
      el("h2", { text: titulo }),
      marca ? el("span", { class: "eyebrow", text: marca }) : null,
    ]),
    prosa ? el("p", { html: prosa }) : null,
  ]);
  s.append(h);
  return s;
}

export function barra({ nome, sub, valor, max, texto, extra, alt, onClick }) {
  const w = max > 0 ? Math.max(0.6, (100 * valor) / max) : 0;
  const linha = el("div", { class: "barra" }, [
    el("span", { class: "nome" }, [nome, sub ? el("small", { text: sub }) : null]),
    el("span", { class: "trilha" }, [
      el("i", { class: alt ? "alt" : null, style: { width: `${w.toFixed(2)}%` } }),
    ]),
    el("span", { class: "val" }, [
      texto ?? brl(valor),
      extra ? el("small", { text: extra }) : null,
    ]),
  ]);
  if (!onClick) return linha;
  return el("button", { class: "barra-btn", onclick: onClick }, [linha]);
}

export function leader(nome, valor, tag) {
  return el("div", { class: "leader" }, [
    el("span", { class: "nome" }, [nome, tag ? el("span", { class: "tag", text: tag }) : null]),
    el("span", { class: "pontos", "aria-hidden": true }),
    el("span", { class: "val", text: valor }),
  ]);
}

export function tabela(cabecalho, linhas) {
  const thead = el("thead", {}, [
    el("tr", {}, cabecalho.map((c) => el("th", { class: c.n ? "n" : null, text: c.t }))),
  ]);
  const tbody = el("tbody", {}, linhas);
  return el("div", { class: "tabwrap" }, [el("table", {}, [thead, tbody])]);
}

export function tr(celulas) {
  return el("tr", {}, celulas.map((c) => {
    if (c && typeof c === "object" && !("nodeType" in c)) {
      return el("td", { class: [c.n ? "n" : "", c.dim ? "dim" : ""].join(" ").trim() || null },
        [c.v]);
    }
    return el("td", {}, [c]);
  }));
}

export function abas(opcoes, atual, onTroca) {
  const box = el("div", { class: "abas" });
  const botoes = opcoes.map(([id, rot]) =>
    el("button", {
      class: "aba", "aria-pressed": id === atual,
      onclick: () => {
        botoes.forEach((b, i) => b.setAttribute("aria-pressed", opcoes[i][0] === id));
        onTroca(id);
      },
    }, [rot]),
  );
  botoes.forEach((b) => box.append(b));
  return box;
}
