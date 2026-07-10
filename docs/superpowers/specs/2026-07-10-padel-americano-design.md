# Pádel Americano — Especificación de diseño

**Fecha:** 2026-07-10
**Estado:** Aprobado por el usuario
**Entrega:** `padel-americano/index.html` (archivo HTML único) + GitHub Pages + Artifact

## Objetivo

Aplicación web para organizar torneos de pádel en formato americano (round robin
individual): N jugadores rotan de pareja cada jornada sin repetir pareja nunca,
se capturan resultados de partidos a 4 games, y al final se suman los games
ganados de forma individual para designar a los ganadores.

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Plataforma | Web móvil: HTML único con JS vanilla, sin servidor ni build |
| Jugadores | Mínimo 6, sin máximo práctico; identificados por nombre |
| Descansos | Cualquier N ≥ 6; descansos rotativos equitativos (descansan los que más partidos llevan jugados) |
| Jornadas | Se generan todas las posibles hasta agotar parejas nuevas; el torneo puede terminarse antes manualmente |
| Marcador | Partidos a exactamente 4 games: resultados válidos 4-0, 3-1, 2-2, 1-3, 0-4 |
| Puntos | Cada jugador suma los games ganados por su pareja en cada partido (ej. 3-1 → 3 puntos a cada ganador, 1 a cada perdedor) |
| Empates finales | Se quedan: los empatados comparten posición (puede haber co-campeones) |
| Rivales | Pueden repetirse; lo único que nunca se repite es la pareja |
| Persistencia | localStorage con guardado automático tras cada acción; botón "Nuevo torneo" con confirmación |
| Distribución | GitHub Pages en `https://acheparra-creator.github.io/repositorio/padel-americano/` + Artifact privado |
| Sincronización | No hay: cada dispositivo tiene su propio torneo independiente |

## Pantallas

### 1. Configuración
- Campo: número de jugadores (entero ≥ 6; si < 6 muestra error y no continúa).
- Campo: número de canchas (entero ≥ 1; la app usa por jornada `min(canchas, floor(N/4))`).
- Casillas de nombre, una por jugador; un nombre vacío se autonombra "Jugador N".
- Botón **Generar torneo**: aleatoriza y genera todas las jornadas.

### 2. Jornadas
- Lista de jornadas numeradas (Jornada 1…K). Cada jornada muestra:
  - Sus partidos: `Cancha X: A/B vs C/D`.
  - Los jugadores que descansan (si N no es múltiplo de 4 o faltan canchas).
- Captura de resultado por partido: botones grandes con los 5 marcadores
  válidos (4-0, 3-1, 2-2, 1-3, 0-4), usables con el pulgar en celular.
- Un resultado capturado puede corregirse en cualquier momento; la tabla se
  recalcula al instante.

### 3. Tabla de posiciones
- Visible en todo momento (pestaña o sección fija).
- Columnas: posición, nombre, puntos (games ganados acumulados), partidos jugados.
- Orden descendente por puntos; empatados comparten número de posición.
- Al primer lugar (o lugares empatados) se les marca con 🏆.

## Algoritmo de generación de jornadas

1. Aleatorizar el orden inicial de los jugadores (Fisher-Yates).
2. Por jornada:
   a. Jugadores activos por jornada = `4 × min(canchas, floor(N/4))`.
   b. Si sobran jugadores, descansan los que **más partidos llevan jugados**
      (desempate aleatorio), para equilibrar partidos jugados.
   c. Formar parejas entre los activos usando **backtracking**: solo parejas
      que no hayan jugado juntas antes. Si no existe un emparejamiento
      completo válido para la jornada, el torneo termina ahí.
   d. Asignar parejas a canchas y emparejar parejas como rivales (los rivales
      pueden repetirse; asignación aleatoria).
3. Repetir hasta que el backtracking no encuentre jornada válida.
4. Mostrar al usuario cuántas jornadas resultaron (ej. 8 jugadores → 7 jornadas).

Notas:
- El backtracking sobre parejas es barato para tamaños reales (≤ ~24 jugadores).
- El registro de parejas usadas se guarda como conjunto de pares ordenados de
  índices de jugador.

## Modelo de datos (localStorage, clave `padel-americano-v1`)

```json
{
  "players": ["Ana", "Luis", "…"],
  "courts": 2,
  "rounds": [
    {
      "matches": [
        { "court": 1, "teamA": [0, 4], "teamB": [1, 2], "score": [3, 1] }
      ],
      "byes": [5]
    }
  ]
}
```

- `teamA`/`teamB`: índices de jugador. `score`: `null` hasta capturarse;
  después `[gamesA, gamesB]` con `gamesA + gamesB === 4`.
- Se guarda el estado completo tras cada mutación.

## Manejo de errores

- N < 6 → mensaje "Se necesitan al menos 6 jugadores".
- Canchas < 1 → mensaje de error.
- Recarga de página → se restaura el torneo desde localStorage.
- "Nuevo torneo" → diálogo de confirmación antes de borrar.
- localStorage corrupto/ausente → arranca en pantalla de configuración.

## Pruebas

- Unitarias del algoritmo (ejecutables con Node sobre el módulo JS embebido o
  extraído): para N ∈ {6, 8, 10, 12, 16} × canchas ∈ {1, 2, 3}:
  - Ninguna pareja se repite en todo el torneo.
  - Cada jornada usa `min(canchas, floor(N/4))` canchas completas.
  - La diferencia de partidos jugados entre jugadores es ≤ 1 en todo momento.
- Cálculo de puntos: casos 4-0, 3-1, 2-2 y corrección de un resultado ya capturado.
- Prueba manual en móvil (viewport angosto) del flujo completo.

## Fuera de alcance (YAGNI)

- Sincronización entre dispositivos / multiusuario.
- Historial de torneos pasados.
- Desempates por partidos ganados o games en contra.
- Formatos distintos a 4 games por partido.
