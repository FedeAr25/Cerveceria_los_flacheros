# 🍺 Cervecería Los Flacheros

> ## *"Arte en cada trago, tradición en cada lote"*

Sistema de gestión para una cervecería artesanal: catálogo, producción, insumos, ventas y opiniones, con una **API REST documentada** y panel de administración. Backend **Django 5.2 LTS + Django REST Framework**, frontend **Next.js** (App Router + Tailwind + JavaScript) a cargo del segundo integrante.

**Evaluación Final Integradora (EFI) — Ingeniería de Software 2026 (ITec)** · Entrega: lunes 2/11/2026 · Defensa oral: martes 3/11/2026.

![Django 5.2.18 LTS](https://img.shields.io/badge/Django-5.2.18_LTS-092E20)
![Django REST Framework 3.17](https://img.shields.io/badge/Django_REST_Framework-3.17-ff1717)
![Python 3.13.5](https://img.shields.io/badge/Python-3.13.5-3776AB)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-4169E1)
![Docker Compose v5.6.0](https://img.shields.io/badge/Docker_Compose-v5.6.0-2496ED)
![EFI 2026](https://img.shields.io/badge/EFI-Ingeniería_de_Software_2026-4A7C59)

## 1. Portada e identidad de marca

| Atributo | Valor |
|---|---|
| Nombre | **Cervecería Los Flacheros** |
| Lema | *"Arte en cada trago, tradición en cada lote"* |
| Tono | Cálido, cercano, artesanal, orgulloso; informal pero profesional |
| Público | Consumidores locales 18-45, bares/restaurantes (B2B), homebrewers y turistas cerveceros |

**Paleta de colores:**

![#F5A623](https://img.shields.io/badge/F5A623-F5A623)
![#4A7C59](https://img.shields.io/badge/4A7C59-4A7C59)
![#8B4513](https://img.shields.io/badge/8B4513-8B4513)
![#F7F7F7](https://img.shields.io/badge/F7F7F7-F7F7F7)
![#2B2B2B](https://img.shields.io/badge/2B2B2B-2B2B2B)

| Color | Hex | Uso en el proyecto |
|---|---|---|
| Ámbar (primaria) | `#F5A623` | Color principal de marca: acentos, botones y destacados |
| Lúpulo (secundaria) | `#4A7C59` | Verde de lúpulo: elementos secundarios y estados |
| Malta tostada (acento) | `#8B4513` | Detalles, títulos y toques cálidos |
| Espuma (fondos) | `#F7F7F7` | Fondos claros |
| Carbón (texto) | `#2B2B2B` | Texto principal |

La paleta y el lema se ven en la vista de bienvenida (`/`) y en el panel de administración.

## Índice

1. [Portada e identidad de marca](#1-portada-e-identidad-de-marca)
2. [Objetivo y alcance](#2-objetivo-y-alcance)
3. [Modelo de datos: planificación de tablas y relaciones](#3-modelo-de-datos-planificación-de-tablas-y-relaciones)
4. [Stack tecnológico](#4-stack-tecnológico)
5. [Instalación y puesta en marcha](#5-instalación-y-puesta-en-marcha)
6. [Tabla de endpoints](#6-tabla-de-endpoints)
7. [Autenticación por token](#7-autenticación-por-token)
8. [Autenticación por sesión](#8-autenticación-por-sesión)
9. [Panel de administración](#9-panel-de-administración)
10. [Capturas de pantalla](#10-capturas-de-pantalla)
11. [Datos de prueba](#11-datos-de-prueba)
12. [Comandos útiles](#12-comandos-útiles)
13. [Verificación](#13-verificación)
14. [Notas de implementación](#14-notas-de-implementación)
15. [Proceso del equipo (Git)](#15-proceso-del-equipo-git)
16. [Estado de la entrega](#16-estado-de-la-entrega)
17. [Autores](#17-autores)

## 2. Objetivo y alcance

**Qué es:** una aplicación Django única con dos caras para la misma base de datos:

- una **API REST** (`/api/`) con los 10 recursos del dominio, paginada, filtrable, autenticada por token o sesión y documentada con OpenAPI/Swagger/ReDoc; y
- un **panel de administración** (`/admin/`) con control total: filtros, búsqueda, orden e inlines.

**Qué resuelve:** gestionar el catálogo de estilos y cervezas, la producción (lotes con sus etapas de fermentación), los insumos (proveedores y materias primas), las ventas (clientes, pedidos y sus líneas) y las opiniones de clientes, todo sobre un dominio real de cervecería artesanal.

**Qué NO hacemos** (recorte explícito del plan, definido con el docente):

| Qué NO hacemos | Motivo del recorte |
|---|---|
| 5 apps (`catalog`, `production`, `inventory`, `sales`, `customers`) | Una sola app `core` con todo el dominio: con dos principiantes, 5 apps multiplican archivos, migraciones y permisos sin que el docente lo pida |
| Más de 10 modelos (12+) | El docente pide ≥10; cada modelo extra arrastra serializer, viewset, admin, tests y migraciones |
| Imágenes de producto (Pillow / `ImageField`) | Cada campo de imagen agrega dependencia, storage y validación; el alcance es textual |
| CI ni pipelines de automatización | El docente pide proceso Git (ramas y commits descriptivos), no automatización |
| Git Flow con ramas `develop` | El flujo chico (rama `feature/*` → commit → PR → merge `--no-ff`) alcanza y se explica en una frase |
| Usuario custom (`AbstractUser`) | La consigna de autenticación se cubre con sesión y token nativos de DRF |

El detalle de cada decisión vive en [`tasks/plan.md`](tasks/plan.md) (§2, Alcance reducido).

## 3. Modelo de datos: planificación de tablas y relaciones

10 modelos, todos en [`backend/core/models.py`](backend/core/models.py). Esta es la **planificación de tablas y relaciones** del proyecto, requerida adjunta al README (requisito R4): se diseñó antes de escribir código y se mantiene sincronizada con [`tasks/plan.md`](tasks/plan.md) §7.

### Diagrama ER

```mermaid
erDiagram
    ESTILO ||--o{ CERVEZA : "clasifica"
    CERVEZA ||--o{ LOTE : "se produce en"
    LOTE ||--|{ ETAPA_FERMENTACION : "tiene"
    PROVEEDOR ||--o{ MATERIA_PRIMA : "suministra"
    CLIENTE ||--o{ PEDIDO : "realiza"
    PEDIDO ||--|{ LINEA_PEDIDO : "contiene"
    CERVEZA ||--o{ LINEA_PEDIDO : "se vende en"
    CERVEZA ||--o{ OPINION : "recibe"
    CLIENTE ||--o{ OPINION : "escribe"
```

### Las 10 tablas, sus campos clave y sus relaciones

`C` = CharField · `T` = TextField · `DT` = DateTimeField · `Dec` = DecimalField · `Int` = IntegerField. Los campos con opciones usan `TextChoices`.

| # | Tabla (modelo) | Campos clave | Relación (FK → modelo · `related_name`) | `on_delete` |
|---|---|---|---|---|
| 1 | `Estilo` | `nombre` C(100) unique · `descripcion` T · `ibu` Int · `color` C(20) · `orden` Int def 0 | — | — |
| 2 | `Cerveza` | `nombre` C(150) unique · `descripcion` T · `precio` Dec(10,2) · `volumen_ml` Int · `alcohol_pct` Dec(4,1) · `stock` Int · `tipo` (ENVASE/GRIFO) · `activo` Bool · `fecha_creacion` DT | `estilo` → `Estilo` (`cervezas`) | **PROTECT** |
| 3 | `Lote` | `numero` C(50) unique · `fecha_inicio` Date · `fecha_fin` Date · `volumen_litros` Dec(8,2) · `estado` (PLANIFICADO/EN_PRODUCCION/FERMENTACION/MADURACION/LISTO/CANCELADO) · `notas` T | `cerveza` → `Cerveza` (`lotes`) · `usuario` → `User` (`lotes`, null) | **PROTECT** · **SET_NULL** |
| 4 | `EtapaFermentacion` | `numero` Int · `tipo` (PRIMARIA/SECUNDARIA/MADURADO) · `fecha_inicio` Date · `fecha_fin` Date · `temperatura` Dec(4,1) · `estado` (PENDIENTE/ACTIVA/COMPLETADA) | `lote` → `Lote` (`etapas`) | **CASCADE** |
| 5 | `Proveedor` | `razon_social` C(150) · `cuit` C(20) unique · `email` · `telefono` · `activo` Bool | — | — |
| 6 | `MateriaPrima` | `nombre` C(150) · `tipo` (MALTA/LUPULO/LEVADURA/OTROS) · `unidad` (KG/G/LT/UNIDAD) · `stock` Dec(10,2) · `stock_minimo` Dec(10,2) · `costo_unitario` Dec(10,2) | `proveedor` → `Proveedor` (`materias_primas`, null) | **SET_NULL** |
| 7 | `Cliente` | `nombre` C(100) · `apellido` C(100) · `email` unique · `telefono` · `dni` unique · `activo` Bool · `fecha_alta` DT · `@property nombre_completo` | — | — |
| 8 | `Pedido` | `fecha` DT · `estado` (PENDIENTE/CONFIRMADO/EN_PREPARACION/LISTO_RETIRO/ENTREGADO/CANCELADO) · `forma_pago` (EFECTIVO/TARJETA/TRANSFERENCIA) · `total` Dec(10,2) · `direccion_entrega` · `observaciones` T | `cliente` → `Cliente` (`pedidos`) | **PROTECT** |
| 9 | `LineaPedido` | `cantidad` Int · `precio_unitario` Dec(10,2) · `@property subtotal` | `pedido` → `Pedido` (`lineas`) · `cerveza` → `Cerveza` (`lineas_pedido`) | **CASCADE** · **PROTECT** |
| 10 | `Opinion` | `puntaje` Int (validators 1–5) · `comentario` T · `fecha` DT | `cerveza` → `Cerveza` (`opiniones`) · `cliente` → `Cliente` (`opiniones`) | **CASCADE** · **CASCADE** |

Son **8 relaciones FK** en total, todas con `related_name` explícito.

### Por qué se eligió cada regla `on_delete`

- **PROTECT en `Cerveza.estilo`, `Lote.cerveza` y `LineaPedido.cerveza`:** no tiene sentido borrar una cerveza que ya se produjo o se vendió; Django bloquea el borrado y protege el histórico.
- **PROTECT en `Pedido.cliente`:** un pedido sin cliente pierde sentido comercial; no se puede borrar un cliente que tiene pedidos.
- **CASCADE en `EtapaFermentacion.lote`:** una etapa de fermentación no existe sin su lote; al borrar el lote, sus etapas se borran con él.
- **CASCADE en `LineaPedido.pedido`:** las líneas son parte del pedido; si desaparece el pedido, sus líneas quedan huérfanas.
- **CASCADE en `Opinion` (desde `Cerveza` y `Cliente`):** una opinión no sobrevive a lo que comenta ni a quien la escribió.
- **SET_NULL en `Lote.usuario`:** si se borra el usuario, el lote se queda sin responsable pero el lote se conserva (es información secundaria).
- **SET_NULL en `MateriaPrima.proveedor`:** la materia prima existe aunque el proveedor se dé de baja; solo desenganchamos el vínculo.

Resumen para la defensa: **el histórico no se borra (`PROTECT`), lo dependiente desaparece con su padre (`CASCADE`), lo opcional se desengancha (`SET_NULL`).**

**Orden de migraciones (por dependencia):** `Estilo` → `Cerveza` → `Lote` → `EtapaFermentacion` · `Proveedor` → `MateriaPrima` · `Cliente` → `Pedido` → `LineaPedido` → `Opinion`. (`User` no necesita migración: lo trae `django.contrib.auth`.)

## 4. Stack tecnológico

### Backend (este repo, [`backend/`](backend/))

| Componente | Versión | Rol |
|---|---|---|
| Python | 3.13.5 | Lenguaje (`requires-python = ">=3.13"`) |
| Django | 5.2.18 **LTS** | Framework: ORM, admin, migraciones, settings |
| Django REST Framework | 3.17.x (3.17.2 fijada en `uv.lock`) | ViewSets, serializers, permisos, paginación, Browsable API |
| drf-spectacular | 0.30.0 | Esquema OpenAPI 3 + Swagger UI + ReDoc |
| django-filter | 26.2 | Filtros por campo en los endpoints (`?tipo=`, `?estado=`, …) |
| django-cors-headers | 4.9.0 | CORS para el frontend Next.js (`http://localhost:3000`) |
| django-environ | 0.14.0 | Settings 12-factor: lee las variables del `.env` |
| psycopg[binary] | 3.3.6 | Driver de PostgreSQL |
| gunicorn | 26.2.0 | Servidor WSGI de producción (dentro de Docker; en Windows local se usa `runserver`) |
| whitenoise | 6.12.0 | Sirve los static files dentro del contenedor, sin nginx |
| PostgreSQL | 17 (imagen `postgres:17`) | Base de datos en Docker (en local, SQLite por defecto) |
| uv | 0.13.1 | Gestor de entornos y dependencias (`uv sync`, `uv run`) |
| Docker + Compose | cliente Docker + Compose **v5.6.0** (v2, sin guion) | Contenedores `db` y `web` |
| pytest + pytest-django | 9.1.1 + 4.14.0 | Tests (grupo dev) |
| ruff | 0.17.1 | Lint + format, una sola herramienta (grupo dev) |

Fuente de verdad de las versiones: [`backend/pyproject.toml`](backend/pyproject.toml) y `backend/uv.lock`.

### Frontend (carpeta `frontend/`, del segundo integrante)

| Componente | Detalle |
|---|---|
| Next.js | App Router |
| Tailwind CSS | Estilos utilitarios |
| JavaScript puro | Sin TypeScript ni librerías de estado |

El contrato con el frontend está congelado en [`tasks/api-contract.md`](tasks/api-contract.md) (base URL, login por token, paginación, filtros y ejemplos de JSON).

## 5. Instalación y puesta en marcha

**Requisitos:** Python 3.13+, [uv](https://docs.astral.sh/uv/) 0.13.1 y, para la vía Docker, Docker Desktop con el motor en marcha (`docker info` debe responder).

### Opción A — local con `uv` (la más rápida para desarrollar)

```bash
cd backend
uv sync                      # crea .venv e instala desde uv.lock
cp .env.example .env         # copia las variables de entorno
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

- Backend en <http://localhost:8000/> · admin en `/admin/` · API en `/api/` · Swagger en `/api/schema/swagger-ui/`.
- En local se usa **SQLite** por defecto (`backend/db.sqlite3`): no hace falta levantar PostgreSQL.
- `gunicorn` no corre en Windows nativo → en Windows se usa `runserver` (gunicorn vive en Docker).

### Opción B — Docker Compose

```bash
cd backend
cp .env.example .env         # paso previo obligatorio: si falta, compose falla al no encontrar el archivo
docker compose up --build
```

- **Estado (19/10/2026):** el [`Dockerfile`](backend/Dockerfile) y el [`compose.yaml`](backend/compose.yaml) **ya están escritos y validados** (`docker compose config` no reporta errores), pero **el build todavía no se ejecutó**: el motor de Docker de la máquina de desarrollo no levanta (falta WSL2). Queda como verificación pendiente antes de la entrega.
- Pasos de verificación pendientes: 1) `docker compose config` (ya pasa) → 2) `docker compose up --build` → 3) `docker compose ps` en verde → 4) admin **con estilos** y API respondiendo en <http://localhost:8000/admin/> y `/api/`.
- Levanta `db` (PostgreSQL 17 con healthcheck) y `web` (migra, `collectstatic` y sirve con gunicorn en el puerto 8000).

### Sobre el `.env`

El archivo `.env` **nunca se sube al repositorio**: está en el `.gitignore` de `backend/`. Solo se commitea la plantilla [`backend/.env.example`](backend/.env.example), con valores de ejemplo sin secretos reales:

```dotenv
DJANGO_SECRET_KEY=cambie-esto-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://flacheros:flacheros@localhost:5432/flacheros
POSTGRES_DB=flacheros
POSTGRES_USER=flacheros
POSTGRES_PASSWORD=flacheros
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 6. Tabla de endpoints

Router `DefaultRouter` en `backend/core/urls.py`, prefijo `/api/`. Los 10 recursos son `ModelViewSet`: cada URL de colección tiene además su detalle en `{id}/` con `GET`, `PUT`, `PATCH` y `DELETE`.

**Regla de permisos de un vistazo:** **leer** (`GET`) = cualquier usuario autenticado (sin token → `401` en **todos** los endpoints); **escribir** (`POST`/`PUT`/`PATCH`/`DELETE`) = solo usuarios staff, **excepto** `/api/pedidos/` y `/api/lineas/`, que es el mostrador de la cervecería (cualquier autenticado crea y edita).

| Método | URL | Permiso | Filtros / búsqueda / orden | Anidado en `list` |
|---|---|---|---|---|
| `POST` | `/api/auth-token/` | Sin autenticación | — (devuelve `{token}`) | — |
| `GET`, `POST` | `/api/estilos/` | Token: lectura · admin escribe | `search=nombre` · `ordering=orden,nombre` | No |
| `GET`, `POST` | `/api/cervezas/` | Token: lectura · admin escribe | filtros `estilo`, `tipo`, `activo` · `search=nombre,descripcion` · `ordering=precio,nombre,-fecha_creacion` | No |
| `GET` | `/api/cervezas/en_grifo/` | Token | `@action` (cervezas GRIFO, activas, con stock) | — |
| `GET`, `POST` | `/api/lotes/` | Token: lectura · admin escribe | `search=numero,cerveza__nombre` · `ordering=-fecha_inicio` | **Sí** (`etapas`) |
| `GET`, `POST` | `/api/etapas/` | Token: lectura · admin escribe | filtro `lote` · `ordering=numero` | No |
| `GET`, `POST` | `/api/proveedores/` | Token: lectura · admin escribe | `search=razon_social,cuit` · `ordering=razon_social` | No |
| `GET`, `POST` | `/api/materias-primas/` | Token: lectura · admin escribe | filtros `tipo`, `proveedor` · `search=nombre` · `ordering=tipo,nombre` | No |
| `GET`, `POST` | `/api/clientes/` | Token: lectura · admin escribe | `search=nombre,apellido,email,dni` · `ordering=-fecha_alta` | No |
| `GET`, `POST` | `/api/pedidos/` | Token: lectura **y escritura** (mostrador) | filtros `estado`, `forma_pago` · `search=cliente__nombre,cliente__apellido` · `ordering=-fecha` | **Sí** (`lineas`) |
| `GET` | `/api/pedidos/estadisticas/` | Token **admin** | `@action` (`total_pedidos`, `monto_total`, `pedidos_por_estado`, `promedio_ticket`) | — |
| `POST` | `/api/lotes/{id}/avanzar/` | Token **admin** | `@action`: avanza el estado del lote; salto inválido → `400` | — |
| `GET`, `POST` | `/api/lineas/` | Token: lectura **y escritura** (mostrador) | `ordering=-pedido__fecha` | No |
| `GET`, `POST` | `/api/opiniones/` | Token: lectura · admin escribe | `ordering=-fecha` | No |
| `GET`, `POST` | `/api-auth/` | Sesión (HTML) | Login/logout de la Browsable API | — |

**Paginación:** todos los listados devuelven `count`, `next`, `previous`, `results` (`page_size` por defecto 10, tope 50 con `?page_size=`).

**Códigos:** `200` OK · `201` creado · `204` borrado · `400` validación · `401` sin token o inválido · `403` sin permiso · `404` no existe.

**Documentación viva:** `/api/schema/` (OpenAPI 3), `/api/schema/swagger-ui/` (Swagger), `/api/schema/redoc/` (ReDoc) y `/api/` (API navegable). El contrato con el frontend, con ejemplos de JSON, está en [`tasks/api-contract.md`](tasks/api-contract.md).

## 7. Autenticación por token

**1) Pedir el token** (una sola vez, con usuario y contraseña):

```bash
curl -X POST http://localhost:8000/api/auth-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<usuario>", "password": "<contraseña>"}'
```

Respuesta:

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```

**2) Usarlo en cada request** (GET y también POST/PUT/PATCH/DELETE):

```bash
curl http://localhost:8000/api/cervezas/ \
  -H "Authorization: Token <clave>"
```

| Respuesta | Significado |
|---|---|
| `401` | Token ausente o inválido (no hay lectura anónima: aplica a **todos** los endpoints) |
| `403` | Token válido pero sin permiso (ej.: `estadisticas` sin usuario staff) |

**Por qué el frontend NO usa cookies de sesión** (punto fuerte de la defensa):

- Las cookies **ignoran el puerto**: `localhost:3000` (frontend) y `localhost:8000` (backend) están en el mismo host, así que **comparten cookies**.
- Si el SPA hiciera login por sesión, DRF exigiría un token **CSRF** en cada POST/PUT/PATCH/DELETE, complicando todos los writes.
- **Decisión del equipo:** el frontend usa **solo** `Authorization: Token <key>`, nunca cookies de sesión. Además, CORS se configura restrictivo (`CORS_ALLOWED_ORIGINS = http://localhost:3000`), sin `CORS_ALLOW_ALL_ORIGINS` junto a `CORS_ALLOW_CREDENTIALS`.

## 8. Autenticación por sesión

La API también acepta **autenticación por sesión** (`SessionAuthentication` en `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]`, junto a `TokenAuthentication`):

- Login y logout con formulario HTML en **`/api-auth/`** (las URLs de `rest_framework.urls`).
- Sirve para la **API navegable** de DRF (`/api/`): botón de login, probar endpoints desde el navegador con la sesión del admin.
- Sirve para el **panel de administración** (`/admin/`), que siempre funcionó por sesión.
- Un `GET` con sesión ya iniciada devuelve `200`, mientras que el mismo `GET` sin autenticar devuelve `401` (cubierto por un test en `backend/core/tests.py`).

Es decir: **sesión para humanos en el navegador (admin y API navegable); token para máquinas y para el frontend.**

## 9. Panel de administración

URL: **`/admin/`** (credenciales: superusuario creado con `createsuperuser`, ver [Datos de prueba](#11-datos-de-prueba)).

Los **10 modelos** están registrados en [`backend/core/admin.py`](backend/core/admin.py) con los tres atributos en los diez (control total, costo cero):

| Función | Qué permite |
|---|---|
| `list_filter` | Filtrar listados por campos clave (ej.: cervezas por `tipo` y `activo`, pedidos por `estado`) |
| `search_fields` | Búsqueda con joins (ej.: `cerveza__nombre`, `cliente__nombre`) |
| `ordering` | Orden por defecto de cada lista |
| `list_display` | Columnas útiles en cada listado (stock, precios, estados) |
| **Inline de etapas** | `EtapaFermentacionInline` en un `Lote`: se crean y editan las etapas de fermentación en la misma pantalla |
| **Inline de líneas** | `LineaPedidoInline` en un `Pedido`: se agregan líneas al pedido sin salir del formulario |
| Autocomplete | Selección de FK con `autocomplete_fields` en modelos con muchos registros |

## 10. Capturas de pantalla

> **Estado (19/10/2026):** las **9 capturas del backend** ya están tomadas y viven en [`docs/capturas/`](docs/capturas/) — son la evidencia en pantalla de los requisitos: vista de bienvenida, documentación OpenAPI (Swagger y ReDoc), API navegable, panel de administración y las respuestas de la API con y sin datos anidados. La guía de qué capturar, cómo y con qué comando (incluida la forma real en que se tomaron) está en **[`docs/capturas/LEEME.md`](docs/capturas/LEEME.md)**. La única captura pendiente es `frontend.png`, que depende del frontend de Ema.

| # | Archivo | Estado | Qué muestra |
|---|---|---|---|
| 1 | `bienvenida.png` | ✅ | Template con identidad de marca en `/` (R13) |
| 2 | `swagger-ui.png` | ✅ | Documentación interactiva de la API (R12) |
| 3 | `redoc.png` | ✅ | Documentación OpenAPI en formato libro (R12) |
| 4 | `browsable-api.png` | ✅ | Browsable API de DRF con login de sesión (R12) |
| 5 | `admin-filtros.png` | ✅ | Filtros, búsqueda y orden en el admin de cervezas (R14) |
| 6 | `admin-pedidos-inline.png` | ✅ | Inline de líneas de pedido en el admin (R14) |
| 7 | `api-pedidos-nested.png` | ✅ | `GET /api/pedidos/` **con** `lineas` anidadas (R7) |
| 8 | `api-lote-detalle.png` | ✅ | `GET /api/lotes/{id}/` **sin** anidar (contraste con el listado, R7) |
| 9 | `api-estadisticas.png` | ✅ | Acción `estadisticas` con los datos del seed (R9) |
| 10 | `frontend.png` | ⏳ | Pantalla del frontend de Ema — **pendiente del frontend** |

![Vista de bienvenida con la identidad de la marca](docs/capturas/bienvenida.png)

![Swagger UI con la documentación OpenAPI de la API](docs/capturas/swagger-ui.png)

![ReDoc con la documentación OpenAPI en formato libro](docs/capturas/redoc.png)

![API navegable de Django REST Framework con login de sesión](docs/capturas/browsable-api.png)

![Panel de administración: cervezas con filtros, búsqueda y orden](docs/capturas/admin-filtros.png)

![Panel de administración: pedido con el inline de líneas de pedido](docs/capturas/admin-pedidos-inline.png)

![GET /api/pedidos/ con las líneas anidadas en la respuesta JSON](docs/capturas/api-pedidos-nested.png)

![GET /api/lotes/{id}/ sin datos anidados, a modo de contraste con el listado](docs/capturas/api-lote-detalle.png)

![Acción estadisticas con los datos del seed](docs/capturas/api-estadisticas.png)

> **`frontend.png` — pendiente del frontend:** la captura de la interfaz Next.js de Ema se agregará acá cuando el frontend esté lista; por ahora se deja este texto en lugar de una imagen rota (no existe el archivo todavía).

## 11. Datos de prueba

Cargar datos realistas con el management command `seed_datos` (es idempotente: se puede repetir sin duplicar registros):

```bash
uv run python manage.py seed_datos            # carga datos de ejemplo
uv run python manage.py seed_datos --flush    # DESTRUCTIVO: borra el dominio y recarga desde cero
uv run python manage.py createsuperuser       # usuario staff para admin y acciones admin
```

- `seed_datos` carga estilos, cervezas, proveedores, materias primas, clientes, lotes con etapas, pedidos con líneas y opiniones; **no** toca usuarios ni tokens.
- `--flush` borra solo los registros de los 10 modelos del dominio (no usuarios ni tokens).
- **Credenciales de demostración (usadas para las capturas):** superusuario `admin` con contraseña `flacheros2026`, creado con `createsuperuser` **en la base local de desarrollo** (`backend/db.sqlite3`, que está en `.gitignore` y por eso no está en el repo). El token se pide en `POST /api/auth-token/` con esas credenciales (ver [Autenticación por token](#7-autenticación-por-token)).
- Es una **cuenta local de demostración**, no un secreto del repo: cualquiera que clone el repositorio debe crear la suya propia con `uv run python manage.py createsuperuser` sobre su base local.

## 12. Comandos útiles

Todos se corren desde `backend/` (excepto `docker compose`).

| Comando | Qué hace |
|---|---|
| `uv sync` | Instala/actualiza las dependencias desde `uv.lock` |
| `uv run python manage.py runserver` | Servidor de desarrollo en `http://localhost:8000/` |
| `uv run python manage.py migrate` | Aplica las migraciones pendientes |
| `uv run python manage.py makemigrations` | Genera migraciones a partir de cambios en los modelos |
| `uv run python manage.py makemigrations --check --dry-run` | Falla si hay cambios de modelo sin migrar (triada de calidad) |
| `uv run python manage.py createsuperuser` | Crea el usuario staff del admin |
| `uv run python manage.py seed_datos [--flush]` | Carga (o recarga) datos de prueba |
| `uv run python manage.py spectacular --validate` | Valida el esquema OpenAPI |
| `uv run pytest` | Corre los tests (`core/tests.py`) — hoy: **17 passed** |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Formateo |
| `docker compose up --build` | Construye y levanta `db` + `web` (build pendiente de ejecutar: falta el motor Docker en la máquina de desarrollo) |

## 13. Verificación

Resultado real de la **triada de calidad** del proyecto, corrida el 19/10/2026 desde `backend/`. Esta triada es la **definición de listo** del proyecto: no se considera terminado ningún cambio que la deje en rojo.

| Comando | Resultado |
|---|---|
| `uv run pytest -v` | **17 passed** |
| `uv run ruff check .` | All checks passed |
| `uv run ruff format --check .` | 23 files already formatted |
| `uv run python manage.py check` | System check identified no issues (0 silenced) |
| `uv run python manage.py makemigrations --check --dry-run` | No changes detected |
| `uv run python manage.py spectacular --validate` | Esquema OpenAPI válido (0 errores, 0 warnings) |

Qué cubren los 17 tests (`backend/core/tests.py`): `401` sin token, `200` con token y con sesión, estructura de paginación, datos anidados **solo en list** (lotes y pedidos), las 3 `@action` (`en_grifo`, `estadisticas` con permiso staff y `avanzar` rechazando la transición inválida con `400`), filtros y búsqueda de cervezas, permisos staff vs. mostrador, y el recálculo del `total` del pedido al modificar sus líneas.

## 14. Notas de implementación

Decisiones técnicas que conviene poder explicar en la defensa:

- **ReDoc fijado a una build UMD (`REDOC_DIST`):** la URL "latest" que servía el CDN pasó a entregar una build solo ESM, lo que dejaba la página `/api/schema/redoc/` en blanco; fijar una versión UMD la vuelve a renderizar correctamente.
- **`DecimalField` con `coerce_to_string=False`** en los serializers del contrato: el JSON devuelve números (`"precio": 1500.00`) en lugar de strings (`"1500.00"`), que es lo que cualquier frontend JavaScript espera y opera cómodamente.
- **`CORS_ALLOW_CREDENTIALS` desactivado a propósito:** el frontend se autentica solo con el header `Authorization: Token`, sin cookies de sesión; al no usar credenciales cross-origin se reduce la superficie de ataque sin perder funcionalidad.
- **`Pedido.total` es un campo guardado en la base,** no un `@property`: lo recalcula la capa de API cuando cambian las líneas del pedido (en `LineaPedidoViewSet`), lo que permite listar y ordenar por total sin agregaciones en cada request.

## 15. Proceso del equipo (Git)

| Qué SÍ hacemos | Qué NO hacemos |
|---|---|
| `main` como rama principal del repo | No commitear `.env`, `__pycache__/`, `.venv/`, `*.sqlite3`, `node_modules/`, `.next/` |
| Ramas `feature/<tarea>` (ej.: `feature/fase-3-admin`) | No commitear secretos ni credenciales |
| Commits chicos, en **Conventional Commits en español** (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`) | No tareas enteras sin commitear ("WIP" al final de la semana) |
| Merges a `main` con `git merge --no-ff feature/x` | No Git Flows con ramas `develop` ni ramas de largo aliento |
| Cada rama `feature/*` publicada como **pull request** hacia `main` (Task 31) y cerrada con merge | No fuerza-push sobre `main` |

Ejemplo real de historial (`git log --oneline --graph -15`, rama `feature/fase-3-admin`, salida al 25/10/2026):

```
* 9fd471c feat(seed): agrega comando seed_datos con datos de ejemplo para capturas y defensa
* df7aa07 feat(api): documenta las acciones en el schema openapi
* 33271d4 feat(api): registra los 10 viewsets con permisos, filtros y acciones
* 0a024ca feat(api): agrega serializers planos y nested de lotes y pedidos
* 4c92967 feat(admin): registra los 10 modelos con filtros, busqueda, orden e inlines
* c116e9f docs: documenta las Tasks 7 a 11 del modelo de datos
*   f4e8815 merge: cierra la Fase 2 (10 modelos con relaciones y sus migraciones)
|\
| * 872c1c9 fix(modelos): corrige __str__ de Opinion sin get_puntaje_display
| * 9bbd750 docs: alinea las guias con la regla de permisos, la paginacion y las 3 acciones
| * c39b95d feat: proyecto Django con settings, vista de bienvenida y documentacion OpenAPI
| * 03a2e63 feat(modelos): agrega Cliente, Pedido, LineaPedido y Opinion con sus relaciones y migracion
| * 08b53ca feat(modelos): agrega Proveedor y MateriaPrima con su relacion y migracion
| * 47566b8 feat(modelos): agrega Lote y EtapaFermentacion con maquina de estados y migracion
| * d09ffb9 feat(modelos): agrega Estilo y Cerveza con su relacion y migracion
|/
*   4f6948e merge: cierra la Fase 1 (Django base + API navegable + plan alineado con la auditoria)
|\
```

Los merges `--no-ff` (`f4e8815`, `4f6948e`) dejan visible en el grafo el cierre de cada fase. **Publicación:** las ramas `feature/*` se suben al repo de GitHub como **pull requests** hacia `main` (Task 31, 1/11) y la entrega se hace con `main` al día.

## 16. Estado de la entrega

Checklist de los **21 requisitos (R1–R21)** de [`docs/08-trazabilidad-requisitos.md`](docs/08-trazabilidad-requisitos.md), con el estado real al 19/10/2026 (verificación de cada uno en la sección [Verificación](#13-verificación)):

**Hecho**

- [x] **R1** ≥10 modelos en la base de datos (10 en `backend/core/models.py`, Tasks 7–10)
- [x] **R2** Modelos relevantes para la temática de la cervecería
- [x] **R3** Relaciones entre modelos (8 FK con `related_name` y `on_delete` según el negocio)
- [x] **R4** Planificación de tablas y relaciones adjunta al README (diagrama ER en la sección 3, sincronizado con `tasks/plan.md` §7)
- [x] **R5** API REST para comunicarse con un frontend (10 ViewSets + `DefaultRouter` en `/api/`, Tasks 14–15)
- [x] **R6** ≥8 modelos con endpoint ViewSet (los 10, con CRUD completo)
- [x] **R7** 2 ViewSets con datos anidados **solo en list** (`lotes/` → `etapas`, `pedidos/` → `lineas`, Task 16)
- [x] **R8** Autenticación de sesión y por tokens (`/api/auth-token/` + `/api-auth/`, Tasks 4 y 6)
- [x] **R9** ≥2 `@action` (las 3: `en_grifo`, `estadisticas`, `avanzar`)
- [x] **R10** Endpoints de listado paginados (`count`/`next`/`previous`/`results`, Task 4)
- [x] **R11** ≥1 ViewSet con filtros y búsquedas (en realidad, varios: `cervezas`, `lotes`, `materias-primas`, `pedidos`…, Task 18)
- [x] **R12** Documentación OpenAPI + Swagger + ReDoc + API navegable (Task 6)
- [x] **R13** Vista principal con template de bienvenida (Task 5)
- [x] **R14** Admin con filtros, ordenamiento, búsqueda e inlines (los 10 modelos, Tasks 12–13)
- [x] **R15** uv como gestor de entornos (Tasks 1–2)
- [x] **R16** CORS configurado para el frontend (`CorsMiddleware` primero, origen `http://localhost:3000`, verificado con un preflight real, Task 19)
- [x] **R18** Proceso Git con ramas `feature/*`, commits convencionales y merges `--no-ff` (los pull requests hacia `main` se publican con R19)
- [x] **R20** README con diagrama ER, stack, instalación, tabla de endpoints, proceso Git **y las 9 capturas del backend** (falta solo `frontend.png`, del frontend de Ema)

**Falta para el cierre**

- [ ] **R17** Proyecto dockerizado: el `Dockerfile` y el `compose.yaml` **ya están escritos y validados** (`docker compose config` sin errores), pero **el build y el `docker compose up` todavía no se ejecutaron**: el motor de Docker de la máquina de desarrollo no levanta (falta WSL2). Verificación pendiente: `docker compose up --build` → `docker compose ps` en verde → admin con estilos y API en `localhost:8000`
- [ ] **R19** Repositorio publicado en GitHub con `main` al día (Task 31, 1/11): todavía no se creó el remoto
- [ ] **Captura `frontend.png`** embebida en la sección 10 (depende del frontend de Ema; el lugar ya está reservado en el README)
- [ ] **R21** Entrega el lunes 2/11 y defensa el martes 3/11 (Task 28)
- [ ] Notas de tarea por tarea ejecutada en `docs/tareas/` (Task 29: están las T01–T11; faltan T12 en adelante)

## 17. Autores

EFI de **Ingeniería de Software 2026** — Instituto Tecnológico (**ITec**). Grupo de 2 integrantes.

| Rol | Integrante |
|---|---|
| Backend (Django, API, admin, tests, Docker, documentación) | **&lt;nombre del integrante backend&gt;** *(completar antes de la entrega — Task 27)* |
| Frontend (Next.js + Tailwind + JavaScript) | **Ema** |

## Documentación relacionada

| Documento | Qué contiene |
|---|---|
| [`tasks/plan.md`](tasks/plan.md) | Plan maestro: alcance, identidad, stack, modelo de datos (§7) y contrato de API (§8) |
| [`tasks/api-contract.md`](tasks/api-contract.md) | Contrato congelado para el frontend: endpoints, filtros, auth y ejemplos de JSON |
| [`tasks/todo.md`](tasks/todo.md) | Las 31 tareas con criterios de aceptación y verificación |
| [`docs/08-trazabilidad-requisitos.md`](docs/08-trazabilidad-requisitos.md) | Matriz de trazabilidad R1–R21 con evidencia |
| [`docs/capturas/LEEME.md`](docs/capturas/LEEME.md) | Guía de capturas: qué capturar, cómo y con qué comando |
| [`backend/pyproject.toml`](backend/pyproject.toml) | Dependencias y versiones exactas del backend |
| [`backend/.env.example`](backend/.env.example) | Plantilla de variables de entorno (el `.env` real no se commitea) |
