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

module.exports = { isValidQuestion, LEVELS, CATEGORIES };
