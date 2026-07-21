// rumbo-alfa-centauri/engine.js
'use strict';

const CHARACTERS = [
  { id: 'hija', name: 'Hija', level: '12-15', emoji: '🚀' },
  { id: 'hijo', name: 'Hijo', level: '9-11', emoji: '🛸' },
  { id: 'mama', name: 'Mamá', level: 'adulto', emoji: '🚀' },
  { id: 'papa', name: 'Papá', level: 'adulto', emoji: '🛸' },
];

const BOARD = [
  { name: 'Tierra', emoji: '🌍' },
  { name: 'Luna', emoji: '🌕' },
  { name: 'Marte', emoji: '🔴' },
  { name: 'Cinturón de asteroides', emoji: '🪨' },
  { name: 'Júpiter', emoji: '🪐' },
  { name: 'Saturno', emoji: '🪐' },
  { name: 'Salto cuántico', emoji: '🌀' },
  { name: 'Alfa Centauri', emoji: '✨' },
];
const GOAL_POSITION = BOARD.length - 1;

function findCharacter(id) {
  return CHARACTERS.find((c) => c.id === id);
}

function validateSelection(characterIds) {
  if (!Array.isArray(characterIds) || characterIds.length < 2 || characterIds.length > 4) {
    throw new Error('Se necesitan entre 2 y 4 jugadores');
  }
  const seen = new Set();
  for (const id of characterIds) {
    if (!findCharacter(id)) throw new Error('Personaje inválido: ' + id);
    if (seen.has(id)) throw new Error('Personaje repetido: ' + id);
    seen.add(id);
  }
}

function shuffle(arr, rng) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function buildPools(levels, questions, rng) {
  const pools = {};
  for (const level of levels) {
    pools[level] = shuffle(questions.filter((q) => q.level === level), rng);
  }
  return pools;
}

function createGame(characterIds, questions, rng = Math.random) {
  validateSelection(characterIds);
  const players = characterIds.map((id) => {
    const c = findCharacter(id);
    return { id: c.id, name: c.name, level: c.level, emoji: c.emoji, position: 0, correct: 0, wrong: 0 };
  });
  const levels = [...new Set(players.map((p) => p.level))];
  return {
    players,
    currentPlayerIndex: 0,
    pools: buildPools(levels, questions, rng),
    fullQuestionsByLevel: levels.reduce((acc, l) => {
      acc[l] = questions.filter((q) => q.level === l);
      return acc;
    }, {}),
    rng,
    pendingQuestion: null,
    pendingResult: null,
    winnerId: null,
  };
}

function currentPlayer(game) {
  return game.players[game.currentPlayerIndex];
}

const RumboEngine = {
  CHARACTERS, BOARD, GOAL_POSITION,
  validateSelection, createGame, currentPlayer,
};
if (typeof module !== 'undefined' && module.exports) module.exports = RumboEngine;
if (typeof window !== 'undefined') window.RumboEngine = RumboEngine;
