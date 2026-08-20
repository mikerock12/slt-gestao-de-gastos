/* Monta a página inteira do relatório. */
import gsap from "gsap";
import {
  D, el, brl, pct, n0, n1, dataDia, diaParaISO, card, secao, tabela, tr, leader,
} from "./util.js";
import { calendario, torres } from "./cenas.js";
import {
  faixaKpis, mapaConsumo, painelAlimentacao, painelHigiene, painelMedicamentos,
} from "./paineis.js";
import {
  painelRitmo, painelPessoas, painelLojas, painelCategorias, painelPrecos,
  painelImpostos, painelExtremos, painelNotas,
} from "./paineis2.js";

const R = D.resumo, A = D.alimentacao, H = D.higiene, M = D.medicamentos;
const M_ = D.meta;
const familia = M_.familia;
const semMovimento = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const dataBR = (iso) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}`;

/* ------------------------------------------------------------ navegação */
const SECOES = [
  ["mapa", "Mapa"], ["alimentacao", "Alimentação"], ["higiene", "Higiene"],
  ["medicamentos", "Remédios"], ["ritmo", "Ritmo"],
  ...(familia ? [["pessoas", "Quem"]] : []),
  ["onde", "Onde"], ["categorias", "Categorias"], ["precos", "Preços"],
  ["impostos", "Impostos"], ["extremos", "Extremos"], ["notas", "Notas"],
];

function navegacao() {
  const ul = el("ul", {}, SECOES.map(([id, rot]) =>
    el("li", {}, [el("a", { href: `#${id}`, text: rot })])));
  const nav = el("nav", { class: "topo" }, [
    el("div", { class: "interno" }, [
      el("span", { class: "marca", text: "SLT · Gestão de Gastos" }), ul,
    ]),
  ]);
  addEventListener("scroll", () => nav.classList.toggle("ver", scrollY > 420), { passive: true });

  const obs = new IntersectionObserver((entradas) => {
    const vis = entradas.filter((e) => e.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (!vis[0]) return;
    ul.querySelectorAll("a").forEach((a) =>
      a.toggleAttribute("aria-current", a.getAttribute("href") === `#${vis[0].target.id}`));
  }, { rootMargin: "-15% 0px -70% 0px" });
  requestAnimationFrame(() => SECOES.forEach(([id]) => {
    const e = document.getElementById(id);
    if (e) obs.observe(e);
  }));
  return nav;
}

/* --------------------------------------------------------- entrada suave */
function revelar(nodes) {
  if (semMovimento() || document.visibilityState === "hidden") return;
  nodes.forEach((n) => {
    gsap.set(n, { opacity: 0, y: 18 });
    const io = new IntersectionObserver((es) => {
      if (!es.some((e) => e.isIntersecting)) return;
      io.disconnect();
      gsap.to(n, { opacity: 1, y: 0, duration: .65, ease: "power2.out", overwrite: "auto" });
    }, { rootMargin: "0px 0px -10% 0px" });
    io.observe(n);
    // rede de segurança: nada fica preso invisível
    setTimeout(() => { io.disconnect(); gsap.to(n, { opacity: 1, y: 0, duration: .3 }); }, 6000);
  });
}

/* ------------------------------------------------------------- abertura */
function abertura() {
  const quem = familia
    ? `${M_.titulo} · família`
    : M_.titulo;
  return el("header", { class: "abertura" }, [
    el("div", { class: "kicker" }, [
      el("span", { class: "selo", text: "Nota Fiscal Gaúcha" }),
      el("span", { class: "eyebrow", text: quem }),
      el("span", { class: "eyebrow", text: `${dataBR(M_.inicio)} → ${dataBR(M_.fim)}` }),
    ]),
    el("h1", { text: familia ? "O mapa do que a casa consome" : "O mapa do que você consome" }),
    el("p", { class: "sub", text:
      `${n0(R.notas)} cupons fiscais consultados na SEFAZ-RS, ${n0(R.itens)} produtos ` +
      "lidos um a um e classificados por grupo alimentar, grau de processamento, " +
      "higiene, limpeza e medicamento. Clique no calendário abaixo para entrar em " +
      "qualquer dia do período." }),
  ]);
}

/* ------------------------------------------------------------ 3D + atalhos */
/* As cenas só nascem depois que o palco está no documento e com tamanho —
   por isso `iniciar()` é chamado no fim da montagem, e não via
   requestAnimationFrame (que nem dispara enquanto a aba está oculta). */
function blocoCalendario() {
  const palco = el("div", { class: "cena", style: { height: "clamp(400px,66vh,640px)" } });
  const atalhos = el("div", { class: "chips", style: { marginTop: "12px", alignItems: "center" } });
  const node = el("div", {}, [
    palco,
    el("p", { class: "legenda", style: { marginTop: "12px", maxWidth: "74ch" }, text:
      "Cada coluna é um dia. As fileiras se repetem a cada semana, de segunda a domingo, " +
      "e os traços no chão separam os meses. Clique numa coluna para abrir a nota daquele dia." }),
    atalhos,
  ]);
  const iniciar = () => {
    const cal = calendario(palco);
    atalhos.append(el("span", { class: "legenda", text: "Ir direto a um dia:" }));
    cal.destaques.forEach((c) => atalhos.append(el("button", {
      class: "chip", onclick: () => cal.abrir(c),
      text: `${dataDia(diaParaISO(c.dia))} · ${brl(c.total)}`,
    })));
  };
  return { node, iniciar };
}

function blocoTorres() {
  const palco = el("div", { class: "cena", style: { height: "clamp(380px,62vh,600px)" } });
  const atalhos = el("div", { class: "chips", style: { marginTop: "12px" } });
  const node = el("div", {}, [palco, atalhos]);
  const iniciar = () => {
    const t = torres(palco);
    t.lista.slice(0, 12).forEach((x) => atalhos.append(el("button", {
      class: "chip", onclick: () => t.abrir(x),
    }, [el("i", { style: { background: corDaTorre(x, t.lista.length) } }), x.nome])));
  };
  return { node, iniciar };
}
function corDaTorre(t, total) {
  const RAMPA = ["#6ee7b0", "#4ec397", "#41b489", "#37a67c", "#2f9770",
    "#288964", "#227b59", "#1c6d4e", "#175f44", "#12523a"];
  return RAMPA[Math.round((total <= 1 ? 0 : t.rank / (total - 1)) * (RAMPA.length - 1))];
}

/* --------------------------------------------------------------- fontes */
function blocoFontes() {
  const itensMetodo = [
    ["Fonte", "Consulta pública da NFC-e na SEFAZ-RS. Para cada chave das planilhas foi " +
      "aberta a página sefaz.rs.gov.br/NFE/NFE-NFC.aspx?chaveNFe=… e acionado o botão " +
      "Avançar, que abre a Consulta Completa da NFC-e."],
    ["Baixadas", `${n0(R.notas)} NFC-e (modelo 65) lidas e detalhadas item a item.`],
    ["Classificação de consumo", "Cada item foi classificado pelo tipo do produto lido na " +
      "descrição, com regras que priorizam o substantivo sobre o sabor. Os grupos " +
      "alimentares e o grau de processamento seguem o Guia Alimentar para a População " +
      "Brasileira (classificação NOVA)."],
    ["Quilos e litros", "Só entram na conta de peso os itens vendidos a quilo, e na de " +
      "volume os que trazem o volume na descrição. Os totais reais são um pouco maiores."],
    ["Período", `${dataBR(M_.inicio)} a ${dataBR(M_.fim)} — ${M_.dias} dias. As médias ` +
      "mensais e semanais são calculadas sobre esse período."],
  ];

  const limites = [
    "Só entram compras em que o CPF foi informado na nota. O que foi pago sem CPF não " +
    "aparece em lugar nenhum aqui.",
    "Os valores de tributo são estimados por categoria — a consulta pública não publica " +
    "o imposto da nota.",
    "Gasto não é a mesma coisa que quantidade consumida. Fruta e verdura são baratas por " +
    "quilo; álcool é caro. Por isso os quilos e litros aparecem ao lado do dinheiro.",
    "A classificação nutricional é do produto comprado, não do que foi efetivamente " +
    "comido. Nada aqui mede porção, caloria ou nutriente.",
  ];

  const cartoes = [
    card("Como os dados foram obtidos", null,
      itensMetodo.map(([t, d]) => el("div", { style: { marginBottom: "14px" } }, [
        el("div", { class: "eyebrow", text: t }),
        el("p", { style: { marginTop: "4px", fontSize: "14.5px", color: "var(--ink-2)" }, text: d }),
      ]))),
    el("div", { class: "grade" }, [
      D.m55.length ? card("Notas sem consulta pública", `${brl(R.m55Total)} sem detalhe`, [
        el("p", { style: { fontSize: "14.5px", color: "var(--ink-2)" }, text:
          `${R.m55Notas} documento(s) das planilhas são NF-e modelo 55, não NFC-e modelo 65. ` +
          "A consulta completa de NF-e migrou para o portal DFe da SVRS e hoje exige " +
          "autenticação pela conta gov.br. Elas entram no total geral pelo valor da " +
          "planilha, sem detalhe de itens." }),
        el("div", { style: { height: "14px" } }),
        tabela([{ t: "Fornecedor" }, { t: "Notas", n: 1 }, { t: "Total", n: 1 }],
          D.m55.map((m) => tr([m.razao, { v: m.notas, n: 1, dim: 1 }, { v: brl(m.total), n: 1 }]))),
      ]) : null,
      card("Limites que vale conhecer", null, [
        el("div", { class: "leaders" }, limites.map((t) =>
          el("p", { style: { fontSize: "14.5px", color: "var(--ink-2)", lineHeight: "1.6" }, text: `• ${t}` }))),
      ]),
    ]),
  ];
  return el("div", { class: "grade g2" }, cartoes);
}

/* ============================================================== montagem */
function montar() {
  const wrap = el("div", { class: "wrap" });
  document.body.append(navegacao(), wrap);

  wrap.append(abertura());
  const cal = blocoCalendario();
  wrap.append(el("div", { style: { marginTop: "38px" } }, [cal.node]));

  const faixa = el("div", { style: { marginTop: "38px" } }, [faixaKpis()]);
  wrap.append(faixa);

  const alcool = A.grupos.find((g) => g.nome === "Bebidas alcoólicas");
  const frutasVerduras =
    (A.grupos.find((g) => g.nome === "Frutas") || { total: 0 }).total +
    (A.grupos.find((g) => g.nome === "Verduras e legumes") || { total: 0 }).total;

  const torres3d = blocoTorres();

  const blocos = [
    [secao("mapa", "O mapa do consumo", `${D.dominioResumo.length} domínios`,
      `Cada um dos ${n0(R.itens)} produtos foi classificado pelo que ele é, não pela loja ` +
      "onde foi comprado — porque a descrição da nota engana muito (&ldquo;desinfetante " +
      "limão&rdquo; não é fruta, &ldquo;sabonete leite&rdquo; não é laticínio). Daí sai " +
      "este mapa: para onde o dinheiro vai, por área da vida."), mapaConsumo()],

    [secao("alimentacao", familia ? "O que a casa come" : "O que você come",
      `${n0(A.itens)} itens de alimentação`,
      `Os ${n0(A.itens)} itens de comida e bebida foram divididos em grupos alimentares e ` +
      "classificados pelo grau de processamento (NOVA, do Guia Alimentar para a População " +
      `Brasileira). A bebida alcoólica leva ${pct((100 * (alcool ? alcool.total : 0)) / (A.total || 1))} ` +
      `do dinheiro da mesa; tirando o álcool da conta, ${pct(A.ultraShareMedio)} do que se ` +
      `compra para comer é ultraprocessado. Fruta e verdura somam ${brl(frutasVerduras)} no ` +
      "período."), painelAlimentacao()],

    [secao("higiene", "Higiene e limpeza",
      `${H.higieneItens + H.limpezaItens} itens`,
      `Higiene pessoal custou ${brl(H.higieneTotal)} e a limpeza da casa ${brl(H.limpezaTotal)} ` +
      `— juntas, ${pct((100 * (H.higieneTotal + H.limpezaTotal)) / R.valorProdutos)} do ` +
      "orçamento. Além do quanto, dá para ver de quanto em quanto tempo cada essencial é " +
      "reposto."), painelHigiene()],

    [secao("medicamentos", "Medicamentos", `${M.itens} itens · ${brl(M.total)}`,
      `${brl(M.total)} no período, ${brl(M.gastoMensal)} por mês, com compra em ` +
      `${M.diasComCompra} dias. A classificação por classe terapêutica vem do princípio ` +
      "ativo lido na descrição da nota — serve para dar panorama, não para orientar " +
      "tratamento."), painelMedicamentos()],

    [secao("ritmo", "O ritmo do gasto",
      `${R.notas} notas · ${R.diasComCompra} dias com compra`,
      `Em ${R.diasComCompra} dos ${M_.dias} dias do período houve pelo menos uma compra. ` +
      `A média é de ${brl(R.mediaSemana)} por semana e ${brl(R.mediaMes)} por mês.`),
      painelRitmo()],

    familia ? [secao("pessoas", "Quem gastou o quê", "CPF na nota",
      "Os gastos são da mesma casa, mas o CPF na nota diz quem estava no caixa."),
      painelPessoas()] : null,

    [secao("onde", "Onde o dinheiro foi parar",
      `${R.lojasDistintas} lojas · ${R.cnpjs} CNPJs`,
      `${D.lojas[0].nome} concentra ${pct(D.lojas[0].share)} de tudo, em ${D.lojas[0].notas} ` +
      `notas. Clique numa barra para ver o detalhe da loja.`), painelLojas()],

    [secao("categorias", "As torres do consumo",
      `${n0(R.itens)} itens · ${D.categorias.length} categorias`,
      "Cada torre é uma categoria de produto, com a altura proporcional ao gasto e fatiada " +
      "pelos meses do período — dá para ver de relance o que é constante e o que foi compra " +
      "pontual. Clique numa torre para entrar nela."),
      torres3d.node, painelCategorias()],

    [secao("precos", "O que subiu e o que caiu",
      `${D.precoMeta.amostra} produtos rastreáveis`,
      `Só dá para medir variação em produtos comprados pelo menos três vezes, com mais de ` +
      `45 dias entre a primeira e a última compra — ${D.precoMeta.amostra} produtos passam ` +
      `nesse filtro. A mediana ficou em <strong>${n1(D.precoMeta.mediana)}%</strong> e a ` +
      `média em <strong>${n1(D.precoMeta.media)}%</strong>.`), painelPrecos()],

    [secao("impostos", "Quanto disso foi imposto", "estimativa",
      `Dos ${brl(R.valorProdutos)} em produtos, cerca de <strong>${brl(R.imposto)} foram ` +
      `tributos</strong> — ${pct(R.aliqMedia)} do total.`), painelImpostos()],

    [secao("extremos", "Os dias que fugiram da curva",
      `média de ${brl(D.diaStats.media)} por dia com compra`,
      `O dia mais caro foi <strong>${dataDia(D.diaTop[0].data)}</strong>, com ` +
      `${brl(D.diaTop[0].total)} em ${D.diaTop[0].notas} nota(s).`), painelExtremos()],

    [secao("notas", `Todas as ${n0(R.notas)} notas`, "filtre, ordene, busque",
      "A base inteira, do jeito que saiu da SEFAZ. Cada linha corresponde a um arquivo " +
      "salvo na pasta Notas."), painelNotas()],

    [secao("fontes", "De onde veio cada número", "metodologia", null), blocoFontes()],
  ].filter(Boolean);

  const paraRevelar = [faixa];
  for (const [sec, ...conteudo] of blocos) {
    conteudo.forEach((c) => {
      const box = el("div", { style: { marginTop: "22px" } }, [c]);
      sec.append(box);
      paraRevelar.push(box);
    });
    wrap.append(sec);
    paraRevelar.push(sec.querySelector(".sechead"));
  }

  wrap.append(el("footer", {}, [
    el("p", { text:
      `Relatório gerado por SLT — Gestão de Gastos em ${dataBR(M_.geradoEm)}, a partir da ` +
      "consulta pública da Secretaria da Fazenda do Rio Grande do Sul. Os valores de " +
      "tributo são estimativas por categoria, não valores informados na nota fiscal. A " +
      "leitura nutricional segue o Guia Alimentar para a População Brasileira e não " +
      "substitui orientação profissional." }),
  ]));

  revelar(paraRevelar.filter(Boolean));

  // agora que tudo está no documento e com tamanho, as cenas podem nascer
  cal.iniciar();
  torres3d.iniciar();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", montar);
} else {
  montar();
}
