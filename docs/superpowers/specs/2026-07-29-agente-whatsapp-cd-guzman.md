# Agente de WhatsApp — Consultorio Cd. Guzmán

**Fecha:** 2026-07-29
**Estado:** Diseño aprobado en decisiones de fondo; faltan datos de contenido (ver "Pendientes")
**Entrega prevista:** `consultorio-wa/` — extensión de Chrome sin backend

## Objetivo

Reducir el trabajo de contestar WhatsApp en el consultorio de Ciudad Guzmán. Cuando
llega un mensaje de un paciente, un panel dentro de WhatsApp Web redacta la respuesta
—resolviendo preguntas frecuentes y consultando huecos reales de la agenda de Google—
y la deja lista para que una persona la revise y la envíe. El agente nunca envía solo
y nunca agenda: informa.

## Hallazgos que condicionan el diseño

Revisé la agenda real de Google Calendar en modo lectura antes de diseñar. Cinco cosas
cambian el planteamiento:

1. **Hay una sola agenda en uso.** No existe un calendario separado por consultorio;
   todo vive en el calendario principal de la cuenta, zona horaria `America/Mexico_City`.
   Los otros calendarios son personales o de terceros y no tienen citas.
2. **Las citas las captura la secretaria** desde una cuenta de Google distinta, con
   permiso de escritura sobre esa agenda.
3. **El título del evento contiene datos personales sensibles**: nombre completo del
   paciente, edad, si es primera vez o subsecuente, y uno o dos teléfonos. El formato
   es estable, del tipo `CONFIRMADA. DR. PARRA. <nombre>. <edad> años. Subsecuente. <teléfono>`,
   con estados al inicio (`CONFIRMADA`, `AVISADO`, `NO CONTESTA`, `BUZÓN`, `llegó`).
   **Consecuencia directa:** el agente no debe leer títulos nunca. Ver "Privacidad".
4. **Ya usas eventos de bloqueo** con títulos como `No citar` y `No citar después de
   las 7pm`, algunos recurrentes. Eso es exactamente lo que el agente necesita para
   saber cuándo no ofrecer horario, y funciona sin cambiar nada de tu operación.
5. **La agenda no distingue el consultorio.** Un evento de Cd. Guzmán y uno de Colima
   se ven igual (algunos anotan `px CD. Guzman` en el título, pero no todos y no de
   forma confiable). El agente no puede deducir dónde estás; los días y horas de
   Cd. Guzmán tienen que declararse en configuración.

La duración típica de cita es de 30 minutos, con algunas de 45.

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Canal | Extensión de Chrome sobre `web.whatsapp.com`, en el navegador del consultorio |
| Autonomía al responder | **Ninguna.** El agente redacta y muestra un borrador; una persona lo revisa y presiona enviar |
| Autonomía sobre la agenda | **Solo lectura.** Informa huecos; no crea, mueve ni cancela eventos |
| Acceso al calendario | API `freeBusy` de Google Calendar — devuelve intervalos ocupados, nunca títulos ni asistentes |
| Backend | Ninguno. La extensión habla directo con la API de Anthropic y con Google |
| Modelo | `claude-sonnet-5` para redactar; suficiente y barato para este volumen |
| Idioma y tono | Español de México, trato de usted, cálido y breve — como contesta hoy el consultorio |
| Alcance clínico | Cero. No orienta, no interpreta estudios, no ajusta medicamentos |
| Datos del consultorio | Archivo `config.json` editable sin tocar código |

### Por qué sin backend

La opción con servidor era la esperable, pero aquí no aporta nada y sí agrega costo y
mantenimiento. Una extensión de Chrome puede hacer peticiones cruzadas desde su service
worker sin CORS, guardar credenciales en `chrome.storage.local` y resolver OAuth con
`chrome.identity`. La llave de Anthropic queda en la máquina del consultorio, que es el
mismo nivel de exposición que un archivo `.env` en un servidor tuyo. La condición es que
la extensión se instale desempaquetada o desde un CRX privado, **nunca publicada en la
Chrome Web Store**, porque ahí la llave sería descargable por cualquiera.

### Por qué el humano envía

Fue tu decisión que el agente solo informe horarios, y la extiendo al envío por dos
razones que conviene tener explícitas:

- **Riesgo de cuenta.** Los Términos de WhatsApp prohíben el mensajeo automatizado y los
  clientes no autorizados. Un panel que redacta y un humano que envía se comporta, hacia
  los servidores de WhatsApp, igual que una persona escribiendo: sin ráfagas, sin
  respuestas a las 3 a.m., sin patrones de bot. Es lo que mantiene fuera de riesgo el
  número del consultorio. Aun así hay que decirlo con claridad: una extensión que lee el
  DOM de WhatsApp Web opera en zona gris, y el riesgo no es cero, solo mucho menor que
  el de automatizar el envío.
- **Riesgo clínico.** Un paciente renal que escribe "amanecí muy hinchado y con falta de
  aire" no puede recibir una respuesta automática sobre horarios. Con revisión humana,
  ese caso se atiende como debe.

## Arquitectura

```
web.whatsapp.com
  └── content script  ── lee la conversación abierta, inyecta el panel lateral
        │                 y escribe el borrador en el cuadro de texto
        ▼
      service worker  ── orquesta: arma el contexto, llama al modelo, ejecuta la
        │                 herramienta de huecos, devuelve el borrador
        ├──▶ Google Calendar API  ·  freeBusy.query      (OAuth, solo lectura)
        └──▶ Anthropic API        ·  messages + tools    (llave local)

  config.json  ── horarios de Cd. Guzmán, datos del consultorio, preguntas frecuentes
```

Tres archivos de lógica y un archivo de datos. Sin build step, igual que el resto del
monorepo.

### Flujo de una respuesta

1. Llega un mensaje. El content script detecta que la conversación abierta tiene un
   mensaje entrante sin responder y habilita el botón **Redactar respuesta** del panel.
2. Al presionarlo, se leen los últimos ~15 mensajes de esa conversación y se mandan al
   service worker.
3. El service worker llama al modelo con el `config.json` en el prompt del sistema y una
   herramienta disponible: `consultar_huecos`.
4. Si el paciente pregunta por horarios, el modelo llama a `consultar_huecos`. El worker
   consulta `freeBusy` y devuelve una lista de huecos ya calculada.
5. El modelo redacta la respuesta final en español.
6. El panel la muestra con dos botones: **Insertar en el chat** (la pone en el cuadro de
   texto, sin enviar) y **Descartar**. La persona edita si quiere y presiona enviar.

El paso 6 es el que sostiene todo el diseño: no hay ninguna ruta de código que envíe un
mensaje.

### Cálculo de huecos

```
huecos = plantilla_cd_guzman(rango)  −  ocupado(freeBusy(rango))  −  margen_de_aviso
```

- `plantilla_cd_guzman` genera los espacios de 30 minutos de los días y horas
  configurados como consulta en Cd. Guzmán.
- `freeBusy` devuelve solo intervalos `{start, end}` de la agenda principal. Un espacio
  se descarta si se traslapa con cualquier intervalo ocupado, aunque sea un minuto.
- `margen_de_aviso` descarta lo que caiga dentro de las próximas N horas (default: 12),
  para no ofrecer una cita imposible de preparar.
- Se ofrecen los primeros 3 huecos, redactados en lenguaje natural
  ("el martes 4 a las 5:30 de la tarde"), nunca una lista cruda de horas.

**Este cálculo es exactamente tan bueno como tus bloqueos.** Si un martes estás en Colima
y ese día está vacío en la agenda, el agente ofrecerá horarios de Cd. Guzmán que no
existen. La regla operativa que acompaña al sistema es que todo lo que no sea consulta en
Cd. Guzmán —viajes, quirófano, el otro consultorio, biopsias— tiene que estar en la
agenda como evento ocupado. Ya lo haces con `No citar`; el agente lo respeta tal cual.

### `config.json`

```jsonc
{
  "consultorio": {
    "nombre": "Consultorio Dr. Héctor Parra Lomelí — Ciudad Guzmán",
    "direccion": "PENDIENTE",
    "maps": "PENDIENTE",
    "telefono": "PENDIENTE",
    "zona_horaria": "America/Mexico_City"
  },
  "agenda": {
    "calendario": "primary",
    "duracion_minutos": 30,
    "margen_aviso_horas": 12,
    "dias_a_futuro": 21,
    "plantilla": [
      { "dia": "martes", "de": "16:30", "a": "20:00" },
      { "dia": "jueves", "de": "16:30", "a": "20:00" }
    ]
  },
  "faq": [
    {
      "id": "costo",
      "pregunta": "¿Cuánto cuesta la consulta?",
      "respuesta": "PENDIENTE",
      "variantes": ["precio", "cuánto sale", "costo de primera vez"]
    }
  ],
  "escalamiento": {
    "aviso": "Permítame un momento, en seguida le contesta el consultorio.",
    "temas": ["resultados de estudios", "cambios de medicamento", "síntomas", "urgencias"]
  }
}
```

Las `variantes` no se usan para hacer coincidencias por palabra clave: van en el prompt
para que el modelo reconozca cómo pregunta la gente en realidad ("¿qué precio tiene la
cita?"). El bloque `faq` es el archivo que tú vas a mantener; todo lo demás se toca una
vez y no se vuelve a abrir.

### Prompt del sistema — reglas duras

El prompt se arma con `config.json` incrustado, más estas restricciones. Están redactadas
como prohibiciones porque son las que producen daño si se rompen:

1. **No das consejo médico de ningún tipo.** No interpretas laboratorios, no opinas sobre
   síntomas, no confirmas ni ajustas dosis, no dices si algo es grave. Si el mensaje trae
   contenido clínico, tu única respuesta es el aviso de escalamiento.
2. **No inventas datos del consultorio.** Costos, dirección, horarios y servicios salen
   literalmente de `config.json`. Si el dato no está ahí, dices que en un momento le
   confirman.
3. **No prometes una cita.** Ofreces horarios disponibles y cierras invitando a que el
   consultorio confirme. No digas "queda agendado" ni "le aparto el lugar".
4. **No menciones a otros pacientes** ni des a entender qué tan llena está la agenda.
5. **Ante cualquier señal de urgencia** —falta de aire, dolor de pecho, no orinar, sangrado,
   fiebre alta, confusión, problemas con el catéter o la fístula— tu respuesta indica
   acudir a urgencias de inmediato y avisa que el consultorio se comunica. No ofreces cita.
6. **Máximo 4 líneas.** Es WhatsApp, no un correo.

Además, el borrador se marca visualmente en el panel con un aviso cuando el modelo activó
la regla 1 o la 5, para que quien revisa sepa que ahí hay algo que atender en persona.

### WhatsApp Web: lectura e inserción

Es la parte frágil del sistema y conviene decirlo sin adornos: WhatsApp Web ofusca sus
clases CSS y quitó buena parte de sus atributos `data-testid`. Los anclajes que se han
mantenido estables y con los que arranca la implementación son:

| Qué | Selector de partida |
|---|---|
| Panel de la conversación abierta | `#main` |
| Burbujas de mensaje | `div.message-in`, `div.message-out` |
| Texto del mensaje | `span.selectable-text` dentro de la burbuja |
| Cuadro de redacción | `div[contenteditable="true"][data-tab]` dentro del pie de `#main` |

Estos selectores hay que verificarlos contra la versión de WhatsApp Web del día en que se
implemente, y aislarlos todos en un solo módulo (`selectors.js`) para que una ruptura se
arregle en un archivo. Es mantenimiento recurrente, no se elimina: cuando WhatsApp cambie
su DOM, el panel deja de leer y hay que actualizar el selector.

Para escribir el borrador no sirve asignar `innerText`: el editor de WhatsApp es un
componente controlado y no registra el cambio. El método que funciona es enfocar el
cuadro y usar `document.execCommand('insertText', false, texto)`, con un respaldo que
despacha un evento `paste` sintético con `DataTransfer` si el primero falla.

## Privacidad y aspectos legales

Esto maneja datos personales sensibles de salud, así que las decisiones de arriba tienen
una contraparte legal que hay que dejar por escrito:

- **`freeBusy` en vez de leer eventos** no es un detalle técnico, es la medida de
  protección principal. El agente físicamente no puede filtrar el nombre, la edad ni el
  teléfono de otro paciente a la conversación, porque nunca los recibe. El alcance OAuth
  que se solicita es `https://www.googleapis.com/auth/calendar.freebusy` — verificar en
  la pantalla de consentimiento que aparezca disponible; si no, el sustituto es
  `calendar.readonly`, que sí ve títulos y obliga a filtrarlos en código antes de
  cualquier llamada al modelo.
- **La app de Google se queda en modo "Testing"** con tu correo como único usuario de
  prueba. Así no requiere el proceso de verificación de Google, que es largo y aquí no
  aplica porque no hay terceros usándola.
- **El contenido del chat del paciente sí sale hacia la API de Anthropic.** Es inherente
  a usar un modelo. Lo que se acota: se mandan los últimos ~15 mensajes de texto, nunca
  imágenes ni documentos adjuntos, y nada del calendario más allá de intervalos. Bajo la
  LFPDPPP esto convierte a Anthropic en encargado del tratamiento, y corresponde
  mencionar el uso de herramientas automatizadas de atención en tu aviso de privacidad.
- **El primer mensaje de cada conversación nueva** debe aclarar que se responde con apoyo
  de un asistente y que un humano revisa. Es honesto con el paciente y evita el problema
  de que alguien crea que está hablando con el médico.

## Costo

| Concepto | Costo mensual estimado |
|---|---|
| API de Anthropic | 2 a 5 USD con ~600 borradores al mes, entradas cortas y prompt cacheado |
| Google Calendar API | 0 — muy por debajo de la cuota gratuita |
| Hosting | 0 — no hay servidor |
| Extensión | 0 — instalación desempaquetada |

## Riesgos y limitaciones

- **Solo funciona con Chrome abierto** y la sesión de WhatsApp Web activa. No hay
  respuestas de madrugada ni con la computadora apagada. Para el caso de uso —un
  consultorio con horario— es aceptable, pero hay que saberlo.
- **El DOM de WhatsApp Web cambia sin aviso** y romperá la lectura o la inserción cada
  cierto tiempo. Presupuestar mantenimiento.
- **Zona gris de Términos.** Sin envío automático el riesgo baja mucho, pero no
  desaparece. Si en algún momento el consultorio crece y esto se vuelve crítico, la
  migración correcta es a la Cloud API oficial de Meta con número dedicado; el
  `config.json`, la lógica de huecos y el prompt se reutilizan tal cual. El diseño deja
  esa puerta abierta a propósito.
- **La calidad de los horarios depende de los bloqueos** en la agenda, como se explicó.
- **La extensión no distingue conversaciones de pacientes de las personales.** Se activa
  solo cuando alguien presiona el botón, así que el control es manual.

## Plan de implementación

Cada fase se puede probar sola antes de seguir.

- **Fase 1 — Panel.** Manifest v3, content script que inyecta el panel en `#main` y lee
  los últimos mensajes de la conversación abierta. Se prueba viendo el texto leído en el
  panel, sin modelo ni calendario.
- **Fase 2 — Calendario.** OAuth con `chrome.identity.launchWebAuthFlow` y PKCE,
  `freeBusy.query`, y la función de huecos con pruebas sobre intervalos fijos. Se prueba
  comparando los huecos calculados contra la agenda real de una semana.
- **Fase 3 — Modelo.** Llamada a la API con la herramienta `consultar_huecos` y el prompt
  del sistema. Se prueba con una batería de mensajes reales de pacientes, incluyendo los
  casos que deben escalar.
- **Fase 4 — Inserción.** Botón que escribe el borrador en el cuadro de texto. Se prueba
  en una conversación propia.
- **Fase 5 — Ajuste del tono y de las FAQ** con mensajes reales de la semana.

## Pendientes (datos que hacen falta para construir)

Ninguno de estos es una decisión de diseño; son contenido que solo tú tienes:

1. Días y horas exactos de consulta en Cd. Guzmán.
2. Dirección del consultorio, referencia para llegar y enlace de Maps.
3. Costo de primera vez y de subsecuente, y si se cobra distinto por revisión de estudios.
4. Qué debe llevar un paciente de primera vez (estudios previos, resumen clínico,
   identificación).
5. Si se aceptan seguros o convenios, y cuáles.
6. Formas de pago.
7. Las 10 o 15 preguntas que más les llegan hoy por WhatsApp, con la respuesta como la
   contestan ustedes. Sirve tanto de contenido como de referencia de tono.
