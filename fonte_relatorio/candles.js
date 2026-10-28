import {D, el, brl, diaParaISO} from './util.js';

const series = [
  ['imposto', 'Impostos estimados', '#f3ce75'],
  ['alcool', 'Bebidas alcoólicas', '#dd91e9'],
  ['comida', 'Alimentação sem álcool', '#70d9a2'],
  ['gato', 'Ração de gato identificada', '#f5a56c'],
  ['higiene', 'Higiene', '#83baff'],
  ['limpeza', 'Limpeza', '#6fd5d9'],
  ['medicamento', 'Medicamentos', '#ed8ca0'],
  ['outro', 'Outros produtos pet', '#b7b1ef'],
];
const gato = /\b(rac[aã]o|alimento)\b.*\b(gato|gatos|felin[oa]s?)\b|\b(gato|gatos|felin[oa]s?)\b.*\b(rac[aã]o|alimento)\b/i;
function inicioPeriodo(iso, modo) {
  if (modo === 'mes') return iso.slice(0, 7) + '-01';
  if (modo === 'semana') {
    const d = new Date(iso + 'T00:00:00Z');
    d.setUTCDate(d.getUTCDate() - (d.getUTCDay() + 6) % 7);
    return d.toISOString().slice(0, 10);
  }
  return iso;
}
export function agregar(dados, modo) {
  const periodos = new Map();
  function periodo(dia) {
    const key = inicioPeriodo(diaParaISO(dia), modo);
    if (!periodos.has(key)) periodos.set(key, {data:key, total:0});
    return periodos.get(key);
  }
  for (const n of dados.notasBrutas) {
    const p = periodo(n[0]); p.total += n[4]; p.imposto = (p.imposto || 0) + n[6];
  }
  for (const i of dados.itensBrutos) {
    const p = periodo(i[0]); const dom = dados.dominios[i[7]];
    const grupo = dados.gruposAlim[i[8]];
    const desc = dados.descricoes[i[6]] || '';
    let k = dom === 'alimentacao' ? (grupo === 'Bebidas alcoólicas' ? 'alcool' : 'comida') : dom;
    if (dom === 'pet') k = gato.test(desc) ? 'gato' : 'outro';
    if (series.some(s => s[0] === k && k !== 'imposto')) p[k] = (p[k] || 0) + i[4];
  }
  // Inclui períodos sem compras para não esconder dias ou meses zerados.
  const d = new Date(dados.meta.inicio + 'T00:00:00Z');
  const fim = new Date(dados.meta.fim + 'T00:00:00Z');
  while (d <= fim) {
    const key = inicioPeriodo(d.toISOString().slice(0, 10), modo);
    if (!periodos.has(key)) periodos.set(key, {data:key, total:0});
    d.setUTCDate(d.getUTCDate() + 1);
  }
  return [...periodos.values()].sort((a,b) => a.data.localeCompare(b.data));
}
export function painelCandles() {
  const seletor = el('select', {'aria-label':'Agrupar gastos por período'}, [
    el('option', {value:'dia', text:'Diário'}), el('option', {value:'semana', text:'Semanal'}), el('option', {value:'mes', text:'Mensal'})]);
  const grafico = el('div', {style:{overflowX:'auto'}});
  const resumo = el('div', {style:{display:'flex',flexWrap:'wrap',gap:'12px',marginTop:'12px'}});
  function desenhar() {
    const ps = agregar(D, seletor.value); const largura = Math.max(820, ps.length * 44 + 200), h = 360, topo = 20, base = 310, eixo = largura - 180;
    const max = Math.max(1, ...ps.flatMap(p => [p.total, ...series.map(([k]) => p[k] || 0)]));
    const y = v => base - (v / max) * (base-topo); const x = i => 25 + (eixo - 50) * (i + .5) / ps.length;
    const ns='http://www.w3.org/2000/svg'; const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox',`0 0 ${largura} ${h}`); svg.setAttribute('width',largura); svg.setAttribute('height',h); svg.setAttribute('role','img'); svg.setAttribute('aria-label','Gasto por período e categorias em reais');
    function forma(tag, attrs, txt) { const a=document.createElementNS(ns,tag); for(const [k,v] of Object.entries(attrs)) a.setAttribute(k,v); if(txt !== undefined) a.textContent=txt; svg.append(a); return a; }
    for(let i=0;i<=4;i++){const v=max*i/4, yy=y(v); forma('line',{x1:0,x2:eixo,y1:yy,y2:yy,stroke:'#39443e'}); forma('text',{x:eixo+8,y:yy+4,fill:'#dce9df','font-size':11},brl(v));}
    ps.forEach((p,i)=>{const xx=x(i), yy=y(p.total); const rect=forma('rect',{x:xx-7,y:Math.min(base,yy),width:14,height:Math.max(2,Math.abs(base-yy)),fill:'#4ec397'}); const title=document.createElementNS(ns,'title'); title.textContent=`${p.data}: ${brl(p.total)}`; rect.append(title); if(ps.length<=16 || i % Math.ceil(ps.length/12)===0) forma('text',{x:xx,y:335,fill:'#b8c8bd','font-size':10,'text-anchor':'middle'},p.data.slice(5)); });
    for(const [k,nome,cor] of series) { const pontos=ps.map((p,i)=>`${x(i)},${y(p[k]||0)}`).join(' '); forma('polyline',{points:pontos,fill:'none',stroke:cor,'stroke-width':2}); const ultimo=ps.at(-1); if(ultimo){const yy=y(ultimo[k]||0); const t=forma('circle',{cx:x(ps.length-1),cy:yy,r:3,fill:cor}); const title=document.createElementNS(ns,'title');title.textContent=`${nome}: ${brl(ultimo[k]||0)}`;t.append(title);} }
    // Valores finais com conectores e espaçamento para evitar sobreposição.
    const ultimo = ps.at(-1);
    if (ultimo) {
      const marcadores = [['total','Total','#4ec397'], ...series]
        .map(([k,n,c]) => ({nome:n, cor:c, valor:ultimo[k] || 0, real:y(ultimo[k] || 0)}))
        .sort((a,b) => a.real-b.real);
      marcadores.forEach((m,i) => { m.pos = Math.max(m.real, i ? marcadores[i-1].pos + 16 : topo); });
      if (marcadores.at(-1).pos > base) {
        marcadores.at(-1).pos = base;
        for (let i=marcadores.length-2;i>=0;i--) marcadores[i].pos=Math.min(marcadores[i].pos,marcadores[i+1].pos-16);
      }
      marcadores.forEach(m => {
        forma('path',{d:`M ${eixo-15} ${m.real} L ${eixo+62} ${m.pos}`,stroke:m.cor,fill:'none','stroke-width':1});
        const t=forma('text',{x:eixo+64,y:m.pos+4,fill:m.cor,'font-size':10},brl(m.valor));
        const title=document.createElementNS(ns,'title'); title.textContent=m.nome; t.append(title);
      });
    }
    grafico.replaceChildren(svg); resumo.replaceChildren(...(ultimo ? [['total','Gasto', '#4ec397'],...series].map(([k,n,c]) => el('span',{style:{color:c},text:`${n}: ${brl(ultimo[k]||0)}`})) : []));
  }
  seletor.addEventListener('change',desenhar); desenhar();
  return el('div',{},[seletor,el('p',{text:'Cada candle vai de zero ao total pago no período. As linhas mostram totais de itens; impostos são estimados e já estão incluídos no gasto. A classificação depende da descrição e pode falhar; ração sem indicação de gato fica em pet.'}),grafico,el('p',{text:'Valores do último período (passe o mouse sobre um candle para consultar seu total):'}),resumo]);
}
