// rumbo-alfa-centauri/tests/engine.test.js
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const {
  CHARACTERS, BOARD, GOAL_POSITION,
  validateSelection, createGame, currentPlayer, drawQuestion, submitAnswer,
} = require('../engine.js');

test('CHARACTERS tiene los 4 personajes fijos con su nivel', () => {
  assert.strictEqual(CHARACTERS.length, 4);
  const byId = Object.fromEntries(CHARACTERS.map((c) => [c.id, c]));
  assert.strictEqual(byId.hija.level, '12-15');
  assert.strictEqual(byId.hijo.level, '9-11');
  assert.strictEqual(byId.mama.level, 'adulto');
  assert.strictEqual(byId.papa.level, 'adulto');
});

test('BOARD tiene 8 casillas y GOAL_POSITION es la última', () => {
  assert.strictEqual(BOARD.length, 8);
  assert.strictEqual(GOAL_POSITION, 7);
  assert.strictEqual(BOARD[0].name, 'Tierra');
  assert.strictEqual(BOARD[7].name, 'Alfa Centauri');
});

test('validateSelection rechaza menos de 2 jugadores', () => {
  assert.throws(() => validateSelection(['hija']));
});

test('validateSelection rechaza más de 4 jugadores', () => {
  assert.throws(() => validateSelection(['hija', 'hijo', 'mama', 'papa', 'hija']));
});

test('validateSelection rechaza un id de personaje inválido', () => {
  assert.throws(() => validateSelection(['hija', 'primo']));
});

test('validateSelection rechaza personajes repetidos', () => {
  assert.throws(() => validateSelection(['hija', 'hija']));
});

test('createGame arranca con todos los jugadores en posición 0 y el primero activo', () => {
  const game = createGame(['hijo', 'papa', 'hija'], []);
  assert.strictEqual(game.players.length, 3);
  assert.ok(game.players.every((p) => p.position === 0));
  assert.strictEqual(game.currentPlayerIndex, 0);
  assert.strictEqual(currentPlayer(game).id, 'hijo');
  assert.strictEqual(game.winnerId, null);
  assert.strictEqual(game.pendingQuestion, null);
});

function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const FIXTURE_QUESTIONS = [
  { id: 'q1', level: '9-11', category: 'espacio', question: '¿1?', options: ['a', 'b', 'c'], correctIndex: 0, explanation: 'e1' },
  { id: 'q2', level: '9-11', category: 'fisica', question: '¿2?', options: ['a', 'b', 'c'], correctIndex: 1, explanation: 'e2' },
  { id: 'q3', level: 'adulto', category: 'quimica', question: '¿3?', options: ['a', 'b', 'c'], correctIndex: 2, explanation: 'e3' },
  { id: 'q4', level: 'adulto', category: 'biologia', question: '¿4?', options: ['a', 'b', 'c'], correctIndex: 0, explanation: 'e4' },
];

test('drawQuestion regresa una pregunta del nivel del jugador activo', () => {
  const game = createGame(['hijo', 'mama'], FIXTURE_QUESTIONS, mulberry32(1));
  const q = drawQuestion(game);
  assert.strictEqual(q.level, '9-11');
  assert.strictEqual(game.pendingQuestion, q);
});

test('drawQuestion no repite preguntas dentro de la partida hasta agotar el pool, y luego se reinicia', () => {
  const game = createGame(['mama', 'papa'], FIXTURE_QUESTIONS, mulberry32(2));
  // mamá y papá comparten nivel 'adulto', que solo tiene 2 preguntas en el fixture (q3, q4)
  const seen = [];
  for (let i = 0; i < 4; i++) {
    const q = drawQuestion(game);
    seen.push(q.id);
    game.pendingQuestion = null; // simula que ya se procesó el turno sin usar answerQuestion todavía
  }
  // las primeras 2 no deben repetirse entre sí
  assert.notStrictEqual(seen[0], seen[1]);
  assert.deepStrictEqual(new Set(seen.slice(0, 2)), new Set(['q3', 'q4']));
  // tras agotar el pool de 2, la 3ra y 4ta vienen del pool reiniciado
  assert.ok(['q3', 'q4'].includes(seen[2]));
  assert.ok(['q3', 'q4'].includes(seen[3]));
});

test('drawQuestion lanza error si ya hay una pregunta pendiente sin responder', () => {
  const game = createGame(['hijo', 'mama'], FIXTURE_QUESTIONS, mulberry32(3));
  drawQuestion(game);
  assert.throws(() => drawQuestion(game));
});

test('submitAnswer marca correcto si el índice coincide con correctIndex', () => {
  const game = createGame(['hijo', 'mama'], FIXTURE_QUESTIONS, mulberry32(4));
  const q = drawQuestion(game);
  const result = submitAnswer(game, q.correctIndex);
  assert.strictEqual(result.correct, true);
  assert.strictEqual(game.pendingResult, result);
});

test('submitAnswer marca incorrecto si el índice no coincide', () => {
  const game = createGame(['hijo', 'mama'], FIXTURE_QUESTIONS, mulberry32(5));
  const q = drawQuestion(game);
  const wrongIndex = (q.correctIndex + 1) % 3;
  const result = submitAnswer(game, wrongIndex);
  assert.strictEqual(result.correct, false);
});

test('submitAnswer lanza error si no hay pregunta pendiente', () => {
  const game = createGame(['hijo', 'mama'], FIXTURE_QUESTIONS, mulberry32(6));
  assert.throws(() => submitAnswer(game, 0));
});
