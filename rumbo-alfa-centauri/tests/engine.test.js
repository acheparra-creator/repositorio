// rumbo-alfa-centauri/tests/engine.test.js
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const {
  CHARACTERS, BOARD, GOAL_POSITION,
  validateSelection, createGame, currentPlayer,
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
