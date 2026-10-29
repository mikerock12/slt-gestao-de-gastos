import {D, el, brl, n0, tabela, tr} from './util.js';

const normalizar = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/[^A-Z0-9]+/g,' ').trim();
const contem = (texto, termo) => !!termo && (` ${normalizar(texto)} `).includes(` ${normalizar(termo)} `);

// A fonte não possui campo de marca: só atribuímos quando um termo informado
// aparece integralmente na descrição. Conflitos permanecem sem atribuição.
export function compararMarcas(dados, categoria, produto, nomes) {
  const marcas = [...new Map(nomes.map(x => x.trim()).filter(x => normalizar(x)).map(x => [normalizar(x),x])).values()];
  const grupos = marcas.map(nome => ({nome, total:0, linhas:0, notas:new Set(), descricoes:new Map()}));
  let elegiveis=0, semMarca=0, ambiguos=0;
  for(const item of dados.itensBrutos) {
    const descricao=dados.descricoes[item[6]] || '';
    if(categoria && dados.nomesCategorias[item[1]] !== categoria) continue;
    if(produto && !contem(descricao,produto)) continue;
    elegiveis++;
    const encontrados=grupos.filter(m => contem(descricao,m.nome));
    if(encontrados.length !== 1) { if(encontrados.length) ambiguos++; else semMarca++; continue; }
    const m=encontrados[0]; m.total+=item[4]; m.linhas++; m.notas.add(item[12]);
    const v=m.descricoes.get(descricao) || {desc:descricao,total:0,linhas:0}; v.total+=item[4];v.linhas++;m.descricoes.set(descricao,v);
  }
  return {elegiveis, semMarca, ambiguos, marcas:grupos.filter(x=>x.linhas).map(m=>({...m,notas:m.notas.size,descricoes:[...m.descricoes.values()].sort((a,b)=>b.total-a.total)})).sort((a,b)=>b.linhas-a.linhas || b.total-a.total)};
}
export function visitasLojas(dados) {
  const lojas=new Map();
  for(const n of dados.notasBrutas) {
    const nome=dados.nomesLojas[n[2]] || 'Não identificado';
    const v=lojas.get(nome)||{nome, dias:new Set(), notas:0,total:0};
    v.dias.add(n[0]);v.notas++;v.total+=n[4];lojas.set(nome,v);
  }
  return [...lojas.values()].map(v=>({...v,dias:v.dias.size,ticket:v.total/v.notas})).sort((a,b)=>b.dias-a.dias || b.notas-a.notas || b.total-a.total);
}
export function produtosFrequentes(dados, categoria, produto) {
  const grupos = new Map();
  for (const i of dados.itensBrutos) {
    const desc = dados.descricoes[i[6]] || '';
    if (categoria && dados.nomesCategorias[i[1]] !== categoria) continue;
    if (produto && !contem(desc,produto)) continue;
    const p = grupos.get(desc) || {desc, total:0, linhas:0, notas:new Set(), lojas:new Set()};
    p.total += i[4]; p.linhas++; p.notas.add(i[12]); p.lojas.add(i[2]); grupos.set(desc,p);
  }
  return [...grupos.values()].map(p=>({...p,notas:p.notas.size,lojas:p.lojas.size})).sort((a,b)=>b.linhas-a.linhas || b.total-a.total);
}
const padrao='Coca Cola, Pepsi, Heineken, Brahma, Skol, Polar, Nestlé, Lacta, Garoto, Sadia, Seara, Perdigão, Ninho, Ypê, Omo, Dove, Colgate, Whiskas, Pedigree, Friskies, Monello, Cat Chow, Dog Chow';
export function painelAnalitico() {
  const categoria=el('select',{'aria-label':'Categoria de produto'}, [el('option',{value:'',text:'Todas as categorias'}), ...D.nomesCategorias.map(n=>el('option',{value:n,text:n}))]);
  const produto=el('input',{type:'search',placeholder:'Ex.: cerveja, leite, ração', 'aria-label':'Filtrar descrição do produto'});
  const marcas=el('input',{type:'text',value:padrao,'aria-label':'Marcas a procurar nas descrições'});
  const resultado=el('div',{'aria-live':'polite'}), produtos=el('div',{});
  function atualizar(){
    const r=compararMarcas(D,categoria.value,produto.value,marcas.value.split(','));
    const linhas=r.marcas.map(m=>tr([m.nome,{v:brl(m.total),n:1},{v:n0(m.linhas),n:1},{v:n0(m.notas),n:1},m.descricoes.slice(0,3).map(d=>d.desc).join(' · ')]));
    const frequentes=produtosFrequentes(D,categoria.value,produto.value);
    produtos.replaceChildren(el('p',{class:'legenda',text:`${n0(frequentes.length)} descrições diferentes no filtro. Linhas não são unidades: quantidades e embalagens podem variar.`}),frequentes.length ? tabela([{t:'Descrição na nota'},{t:'Linhas',n:1},{t:'Notas',n:1},{t:'Lojas',n:1},{t:'Valor dos itens',n:1}],frequentes.slice(0,20).map(p=>tr([p.desc,{v:n0(p.linhas),n:1},{v:n0(p.notas),n:1},{v:n0(p.lojas),n:1},{v:brl(p.total),n:1}]))) : el('p',{text:'Nenhum produto encontrado neste filtro.'}));
    resultado.replaceChildren(el('p',{class:'legenda',text:`${n0(r.elegiveis)} linhas de itens no filtro; ${n0(r.semMarca)} sem marca reconhecida e ${n0(r.ambiguos)} com mais de uma marca, excluídas do ranking.`}),
      linhas.length ? tabela([{t:'Marca procurada'},{t:'Valor dos itens',n:1},{t:'Linhas',n:1},{t:'Notas',n:1},{t:'Descrições encontradas'}],linhas) : el('p',{text:'Nenhuma marca da lista foi encontrada neste filtro.'}));
  }
  for(const input of [categoria,produto,marcas]) input.addEventListener('input',atualizar);
  atualizar();
  const lojas=visitasLojas(D);
  const lista=lojas.slice(0,20).map(l=>tr([l.nome,{v:n0(l.dias),n:1},{v:n0(l.notas),n:1},{v:brl(l.total),n:1},{v:brl(l.ticket),n:1}]));
  return el('div',{class:'analitica'},[
    el('div',{class:'card'},[el('h3',{text:'Estabelecimentos mais frequentados'}),el('p',{class:'legenda',text:'Ordenado por dias distintos com compras, depois por notas. Duas notas no mesmo dia contam um dia; isso não comprova visitas físicas. Lojas são agrupadas pelo nome usado no relatório.'}),
      tabela([{t:'Estabelecimento'},{t:'Dias com compra',n:1},{t:'Notas',n:1},{t:'Total pago',n:1},{t:'Por nota',n:1}],lista)]),
    el('div',{class:'card'},[el('h3',{text:'Compare marcas por produto'}),el('p',{class:'legenda',text:'Selecione a categoria, filtre pelo nome do produto e edite a lista de marcas separadas por vírgulas. O ranking ordena pelo número de linhas de itens; o reconhecimento procura palavras inteiras na descrição; não confirma a marca real e pode perder abreviações. Confira as descrições. Valores são dos itens, antes de descontos ou acréscimos da nota.'}),
      el('div',{class:'filtros-analise'},[el('label',{},['Categoria',categoria]),el('label',{},['Produto na descrição',produto]),el('label',{},['Marcas para procurar',marcas])]),resultado]),
    el('div',{class:'card'},[el('h3',{text:'Produtos que mais se repetem'}),el('p',{class:'legenda',text:'Usa os mesmos filtros de categoria e produto acima; cada linha representa uma descrição exatamente como aparece na nota.'}),produtos])]);
}
