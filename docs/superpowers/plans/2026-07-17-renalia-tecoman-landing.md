# Renalia Tecomán — Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sitio web de una página (landing) para la clínica de hemodiálisis Renalia Tecomán, alineado con la campaña activa de Meta Ads, con WhatsApp como CTA principal.

**Architecture:** Sitio estático (HTML + CSS + JS mínimo) en carpeta nueva `renalia-tecoman/` del monorepo, publicado por GitHub Pages vía Actions (mismo patrón que `padel-americano/`). Una sola página con secciones ancla; sin frameworks ni build step.

**Tech Stack:** HTML5 semántico, CSS puro (variables + `prefers-color-scheme`), JSON-LD (`MedicalClinic`), Google Maps embed. Sin dependencias externas salvo el iframe de Maps.

---

## Contexto de negocio (fuente: FB page + campaña Meta 16-jul-2026)

**Datos duros:**
- Nombre: Renalia Tecomán (grupo Renalia — renalia.mx, "Expertos en salud renal")
- Dirección: **Valentín Gómez Farías 699 (esq. Miguel Bracamontes), Tecomán, Colima, CP 28110** (confirmada en anuncios activos Y en Google Maps; coords 18.9215835, -103.8777819)
- Tel/WhatsApp: **313 151 9215** (+52 1 313 151 9215)
- Email: renaliatecoman@gmail.com
- Maps: https://maps.google.com/?q=Renalia+Tecoman (place id 0x843ab75a141eec93:0x10d5038d7092d679)
- Horario: cierre a las **3:00 p.m.** (confirmado por el usuario y por Maps). **Hora de apertura y días: PENDIENTE de confirmar.**
- **Equipo médico:** Dr. Héctor Parra Lomelí — Nefrólogo, Director de la unidad y Responsable Sanitario (es el usuario; hay material gráfico de campaña con su foto y nombre). El Dr. José Llamas Ríos es urólogo (servicio aparte que también atiende en Renalia Tecomán según flyers; NO nombrarlo como nefrólogo).
- **Fotos disponibles:** interior de la sala de hemodiálisis (foto del propietario en Google Maps, buena calidad); Street View de la esquina (baja calidad, no usable); portada FB = fotomontaje letrero Tecomán + logo. No existe foto de fachada buena — pedirla al usuario o usar la foto del interior en "Conoce la unidad".

**Propuesta de valor (los 4 ángulos de la campaña, deben ser secciones/mensajes del sitio):**
- A. Lista de espera / traslados: "lugares disponibles esta misma semana, sin viajar a Colima"
- B. Recién diagnosticado: "te orientamos sin costo — proceso, catéter, fístula, frecuencia"
- C. Calidad y confianza: "equipos modernos, monitoreo continuo, conoce la unidad sin compromiso, sala de espera para acompañantes"
- D. Paciente en tránsito: "sesiones temporales con tu mismo esquema; solo resumen clínico y laboratorios; confirmación el mismo día"

**Mensaje transversal (aparece en los 4 anuncios — repetir en hero y footer):**
"Médico altamente capacitado en cada turno y nefrólogo supervisando."

**Identidad visual:** Azul Renalia (logo: azul #1e4e9c aprox sobre blanco), acento azul claro, tipografía sans limpia. Tema claro/oscuro automático como en padel-americano. **Sin fotos de pacientes** (privacidad); usar solo logo, foto de fachada/portada si el usuario la provee, e iconografía.

---

## Estructura de la página

1. **Header fijo**: logo texto "RENALIA · Tecomán", nav ancla (Servicios · La unidad · Pacientes en tránsito · Ubicación), botón WhatsApp.
2. **Hero**: titular "Hemodiálisis en Tecomán, cerca de tu casa"; subtítulo con el mensaje transversal; 2 CTAs (WhatsApp primario, "Conoce la unidad" secundario); badge "Lugares disponibles esta semana".
3. **Barra de confianza**: 4 ítems con icono (Nefrólogo supervisando · Equipos modernos · Enfermería especializada · Sala de espera para acompañantes).
4. **¿Te suena familiar?** — 4 tarjetas, una por ángulo de campaña (A/B/C/D), cada una con su micro-CTA de WhatsApp con mensaje precargado distinto (para atribución).
5. **Servicios**: hemodiálisis de alta eficiencia, primera orientación sin costo, sesiones para pacientes en tránsito, consulta de nefrología (del catálogo renalia.mx).
6. **Conoce la unidad**: texto "te la mostramos sin compromiso" + foto del interior de la sala (o la que provea el usuario).
6b. **Nuestro equipo**: tarjeta del Dr. Héctor Parra Lomelí — Nefrólogo certificado, Director de la unidad y Responsable Sanitario; refuerza el mensaje "nefrólogo supervisando" de la campaña con nombre y cara real.
7. **Ubicación y horario**: mapa embed, dirección Valentín Gómez Farías 699 esq. Miguel Bracamontes, horario (cierre 3 p.m.; apertura pendiente), teléfono y email.
8. **CTA final**: "Cada sesión cuenta. No dejes pasar más semanas." + botón WhatsApp grande.
9. **Footer**: datos de contacto, enlace a FB, enlace a renalia.mx, aviso "Sitio informativo — no sustituye consulta médica".
10. **Botón flotante de WhatsApp** (siempre visible en móvil).

**Enlaces WhatsApp** (`https://wa.me/5213131519215?text=...`), texto precargado por sección:
- Hero/CTA final: "Hola, quiero información sobre hemodiálisis en Renalia Tecomán"
- Tarjeta A: "Hola, mi familiar necesita lugar para hemodiálisis en Tecomán"
- Tarjeta B: "Hola, me acaban de indicar hemodiálisis y quiero orientación"
- Tarjeta C: "Hola, quiero agendar una visita para conocer la unidad"
- Tarjeta D: "Hola, estoy de visita en la zona y necesito una sesión de hemodiálisis"

**SEO/GEO básico:** title/description optimizados ("Hemodiálisis en Tecomán"), JSON-LD `MedicalClinic` (nombre, dirección, geo, teléfono, horario), Open Graph, `lang="es-MX"`, favicon con gota/riñón estilizado en SVG inline.

---

## File Structure

- Create: `renalia-tecoman/index.html` — toda la página (contenido + JSON-LD)
- Create: `renalia-tecoman/styles.css` — variables de tema, layout, responsive
- Create: `renalia-tecoman/favicon.svg` — icono simple (gota azul)
- Modify: `.github/workflows/` (workflow de Pages) — agregar `renalia-tecoman/` al deploy
- Modify: `.claude/launch.json` — entrada de preview local

---

### Task 1: Esqueleto del proyecto y preview local

**Files:**
- Create: `renalia-tecoman/index.html`
- Create: `renalia-tecoman/styles.css`
- Modify: `.claude/launch.json`

- [ ] **Step 1:** Crear `index.html` con estructura semántica completa (header/nav, main con las 8 secciones vacías con sus `id`, footer) y meta tags (charset, viewport, title "Hemodiálisis en Tecomán | Renalia", description, OG, lang es-MX).
- [ ] **Step 2:** Crear `styles.css` con variables de tema (claro/oscuro vía `prefers-color-scheme` + `data-theme`), reset mínimo y tipografía.
- [ ] **Step 3:** Agregar server estático a `.claude/launch.json` (python3 -m http.server sobre `renalia-tecoman/`, puerto libre) y verificar en el preview que carga sin errores de consola.
- [ ] **Step 4:** Commit: `feat(renalia): esqueleto de landing page`

### Task 2: Hero, barra de confianza y tarjetas de los 4 ángulos

**Files:**
- Modify: `renalia-tecoman/index.html`
- Modify: `renalia-tecoman/styles.css`

- [ ] **Step 1:** Maquetar hero con titular, mensaje transversal, badge de disponibilidad y CTAs de WhatsApp (enlaces `wa.me` con texto precargado según la tabla de arriba).
- [ ] **Step 2:** Maquetar barra de confianza (4 ítems, iconos SVG inline).
- [ ] **Step 3:** Maquetar las 4 tarjetas (grid 2×2 desktop, columna en móvil) con los textos derivados de los anuncios A-D y micro-CTAs.
- [ ] **Step 4:** Verificar en preview (desktop + móvil 375px + tema oscuro) con screenshots.
- [ ] **Step 5:** Commit: `feat(renalia): hero, confianza y ángulos de campaña`

### Task 3: Servicios, unidad, ubicación, CTA final y footer

**Files:**
- Modify: `renalia-tecoman/index.html`
- Modify: `renalia-tecoman/styles.css`

- [ ] **Step 1:** Maquetar servicios (4 tarjetas), sección "Conoce la unidad" (con `<figure>` placeholder listo para la foto), ubicación con iframe de Google Maps + datos de contacto + horario placeholder marcado `<!-- TODO: confirmar horario -->`.
- [ ] **Step 2:** Maquetar CTA final, footer y botón flotante de WhatsApp.
- [ ] **Step 3:** Insertar JSON-LD `MedicalClinic` en el `<head>` con todos los datos duros.
- [ ] **Step 4:** Verificar en preview (scroll completo, anclas del nav, enlaces de WhatsApp abren con el texto correcto) y revisar consola sin errores.
- [ ] **Step 5:** Commit: `feat(renalia): servicios, ubicación y cierre`

### Task 4: Deploy

**Files:**
- Modify: workflow de Pages en `.github/workflows/`

- [ ] **Step 1:** Revisar el workflow actual (hoy solo publica `padel-americano/`) y extenderlo para incluir `renalia-tecoman/`.
- [ ] **Step 2:** Ejecutar the-security-sweep antes de commitear/publicar.
- [ ] **Step 3:** Commit + push, verificar el run de Actions y la URL pública.
- [ ] **Step 4:** Confirmar con el usuario: horario real y foto de fachada para "Conoce la unidad".

---

## Decisiones tomadas (respuestas del usuario, 17-jul-2026)

1. **Horario**: cierra a las 3:00 p.m. Falta hora de apertura y días de la semana.
2. **Foto**: no hay fachada pública buena; se usará la foto del interior de la sala (Maps, del propietario) salvo que el usuario envíe una propia.
3. **Equipo**: destacar al **Dr. Héctor Parra Lomelí — Nefrólogo, Director de la unidad y Responsable Sanitario**. Sección "Nuestro equipo" con él al frente. José Llamas Ríos = urólogo, no protagonista (posible mención de urología como servicio adicional si el usuario quiere).
4. **Dominio**: GitHub Pages por ahora; dominio propio después.

## Dudas resueltas (17-jul-2026, segunda ronda)

1. **Horario**: lunes a sábado, 7:00 a.m. – 3:00 p.m. ("por lo pronto").
2. **Urología**: SÍ incluir como servicio adicional — "Urología · Dr. José Llamas Ríos".
3. **Foto del Dr. Parra**: usar la más profesional disponible en los creativos de la campaña de Meta.
