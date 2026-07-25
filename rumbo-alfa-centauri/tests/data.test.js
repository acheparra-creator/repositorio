// rumbo-alfa-centauri/tests/data.test.js
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { QUESTIONS } = require('../data.js');

const LEVELS = ['9-11', '12-15', 'adulto'];
const CATEGORIES = ['espacio', 'fisica', 'biologia', 'quimica'];

function isValidQuestion(q) {
  return (
    typeof q.id === 'string' && q.id.length > 0 &&
    LEVELS.includes(q.level) &&
    CATEGORIES.includes(q.category) &&
    [1, 2, 3].includes(q.difficulty) &&
    typeof q.question === 'string' && q.question.length > 0 &&
    Array.isArray(q.options) && q.options.length === 3 &&
    q.options.every((o) => typeof o === 'string' && o.length > 0) &&
    Number.isInteger(q.correctIndex) && q.correctIndex >= 0 && q.correctIndex <= 2 &&
    typeof q.explanation === 'string' && q.explanation.length > 0
  );
}

test('QUESTIONS es un arreglo', () => {
  assert.ok(Array.isArray(QUESTIONS));
});

test('nivel 9-11 tiene 96 preguntas válidas, 24 por categoría', () => {
  const nivel = QUESTIONS.filter((q) => q.level === '9-11');
  assert.strictEqual(nivel.length, 96);
  for (const cat of CATEGORIES) {
    assert.strictEqual(
      nivel.filter((q) => q.category === cat).length, 24,
      `nivel 9-11, categoría ${cat}`
    );
  }
  for (const q of nivel) assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
});

test('nivel 12-15 tiene 96 preguntas válidas, 24 por categoría', () => {
  const nivel = QUESTIONS.filter((q) => q.level === '12-15');
  assert.strictEqual(nivel.length, 96);
  for (const cat of CATEGORIES) {
    assert.strictEqual(
      nivel.filter((q) => q.category === cat).length, 24,
      `nivel 12-15, categoría ${cat}`
    );
  }
  for (const q of nivel) assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
});

test('nivel adulto tiene 96 preguntas válidas, 24 por categoría', () => {
  const nivel = QUESTIONS.filter((q) => q.level === 'adulto');
  assert.strictEqual(nivel.length, 96);
  for (const cat of CATEGORIES) {
    assert.strictEqual(
      nivel.filter((q) => q.category === cat).length, 24,
      `nivel adulto, categoría ${cat}`
    );
  }
  for (const q of nivel) assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
});

test('cada nivel tiene una progresión de dificultad (24 fáciles, 40 medias, 32 difíciles)', () => {
  for (const level of LEVELS) {
    const nivel = QUESTIONS.filter((q) => q.level === level);
    const counts = { 1: 0, 2: 0, 3: 0 };
    for (const q of nivel) counts[q.difficulty]++;
    assert.strictEqual(counts[1], 24, `nivel ${level}, dificultad 1 (fácil)`);
    assert.strictEqual(counts[2], 40, `nivel ${level}, dificultad 2 (media)`);
    assert.strictEqual(counts[3], 32, `nivel ${level}, dificultad 3 (difícil)`);
  }
});

// --- Anti-pistas: la respuesta correcta no debe delatarse sola ---

test('la opción más larga no es la correcta más del 45% de las veces', () => {
  let longestIsCorrect = 0;
  for (const q of QUESTIONS) {
    const lens = q.options.map((o) => o.length);
    if (lens[q.correctIndex] === Math.max(...lens)) longestIsCorrect++;
  }
  const pct = (100 * longestIsCorrect) / QUESTIONS.length;
  assert.ok(pct <= 45, `la más larga es correcta en ${pct.toFixed(1)}% de las preguntas (máx 45%, azar ~33%)`);
});

test('la respuesta correcta se reparte entre las tres posiciones (cada una 25%-42%)', () => {
  const counts = [0, 0, 0];
  for (const q of QUESTIONS) counts[q.correctIndex]++;
  counts.forEach((n, i) => {
    const pct = (100 * n) / QUESTIONS.length;
    assert.ok(pct >= 25 && pct <= 42, `posición ${i} es correcta en ${pct.toFixed(1)}% (debe estar entre 25% y 42%)`);
  });
});

test('dentro de una pregunta ninguna opción es desproporcionadamente larga', () => {
  for (const q of QUESTIONS) {
    const lens = q.options.map((o) => o.length);
    const min = Math.min(...lens);
    if (min < 12) continue; // opciones cortas (números, nombres) son parejas por naturaleza
    assert.ok(
      Math.max(...lens) <= min * 2.2,
      `${q.id}: opciones muy dispares (${lens.join('/')} caracteres)`
    );
  }
});

test('el banco completo tiene 288 preguntas sin ids duplicados y con datos válidos', () => {
  assert.strictEqual(QUESTIONS.length, 288);
  const ids = new Set();
  for (const q of QUESTIONS) {
    assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
    assert.ok(!ids.has(q.id), `id duplicado: ${q.id}`);
    ids.add(q.id);
  }
});

module.exports = { isValidQuestion, LEVELS, CATEGORIES };
