# Pádel Americano — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** App web móvil (HTML + JS vanilla, sin build ni servidor) para torneos de pádel americano: genera jornadas sin repetir parejas, captura resultados a 4 games y calcula tabla individual de puntos.

**Architecture:** Lógica pura en `engine.js` (generación de jornadas con backtracking, captura de marcadores, tabla de posiciones) testeable con Node; UI en `index.html` que carga `engine.js` y persiste en localStorage. Distribución por GitHub Pages y como Artifact (versión con engine inlineado).

**Tech Stack:** JavaScript vanilla (ES2020), `node --test` (sin dependencias), localStorage, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-07-10-padel-americano-design.md`

---

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `padel-americano/engine.js` | Lógica pura: `createTournament`, `generateRounds`, `setScore`, `standings`. Sin DOM. Exporta para Node y expone global `PadelEngine` en navegador. |
| `padel-americano/index.html` | UI completa: pantalla de configuración, jornadas con captura de marcador, tabla de posiciones, persistencia localStorage. |
| `padel-americano/tests/engine.test.js` | Pruebas con `node:test` y RNG sembrado. |

---

### Task 1: Motor de generación de jornadas (`generateRounds`, `createTournament`)

**Files:**
- Create: `padel-americano/engine.js`
- Test: `padel-americano/tests/engine.test.js`

- [ ] **Step 1: Escribir pruebas que fallan**

Crear `padel-americano/tests/engine.test.js`:

```js
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
```

- [ ] **Step 2: Correr las pruebas y verificar que fallan**

Run: `node --test padel-americano/tests/`
Expected: FAIL — `Cannot find module '../engine.js'`

- [ ] **Step 3: Implementar el motor**

Crear `padel-americano/engine.js`:

```js
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

const PadelEngine = { createTournament, generateRounds, pairKey, findPairing };
if (typeof module !== 'undefined' && module.exports) module.exports = PadelEngine;
if (typeof window !== 'undefined') window.PadelEngine = PadelEngine;
```

- [ ] **Step 4: Correr las pruebas y verificar que pasan**

Run: `node --test padel-americano/tests/`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add padel-americano/engine.js padel-americano/tests/engine.test.js
git commit -m "feat(padel): motor de jornadas americano sin repetir parejas"
```

---

### Task 2: Marcadores y tabla de posiciones (`setScore`, `standings`)

**Files:**
- Modify: `padel-americano/engine.js`
- Test: `padel-americano/tests/engine.test.js`

- [ ] **Step 1: Agregar pruebas que fallan**

Añadir al final de `padel-americano/tests/engine.test.js` (y agregar `setScore, standings` al require del inicio):

```js
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
```

- [ ] **Step 2: Correr las pruebas y verificar que fallan**

Run: `node --test padel-americano/tests/`
Expected: FAIL — `setScore is not a function`

- [ ] **Step 3: Implementar `setScore` y `standings`**

En `padel-americano/engine.js`, antes de la línea `const PadelEngine = ...`:

```js
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
```

Y actualizar la línea de exports:

```js
const PadelEngine = { createTournament, generateRounds, pairKey, findPairing, setScore, standings };
```

- [ ] **Step 4: Correr las pruebas y verificar que pasan**

Run: `node --test padel-americano/tests/`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add padel-americano/engine.js padel-americano/tests/engine.test.js
git commit -m "feat(padel): marcadores a 4 games y tabla de posiciones individual"
```

---

### Task 3: Interfaz completa (`index.html`)

**Files:**
- Create: `padel-americano/index.html`

- [ ] **Step 1: Crear `padel-americano/index.html` con este contenido completo**

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pádel Americano</title>
<style>
  :root {
    --bg: #f4f6f8; --card: #ffffff; --ink: #1a2b3c; --muted: #6b7a89;
    --accent: #0a7d4f; --accent-ink: #ffffff; --line: #dfe5ea; --warn: #b3261e;
  }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--ink); }
  .wrap { max-width: 560px; margin: 0 auto; padding: 12px 12px 80px; }
  h1 { font-size: 1.3rem; margin: 8px 0 16px; }
  h2 { font-size: 1.05rem; margin: 18px 0 8px; }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px; margin-bottom: 12px; }
  label { display: block; font-size: .9rem; color: var(--muted); margin: 10px 0 4px; }
  input[type=number], input[type=text] {
    width: 100%; padding: 12px; font-size: 1rem; border: 1px solid var(--line); border-radius: 8px;
  }
  button { font-size: 1rem; border: none; border-radius: 10px; padding: 12px 16px; cursor: pointer; }
  .primary { background: var(--accent); color: var(--accent-ink); width: 100%; margin-top: 14px; }
  .danger { background: transparent; color: var(--warn); border: 1px solid var(--warn); width: 100%; margin-top: 20px; }
  .error { color: var(--warn); font-size: .9rem; margin-top: 8px; }
  .tabs { position: fixed; bottom: 0; left: 0; right: 0; display: flex; background: var(--card); border-top: 1px solid var(--line); }
  .tabs button { flex: 1; border-radius: 0; background: var(--card); color: var(--muted); padding: 14px; }
  .tabs button.active { color: var(--accent); font-weight: 700; }
  .match { border-top: 1px solid var(--line); padding: 10px 0; }
  .match:first-of-type { border-top: none; }
  .teams { font-size: .98rem; margin-bottom: 8px; }
  .court { color: var(--muted); font-size: .8rem; }
  .scores { display: flex; gap: 6px; }
  .scores button {
    flex: 1; padding: 10px 0; background: var(--bg); border: 1px solid var(--line); color: var(--ink); font-weight: 600;
  }
  .scores button.sel { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
  .byes { color: var(--muted); font-size: .85rem; margin-top: 8px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); font-size: .95rem; }
  th { color: var(--muted); font-size: .8rem; text-transform: uppercase; }
  td.num, th.num { text-align: right; }
  .done { color: var(--accent); font-size: .85rem; }
</style>
</head>
<body>
<div class="wrap" id="app"></div>
<div class="tabs" id="tabs" hidden>
  <button id="tabRounds" onclick="ui.tab='rounds';render()">Jornadas</button>
  <button id="tabTable" onclick="ui.tab='table';render()">Tabla</button>
</div>
<script src="engine.js"></script>
<script>
'use strict';
const KEY = 'padel-americano-v1';
const SCORES = [[4,0],[3,1],[2,2],[1,3],[0,4]];
const ui = { tab: 'rounds', setupCount: null };
let tournament = load();

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const t = JSON.parse(raw);
    return t && Array.isArray(t.players) && Array.isArray(t.rounds) ? t : null;
  } catch (e) { return null; }
}
function save() { localStorage.setItem(KEY, JSON.stringify(tournament)); }
function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function names(team) { return team.map(i => esc(tournament.players[i])).join('/'); }

// --- Pantalla de configuración -------------------------------------------
function renderSetup() {
  const app = document.getElementById('app');
  document.getElementById('tabs').hidden = true;
  if (ui.setupCount === null) {
    app.innerHTML = `
      <h1>🎾 Pádel Americano</h1>
      <div class="card">
        <label>¿Cuántos jugadores? (mínimo 6)</label>
        <input type="number" id="nPlayers" min="6" inputmode="numeric" value="8">
        <label>¿Cuántas canchas disponibles?</label>
        <input type="number" id="nCourts" min="1" inputmode="numeric" value="2">
        <button class="primary" onclick="stepNames()">Continuar</button>
        <div class="error" id="err"></div>
      </div>`;
  } else {
    let fields = '';
    for (let i = 0; i < ui.setupCount; i++) {
      fields += `<label>Jugador ${i + 1}</label><input type="text" id="p${i}" placeholder="Jugador ${i + 1}">`;
    }
    app.innerHTML = `
      <h1>🎾 Nombres de jugadores</h1>
      <div class="card">${fields}
        <button class="primary" onclick="startTournament()">Generar torneo</button>
        <div class="error" id="err"></div>
      </div>`;
  }
}
function stepNames() {
  const n = parseInt(document.getElementById('nPlayers').value, 10);
  const c = parseInt(document.getElementById('nCourts').value, 10);
  if (!Number.isInteger(n) || n < 6) { document.getElementById('err').textContent = 'Se necesitan al menos 6 jugadores.'; return; }
  if (!Number.isInteger(c) || c < 1) { document.getElementById('err').textContent = 'Se necesita al menos 1 cancha.'; return; }
  ui.setupCount = n; ui.setupCourts = c;
  render();
}
function startTournament() {
  const list = [];
  for (let i = 0; i < ui.setupCount; i++) {
    const v = document.getElementById('p' + i).value.trim();
    list.push(v || 'Jugador ' + (i + 1));
  }
  tournament = PadelEngine.createTournament(list, ui.setupCourts);
  ui.setupCount = null; ui.tab = 'rounds';
  save(); render();
  alert('Torneo generado: ' + tournament.rounds.length + ' jornadas.');
}

// --- Torneo ----------------------------------------------------------------
function renderRounds() {
  let html = `<h1>🎾 Jornadas (${tournament.rounds.length})</h1>`;
  tournament.rounds.forEach((round, r) => {
    let matches = '';
    round.matches.forEach((m, i) => {
      const btns = SCORES.map(([a, b]) => {
        const sel = m.score && m.score[0] === a && m.score[1] === b ? ' class="sel"' : '';
        return `<button${sel} onclick="pick(${r},${i},${a},${b})">${a}-${b}</button>`;
      }).join('');
      matches += `
        <div class="match">
          <div class="court">Cancha ${m.court}</div>
          <div class="teams"><b>${names(m.teamA)}</b> vs <b>${names(m.teamB)}</b></div>
          <div class="scores">${btns}</div>
        </div>`;
    });
    const byes = round.byes.length
      ? `<div class="byes">Descansan: ${round.byes.map(i => esc(tournament.players[i])).join(', ')}</div>` : '';
    html += `<div class="card"><h2>Jornada ${r + 1}</h2>${matches}${byes}</div>`;
  });
  html += `<button class="danger" onclick="reset()">Nuevo torneo</button>`;
  return html;
}
function renderTable() {
  const rows = PadelEngine.standings(tournament);
  const total = tournament.rounds.reduce((s, r) => s + r.matches.length, 0);
  const scored = tournament.rounds.reduce((s, r) => s + r.matches.filter(m => m.score).length, 0);
  const trophy = rows[0].points > 0;
  let body = '';
  for (const r of rows) {
    const cup = trophy && r.rank === 1 ? ' 🏆' : '';
    body += `<tr><td>${r.rank}</td><td>${esc(r.name)}${cup}</td><td class="num">${r.points}</td><td class="num">${r.played}</td></tr>`;
  }
  return `<h1>🏆 Tabla de posiciones</h1>
    <div class="card">
      <div class="done">${scored} de ${total} partidos capturados</div>
      <table><thead><tr><th>#</th><th>Jugador</th><th class="num">Puntos</th><th class="num">PJ</th></tr></thead>
      <tbody>${body}</tbody></table>
    </div>`;
}
function pick(r, i, a, b) {
  PadelEngine.setScore(tournament, r, i, [a, b]);
  save(); render();
}
function reset() {
  if (!confirm('¿Seguro? Se borrará el torneo actual.')) return;
  localStorage.removeItem(KEY);
  tournament = null; ui.setupCount = null;
  render();
}
function render() {
  if (!tournament) { renderSetup(); return; }
  const tabs = document.getElementById('tabs');
  tabs.hidden = false;
  document.getElementById('tabRounds').className = ui.tab === 'rounds' ? 'active' : '';
  document.getElementById('tabTable').className = ui.tab === 'table' ? 'active' : '';
  document.getElementById('app').innerHTML = ui.tab === 'rounds' ? renderRounds() : renderTable();
}
render();
</script>
</body>
</html>
```

- [ ] **Step 2: Verificar que las pruebas del motor siguen pasando**

Run: `node --test padel-americano/tests/`
Expected: PASS (10 tests)

- [ ] **Step 3: Commit**

```bash
git add padel-americano/index.html
git commit -m "feat(padel): interfaz móvil con jornadas, marcadores y tabla"
```

---

### Task 4: Verificación end-to-end en navegador

**Files:**
- Create: `.claude/launch.json` (si no existe)

- [ ] **Step 1: Configurar servidor estático de preview**

Crear/actualizar `.claude/launch.json`:

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "padel",
      "runtimeExecutable": "python3",
      "runtimeArgs": ["-m", "http.server", "8734", "--directory", "padel-americano"],
      "port": 8734
    }
  ]
}
```

- [ ] **Step 2: Arrancar preview y probar el flujo completo**

Usar `preview_start` con name `padel`, viewport móvil (`preview_resize` preset `mobile`) y verificar con snapshot/clicks:
1. Pantalla de configuración visible; poner 5 jugadores → aparece error "al menos 6".
2. Con 8 jugadores y 2 canchas → capturar 8 nombres → "Generar torneo" → aparecen jornadas.
3. En cada jornada: 2 partidos con 5 botones de marcador; nadie aparece dos veces.
4. Capturar un 3-1 → pestaña Tabla → ganadores con 3 puntos, perdedores con 1, PJ=1.
5. Corregir a 0-4 → tabla se recalcula.
6. Recargar la página (`preview_eval` con `location.reload()`) → el torneo persiste.
7. "Nuevo torneo" → confirm → regresa a configuración.
8. Revisar consola sin errores (`preview_console_logs` level error).

- [ ] **Step 3: Commit**

```bash
git add .claude/launch.json
git commit -m "chore(padel): configuración de preview local"
```

---

### Task 5: Publicar en GitHub Pages

**Files:** ninguno nuevo (operaciones git/gh)

- [ ] **Step 1: Push a main**

Run: `git push origin main`
Expected: push exitoso a `acheparra-creator/repositorio`.

- [ ] **Step 2: Habilitar GitHub Pages desde main /**

```bash
gh api -X POST repos/acheparra-creator/repositorio/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
```

Expected: 201 Created. Si responde 409 (ya existe), verificar con
`gh api repos/acheparra-creator/repositorio/pages -q .html_url`.

- [ ] **Step 3: Verificar la URL pública**

Esperar el build (~1-2 min) y comprobar:

```bash
curl -s -o /dev/null -w "%{http_code}" https://acheparra-creator.github.io/repositorio/padel-americano/
```

Expected: `200`. Compartir la URL con el usuario.

---

### Task 6: Publicar como Artifact

**Files:**
- Create: `<scratchpad>/padel-artifact.html` (archivo temporal, NO va al repo)

- [ ] **Step 1: Cargar la skill `artifact-design`** (requisito del tool Artifact)

- [ ] **Step 2: Generar versión autocontenida**

Construir `<scratchpad>/padel-artifact.html` con el contenido de `index.html` PERO:
- Sin `<!doctype>`, `<html>`, `<head>`, `<body>` (el Artifact los agrega).
- Conservar `<title>Pádel Americano</title>`, el `<style>`, el markup y los scripts.
- Reemplazar `<script src="engine.js"></script>` por `<script>` + contenido íntegro de `engine.js` + `</script>` (CSP del artifact bloquea archivos externos).

- [ ] **Step 3: Publicar**

Llamar al tool `Artifact` con `file_path` del archivo temporal, `favicon: "🎾"`,
`description: "Organizador de torneos de pádel americano: jornadas sin repetir pareja, marcadores a 4 games y tabla de puntos"`.
Compartir la URL con el usuario.

---

## Self-review

- **Cobertura del spec:** pantallas 1-3 (Task 3), algoritmo con backtracking y descansos equitativos (Task 1), marcadores/puntos/empates compartidos (Task 2 + UI), persistencia y "Nuevo torneo" (Task 3, verificado en Task 4), errores de validación (Tasks 1-3), pruebas N×canchas (Task 1), GitHub Pages + Artifact (Tasks 5-6). Sin huecos.
- **Placeholders:** ninguno; todo el código está completo.
- **Consistencia de tipos:** `createTournament/generateRounds/setScore/standings` y el shape `{court, teamA, teamB, score}` coinciden entre engine, tests y UI.
