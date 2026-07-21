# Rumbo a Alfa Centauri — Especificación de diseño

**Fecha:** 2026-07-20
**Estado:** Aprobado por el usuario
**Entrega:** `rumbo-alfa-centauri/index.html` + `data.js` + `engine.js` + GitHub Pages + Artifact

## Objetivo

Juego educativo de trivia científica, formato carrera de mesa, para que una familia
de 2 a 4 jugadores se pase un solo dispositivo y compita respondiendo preguntas de
opción múltiple. Cada acierto avanza una casilla en una ruta espacial (Tierra →
Alfa Centauri); cada respuesta —acierte o falle el jugador— muestra una explicación
con el dato curioso. Gana quien llegue primero a la meta.

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Plataforma | Web sin build ni servidor: `index.html` + `data.js` (banco de preguntas) + `engine.js` (lógica), igual que padel-americano |
| Modo de juego | Un solo dispositivo que se pasa entre jugadores (pass-and-play) |
| Jugadores | 2 a 4, elegidos entre 4 personajes fijos de la familia (ver "Personajes") |
| Formato | Carrera por turnos: cada jugador saca una pregunta en su turno; si acierta avanza 1 casilla, si falla se queda y pasa el turno |
| Tablero | Ruta fija de 8 casillas temáticas: Tierra (salida) → Luna → Marte → Cinturón de asteroides → Júpiter → Saturno → Salto cuántico (decorativa, sin efecto de juego) → Alfa Centauri (meta) |
| Victoria | El primero en llegar a Alfa Centauri gana; termina la partida de inmediato |
| Preguntas | Opción múltiple (3 opciones), banco propio por nivel — preguntas distintas por nivel, no la misma reformulada |
| Categorías | Espacio/astronomía, física/naturaleza, cuerpo humano/biología, química/materia — mezcladas al azar en cada turno |
| Tamaño del banco | ~100-150 preguntas repartidas entre los 3 niveles activos (12-15, 9-11, adulto/experto) — el nivel 6-8 no se usa con el roster actual, ver "Personajes" |
| Explicaciones | Se muestran siempre tras responder (acierte o falle), con el dato curioso |
| Tiempo | Sin temporizador |
| Repetición | Dentro de una partida no se repite una pregunta ya usada del pool de un nivel (se descarta hasta agotar el pool; si se agota, se reinicia) |
| Al fallar | Solo pasa el turno, sin castigo adicional |
| Persistencia | Ninguna: cada partida empieza siempre de cero (no se retoma tras cerrar el navegador) |
| Distribución | GitHub Pages en `rumbo-alfa-centauri/` vía Actions + Artifact privado |

## Personajes

4 avatares fijos inspirados en la familia real (representación estilizada tipo
traje espacial, no fotos ni rostros realistas). Cada partida, cada jugador presente
toca su propio avatar para unirse (2 a 4 de los 4 pueden jugar; los que no se
seleccionan quedan fuera de esa partida). El orden de turno sigue el orden de
selección.

| Personaje | Apariencia | Nivel de preguntas |
|---|---|---|
| Hija | Güera, pelo rizado largo, la más chaparrita, traje rosa | 12-15 |
| Hijo | Pelo negro en moicana, traje naranja | 9-11 |
| Mamá | Pelo lacio oscuro, estatura alta, traje negro | Adulto/experto |
| Papá | El más alto, barba, pelo negro en coleta, traje beige | Adulto/experto |

Los 4 personajes y sus niveles son fijos (no editables) — no hace falta pantalla
de "nombre y edad" al iniciar partida, se reemplaza por la selección de avatar.
Mamá y Papá comparten el mismo nivel (`adulto`) y por lo tanto el mismo pool de
preguntas sin repetir dentro de la partida: si uno de los dos saca una pregunta,
al otro no puede volver a tocarle esa misma pregunta en esa partida.

## Estructura de datos (`data.js`)

Cada pregunta es un objeto plano, sin relación 1:1 entre niveles (bancos
independientes por nivel):

```js
{
  id: 'space-01',
  level: '6-8' | '9-11' | '12-15' | 'adulto',
  category: 'espacio' | 'fisica' | 'biologia' | 'quimica',
  question: '¿Qué cae más rápido en la Luna: una pluma o un martillo?',
  options: ['La pluma', 'El martillo', 'Caen igual de rápido'],
  correctIndex: 2,
  explanation: 'En la Luna no hay aire que frene a la pluma, así que ambos caen a la misma velocidad por la gravedad lunar.'
}
```

Nota: el nivel `6-8` queda definido en el banco por si en el futuro se agrega un
quinto personaje o modo infantil, pero con el roster actual de 4 personajes
(12-15, 9-11, adulto, adulto) no se usa en el juego — no es necesario redactar
preguntas para ese nivel en esta primera versión.

## Pantallas

### 1. Selección de personajes
- Los 4 avatares fijos (Hija, Hijo, Mamá, Papá) con su nombre y nivel visibles.
- Tocar un avatar lo marca "en juego"; tocar de nuevo lo desmarca.
- Botón **Empezar partida**: habilitado solo con 2 a 4 avatares seleccionados.

### 2. Partida
- Vista de la ruta espacial (fondo estrellado, 8 casillas temáticas) con la
  posición actual de cada jugador en juego.
- Indicador de turno activo (nombre + avatar resaltado).
- Tarjeta de pregunta: categoría, texto de la pregunta, 3 opciones tocables.
- Al responder: resaltar la opción elegida, mostrar si acertó, mostrar
  explicación, botón **Continuar** que avanza el turno (y la ficha, si acertó).
- Si el jugador llega a la casilla final (Alfa Centauri) → pasa a pantalla de
  victoria de inmediato, sin esperar a que respondan los demás.

### 3. Victoria
- Anuncia al ganador.
- Resumen por jugador: preguntas respondidas, aciertos y fallos.
- Botón **Jugar de nuevo**: vuelve a la pantalla de selección de personajes con
  el tablero y los pools de preguntas reiniciados.

## Fuera de alcance (explícitamente no incluido)

- Sincronización multi-dispositivo o backend.
- Edición de nombres/niveles de los 4 personajes.
- Temporizador por pregunta.
- Persistencia de partida a medias.
- Efecto especial en la casilla "Salto cuántico" (puramente decorativa por ahora).
