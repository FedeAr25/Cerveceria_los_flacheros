# backend/Dockerfile — single-stage (decisión del plan §10): UN solo FROM, sin
# multi-stage ni --mount=type=cache, para que se lea y se debuggee de una pasada.

# Base: imagen oficial de Python 3.13 en variante slim (misma versión que
# requires-python = ">=3.13" y que .python-version; slim mantiene la imagen chica).
FROM python:3.13-slim

# Traemos uv 0.13.1 copiando SOLO sus binarios desde la imagen oficial de astral.
# Esa imagen es distroless: no trae Python ni shell, por eso el binario se copia
# encima de una base que sí los tiene (python:3.13-slim) y no al revés.
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/

# Carpeta de trabajo: todas las instrucciones siguientes arrancan acá.
WORKDIR /app

# PATH="/app/.venv/bin:$PATH"  -> el venv queda primero: `python`, `gunicorn` y
#   `manage.py` se resuelven ahí, sin escribir rutas.
# UV_LINK_MODE=copy            -> uv copia en vez de enlazar paquetes, evita
#   errores "device or resource busy" cuando algo se monta por volumen.
# UV_COMPILE_BYTECODE=1        -> compila .py a .pyc: arranque más rápido.
# PYTHONUNBUFFERED=1           -> los logs de Django salen de inmediato a
#   `docker compose logs`, sin quedar bufferizados.
ENV PATH="/app/.venv/bin:$PATH" \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1

# Capa de dependencias: copiamos SOLO los archivos que definen el lock, antes que
# el código, para que el cache de capas de Docker invalide esta parte únicamente
# cuando cambian ellos (un cambio en un .py no reinstala Django y compañía).
COPY pyproject.toml uv.lock .python-version ./

# --frozen            : prohíbe que uv modifique uv.lock (determinismo del lockfile).
# --no-dev            : deja afuera el grupo dev (pytest, ruff) de la imagen.
# --no-install-project: OBLIGATORIO — el proyecto tiene [tool.uv] package = false;
#   sin esta flag uv intenta construir el propio paquete y el build falla.
RUN uv sync --frozen --no-dev --no-install-project

# Código del backend, DESPUÉS de las dependencias (ver comentario de cache arriba).
COPY . .

# Segunda pasada: instala lo que haya quedado pendiente del lock. Con
# package = false el proyecto sigue sin construirse; mantiene el venv al día.
RUN uv sync --frozen --no-dev

# Documenta el puerto que escucha el contenedor (no abre nada por sí solo;
# el mapeo real lo hace el `ports:` del compose.yaml).
EXPOSE 8000

# El CMD arranca SOLO gunicorn (punto de entrada WSGI: config.wsgi:application).
# migrate y collectstatic NO van acá: los ejecuta el `command` del compose.yaml.
# OJO con el orden: collectstatic debe correr ANTES que gunicorn, porque
# whitenoise sirve la carpeta staticfiles/ y sin ese paso el admin de Django
# aparece sin estilos (CSS 404) dentro del contenedor.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
