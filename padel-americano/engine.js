'use strict';

function shuffle(arr, rng) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pairKey(a, b) {
  return a < b ? a + '-' + b : b + '-' + a;
}

// Particiona `active` en parejas nunca usadas, con backtracking. null si imposible.
function findPairing(active, usedPairs, rng) {
  const result = [];
  function bt(remaining) {
    if (remaining.length === 0) return true;
    const first = remaining[0];
    const rest = remaining.slice(1);
    for (const partner of shuffle(rest, rng)) {
      if (usedPairs.has(pairKey(first, partner))) continue;
      result.push([first, partner]);
      if (bt(rest.filter((p) => p !== partner))) return true;
      result.pop();
    }
    return false;
  }
  return bt(shuffle(active, rng)) ? result : null;
}

// Un intento de calendario completo (greedy jornada por jornada).
function tryGenerate(playerCount, courts, rng) {
  const courtsUsed = Math.min(courts, Math.floor(playerCount / 4));
  const activeCount = courtsUsed * 4;
  const usedPairs = new Set();
  const played = new Array(playerCount).fill(0);
  const rounds = [];
  for (;;) {
    let pairing = null;
    let byes = [];
    // Reintentos: el shuffle antes del sort estable aleatoriza los empates
    for (let t = 0; t < 20 && !pairing; t++) {
      const idx = shuffle([...Array(playerCount).keys()], rng).sort(
        (a, b) => played[a] - played[b]
      );
      const active = idx.slice(0, activeCount); // juegan los que menos han jugado
      byes = idx.slice(activeCount).sort((a, b) => a - b);
      pairing = findPairing(active, usedPairs, rng);
    }
    if (!pairing) break;
    const teams = shuffle(pairing, rng);
    const matches = [];
    for (let c = 0; c < courtsUsed; c++) {
      const teamA = teams[2 * c];
      const teamB = teams[2 * c + 1];
      matches.push({ court: c + 1, teamA, teamB, score: null });
      for (const p of [...teamA, ...teamB]) played[p]++;
    }
    for (const [a, b] of pairing) usedPairs.add(pairKey(a, b));
    rounds.push({ matches, byes });
  }
  return rounds;
}

// Mejor calendario entre varios reinicios (maximiza jornadas).
function generateRounds(playerCount, courts, rng = Math.random) {
  let best = null;
  for (let attempt = 0; attempt < 60; attempt++) {
    const rounds = tryGenerate(playerCount, courts, rng);
    if (!best || rounds.length > best.length) best = rounds;
  }
  return best;
}

function createTournament(names, courts, rng = Math.random) {
  if (!Array.isArray(names) || names.length < 6) {
    throw new Error('Se necesitan al menos 6 jugadores');
  }
  if (!Number.isInteger(courts) || courts < 1) {
    throw new Error('Se necesita al menos 1 cancha');
  }
  return {
    players: names.slice(),
    courts,
    rounds: generateRounds(names.length, courts, rng),
  };
}

function setScore(tournament, roundIndex, matchIndex, score) {
  const round = tournament.rounds[roundIndex];
  const match = round && round.matches[matchIndex];
  if (!match) throw new Error('Partido inexistente');
  const [a, b] = score;
  if (!Number.isInteger(a) || !Number.isInteger(b) || a < 0 || b < 0 || a + b !== 4) {
    throw new Error('Marcador inválido: debe sumar 4 games');
  }
  match.score = [a, b];
}

function standings(tournament) {
  const rows = tournament.players.map((name, i) => ({
    player: i,
    name,
    points: 0,
    played: 0,
  }));
  for (const round of tournament.rounds) {
    for (const m of round.matches) {
      if (!m.score) continue;
      const [ga, gb] = m.score;
      for (const p of m.teamA) { rows[p].points += ga; rows[p].played++; }
      for (const p of m.teamB) { rows[p].points += gb; rows[p].played++; }
    }
  }
  rows.sort((x, y) => y.points - x.points);
  let rank = 0;
  let prev = null;
  rows.forEach((r, i) => {
    if (prev === null || r.points < prev) { rank = i + 1; prev = r.points; }
    r.rank = rank;
  });
  return rows;
}

const PadelEngine = { createTournament, generateRounds, pairKey, findPairing, setScore, standings };
if (typeof module !== 'undefined' && module.exports) module.exports = PadelEngine;
if (typeof window !== 'undefined') window.PadelEngine = PadelEngine;
