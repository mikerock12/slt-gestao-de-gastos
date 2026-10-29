const assert=require('node:assert/strict');
global.window={__SLT_DADOS__:{meta:{inicio:'2026-01-01'}}};
const {compararMarcas,visitasLojas,produtosFrequentes}=require('./analitica-test-bundle.cjs');
const d={nomesLojas:['Mercado A','Mercado B'],nomesCategorias:['Bebidas','Pet'],descricoes:['CERVEJA BRAHMA LATA','CERVEJA SKOL','RACAO WHISKAS','CERVEJA BRAHMA SKOL','CERVEJA SEM MARCA'],notasBrutas:[[0,0,0,0,20],[0,0,0,0,15],[1,0,1,0,30],[2,0,1,0,10]],itensBrutos:[[0,0,0,0,10,0,0,0,0,0,1,0,0],[0,0,0,0,5,0,1,0,0,0,1,0,1],[1,1,1,0,30,0,2,0,0,0,1,0,2],[1,0,1,0,10,0,3,0,0,0,1,0,2],[2,0,1,0,10,0,4,0,0,0,1,0,3]]};
const ranking=visitasLojas(d); assert.equal(ranking[0].nome,'Mercado B');assert.equal(ranking[0].dias,2);assert.equal(ranking[1].dias,1);assert.equal(ranking[1].notas,2);
const marcas=compararMarcas(d,'Bebidas','cerveja',['brahma','SKOL','skol']);assert.equal(marcas.elegiveis,4);assert.equal(marcas.ambiguos,1);assert.equal(marcas.semMarca,1);assert.equal(marcas.marcas[0].total,10);assert.equal(marcas.marcas[0].notas,1);
assert.equal(compararMarcas(d,'Pet','cerveja',['BRAHMA']).elegiveis,0);
assert.equal(produtosFrequentes(d,'Bebidas','cerveja').length,4);
console.log('Análise de lojas e marcas: OK');
