# T03 — Repositorio git local y primer commit

**Fase:** 0
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Inicializamos el repositorio git **en la raíz del proyecto** con la rama `main` (`git init --initial-branch=main`), configuramos la identidad del autor (`FedeAr25 <f.arballo@itecriocuarto.org.ar>`) y escribimos el `.gitignore` de la raíz, que es el que manda para todo el repo: `.venv/`, `.env`, `*.sqlite3`, `__pycache__/`, `node_modules/`, `.next/`, etc. Después hicimos el primer commit con todo el contenido inicial (backend, docs, tasks y el README del frontend).

Un detalle que hay que entender acá: git no trackea carpetas vacías, y `frontend/` estaba vacía (la completa Ema). Por eso le escribimos un `README.md` mínimo adentro: es la única forma de que esa carpeta exista en el repositorio desde el primer commit.

El repo quedó en **un solo git, en la raíz**, no uno por subcarpeta: recordemos que tuvimos que borrar el `.git/` que `uv init` había creado dentro de `backend/` justamente para que no hubiera dos repositorios.

## Conceptos que aparecen acá
- **Repositorio git y commit** — el repositorio es la base de datos del historial del proyecto (carpeta `.git/`); un commit es una foto del estado del proyecto en un momento, con mensaje y autor. Sirve para volver atrás, comparar versiones y, sobre todo, para mostrar el proceso al docente.
- **`.gitignore`** — lista de archivos que git debe ignorar. `.env` no puede subirse porque tiene secretos (quien lo clone tendría las credenciales); `*.sqlite3` no sube porque es la base de datos local, que se regenera con `migrate` y además cambia en cada máquina.
- **Ramas `feature/<tarea>`** — cada tarea se hace en su propia rama (`feature/estilos`, `feature/docker`, ...) para no dejar `main` roto mientras se trabaja; al terminar, se mergea a `main`.
- **Merge `--no-ff`** — `git merge --no-ff feature/x` fuerza un commit de merge aunque se pudiera hacer fast-forward. Deja en el historial un nodo explícito de "acá se integró esta tarea", que es justamente lo que el docente quiere ver.
- **Commits convencionales** — prefijos estandarizados en el mensaje: `feat:` (funcionalidad nueva), `fix:` (arreglo), `docs:` (documentación), `chore:` (tareas de mantenimiento, sin impacto en el código), `test:` (tests), `refactor:` (reorganizar código sin cambiar comportamiento).

## Archivos
- `.gitignore` (raíz) — reglas de ignore para todo el repo: entornos y Python, Django (`*.sqlite3`, `staticfiles/`, `media/`), secretos (`.env`), testing (`.pytest_cache/`, `.coverage`) y frontend (`node_modules/`, `.next/`, `.env.local`).
- `frontend/README.md` — README placeholder en español: documenta brevemente que esa carpeta la completa Ema y que la API se consume solo con `Authorization: Token <key>`. Existe también para que git trackee la carpeta `frontend/`.
- Primer commit con todo lo anterior más `backend/`, `docs/` y `tasks/`.

## Lo que hay que mirar en el código
- `.gitignore`::sección "Secretos" (`.env`) y sección "Django" (`*.sqlite3`) — las dos reglas que evitan filtrar información sensible o archivos regenerables.
- `.gitignore`::sección "Entornos y Python" (`.venv/`) — sin esta línea, el entorno virtual completo (miles de archivos de Windows) entraría al repo en el primer commit.
- `git log --oneline` — el historial es la evidencia de proceso; a partir de acá cada tarea debe sumar un commit.

## Para la defensa
> **Pregunta:** ¿Cómo evidenciaron el trabajo en equipo?
> **Respuesta:** Con el historial de git: una rama por tarea, commits chicos y descriptivos con prefijos convencionales (`feat:`, `fix:`, `docs:`), y merges a `main` con `--no-ff`. Eso deja registrado qué se hizo, cuándo y en qué orden, y es lo que se muestra en la defensa.

> **Pregunta:** ¿Qué pasa si alguien sube un `.env` con secretos?
> **Respuesta:** No puede pasar: `.gitignore` excluye `.env` desde el primer commit y lo verificamos con `git ls-files`. Ese archivo queda solo en la máquina de cada uno; lo que se commitea es `.env.example`, que tiene la plantilla sin valores reales.

## Errores que nos pasaron y cómo los resolvimos
Sin errores.

## Verificación
- [ ] `git log --oneline` → muestra 1 commit: `chore: inicializa proyecto con estructura base`
- [ ] `git branch` → muestra solo `main`
- [ ] `git status` → limpio, sin archivos pendientes
- [ ] `git ls-files | Select-String "venv|\.env$"` → cero coincidencias (no se commiteó `backend/.venv/` ni ningún `.env`)
