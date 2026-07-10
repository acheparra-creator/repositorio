'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { createTournament, generateRounds, pairKey } = require('../engine.js');

// RNG determinista (mulberry32) para pruebas reproducibles
function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const CASES = [];
for (const n of [6, 8, 10, 12, 16]) {
  for (const courts of [1, 2, 3]) CASES.push([n, courts]);
}

test('ninguna pareja se repite en todo el torneo', () => {
  for (const [n, courts] of CASES) {
    const rounds = generateRounds(n, courts, mulberry32(42));
    const seen = new Set();
    for (const round of rounds) {
      for (const m of round.matches) {
        for (const team of [m.teamA, m.teamB]) {
          const key = pairKey(team[0], team[1]);
          assert.ok(!seen.has(key), `pareja repetida ${key} (n=${n}, courts=${courts})`);
          seen.add(key);
        }
      }
    }
  }
});

test('cada jornada usa min(canchas, floor(N/4)) canchas y nadie juega dos veces en la jornada', () => {
  for (const [n, courts] of CASES) {
    const expected = Math.min(courts, Math.floor(n / 4));
    const rounds = generateRounds(n, courts, mulberry32(7));
    assert.ok(rounds.length >= 1, `sin jornadas (n=${n}, courts=${courts})`);
    for (const round of rounds) {
      assert.strictEqual(round.matches.length, expected);
      const inRound = [];
      for (const m of round.matches) inRound.push(...m.teamA, ...m.teamB);
      inRound.push(...round.byes);
      assert.strictEqual(inRound.length, n, 'todos los jugadores aparecen una vez');
      assert.strictEqual(new Set(inRound).size, n, 'sin duplicados en la jornada');
    }
  }
});

test('los descansos son equitativos: diferencia de partidos jugados <= 1 al final', () => {
  for (const [n, courts] of CASES) {
    const rounds = generateRounds(n, courts, mulberry32(99));
    const played = new Array(n).fill(0);
    for (const round of rounds) {
      for (const m of round.matches) {
        for (const p of [...m.teamA, ...m.teamB]) played[p]++;
      }
    }
    const diff = Math.max(...played) - Math.min(...played);
    assert.ok(diff <= 1, `diferencia ${diff} > 1 (n=${n}, courts=${courts})`);
  }
});

test('con 8 jugadores y 2 canchas salen varias jornadas', () => {
  const rounds = generateRounds(8, 2, mulberry32(1));
  assert.ok(rounds.length >= 5, `solo ${rounds.length} jornadas`);
});

test('createTournament valida entradas', () => {
  assert.throws(() => createTournament(['a', 'b', 'c', 'd', 'e'], 1), /al menos 6/);
  assert.throws(() => createTournament(['a', 'b', 'c', 'd', 'e', 'f'], 0), /al menos 1 cancha/);
  const t = createTournament(['a', 'b', 'c', 'd', 'e', 'f'], 2, mulberry32(3));
  assert.strictEqual(t.players.length, 6);
  assert.strictEqual(t.courts, 2);
  assert.ok(Array.isArray(t.rounds) && t.rounds.length >= 1);
  for (const m of t.rounds[0].matches) assert.strictEqual(m.score, null);
});
