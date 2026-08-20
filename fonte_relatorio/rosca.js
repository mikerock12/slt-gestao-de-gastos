/* Gráfico de rosca (parte-do-todo).
   Toda fatia aparece na legenda com nome e número — a cor nunca identifica
   sozinha. Fatias finas continuam legíveis porque a leitura real é na lista. */
import { el, brl, pct } from "./util.js";

export function rosca(fatias, { centroRotulo, centroValor, tamanho = 210, espessura = 25, titulo } = {}) {
  const total = fatias.reduce((a, f) => a + f.valor, 0) || 1;
  const R = tamanho / 2;
  const raio = R - espessura / 2 - 2;
  const circ = 2 * Math.PI * raio;

  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", tamanho);
  svg.setAttribute("height", tamanho);
  svg.setAttribute("viewBox", `0 0 ${tamanho} ${tamanho}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", titulo || "Composição");

  const g = document.createElementNS(ns, "g");
  g.setAttribute("transform", `translate(${R} ${R}) rotate(-90)`);
  svg.append(g);

  const centro = el("div", { class: "centro" });
  const rotuloEl = el("span", { class: "eyebrow", text: centroRotulo || "" });
  const valorEl = el("span", { class: "v", text: centroValor || "" });
  centro.append(rotuloEl, valorEl);

  const lista = el("ul");
  const arcos = [];
  let acumulado = 0;

  fatias.forEach((f, i) => {
    const frac = f.valor / total;
    const c = document.createElementNS(ns, "circle");
    c.setAttribute("r", raio);
    c.setAttribute("fill", "none");
    c.setAttribute("stroke", f.cor);
    c.setAttribute("stroke-width", espessura);
    c.setAttribute("stroke-dasharray", `${Math.max(0, frac * circ - 2)} ${circ}`);
    c.setAttribute("stroke-dashoffset", -acumulado * circ);
    c.style.transition = "opacity .15s, stroke-width .15s";
    const t = document.createElementNS(ns, "title");
    t.textContent = `${f.nome}: ${brl(f.valor)} (${pct(100 * frac)})`;
    c.append(t);
    g.append(c);
    acumulado += frac;

    const li = el("li", {}, [
      el("i", { style: { background: f.cor } }),
      el("span", { class: "nome" }, [f.nome, f.nota ? el("span", { class: "tag", text: f.nota }) : null]),
      el("span", { class: "pontos", "aria-hidden": true }),
      el("span", { class: "val", text: pct(100 * frac) }),
      el("span", { class: "val dim", text: brl(f.valor) }),
    ]);
    lista.append(li);
    arcos.push({ c, li, f, frac, i });
  });

  const foca = (k) => {
    arcos.forEach((a) => {
      const on = k === null || k === a.i;
      a.c.style.opacity = on ? 1 : 0.32;
      a.c.setAttribute("stroke-width", k === a.i ? espessura + 5 : espessura);
      a.li.style.opacity = on ? 1 : 0.45;
    });
    if (k === null) {
      rotuloEl.textContent = centroRotulo || "";
      valorEl.textContent = centroValor || "";
    } else {
      rotuloEl.textContent = arcos[k].f.nome;
      valorEl.textContent = `${pct(100 * arcos[k].frac)} · ${brl(arcos[k].f.valor)}`;
    }
  };
  arcos.forEach((a) => {
    for (const alvo of [a.c, a.li]) {
      alvo.addEventListener("mouseenter", () => foca(a.i));
      alvo.addEventListener("mouseleave", () => foca(null));
    }
  });

  return el("div", { class: "rosca" }, [
    el("div", { class: "disco", style: { width: `${tamanho}px`, height: `${tamanho}px` } }, [svg, centro]),
    lista,
  ]);
}
