# T02 — Estructura del proyecto y dependencias con uv

**Fase:** 0
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Creamos la estructura de carpetas (`backend/`, `frontend/`, `docs/`, `tasks/`) e inicializamos el proyecto Python dentro de `backend/` con `uv init --app --name cerveceria-backend --python 3.13`. Después declaramos todas las dependencias del stack en `pyproject.toml`, generamos el `uv.lock` con `uv lock` e instalamos el entorno con `uv sync`. También escribimos los archivos de configuración que acompañan al proyecto: `.env.example` (plantilla de variables de entorno), `.gitignore` y `.dockerignore`.

La decisión de la fase fue la base de datos: en local usamos **SQLite** (`DATABASE_URL=sqlite:///db.sqlite3`) porque no requiere instalar nada y la app levanta con un solo comando; en Docker, que es el entregable, corre **PostgreSQL 17**. La misma variable `DATABASE_URL` cambia según dónde corra la app, así que el código es idéntico en los dos casos.

El error importante de la fase fue el `uv add` que falló porque uv intentaba **construir el proyecto como si fuera un paquete instalable**; está explicado más abajo, es el que hay que poder contar en la defensa.

## Conceptos que aparecen acá
- **`pyproject.toml`** — el archivo único de configuración del proyecto Python moderno: declara nombre, versión, dependencias y la config de las herramientas (ruff, pytest). Se usa en vez de `requirements.txt` porque un solo archivo reemplaza al requirements, al setup.py y a los archivos de configuración de cada herramienta.
- **Dependency group (`[dependency-groups] dev`)** — grupo de dependencias que solo se instalan para desarrollar (pytest, ruff) y no van a producción. Se instalan con `uv sync --group dev` y así la imagen de Docker puede hacer `--no-dev` y no se lleva herramientas de test.
- **`uv.lock`** — lockfile: congela la versión exacta de cada una de las dependencias (y de sus dependencias) que resolvió uv. Se commitea a propósito: es lo que garantiza que el proyecto se instale igual en mi máquina, en la de mi compañero y en Docker.
- **`[tool.uv] package = false`** — le dice a uv que este proyecto es una **aplicación**, no una librería para distribuir. Sin esto, uv intenta construir e instalar el proyecto como paquete y falla (fue justo el error que nos trabó).
- **`.venv`** — la carpeta del entorno virtual: Python + paquetes instalados, aislados del sistema. La crea uv con `uv sync`; no se commitea porque cada máquina lo genera con `uv sync`.
- **`.env` vs `.env.example`** — `.env` tiene los valores reales (secretos, contraseñas) y **nunca** se sube al repo; `.env.example` es la plantilla con valores de ejemplo que sí se commitea, para que otro sepa qué variables hay que crear.

## Archivos
- `backend/pyproject.toml` — declaró las 9 dependencias de producción, el group `dev`, `[tool.uv] package = false` y la config de ruff y pytest.
- `backend/uv.lock` — generado por `uv lock`; congela 30 paquetes. Se commitea.
- `backend/.python-version` — fija Python 3.13 para uv.
- `backend/.env.example` — plantilla con `DATABASE_URL=sqlite:///db.sqlite3` local y la línea de PostgreSQL 17 para Docker comentada.
- `backend/.gitignore` — generado por `uv init` y completado: `.venv/`, `__pycache__/`, `.env`, `*.sqlite3`.
- `backend/.dockerignore` — evita que el `COPY . .` del `Dockerfile` se lleve `.venv/`, `.env` y `*.sqlite3` a la imagen.
- `backend/README.md` — el README mínimo que creó `uv init`.

## Lo que hay que mirar en el código
- `backend/pyproject.toml`::`[tool.uv] package = false` — la línea que hizo funcionar `uv sync`. Sin ella, uv intenta construir el proyecto.
- `backend/pyproject.toml`::`[dependency-groups] dev` — pytest, pytest-django y ruff viven acá, fuera de las dependencias de producción.
- `backend/.env.example`::línea `DATABASE_URL=sqlite:///db.sqlite3` — la variable que decide la base de datos; en Docker se pisa con la URL de PostgreSQL del compose.
- `backend/uv.lock` — no se edita a mano; lo genera y actualiza `uv`.

## Para la defensa
> **Pregunta:** ¿Por qué SQLite y no PostgreSQL?
> **Respuesta:** En local usamos SQLite para no instalar un servidor de base de datos y que la app levante con un solo comando; en Docker, que es el entregable, corre PostgreSQL 17. La conexión se cambia únicamente con la variable `DATABASE_URL`, así que el código es idéntico en los dos casos.

> **Pregunta:** ¿Por qué commitean `uv.lock`?
> **Respuesta:** Porque fija la versión exacta de cada dependencia: es lo que hace que el proyecto se instale igual en cualquier máquina y en Docker. Sin lockfile, cada uno instala la última versión disponible y el "en mi máquina funciona" es literal.

## Errores que nos pasaron y cómo los resolvimos
- **Error:** `uv add` → `error: Failed to build 'cerveceria-backend @ file:///.../backend'` / `cause: Expected a Python module at: src\cerveceria_backend\__init__.py`
  **Causa:** `uv init --app` dejó en `pyproject.toml` un `[build-system]` con `uv_build`, y eso le decía a uv que el proyecto era un **paquete distribuible**: uv intentaba construirlo e instalarlo como librería, para lo cual esperaba encontrar el módulo de Python en `src/cerveceria_backend/__init__.py`. Un proyecto Django no es una librería: es una aplicación que se corre con `manage.py`, no algo que se instala con `pip install`.
  **Solución:** sacamos `[build-system]` y `[project.scripts]` del `pyproject.toml` y agregamos `[tool.uv] package = false`. Con eso uv deja de intentar construir el proyecto y `uv sync` instaló las dependencias sin errores.
- **Error:** `uv init --app` creó carpetas y archivos que no queríamos: `src/cerveceria_backend/` (la estructura de paquete que uv asume por defecto) y un `.git/` propio dentro de `backend/`.
  **Causa:** uv genera un esqueleto de paquete y, por defecto, también inicializa git en la carpeta; nosotros no seguimos esa estructura (Django va con `manage.py` en la raíz de `backend/`) y el repositorio git es **uno solo, en la raíz del proyecto**, no uno por subcarpeta.
  **Solución:** borramos `src/` y `backend/.git/`. Al no haber commiteado nada con `uv init`, no se perdió ningún trabajo.
- **Warning (no es error):** `Failed to hardlink files; falling back to full copy` — la caché de uv y el `.venv` están en filesystems distintos, así que uv copia en vez de enlazar. Es cosmético, no afecta nada.

## Verificación
- [ ] `uv lock` → resolvió **30 paquetes** (`uv lock --check` confirma "Resolved 30 packages")
- [ ] `uv sync` → instaló **29** sin errores (30 menos el propio proyecto, que no se instala como paquete por `package = false`)
- [ ] `uv run python --version` → `Python 3.13.5`
- [ ] `uv run python -c "import django; print(django.get_version())"` → `5.2.18`
- [ ] `uv run ruff --version` → `ruff 0.17.1`
- [ ] `uv run pytest --version` → `pytest 9.1.1`

### Versiones resueltas por `uv lock` (12 directas de las 30)

| Paquete | Versión | Para qué sirve |
|---|---|---|
| django | 5.2.18 | Framework web: ORM, admin, migraciones, settings (LTS) |
| djangorestframework | 3.17.2 | Capa de API REST: serializers, ViewSets, permisos, paginación |
| drf-spectacular | 0.30.0 | Documentación OpenAPI (Swagger UI y ReDoc) |
| django-filter | 26.2 | Filtros, búsqueda y orden en los endpoints |
| django-cors-headers | 4.9.0 | CORS: permite que el frontend en :3000 llame al backend en :8000 |
| django-environ | 0.14.0 | Lee las variables del `.env` dentro de `settings.py` |
| psycopg + psycopg-binary | 3.3.6 | Driver de PostgreSQL (se usa en Docker) |
| gunicorn | 26.2.0 | Servidor WSGI para Linux/Docker (en Windows local corre `runserver`) |
| whitenoise | 6.12.0 | Sirve los static files dentro del contenedor, sin nginx |
| pytest | 9.1.1 | Corredor de tests |
| pytest-django | 4.14.0 | Integra pytest con Django (`DJANGO_SETTINGS_MODULE`) |
| ruff | 0.17.1 | Linter y formateador, una sola herramienta |

Las otras 18 son dependencias transitivas (asgiref, sqlparse, jsonschema, inflection, etc.): las trajeron estas 12 y no hay que tocarlas.
