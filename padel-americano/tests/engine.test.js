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

const { setScore, standings } = require('../engine.js');

function fixedTournament() {
  // Torneo artificial de 6 jugadores con 2 jornadas conocidas
  return {
    players: ['Ana', 'Beto', 'Caro', 'Dani', 'Efra', 'Fer'],
    courts: 1,
    rounds: [
      { matches: [{ court: 1, teamA: [0, 1], teamB: [2, 3], score: null }], byes: [4, 5] },
      { matches: [{ court: 1, teamA: [0, 2], teamB: [4, 5], score: null }], byes: [1, 3] },
    ],
  };
}

test('setScore acepta marcadores que suman 4 y rechaza el resto', () => {
  const t = fixedTournament();
  setScore(t, 0, 0, [3, 1]);
  assert.deepStrictEqual(t.rounds[0].matches[0].score, [3, 1]);
  assert.throws(() => setScore(t, 0, 0, [3, 2]), /sumar 4/);
  assert.throws(() => setScore(t, 0, 0, [5, -1]), /sumar 4/);
  assert.throws(() => setScore(t, 9, 0, [2, 2]), /inexistente/);
});

test('standings suma games individuales y cuenta partidos jugados', () => {
  const t = fixedTournament();
  setScore(t, 0, 0, [3, 1]); // Ana+Beto 3, Caro+Dani 1
  setScore(t, 1, 0, [2, 2]); // Ana+Caro 2, Efra+Fer 2
  const rows = standings(t);
  const byName = Object.fromEntries(rows.map((r) => [r.name, r]));
  assert.strictEqual(byName['Ana'].points, 5); // 3 + 2
  assert.strictEqual(byName['Ana'].played, 2);
  assert.strictEqual(byName['Beto'].points, 3);
  assert.strictEqual(byName['Caro'].points, 3); // 1 + 2
  assert.strictEqual(byName['Dani'].points, 1);
  assert.strictEqual(byName['Efra'].points, 2);
  assert.strictEqual(byName['Fer'].points, 2);
});

test('standings: corrección de resultado recalcula', () => {
  const t = fixedTournament();
  setScore(t, 0, 0, [4, 0]);
  setScore(t, 0, 0, [1, 3]); // corrección
  const byName = Object.fromEntries(standings(t).map((r) => [r.name, r]));
  assert.strictEqual(byName['Ana'].points, 1);
  assert.strictEqual(byName['Caro'].points, 3);
});

test('standings: empatados comparten posición (ranking 1,1,3...)', () => {
  const t = fixedTournament();
  setScore(t, 0, 0, [2, 2]); // Ana,Beto,Caro,Dani = 2; Efra,Fer = 0
  const rows = standings(t);
  assert.strictEqual(rows[0].rank, 1);
  assert.strictEqual(rows[1].rank, 1);
  assert.strictEqual(rows[2].rank, 1);
  assert.strictEqual(rows[3].rank, 1);
  assert.strictEqual(rows[4].rank, 5);
  assert.strictEqual(rows[5].rank, 5);
});

test('standings sin resultados: todos 0 puntos, 0 jugados, rank 1', () => {
  const rows = standings(fixedTournament());
  for (const r of rows) {
    assert.strictEqual(r.points, 0);
    assert.strictEqual(r.played, 0);
    assert.strictEqual(r.rank, 1);
  }
});
