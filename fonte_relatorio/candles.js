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
  const selecionadas=new Set(['imposto','comida','alcool']);
  const grafico=el('div',{class:'grafico-periodos'}), resumo=el('div',{class:'valores-finais'}), tabelaDetalhe=el('div',{});
  const anterior=el('button',{type:'button',text:'← Períodos anteriores'}), proximo=el('button',{type:'button',text:'Períodos seguintes →'}), pagina=el('span',{class:'legenda'});
  let fim=null;
  const controles=el('div',{class:'series-controles'},series.map(([k,n,cor])=>{
    const input=el('input',{type:'checkbox',checked:selecionadas.has(k)});
    input.addEventListener('change',()=>{if(input.checked)selecionadas.add(k);else selecionadas.delete(k);desenhar();});
    return el('label',{},[input,el('i',{style:{background:cor},'aria-hidden':'true'}),n]);
  }));
  function desenhar() {
    const todos=agregar(D,seletor.value); const limite=30; if(fim===null)fim=todos.length; fim=Math.max(Math.min(limite,todos.length),Math.min(fim,todos.length));
    const inicio=Math.max(0,fim-limite), ps=todos.slice(inicio,fim), ativas=series.filter(([k])=>selecionadas.has(k));
    anterior.disabled=inicio===0; proximo.disabled=fim===todos.length; pagina.textContent=`${inicio+1}–${fim} de ${todos.length} períodos`;
    const largura=1000,h=360,topo=20,base=300,eixo=805;
    const max=Math.max(1,...ps.flatMap(p=>[p.total,...ativas.map(([k])=>p[k]||0)]));
    const y=v=>base-v/max*(base-topo), x=i=>30+(eixo-55)*(i+.5)/ps.length;
    const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox',`0 0 ${largura} ${h}`);svg.setAttribute('role','img');svg.setAttribute('aria-label','Gasto por período e categorias selecionadas em reais');
    function forma(tag, attrs, txt){const a=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))a.setAttribute(k,v);if(txt!==undefined)a.textContent=txt;svg.append(a);return a;}
    for(let i=0;i<=4;i++){const v=max*i/4,yy=y(v);forma('line',{x1:0,x2:eixo,y1:yy,y2:yy,stroke:'#51463e'});forma('text',{x:eixo+6,y:yy+4,fill:'#efe4da','font-size':12},brl(v));}
    ps.forEach((p,i)=>{const xx=x(i),yy=y(p.total);const rect=forma('rect',{x:xx-7,y:Math.min(base,yy),width:14,height:Math.max(2,Math.abs(base-yy)),fill:'#ff9f4a'});const t=document.createElementNS(ns,'title');t.textContent=`${p.data}: ${brl(p.total)}`;rect.append(t);if(i%Math.ceil(ps.length/10)===0)forma('text',{x:xx,y:322,fill:'#e4d7cc','font-size':11,'text-anchor':'middle'},seletor.value==='mes' ? p.data.slice(0,7) : `${p.data.slice(8,10)}/${p.data.slice(5,7)}/${p.data.slice(2,4)}`);});
    for(const [k,nome,cor] of ativas){forma('polyline',{points:ps.map((p,i)=>`${x(i)},${y(p[k]||0)}`).join(' '),fill:'none',stroke:cor,'stroke-width':2.5});}
    const ultimo=ps.at(-1);
    if(ultimo){const marcadores=[['total','Total','#ff9f4a'],...ativas].map(([k,n,c])=>({nome:n,cor:c,valor:ultimo[k]||0,real:y(ultimo[k]||0)})).sort((a,b)=>a.real-b.real);
      marcadores.forEach((m,i)=>{m.pos=Math.max(m.real,i?marcadores[i-1].pos+18:topo);});
      if(marcadores.at(-1).pos>base){marcadores.at(-1).pos=base;for(let i=marcadores.length-2;i>=0;i--)marcadores[i].pos=Math.min(marcadores[i].pos,marcadores[i+1].pos-18);}
      marcadores.forEach(m=>{forma('path',{d:`M ${eixo-10} ${m.real} L ${eixo+96} ${m.pos}`,stroke:m.cor,fill:'none','stroke-width':1});const t=forma('text',{x:eixo+98,y:m.pos+4,fill:m.cor,'font-size':11},brl(m.valor));const title=document.createElementNS(ns,'title');title.textContent=m.nome;t.append(title);});}
    grafico.replaceChildren(svg);
    resumo.replaceChildren(...(ultimo?[['total','Gasto','#ff9f4a'],...ativas].map(([k,n,c])=>el('span',{style:{borderColor:c},text:`${n}: ${brl(ultimo[k]||0)}`})):[]));
    const tabela=document.createElement('table'); const cab=document.createElement('thead');const linha=document.createElement('tr');
    for(const t of ['Período','Total',...ativas.map(s=>s[1])]) linha.append(el('th',{text:t}));cab.append(linha);tabela.append(cab);
    const corpo=document.createElement('tbody');for(const p of ps){const row=document.createElement('tr');for(const v of [p.data,brl(p.total),...ativas.map(([k])=>brl(p[k]||0))])row.append(el('td',{text:v}));corpo.append(row);}tabela.append(corpo);tabelaDetalhe.replaceChildren(tabela);
  }
  seletor.addEventListener('change',()=>{fim=null;desenhar();});anterior.addEventListener('click',()=>{fim=Math.max(30,fim-30);desenhar();});proximo.addEventListener('click',()=>{fim+=30;desenhar();});desenhar();
  return el('div',{class:'card grafico-card'},[el('div',{class:'grafico-cabecalho'},[el('label',{},['Agrupamento',seletor]),el('p',{text:'O corpo laranja vai de zero ao total pago no período. Escolha as linhas que deseja comparar.'})]),
    el('p',{class:'legenda',text:'Imposto é estimado e já está incluído nos preços. As categorias somam itens antes de descontos e acréscimos; os períodos sem notas podem não refletir todos os seus gastos.'}),
    el('fieldset',{class:'series-fieldset'},[el('legend',{text:'Linhas no gráfico'}),controles]),el('div',{class:'paginacao-grafico'},[anterior,pagina,proximo]),grafico,
    el('p',{class:'legenda',text:'Último período exibido — valores também aparecem à direita do gráfico:'}),resumo,
    el('details',{class:'opcional'},[el('summary',{text:'Ver valores de todos os períodos desta página'}),el('div',{class:'tabwrap'},[tabelaDetalhe])])]);
}
