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

test('nivel 9-11 tiene 40 preguntas válidas, 10 por categoría', () => {
  const nivel = QUESTIONS.filter((q) => q.level === '9-11');
  assert.strictEqual(nivel.length, 40);
  for (const cat of CATEGORIES) {
    assert.strictEqual(
      nivel.filter((q) => q.category === cat).length, 10,
      `nivel 9-11, categoría ${cat}`
    );
  }
  for (const q of nivel) assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
});

test('nivel 12-15 tiene 40 preguntas válidas, 10 por categoría', () => {
  const nivel = QUESTIONS.filter((q) => q.level === '12-15');
  assert.strictEqual(nivel.length, 40);
  for (const cat of CATEGORIES) {
    assert.strictEqual(
      nivel.filter((q) => q.category === cat).length, 10,
      `nivel 12-15, categoría ${cat}`
    );
  }
  for (const q of nivel) assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
});

test('nivel adulto tiene 40 preguntas válidas, 10 por categoría', () => {
  const nivel = QUESTIONS.filter((q) => q.level === 'adulto');
  assert.strictEqual(nivel.length, 40);
  for (const cat of CATEGORIES) {
    assert.strictEqual(
      nivel.filter((q) => q.category === cat).length, 10,
      `nivel adulto, categoría ${cat}`
    );
  }
  for (const q of nivel) assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
});

test('cada nivel tiene una progresión de dificultad (12 fáciles, 16 medias, 12 difíciles)', () => {
  for (const level of LEVELS) {
    const nivel = QUESTIONS.filter((q) => q.level === level);
    const counts = { 1: 0, 2: 0, 3: 0 };
    for (const q of nivel) counts[q.difficulty]++;
    assert.strictEqual(counts[1], 12, `nivel ${level}, dificultad 1 (fácil)`);
    assert.strictEqual(counts[2], 16, `nivel ${level}, dificultad 2 (media)`);
    assert.strictEqual(counts[3], 12, `nivel ${level}, dificultad 3 (difícil)`);
  }
});

test('el banco completo tiene 120 preguntas sin ids duplicados y con datos válidos', () => {
  assert.strictEqual(QUESTIONS.length, 120);
  const ids = new Set();
  for (const q of QUESTIONS) {
    assert.ok(isValidQuestion(q), `pregunta inválida: ${q.id}`);
    assert.ok(!ids.has(q.id), `id duplicado: ${q.id}`);
    ids.add(q.id);
  }
});

module.exports = { isValidQuestion, LEVELS, CATEGORIES };
