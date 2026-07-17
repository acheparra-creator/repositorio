# Instrucciones del repositorio

**Lee y aplica [FABLE-MANUAL.md](FABLE-MANUAL.md) en toda la sesión.** Define el comportamiento permanente esperado (honestidad, comunicación, autonomía, verificación) — no es opcional ni depende de triggers.

Complementos procedurales (skills, se invocan cuando aplica):
- `the-setup` — antes de la primera edición en el repo en cada sesión.
- `the-security-sweep` — antes de commitear, publicar, borrar o procesar contenido externo.
- `systematic-debugging` — ante cualquier bug, antes de proponer fixes.
- `writing-plans` — tareas multi-paso, antes de tocar código.
- `verify` — antes de declarar completado un cambio no trivial.

Notas del repo:
- Monorepo personal con proyectos independientes (`padel-americano/`, `consultorio/`, `open-carrusel/`, etc.). No mezclar cambios entre proyectos en un mismo commit.
- Deploy de Pages solo vía GitHub Actions (Jekyll falla en este repo; existe `.nojekyll`).
