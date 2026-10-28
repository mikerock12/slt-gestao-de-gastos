const assert = require('node:assert/strict');
global.window = {__SLT_DADOS__: {meta:{inicio:'2026-01-01'}}};
const {agregar} = require('./candles-test-bundle.cjs');
const d = {meta:{inicio:'2026-01-01',fim:'2026-01-03'}, notasBrutas:[[0,0,0,0,100,1,10],[2,0,0,0,20,1,2]], itensBrutos:[[0,0,0,0,40,0,0,0,0],[2,0,0,0,20,0,1,1,-1]], dominios:['alimentacao','pet'], gruposAlim:['Bebidas alcoólicas'], descricoes:['cerveja','racao gatos']};
const dias = agregar(d,'dia');
assert.equal(dias.length,3); assert.equal(dias[0].total,100); assert.equal(dias[0].alcool,40); assert.equal(dias[1].total,0); assert.equal(dias[2].gato,20);
const mes = agregar(d,'mes'); assert.equal(mes.length,1); assert.equal(mes[0].total,120); assert.equal(mes[0].imposto,12);
console.log('Agregação diária e mensal: OK');
