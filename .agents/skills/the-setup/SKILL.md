---
name: the-setup
description: Reconocimiento inicial estilo Fable antes de tocar código. Úsala al inicio de cada sesión de trabajo sobre un repo, o antes de la primera edición en un proyecto que no has explorado en esta conversación. Triggers: setup, orientación, empezar tarea, nueva sesión, primer cambio en el repo, "no conozco este proyecto".
---

# The Setup — orientarse antes de actuar

Objetivo: nunca hacer la primera edición a ciegas. Fable dedica 1-2 minutos a reconocimiento barato antes de tocar nada; eso evita el 80% de los errores de contexto (convención equivocada, archivo duplicado, rama incorrecta, trabajo ya hecho).

## Procedimiento

Ejecuta los pasos 1-4 en paralelo cuando sea posible (son lecturas independientes).

### 1. Instrucciones del proyecto
- Lee `CLAUDE.md` (raíz y subdirectorio donde vas a trabajar) y cualquier manual que referencie (p. ej. `FABLE-MANUAL.md`). Sus instrucciones tienen prioridad sobre tu comportamiento por defecto.
- Si hay memoria persistente o `MEMORY.md`, revisa el índice: puede haber decisiones previas sobre este proyecto (p. ej. "deploy solo via Actions").

### 2. Estado del repositorio
- `git status` — ¿rama actual? ¿archivos modificados que NO son tuyos? Si hay cambios sin commitear que tú no hiciste, no los pises ni los incluyas en tus commits.
- `git log --oneline -10` — estilo de mensajes de commit (idioma, prefijos como `feat:`/`fix:`, scope). Imítalo.
- ¿Estás en la rama correcta para el cambio? Si vas a commitear y estás en la rama por defecto, crea una rama primero (salvo instrucción contraria).

### 3. Estructura y convenciones
- Lista la raíz y el directorio objetivo. Identifica: ¿monorepo con varios proyectos? ¿dónde vive lo que vas a tocar?
- Detecta el stack ANTES de escribir código: gestor de paquetes (lockfile presente: `package-lock.json` vs `yarn.lock` vs `pnpm-lock.yaml`; `requirements.txt` vs `pyproject.toml`), framework, versión.
- Abre 1-2 archivos similares al que vas a crear/editar y copia su idioma: nombres, densidad de comentarios, estilo de imports, patrones de error. Tu código debe leerse como el código de alrededor.

### 4. Trabajo previo relacionado
- Busca (Grep/Glob) si ya existe algo que haga lo que te pidieron: una función similar, un script, una skill, un documento. Duplicar trabajo existente es peor que no hacerlo.
- Si encuentras algo que contradice lo que el usuario pidió (p. ej. "crea X" pero X ya existe distinto), repórtalo antes de proceder.

### 5. Síntesis (obligatoria, una frase)
Antes de la primera edición, di al usuario en 1-3 frases qué encontraste que condiciona el trabajo: rama, convención relevante, algo inesperado. Si no hay nada notable, una frase basta ("Repo limpio en main, convención de commits en español, procedo").

## Anti-patrones (lo que un modelo menor hace y Fable no)

- Editar el primer archivo que aparece en la búsqueda sin verificar que es el que se usa realmente.
- Asumir npm/pip sin mirar el lockfile.
- Instalar dependencias o correr builds pesados como "exploración" — la exploración es de solo lectura.
- Explorar en exceso: si la tarea es trivial y ya conoces el contexto de esta sesión, no repitas el ritual completo. Este procedimiento es para la PRIMERA intervención, no para cada mensaje.
