# 05 — Stack y entorno: uv, Docker, PostgreSQL, gunicorn, pytest y ruff

> Guía de autoaprendizaje. Equipo: Cervecería Los Flacheros — EFI Ingeniería de Software 2026.
> Todo lo que hay que saber sobre la caja donde vive el backend y las herramientas que lo sostienen.
> En la defensa el docente puede preguntar "¿por qué uv y no pip?" o "¿por qué Docker?". Este documento es la respuesta.

---

## Qué es un entorno virtual y por qué lo necesitamos

Cuando instalás una librería de Python con `pip install django`, esa librería se va al **ambiente global** de Python de tu computadora. Si otro proyecto necesita otra versión de Django, se pisan y algo se rompe.

Un **entorno virtual** es una carpeta del proyecto con su propia copia de Python y sus propias librerías, aislada del resto. Cada proyecto tiene el suyo:

```
backend/
├── .venv/            <- entorno virtual de ESTE proyecto (creado por uv)
│   ├── python.exe
│   └── Lib/site-packages/
│       ├── django/
│       └── rest_framework/
├── pyproject.toml    <- declara qué librerías hacen falta
└── uv.lock           <- declara qué versión exacta de cada librería
```

En nuestro caso el aislamiento es doble de importante: localmente trabajamos en Windows, y en Docker el backend corre sobre **Linux con Python 3.13**. El mismo `pyproject.toml` y el mismo `uv.lock` levantan el entorno en los dos lados.

---

## uv

**uv** es un gestor de entornos virtuales y dependencias de Python, escrito en Rust. Es la herramienta que el docente pidió para este proyecto y que usamos para todo.

### Por qué uv y no pip + venv

| | pip + venv | uv |
|---|---|---|
| Velocidad | Lento al instalar (escribe archivo por archivo) | Muy rápido (está optimizado a nivel binario) |
| Determinismo | No guarda la versión exacta resuelta; cada instalación puede dar un resultado distinto | Genera `uv.lock` con la versión exacta de cada paquete |
| Cantidad de herramientas | `python -m venv` + `pip` + `pip-tools` | **Una sola** herramienta para venv, instalación y lockfile |
| Versión de Python | Usá la que tengas instalada | Puede bajar y gestionar el Python que pidas (3.13) |

La palabra clave es **determinismo**: con `uv.lock`, lo que corre en tu máquina, en la máquina de Ema y dentro de Docker es exactamente lo mismo.

### Comandos que usamos

| Comando | Qué hace |
|---|---|
| `uv init` | Inicializa un proyecto Python (crea el `pyproject.toml` base) |
| `uv venv` | Crea el entorno virtual `.venv` |
| `uv add django` | Agrega una dependencia y actualiza `pyproject.toml` + `uv.lock` |
| `uv add --dev pytest` | Agrega una dependencia del grupo de desarrollo |
| `uv sync` | Instala **exactamente** lo que dice `uv.lock` en `.venv` (con el grupo dev) |
| `uv sync --no-dev` | Igual, pero sin el grupo dev (lo usa Docker en producción) |
| `uv lock` | Regenera el lockfile después de tocar dependencias a mano |
| `uv run python manage.py runserver` | Ejecuta un comando **dentro** del entorno, sin activarlo a mano |
| `uv python pin 3.13` | Fija la versión de Python del proyecto en `.python-version` |

Truco que ahorra dolores de cabeza: no hace falta "activar" el entorno (`activate`). Con `uv run ...` uv ya lo usa. Si un comando falla con "No module named X", casi siempre es porque lo corriste sin `uv run`.

### Instalación en Windows

```powershell
winget install --id=astral-sh.uv -e
```

El instalador agrega uv al **PATH**, que es la lista de carpetas desde donde Windows busca los comandos. Pero la terminal abierta no se entera del cambio: **hay que cerrar y abrir una terminal nueva**. Ese es el error número uno de la Fase 0.

Verificación:

```powershell
uv --version
# uv 0.13.2
```

Y el PATH de uv en Windows vive en `%USERPROFILE%\.local\bin`. Si `uv` no se encuentra, agregá esa carpeta al PATH del sistema o abrí una terminal nueva.

> **Para la defensa:** "Usamos uv porque es una sola herramienta para el entorno virtual, la instalación y el lockfile, es rápido y genera un `uv.lock` determinista. El docente pidió uv explícitamente y nos sirve porque el mismo lockfile levanta el entorno igual en Windows y dentro de Docker."

---

## `pyproject.toml`

Es el archivo de declaraciones del proyecto: qué dependencias necesita, con qué versión de Python, y cómo se configuran las herramientas. Es el archivo estándar de Python desde PEP 621.

Nuestro `pyproject.toml` tiene estas secciones:

```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "django>=5.2,<5.3",
    "djangorestframework>=3.17,<3.18",
    "drf-spectacular>=0.28",
    "django-filter>=25.1",
    "django-cors-headers>=5.0",
    "psycopg[binary]>=3.2",
    "whitenoise>=6.12",
    "gunicorn>=26.2",
    "dj-database-url>=3.0",
]

[dependency-groups]
dev = [
    "pytest>=9.1",
    "pytest-django>=4.14",
    "ruff>=0.17",
]

[tool.uv]
package = false

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["tests.py", "test_*.py"]
```

Qué significa cada cosa:

- **`[project]`**: identidad y dependencias de producción. Estas van a producción y a Docker.
- **`dependencies`**: lo que el backend necesita para funcionar: Django 5.2 LTS, DRF 3.17.x, drf-spectacular (documentación OpenAPI), django-filter (filtros), django-cors-headers (CORS), psycopg (driver de PostgreSQL), whitenoise y gunicorn.
- **`[dependency-groups]` con `dev`**: herramientas **solo de desarrollo**: pytest, pytest-django y ruff. No van a producción; por eso Docker instala con `--no-dev`.
- **`[tool.uv] package = false`**: dice que este proyecto **no es un paquete instalable**. Un proyecto Django es un código que se ejecuta, no una librería que otros importan desde PyPI. Sin esto, `uv sync` intenta construir e instalar el propio proyecto y falla porque no hay `build-system` ni módulo del mismo nombre. Es la línea que más gente se saltea y la que más rompe.
- **`[tool.ruff]`**: configuración del linter/formatter: ancho de línea 88 y objetivo Python 3.13.
- **`[tool.pytest.ini_options]`**: le dice a pytest dónde viven los settings de Django (`config.settings`) y cómo reconocer archivos de tests.

---

## `uv.lock`

`uv.lock` es un archivo **generado** que congela la resolución completa de dependencias: paquete por paquete, versión exacta, hash del archivo, y hasta las dependencias transitivas (las que trae cada paquete sin que las pidas).

Se **commitea** sí o sí, junto con `pyproject.toml`. Motivos concretos en nuestro proyecto:

1. **Reproducibilidad local**: Ema (o vos en otra máquina) ejecuta `uv sync` y recibe exactamente las mismas versiones.
2. **Reproducibilidad en Docker**: el `Dockerfile` usa `uv sync --frozen`, que **prohibe** que uv actualice el lockfile. Si el `uv.lock` del repo no coincide con el `pyproject.toml`, el build falla en lugar de instalar una versión sorpresa.
3. **Auditoría**: en la defensa se puede mostrar que el proyecto está congelado y no depende de la suerte de la red.

Regla simple: **`pyproject.toml` lo escribís vos; `uv.lock` lo escribe uv; los dos van a git.**

---

## Docker

Tres definiciones chiquitas:

- **Imagen**: una plantilla inmutable con el sistema operativo base, Python y todo lo instalado. Es la receta horneada.
- **Contenedor**: una ejecución de esa imagen. Arranca, corre y se puede borrar. Podés tener cinco contenedores de la misma imagen.
- **Volumen**: una carpeta del host que se "engancha" dentro del contenedor para que los datos **sobrevivan** a borrarlo.

### Por qué nos sirve, y qué resuelve en nuestro caso

- **Levanta igual en cualquier máquina**: no importa si en la compu de Ema falta PostgreSQL o tiene otra versión; el contenedor trae todo.
- **Reproduce producción**: en producción el backend corre en Linux con PostgreSQL, no en Windows con SQLite. Con Docker, localmente corremos casi lo mismo que en el servidor.
- **Aísla servicios**: PostgreSQL 17 corre en su propio contenedor, separado del backend. No hay que instalar Postgres en Windows.
- **Se documenta en el README**: `docker compose up --build` es una línea que cualquiera puede ejecutar para ver el proyecto andando.

---

## Dockerfile

Nuestro Dockerfile es **single-stage**: un solo `FROM`, sin etapas intermedias de compilación. Con dos semanas y dos principiantes, un archivo que se lee de una pasada vale más que unos segundos de ahorro de imagen.

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.2 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uv run python manage.py collectstatic --noinput && uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
```

Instrucción por instrucción:

| Instrucción | Qué hace | Por qué |
|---|---|---|
| `FROM python:3.13-slim` | Parte de la imagen oficial de Python 3.13 en su variante "slim" (sin herramientas de más) | Misma versión que localmente (`requires-python = ">=3.13"`); "slim" mantiene la imagen chica |
| `COPY --from=ghcr.io/astral-sh/uv:0.13.2 /uv /uvx /bin/` | Copia los binarios de **uv 0.13.2** desde su propia imagen oficial adentro de la nuestra | Traemos uv sin instalarlo ni compilarlo; además fijamos la versión exacta |
| `ENV PYTHONUNBUFFERED=1` | Los prints salen inmediatamente a los logs | Si no, en `docker compose logs` los mensajes de Django quedan bufferizados y los ves tarde |
| `ENV UV_COMPILE_BYTECODE=1` | uv compila los `.py` a `.pyc` | Arranque más rápido del contenedor |
| `ENV UV_LINK_MODE=copy` | uv copia en vez de enlazar paquetes | Evita errores de "device or resource busy" en volúmenes |
| `ENV PATH="/app/.venv/bin:$PATH"` | El venv queda primero en el PATH | `python`, `gunicorn` y `manage.py` se resuelven sin escribir rutas raras |
| `WORKDIR /app` | Carpeta de trabajo del contenedor | Todas las instrucciones siguientes arrancan ahí |
| `COPY pyproject.toml uv.lock ./` | Copia **solo** los archivos de dependencias | Ver capa de cache abajo |
| `RUN uv sync --frozen --no-dev --no-install-project` | Instala las dependencias de `uv.lock` tal cual | `--frozen` no deja que uv modifique el lockfile; `--no-dev` deja afuera pytest y ruff; `--no-install-project` no intenta instalar el proyecto (porque es `package = false`) |
| `COPY . .` | Copia el código del backend | El código va **después** de las dependencias |
| `EXPOSE 8000` | Documenta que el contenedor escucha en el puerto 8000 | No abre nada por sí solo; es documentación para el compose |
| `CMD` | Lo que corre al arrancar el contenedor | Primero `collectstatic`, después gunicorn |

### Por qué el cache de la capa de dependencias funciona

Docker guarda una **capa** (imagen en caché) por cada instrucción. Si cambiás una, todas las de abajo se invalidan y se reconstruyen.

Por eso el orden importa: `COPY pyproject.toml uv.lock ./` + `RUN uv sync ...` van **antes** del `COPY . .` del código. Si solo cambiaste un `.py` de `core/views.py`, Docker ve que los archivos de dependencias no cambiaron, **reusa la capa con todo ya instalado** y solo vuelve a copiar el código. Si fuera al revés, cada tipeo en un modelo dispararía una reinstalación completa de Django y compañía.

> **Para la defensa:** "El Dockerfile es single-stage sobre python:3.13-slim, copia el binario de uv desde su imagen oficial y ejecuta `uv sync --frozen --no-dev` con los archivos de dependencias primero que el código, así el caché de capas evita reinstalar las librerías en cada cambio. `--no-dev` mantiene pytest y ruff fuera de la imagen de producción."

---

## Docker Compose

**Compose** describe y levanta varios servicios de una vez desde un solo archivo, `compose.yaml`. El nuestro levanta dos: `db` (PostgreSQL 17) y `web` (el backend).

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-flacheros}
      POSTGRES_USER: ${POSTGRES_USER:-flacheros}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-flacheros}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-flacheros} -d ${POSTGRES_DB:-flacheros}"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DATABASE_URL: postgres:// ${POSTGRES_USER:-flacheros}:${POSTGRES_PASSWORD:-flacheros}@db:5432/${POSTGRES_DB:-flacheros}
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
```

Conceptos:

- **Servicios**: cada bloque es un contenedor con su configuración. `db` y `web`.
- **`depends_on` + `condition: service_healthy`**: "no arranques `web` hasta que `db` esté sano". Sin la condición, Django intentaría conectarse a Postgres antes de que Postgres esté listo y el primer `migrate` fallaría. Es el error clásico del "first run".
- **`healthcheck` con `pg_isready`**: el contenedor de Postgres responde a ese comando cuando está aceptando conexiones. Es el semáforo que usa `depends_on`.
- **Volúmenes**: `postgres_data` guarda los datos de la base de fuera del ciclo de vida del contenedor. `docker compose down` no borra los datos; `down -v` sí.
- **`env_file`**: lee el archivo `.env` (copia de `.env.example`, con tus valores). Ahí viven `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `POSTGRES_*` y `CORS_ALLOWED_ORIGINS`.
- **`${VAR:-default}`**: usa la variable `VAR` si existe; si no, usa el valor por defecto de la derecha. Así el compose anda sin `.env` para arrancar.
- **`ports: "8000:8000"`**: mapea el puerto 8000 del contenedor al 8000 de la máquina. Sin esto, el backend sería inaccesible desde `localhost:8000`.
- **`version:`**: ya no se usa. Las versiones modernas de Compose lo ignoran y los linters lo marcan como obsoleto. Nuestro archivo no lo trae.

Dato clave: dentro de Compose, el backend no habla con `localhost:5432` sino con el **nombre del servicio**: `db`. Por eso `DATABASE_URL` apunta a `db:5432`.

> **Para la defensa:** "El compose define dos servicios: `db` con PostgreSQL 17 y su healthcheck con `pg_isready`, y `web` que espera a que la base esté sana con `depends_on: condition: service_healthy`. Los datos viven en el volumen `postgres_data`, la configuración en `.env`, y `db` es el hostname que usa el backend en `DATABASE_URL`."

---

## PostgreSQL

**PostgreSQL 17** es el Sistema de Gestión de Bases de Datos Relacionales (SGBD) que corre en su contenedor, en el puerto 5432.

¿Por qué no SQLite, que trae Django por defecto? Cuatro motivos:

1. **Concurrencia real**: SQLite escribe con un candado a la vez; en un entorno con varios usuarios se vuelve cuello de botella. PostgreSQL atiende conexiones en paralelo.
2. **Tipos y restricciones**: `DecimalField` se comporta de verdad, hay constraints, hay transacciones serias.
3. **Cerca de producción**: lo que el docente ve en la defensa es lo que se desplegaría.
4. **Práctica**: es el SGBD que vas a encontrar en cualquier trabajo.

Credenciales y datos, definidos con variables de entorno:

| Variable | Qué define | Valor en dev |
|---|---|---|
| `POSTGRES_DB` | Nombre de la base | `flacheros` |
| `POSTGRES_USER` | Usuario | `flacheros` |
| `POSTGRES_PASSWORD` | Contraseña | la que pongas en `.env` |

Y el cambio más lindo de todo el stack: **para pasar de SQLite a PostgreSQL solo cambia una línea**, la `DATABASE_URL` en `.env`:

```
# SQLite (Fase 1, a piacere)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL en Docker (Fase 6)
DATABASE_URL=postgres://flacheros:flacheros@db:5432/flacheros
```

El código de `config/settings.py` lee esa variable con `dj-database-url` y arma el `DATABASES`. Ninguna vista, modelo ni serializer se entera.

---

## gunicorn vs runserver

- **`python manage.py runserver`** es el servidor de desarrollo de Django: recarga al detectar cambios, muestra pantallas de error detalladas, maneja una request a la vez. Sirve para trabajar, **no para producción**.
- **`gunicorn`** (*Green Unicorn*) es un servidor de aplicaciones WSGI de producción: maneja varias conexiones en paralelo con varios *workers* (procesos), es rápido y no sirve pantallitas de debug.

En nuestro proyecto:

| Dónde | Qué corre | Por qué |
|---|---|---|
| Local en Windows (Fase 1-5) | `uv run python manage.py runserver` | Recarga instantánea y errores legibles mientras desarrollamos |
| Contenedor Docker (Fase 6) | `gunicorn config.wsgi:application --bind 0.0.0.0:8000` | Es lo que se desplegaría de verdad |

Dos detalles de gunicorn que salen en la defensa:

1. **No corre en Windows nativo.** Gunicorn depende de mecanismos de Unix (señales y `fork`) que no existen en Windows. Por eso en local usamos `runserver` y gunicorn vive adentro del contenedor Linux. Para probarlo en Windows hay que usar el contenedor o WSL.
2. **`config.wsgi:application`** le dice a gunicorn dónde está la entrada del proyecto: el módulo `config/wsgi.py` y su objeto `application`. Es el mismo punto de entrada que usa cualquier servidor WSGI.

---

## whitenoise y `collectstatic`

Los **archivos estáticos** son los que no cambian con cada request: CSS, JavaScript, imágenes, fuentes de los íconos del admin. Django no los sirve por sí mismo en producción; hace falta algo que los entregue.

- **`collectstatic`** es un comando de Django que **recolecta** los estáticos de todas las apps (por ejemplo, los del admin de Django) y de nuestro `static/` propio, y los junta en una sola carpeta (`staticfiles/`).
- **whitenoise** es una librería que **sirve esa carpeta** desde dentro del propio proceso de gunicorn. Sin ella haría falta otro servicio (nginx o un CDN) para entregar los CSS.

En la práctica, dos piezas:

```python
# config/settings.py
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]   # nuestros archivos
STATIC_ROOT = BASE_DIR / "staticfiles"     # dónde juntarlos

MIDDLEWARE = [
    # ... django.middleware.security ...
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]
```

Y el `CMD` del contenedor:

```
uv run python manage.py collectstatic --noinput && uv run gunicorn ...
```

¿Por qué `collectstatic` va **antes** de gunicorn en el mismo comando? Porque whitenoise sirve la carpeta `staticfiles/`, y esa carpeta no existe hasta que se ejecuta `collectstatic`. El `--no-input` evita la pregunta interactiva de "¿sobrescribo?" para que el contenedor arranque solo.

> **Para la defensa:** "whitenoise sirve los archivos estáticos desde el mismo proceso de gunicorn, sin servicios extra. `collectstatic` junta los estáticos del admin y los nuestros en `STATIC_ROOT`, y por eso corre antes de arrancar gunicorn en el comando del contenedor."

---

## pytest y pytest-django

Un **test** es un pedacito de código que verifica que algo se comporta como esperamos. Si mañana tocamos `serializers.py` y el test falla, sabemos al instante que rompimos algo.

**pytest** es el corredor de tests más usado de Python. **pytest-django** es el plugin que le habla a Django: le da acceso a la base de datos, a los settings y al cliente de pruebas.

### Estructura: arrange-act-assert

Todo test tiene tres tiempos:

```python
def test_crear_pedido_suma_total(client):
    # Arrange: preparar los datos
    cliente_db = Cliente.objects.create(nombre="Marcela", apellido="Paz",
                                        email="m@f.com", dni="30111222")
    cerveza = Cerveza.objects.create(nombre="IPA del Flachero", precio=12500,
                                     volumen_ml=473, alcohol_pct=6.5,
                                     stock=10, tipo="ENVASE")

    # Act: hacer la acción que queremos probar
    respuesta = client.post("/api/pedidos/", {"cliente": cliente_db.id}, format="json")

    # Assert: verificar el resultado
    assert respuesta.status_code == 201
```

- **Arrange** (preparar): crear los datos que el test necesita.
- **Act** (actuar): ejecutar exactamente una cosa.
- **Assert** (verificar): comprobar el resultado. Si falla, pytest marca el test en rojo con el detalle.

### Dos piezas clave

- **`APIClient`** de `rest_framework.test`: es un cliente HTTP de prueba. Hace `get`, `post`, `patch`, `delete` contra nuestras URLs sin levantar un servidor ni tocar la red. Es el que aparece arriba como `client`.
- **`@pytest.mark.django_db`**: marcador que le dice a pytest "este test necesita la base de datos". Crea una base de prueba y la limpia al terminar, así los tests no contaminan los datos reales.

### Fixtures

Una **fixture** es un dato de prueba reutilizable: una función que devuelve un objeto listo para que todos los tests la compartan.

```python
@pytest.fixture
def cerveza(db):
    return Cerveza.objects.create(nombre="Stout del Flachero", precio=9900,
                                  volumen_ml=473, alcohol_pct=5.8,
                                  stock=5, tipo="ENVASE")

def test_precio_positivo(cerveza):
    assert cerveza.precio > 0
```

pytest inyecta la fixture por nombre de parámetro. Evita repetir el mismo `create()` en cada test.

---

## ruff

**ruff** es un linter y formatter de Python, escrito en Rust: revisa el código, lo marca si está mal escrito y lo reordena según la convención. Lo usamos en dos modos distintos:

| Comando | Qué hace | Cuándo |
|---|---|---|
| `uv run ruff check .` | **Lector**: encuentra errores y código sospechoso (variables sin usar, imports rotos) | Antes de cada commit |
| `uv run ruff check --fix .` | Igual, pero arregla lo que puede arreglar solo | Cuando marca cosas fáciles |
| `uv run ruff format .` | **Formateador**: reescribe el archivo con la convención de estilo (indentación, comillas, saltos) | Después de escribir código |

La diferencia que no se ve al principio: **`check` puede cambiar el comportamiento** (saca un import muerto que a veces hacía efecto), **`format` nunca lo cambia**, solo recorta y ordena.

---

## Tabla de comandos por propósito

Todo se corre desde `backend/` con `uv run` (salvo los comandos de Docker).

| Propósito | Comando |
|---|---|
| **Cotidiano** | |
| Arrancar el servidor de desarrollo | `uv run python manage.py runserver` |
| Shell interactiva con el proyecto | `uv run python manage.py shell` |
| Revisar la salud del proyecto | `uv run python manage.py check` |
| Crear admin para probar el panel | `uv run python manage.py createsuperuser` |
| **Migraciones** | |
| Generar migración tras tocar modelos | `uv run python manage.py makemigrations` |
| Aplicar migraciones | `uv run python manage.py migrate` |
| Ver migraciones pendientes | `uv run python manage.py showmigrations` |
| Ver SQL de una migración | `uv run python manage.py sqlmigrate core 0001` |
| Recolectar estáticos | `uv run python manage.py collectstatic --noinput` |
| **Dependencias** | |
| Instalar todo lo del lockfile | `uv sync` |
| Agregar una dependencia | `uv add django-filter` |
| Agregar una de desarrollo | `uv add --dev pytest-django` |
| **Calidad** | |
| Tests | `uv run pytest` |
| Tests con detalle de fallos | `uv run pytest -v` |
| Un solo test | `uv run pytest core/tests.py::test_nombre` |
| Linter | `uv run ruff check .` |
| Formateo | `uv run ruff format .` |
| **Docker** | |
| Levantar todo | `docker compose up --build` |
| Levantar en segundo plano | `docker compose up -d --build` |
| Ver logs | `docker compose logs -f web` |
| Estado de los servicios | `docker compose ps` |
| Abrir psql adentro del contenedor | `docker compose exec db psql -U flacheros -d flacheros` |
| Parar servicios | `docker compose down` |
| Parar y borrar los datos | `docker compose down -v` |

---

## Ejercicios

### 1. Entorno virtual y uv

a) ¿Qué carpeta crea `uv sync` y qué contiene?
b) ¿Para qué sirve `[tool.uv] package = false`? ¿Qué falla sin eso?
c) Un compañero corrió `uv add --dev ruff` y le quedó en `dependencies` en vez de en el grupo `dev`. ¿Cómo se arregla?

<details>
<summary>Respuestas</summary>

a) Crea `.venv/` con el binario de Python, las librerías instaladas y los scripts de cada paquete. Es el entorno aislado del proyecto.
b) Le dice a uv que el proyecto no es un paquete instalable. Sin eso, `uv sync` intenta construir e instalar el propio proyecto y falla porque no hay `build-system` ni un módulo con el nombre del proyecto.
c) Quitando el paquete de `[project] dependencies` y dejándolo solo en `[dependency-groups] dev`, y después corriendo `uv sync`. O directamente `uv remove <paquete>` y volver a agregarlo con `--dev`.

</details>

### 2. Dockerfile

a) ¿Por qué el `COPY pyproject.toml uv.lock ./` va antes del `COPY . .`?
b) ¿Qué pasa si sacás `--frozen` del `uv sync`?
c) ¿Para qué sirve `EXPOSE 8000` y qué pasaría si lo borrás?

<details>
<summary>Respuestas</summary>

a) Porque la capa de dependencias queda cacheada: si después cambiás solo un `.py`, Docker no reinstala nada y solo vuelve a copiar el código.
b) uv podría actualizar dependencias para que se cumplan los rangos del `pyproject.toml`, rompiendo el determinismo del lockfile. En un build de producción eso es indeseable.
c) Es documentación de qué puerto escucha el contenedor; no abre nada. Si lo borrás, el build funciona igual y el puerto sigue mapeado en el compose; se pierde solo la pista para quien lee el Dockerfile.

</details>

### 3. Compose y PostgreSQL

a) ¿Por qué en `DATABASE_URL` se usa `db:5432` y no `localhost:5432`?
b) ¿Qué hace `condition: service_healthy` y qué error evita?
c) ¿Cómo se llama el archivo que guarda los datos de Postgres y por qué sobrevive a `docker compose down`?

<details>
<summary>Respuestas</summary>

a) Porque dentro de la red de Compose, el hostname del servicio `db` es su nombre. `localhost` dentro del contenedor `web` sería el propio contenedor `web`.
b) Espera a que el healthcheck de Postgres (`pg_isready`) dé OK antes de arrancar `web`. Evita que Django intente migrar la base antes de que esté disponible.
c) El volumen `postgres_data`, montado en `/var/lib/postgresql/data`. Los volúmenes viven fuera del contenedor, así que `down` borra los contenedores y conserva los datos; solo `down -v` los borra.

</details>

### 4. gunicorn, whitenoise y estáticos

a) ¿Por qué el contenedor usa gunicorn y no `runserver`?
b) Explicá con tus palabras por qué `collectstatic` va antes de gunicorn.
c) ¿Por qué gunicorn no puede correr en Windows nativo?

<details>
<summary>Respuestas</summary>

a) Porque `runserver` es el servidor de desarrollo: recarga, debug detallado y una request a la vez. Gunicorn es un servidor WSGI de producción con varios workers.
b) whitenoise sirve la carpeta `staticfiles/`, que es la que arma `collectstatic`. Si arrancara gunicorn sin haberla creado, los CSS del admin y los del front devuelven 404.
c) Depende de señales de Unix y de `fork` para crear workers, mecanismos que Windows nativo no ofrece.

</details>

### 5. Tests y ruff

a) Escribí el esqueleto (arrange-act-assert) de un test que verifique que `GET /api/cervezas/` responde 200.
b) ¿Qué marcador necesita ese test y por qué?
c) Si `ruff format` marca un archivo como modificado, ¿puede haberse roto la lógica?

<details>
<summary>Respuestas</summary>

a)

```python
def test_listar_cervezas_devuelve_200(client, cerveza):
    respuesta = client.get("/api/cervezas/")
    assert respuesta.status_code == 200
```

b) `@pytest.mark.django_db`, porque el listado consulta la base de datos; sin el marcador, pytest falla con un error de "database access not allowed".
c) No. `ruff format` solo reordena y recorta estilo (indentación, comillas, saltos de línea), sin cambiar el comportamiento. `ruff check --fix` en cambio puede tocar cosas con efecto, como sacar imports.

</details>

---

> **Para la defensa:** "El entorno está gestionado con uv 0.13.2 y su `uv.lock` congelado, que sirve igual en Windows y en Docker. La imagen es single-stage sobre python:3.13-slim con el binario de uv copiado desde su imagen oficial; el compose levanta PostgreSQL 17 con healthcheck y gunicorn 26.2.0 con whitenoise para los estáticos. Localmente desarrollo con `runserver` y pruebo con pytest; en el contenedor corre gunicorn como en producción."
