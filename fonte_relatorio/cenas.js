/* As duas cenas em Three.js: o calendário do ano e as torres por categoria.
   Ambas são InstancedMesh, com hover por raycast, clique que abre um painel
   lateral e voo de câmera animado com GSAP. */
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import gsap from "gsap";
import {
  D, IB, el, brl, pct, n0, n1, desc, unidade, dataDia, dataLonga, diaParaISO,
  diaDaSemana, corPorRank, leader,
} from "./util.js";

const semMovimento = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const DIAS_ABREV = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

/* ------------------------------------------------ voo de câmera */
function voarPara(camera, ctrl, destino, alvo, dur = 1.1) {
  if (semMovimento()) {
    camera.position.copy(destino);
    ctrl.target.copy(alvo);
    ctrl.update();
    return;
  }
  const s = {
    px: camera.position.x, py: camera.position.y, pz: camera.position.z,
    tx: ctrl.target.x, ty: ctrl.target.y, tz: ctrl.target.z,
  };
  gsap.killTweensOf(s);
  gsap.to(s, {
    px: destino.x, py: destino.y, pz: destino.z,
    tx: alvo.x, ty: alvo.y, tz: alvo.z,
    duration: dur, ease: "power3.inOut",
    onUpdate() {
      camera.position.set(s.px, s.py, s.pz);
      ctrl.target.set(s.tx, s.ty, s.tz);
      ctrl.update();
    },
  });
}

function pontoDeVista(camera, alvo, dist, alturaMin = 0.4) {
  const dir = new THREE.Vector3().subVectors(camera.position, alvo);
  if (dir.lengthSq() < 1e-6) dir.set(0.5, 0.6, 0.6);
  dir.normalize();
  dir.y = Math.max(dir.y, alturaMin);
  dir.normalize();
  return alvo.clone().add(dir.multiplyScalar(dist));
}

/* ------------------------------------------------ base comum */
function montarCena(hospedeiro, { posInicial, alvoInicial, fov = 40, fog }) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.8));
  hospedeiro.append(renderer.domElement);

  const cena = new THREE.Scene();
  cena.background = new THREE.Color("#0a0c0a");
  cena.fog = new THREE.Fog("#0a0c0a", fog[0], fog[1]);

  const camera = new THREE.PerspectiveCamera(fov, 1, 0.1, 400);
  camera.position.set(...posInicial);

  cena.add(new THREE.AmbientLight(0xffffff, 0.6));
  const l1 = new THREE.DirectionalLight(0xdff5e9, 1.45);
  l1.position.set(12, 20, 10);
  cena.add(l1);
  const l2 = new THREE.DirectionalLight(0x8f6fd0, 0.5);
  l2.position.set(-16, 9, -12);
  cena.add(l2);

  const ctrl = new OrbitControls(camera, renderer.domElement);
  ctrl.enablePan = false;
  ctrl.enableDamping = true;
  ctrl.dampingFactor = 0.07;
  ctrl.minPolarAngle = 0.12;
  ctrl.maxPolarAngle = Math.PI / 2.3;
  ctrl.target.set(...alvoInicial);
  ctrl.autoRotate = !semMovimento();
  ctrl.autoRotateSpeed = 0.35;

  const ajusta = () => {
    const { clientWidth: w, clientHeight: h } = hospedeiro;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };
  ajusta();
  new ResizeObserver(ajusta).observe(hospedeiro);

  const raycaster = new THREE.Raycaster();
  const ponteiro = new THREE.Vector2();
  const posDoEvento = (ev) => {
    const r = renderer.domElement.getBoundingClientRect();
    ponteiro.x = ((ev.clientX - r.left) / r.width) * 2 - 1;
    ponteiro.y = -((ev.clientY - r.top) / r.height) * 2 + 1;
  };

  let quadros = [];
  const laco = () => {
    requestAnimationFrame(laco);
    ctrl.update();
    for (const f of quadros) f();
    renderer.render(cena, camera);
  };
  requestAnimationFrame(laco);

  return {
    cena, camera, ctrl, renderer, raycaster, ponteiro, posDoEvento,
    aCadaQuadro: (f) => quadros.push(f),
  };
}

/* ============================================================ CALENDÁRIO */
const PASSO = 1.15, ALT_MAX = 9, FOLGA_MES = 0.9;

function gradeDoAno() {
  const porDia = new Map();
  for (const [dia, , , , valor] of D.notasBrutas) {
    const a = porDia.get(dia) || { total: 0, notas: 0 };
    a.total += valor; a.notas += 1;
    porDia.set(dia, a);
  }
  const inicio = new Date(`${D.meta.inicio}T12:00:00`);
  const dowInicio = D.meta.dowInicio;
  const desloc = [];
  let acc = 0, mesAnterior = -1;
  for (let dia = 0; dia < D.meta.dias; dia++) {
    const m = new Date(inicio.getTime() + dia * 86400000).getMonth();
    const s = Math.floor((dia + dowInicio) / 7);
    if (m !== mesAnterior && mesAnterior !== -1) acc += FOLGA_MES;
    mesAnterior = m;
    if (desloc[s] === undefined) desloc[s] = acc;
  }

  const celulas = [];
  let maxTotal = 0, semanas = 0;
  for (let dia = 0; dia < D.meta.dias; dia++) {
    const pos = dia + dowInicio;
    const semana = Math.floor(pos / 7);
    const dt = new Date(inicio.getTime() + dia * 86400000);
    const a = porDia.get(dia);
    const total = a ? a.total : 0;
    maxTotal = Math.max(maxTotal, total);
    semanas = Math.max(semanas, semana + 1);
    celulas.push({
      dia, semana, dow: pos % 7, mes: dt.getMonth(),
      x: semana * PASSO + (desloc[semana] || 0), z: (pos % 7) * PASSO,
      total, notas: a ? a.notas : 0,
    });
  }
  const largura = Math.max(...celulas.map((c) => c.x));
  const profundidade = 6 * PASSO;
  for (const c of celulas) { c.x -= largura / 2; c.z -= profundidade / 2; }

  const marcas = [];
  let ultimo = -1;
  for (const c of celulas) {
    if (c.mes !== ultimo) { marcas.push(c.x); ultimo = c.mes; }
  }
  return { celulas, maxTotal, semanas, largura, profundidade, marcas };
}

function painelDoDia(dia, aoFechar) {
  const notas = D.notasBrutas.filter((n) => n[0] === dia);
  const itens = D.itensBrutos.filter((i) => i[IB.dia] === dia)
    .sort((a, b) => b[IB.valor] - a[IB.valor]);
  const total = notas.reduce((a, n) => a + n[4], 0);
  const imposto = notas.reduce((a, n) => a + n[6], 0);
  const iso = diaParaISO(dia);

  const porDominio = new Map();
  for (const i of itens) porDominio.set(i[IB.dom], (porDominio.get(i[IB.dom]) || 0) + i[IB.valor]);

  const corpo = el("div", { class: "corpo" });
  corpo.append(el("div", { class: "chips", style: { marginBottom: "14px" } },
    [...porDominio.entries()].sort((a, b) => b[1] - a[1]).map(([d, v]) =>
      el("span", { class: "chip", style: { pointerEvents: "none" } },
        [`${D.dominioNomes[d]} ${brl(v)}`]))));

  // a posição da nota no vetor global é o que liga item e nota — duas compras
  // na mesma loja, no mesmo dia, têm a mesma loja mas notas diferentes
  const idxGlobal = new Map();
  D.notasBrutas.forEach((n, k) => { if (n[0] === dia) idxGlobal.set(n, k); });

  for (const n of notas) {
    const k = idxGlobal.get(n);
    const daNota = itens.filter((i) => i[IB.nota] === k);
    const bloco = el("div", { style: { marginBottom: "16px" } });
    bloco.append(el("div", {
      style: { display: "flex", justifyContent: "space-between", gap: "8px",
               alignItems: "baseline", borderBottom: "1px solid var(--rule)",
               paddingBottom: "5px" },
    }, [
      el("span", { style: { fontWeight: "600", fontSize: "14px" }, text: D.nomesLojas[n[2]] }),
      el("span", { class: "mono", style: { fontSize: "13px" }, text: brl(n[4]) }),
    ]));
    bloco.append(el("div", {
      class: "legenda", style: { margin: "4px 0 6px" },
      text: `${String(n[1]).padStart(2, "0")}h · ${D.pessoasNomes[n[3]]} · `
            + `${n[5]} ${n[5] === 1 ? "item" : "itens"}`,
    }));
    const ul = el("div", { class: "leaders" });
    for (const i of daNota) {
      const q = i[IB.qtd] !== 1 ? ` ${n1(i[IB.qtd])} ${unidade(i).toLowerCase()}` : "";
      ul.append(leader(desc(i) + q, brl(i[IB.valor])));
    }
    bloco.append(ul);
    corpo.append(bloco);
  }

  return el("div", { class: "lateral" }, [
    el("div", { class: "topo" }, [
      el("div", {}, [
        el("div", { class: "eyebrow", text: `${diaDaSemana(dia)} · ${dataLonga(iso)}` }),
        el("div", { class: "v", text: brl(total) }),
        el("div", { class: "legenda", text:
          `${notas.length} ${notas.length > 1 ? "notas" : "nota"} · ${itens.length} itens · ${brl(imposto)} de imposto estimado` }),
      ]),
      el("button", { class: "btn-voltar", onclick: aoFechar, "aria-label": "Fechar o dia" }, ["voltar"]),
    ]),
    corpo,
  ]);
}

export function calendario(hospedeiro) {
  const { celulas, maxTotal, semanas, largura, profundidade, marcas } = gradeDoAno();
  const pos = [22, 17, 27];
  const ctx = montarCena(hospedeiro, {
    posInicial: pos, alvoInicial: [0, 0, 0], fov: 40, fog: [46, 105],
  });

  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshStandardMaterial({ roughness: 0.4, metalness: 0.1 });
  const malha = new THREE.InstancedMesh(geo, mat, celulas.length);
  malha.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  ctx.cena.add(malha);

  const baixo = new THREE.Color("#0f3a2a"), alto = new THREE.Color("#7bf0bd");
  const cores = new Float32Array(celulas.length * 3);
  celulas.forEach((c, i) => {
    const t = maxTotal ? Math.pow(c.total / maxTotal, 0.5) : 0;
    const cc = baixo.clone().lerp(alto, t);
    cores[i * 3] = cc.r; cores[i * 3 + 1] = cc.g; cores[i * 3 + 2] = cc.b;
  });

  const piso = new THREE.Mesh(
    new THREE.PlaneGeometry(largura + 6, profundidade + 5),
    new THREE.MeshStandardMaterial({ color: "#0c0f0c", roughness: 1 }));
  piso.rotation.x = -Math.PI / 2;
  piso.position.y = -0.02;
  ctx.cena.add(piso);

  for (const x of marcas) {
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(0.05, profundidade + 3),
      new THREE.MeshBasicMaterial({ color: "#2c4438" }));
    m.rotation.x = -Math.PI / 2;
    m.position.set(x - PASSO * 0.62, 0.01, 0);
    ctx.cena.add(m);
  }

  const dummy = new THREE.Object3D(), cor = new THREE.Color();
  const prog = { t: semMovimento() ? 1 : 0 };
  if (!semMovimento()) gsap.to(prog, { t: 1, duration: 2.4, ease: "power3.out", delay: 0.2 });

  let ativo = null, selecionado = null;
  ctx.aCadaQuadro(() => {
    const espalha = 0.5;
    for (let i = 0; i < celulas.length; i++) {
      const c = celulas[i];
      const atraso = (c.semana / Math.max(1, semanas - 1)) * espalha;
      const p = Math.min(1, Math.max(0, (prog.t - atraso) / (1 - espalha)));
      const suave = 1 - Math.pow(1 - p, 3);
      const h = Math.max(0.05, (maxTotal ? (c.total / maxTotal) * ALT_MAX : 0) * suave);
      const sel = selecionado === c.dia;
      const larg = sel ? 1.02 : ativo === i ? 0.94 : 0.8;
      dummy.position.set(c.x, h / 2, c.z);
      dummy.scale.set(larg, h, larg);
      dummy.updateMatrix();
      malha.setMatrixAt(i, dummy.matrix);
      if (sel) cor.set("#ffffff");
      else if (ativo === i) cor.set("#d8fff0");
      else {
        const f = selecionado !== null ? 0.4 : 1;
        cor.setRGB(cores[i * 3] * f, cores[i * 3 + 1] * f, cores[i * 3 + 2] * f);
      }
      malha.setColorAt(i, cor);
    }
    malha.instanceMatrix.needsUpdate = true;
    if (malha.instanceColor) malha.instanceColor.needsUpdate = true;
  });

  /* ---------------- sobreposições ---------------- */
  const dica = el("div", { class: "dica off" });
  const eixos = el("div", { class: "eixos" }, [
    el("div", { class: "legenda" }, [
      el("div", { text: `eixo largo — as ${semanas} semanas, separadas por mês` }),
      el("div", { text: `eixo curto — ${DIAS_ABREV.join(" · ")}` }),
      el("div", { text: "altura e cor — quanto se gastou naquele dia" }),
    ]),
    el("div", { class: "legenda", text: "clique numa coluna para entrar no dia" }),
  ]);
  hospedeiro.append(dica, eixos);

  let lateral = null;
  const fechar = () => {
    selecionado = null;
    if (lateral) { lateral.remove(); lateral = null; }
    eixos.style.opacity = 1;
    ctx.ctrl.autoRotate = !semMovimento();
    voarPara(ctx.camera, ctx.ctrl, new THREE.Vector3(...pos), new THREE.Vector3(0, 0, 0), 1);
  };
  const abrir = (c) => {
    selecionado = c.dia;
    ctx.ctrl.autoRotate = false;
    if (lateral) lateral.remove();
    lateral = painelDoDia(c.dia, fechar);
    hospedeiro.append(lateral);
    eixos.style.opacity = 0;
    dica.classList.add("off");
    const h = maxTotal ? (c.total / maxTotal) * ALT_MAX : 1;
    const alvo = new THREE.Vector3(c.x, h * 0.55, c.z);
    voarPara(ctx.camera, ctx.ctrl, pontoDeVista(ctx.camera, alvo, 9.5, 0.35), alvo, 1.1);
  };

  const acha = (ev) => {
    ctx.posDoEvento(ev);
    ctx.raycaster.setFromCamera(ctx.ponteiro, ctx.camera);
    const hits = ctx.raycaster.intersectObject(malha);
    return hits.length ? hits[0].instanceId : null;
  };

  ctx.renderer.domElement.addEventListener("pointermove", (ev) => {
    const id = acha(ev);
    ativo = id;
    if (id === null || selecionado !== null) { dica.classList.add("off"); return; }
    const c = celulas[id];
    dica.innerHTML = "";
    dica.append(
      el("div", { class: "eyebrow", text: `${dataLonga(diaParaISO(c.dia))} · ${DIAS_ABREV[c.dow]}` }),
      el("div", { class: "v", text: c.total > 0 ? brl(c.total) : "sem compra" }),
      c.notas ? el("div", { class: "legenda", text: `${c.notas} ${c.notas > 1 ? "notas" : "nota"} · clique para abrir` }) : null,
    );
    dica.classList.remove("off");
  });
  ctx.renderer.domElement.addEventListener("pointerleave", () => {
    ativo = null;
    dica.classList.add("off");
  });
  ctx.renderer.domElement.addEventListener("click", (ev) => {
    const id = acha(ev);
    if (id === null || celulas[id].total <= 0) return;
    abrir(celulas[id]);
  });
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && selecionado !== null) fechar();
  });

  return {
    destaques: [...celulas].filter((c) => c.total > 0)
      .sort((a, b) => b.total - a.total).slice(0, 8),
    abrir, fechar,
    selecionado: () => selecionado,
  };
}

/* ================================================================ TORRES */
const COLS = 5, ESPACO = 3.6, ALT_TORRE = 11, LADO = 1.5;

function montarTorres() {
  const nMes = D.meses.length;
  const mesIdx = new Map(D.meses.map((m, i) => [m.mes, i]));
  const inicio = new Date(`${D.meta.inicio}T12:00:00`);
  const acc = new Map();
  for (const it of D.itensBrutos) {
    const c = it[IB.cat];
    let a = acc.get(c);
    if (!a) { a = { total: 0, itens: 0, meses: new Array(nMes).fill(0) }; acc.set(c, a); }
    a.total += it[IB.valor];
    a.itens += 1;
    const k = mesIdx.get(new Date(inicio.getTime() + it[IB.dia] * 86400000)
      .toISOString().slice(0, 7));
    if (k !== undefined) a.meses[k] += it[IB.valor];
  }
  const lista = [...acc.entries()].map(([cat, a]) => ({ cat, ...a }))
    .sort((a, b) => b.total - a.total);
  const linhas = Math.ceil(lista.length / COLS);
  const torres = lista.map((t, rank) => ({
    ...t, rank, nome: D.nomesCategorias[t.cat],
    // as maiores ficam ao fundo, para nenhuma esconder a outra
    x: ((rank % COLS) - (COLS - 1) / 2) * ESPACO,
    z: (Math.floor(rank / COLS) - (linhas - 1) / 2) * ESPACO,
  }));
  return { torres, maxTotal: torres[0] ? torres[0].total : 1 };
}

function painelDaCategoria(t, aoFechar) {
  const itens = D.itensBrutos.filter((i) => i[IB.cat] === t.cat);
  const porProduto = new Map();
  for (const i of itens) {
    const k = desc(i);
    const a = porProduto.get(k) || { total: 0, vezes: 0 };
    a.total += i[IB.valor]; a.vezes += 1;
    porProduto.set(k, a);
  }
  const produtos = [...porProduto.entries()].sort((a, b) => b[1].total - a[1].total).slice(0, 10);
  const porLoja = new Map();
  for (const i of itens) porLoja.set(i[IB.loja], (porLoja.get(i[IB.loja]) || 0) + i[IB.valor]);
  const lojas = [...porLoja.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
  const maiorMes = Math.max(...t.meses, 1);
  const cat = D.categorias.find((c) => c.nome === t.nome);
  const maior = itens.reduce((a, b) => (b[IB.valor] > a[IB.valor] ? b : a), itens[0]);

  const corpo = el("div", { class: "corpo" });
  corpo.append(el("div", { class: "eyebrow", text: "Mês a mês" }));
  corpo.append(el("div", { class: "colunas", style: { height: "80px", marginTop: "8px" } },
    t.meses.map((v, i) => el("div", { class: "col", title: `${D.meses[i].label}: ${brl(v)}` },
      [el("i", { style: { height: `${Math.max(1.5, (100 * v) / maiorMes)}%` } })]))));
  corpo.append(el("div", { class: "eixo-x" },
    D.meses.map((m) => el("span", { class: "legenda", text: m.curto }))));

  corpo.append(el("div", { class: "eyebrow", style: { marginTop: "22px" }, text: "Produtos que mais pesaram" }));
  const lp = el("div", { class: "leaders", style: { marginTop: "8px" } });
  produtos.forEach(([nome, a]) => lp.append(leader(nome, brl(a.total), `${a.vezes}×`)));
  corpo.append(lp);

  corpo.append(el("div", { class: "eyebrow", style: { marginTop: "22px" }, text: "Onde se compra" }));
  const ll = el("div", { class: "leaders", style: { marginTop: "8px" } });
  lojas.forEach(([l, v]) => ll.append(leader(D.nomesLojas[l], brl(v))));
  corpo.append(ll);

  if (maior) {
    corpo.append(el("div", {
      style: { marginTop: "22px", border: "1px solid var(--rule)", borderRadius: "5px",
               background: "var(--surface-2)", padding: "11px 14px" },
    }, [
      el("div", { class: "eyebrow", text: "Maior compra da categoria" }),
      el("div", { style: { fontSize: "14px", marginTop: "3px" }, text: desc(maior) }),
      el("div", { class: "legenda", text:
        `${brl(maior[IB.valor])} · ${dataDia(diaParaISO(maior[IB.dia]))} · ${D.nomesLojas[maior[IB.loja]]}` }),
    ]));
  }

  return el("div", { class: "lateral" }, [
    el("div", { class: "topo" }, [
      el("div", {}, [
        el("div", { class: "eyebrow", text: `Categoria #${t.rank + 1} em gasto` }),
        el("h4", { style: { marginTop: "4px", fontSize: "19px" }, text: t.nome }),
        el("div", { class: "v", text: brl(t.total) }),
        el("div", { class: "legenda", text:
          `${t.itens} itens · ${cat ? pct(cat.share) : "—"} do gasto · ${cat ? brl(cat.imposto) : "—"} de imposto` }),
      ]),
      el("button", { class: "btn-voltar", onclick: aoFechar, "aria-label": "Fechar a categoria" }, ["voltar"]),
    ]),
    corpo,
  ]);
}

export function torres(hospedeiro) {
  const { torres: lista, maxTotal } = montarTorres();
  const pos = [0, 16, 30];
  const ctx = montarCena(hospedeiro, {
    posInicial: pos, alvoInicial: [0, 2, 0], fov: 42, fog: [44, 110],
  });
  ctx.ctrl.autoRotateSpeed = 0.3;

  const segmentos = [];
  lista.forEach((t, ti) => {
    const escala = (t.total / maxTotal) * ALT_TORRE;
    let base = 0;
    t.meses.forEach((v, mi) => {
      const alt = t.total > 0 ? (v / t.total) * escala : 0;
      if (alt > 0.001) segmentos.push({ torre: ti, mes: mi, base, alt });
      base += alt;
    });
  });

  const malha = new THREE.InstancedMesh(
    new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshStandardMaterial({ roughness: 0.38, metalness: 0.12 }),
    segmentos.length);
  malha.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  ctx.cena.add(malha);
  ctx.cena.add(new THREE.GridHelper(26, 13, 0x1c2620, 0x141a16));

  const cores = new Float32Array(segmentos.length * 3);
  const c0 = new THREE.Color();
  segmentos.forEach((s, i) => {
    c0.set(corPorRank(lista[s.torre].rank, lista.length));
    const f = s.mes % 2 === 0 ? 1 : 0.82;  // marca a divisão dos meses
    cores[i * 3] = c0.r * f; cores[i * 3 + 1] = c0.g * f; cores[i * 3 + 2] = c0.b * f;
  });

  const dummy = new THREE.Object3D(), cor = new THREE.Color();
  const prog = { t: semMovimento() ? 1 : 0 };
  if (!semMovimento()) gsap.to(prog, { t: 1, duration: 2, ease: "power3.out", delay: 0.15 });

  let ativo = null, selecionada = null;
  ctx.aCadaQuadro(() => {
    for (let i = 0; i < segmentos.length; i++) {
      const s = segmentos[i], t = lista[s.torre];
      const atraso = (t.rank / Math.max(1, lista.length - 1)) * 0.45;
      const q = Math.min(1, Math.max(0, (prog.t - atraso) / 0.55));
      const suave = 1 - Math.pow(1 - q, 3);
      const alt = Math.max(0.01, (s.alt - 0.045) * suave);
      const sel = selecionada === t.cat;
      const realce = sel ? 1.12 : ativo === i ? 1.06 : 1;
      dummy.position.set(t.x, s.base * suave + alt / 2, t.z);
      dummy.scale.set(LADO * realce, alt, LADO * realce);
      dummy.updateMatrix();
      malha.setMatrixAt(i, dummy.matrix);
      if (sel) cor.set("#ffffff");
      else {
        const f = selecionada !== null ? 0.32 : ativo === i ? 1.35 : 1;
        cor.setRGB(Math.min(1, cores[i * 3] * f), Math.min(1, cores[i * 3 + 1] * f),
          Math.min(1, cores[i * 3 + 2] * f));
      }
      malha.setColorAt(i, cor);
    }
    malha.instanceMatrix.needsUpdate = true;
    if (malha.instanceColor) malha.instanceColor.needsUpdate = true;
  });

  const dica = el("div", { class: "dica off" });
  hospedeiro.append(dica);

  let lateral = null;
  const fechar = () => {
    selecionada = null;
    if (lateral) { lateral.remove(); lateral = null; }
    ctx.ctrl.autoRotate = !semMovimento();
    voarPara(ctx.camera, ctx.ctrl, new THREE.Vector3(...pos), new THREE.Vector3(0, 2, 0), 1);
  };
  const abrir = (t) => {
    selecionada = t.cat;
    ctx.ctrl.autoRotate = false;
    if (lateral) lateral.remove();
    lateral = painelDaCategoria(t, fechar);
    hospedeiro.append(lateral);
    dica.classList.add("off");
    const h = (t.total / maxTotal) * ALT_TORRE;
    const alvo = new THREE.Vector3(t.x, h * 0.5, t.z);
    voarPara(ctx.camera, ctx.ctrl, pontoDeVista(ctx.camera, alvo, Math.max(9, h * 1.4), 0.35), alvo, 1.1);
  };

  const acha = (ev) => {
    ctx.posDoEvento(ev);
    ctx.raycaster.setFromCamera(ctx.ponteiro, ctx.camera);
    const hits = ctx.raycaster.intersectObject(malha);
    return hits.length ? hits[0].instanceId : null;
  };

  ctx.renderer.domElement.addEventListener("pointermove", (ev) => {
    const id = acha(ev);
    ativo = id;
    if (id === null || selecionada !== null) { dica.classList.add("off"); return; }
    const t = lista[segmentos[id].torre];
    dica.innerHTML = "";
    dica.append(
      el("div", { class: "eyebrow", text: `#${t.rank + 1} · ${t.itens} itens` }),
      el("div", { style: { fontSize: "15px", fontWeight: "600", marginTop: "2px" }, text: t.nome }),
      el("div", { class: "v", style: { fontSize: "19px" }, text: brl(t.total) }),
      el("div", { class: "legenda", text: "clique para abrir a categoria" }),
    );
    dica.classList.remove("off");
  });
  ctx.renderer.domElement.addEventListener("pointerleave", () => {
    ativo = null;
    dica.classList.add("off");
  });
  ctx.renderer.domElement.addEventListener("click", (ev) => {
    const id = acha(ev);
    if (id === null) return;
    abrir(lista[segmentos[id].torre]);
  });
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && selecionada !== null) fechar();
  });

  return { lista, abrir, fechar, selecionada: () => selecionada };
}
