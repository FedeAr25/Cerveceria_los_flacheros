# Plan maestro — Cervecería Los Flacheros

> Documento de planificación de la EFI. Reescrito el 19/10/2026: el proyecto no arrancó (no hay código de aplicación ni tareas ejecutadas), así que este plan define el alcance desde cero.
> Archivos hermanos: [`tasks/todo.md`](todo.md) (29 tareas) y [`tasks/api-contract.md`](api-contract.md) (contrato para Ema).

## 1. Overview

Cervecería Los Flacheros es la **Evaluación Final Integradora (EFI)** de Ingeniería de Software 2026: un sistema de gestión para una cervecería artesanal con backend **Django 5.2 LTS + Django REST Framework** (API REST documentada con OpenAPI) y frontend **Next.js (App Router, Tailwind, JavaScript puro)** desarrollado por un segundo integrante. Se entrega un `README.md` trabajado con capturas del proyecto en funcionamiento y una defensa oral en la que el docente evalúa el backend y el proceso. Fecha límite de entrega: **lunes 2 de noviembre de 2026**; defensas desde el **martes 3 de noviembre**.

**Qué se entrega:**

- Backend Django funcional con **10 modelos**, **10 endpoints** con ViewSets, autenticación por sesión y token, documentación OpenAPI/Swagger/ReDoc, panel de admin, CORS y dockerizado.
- `README.md` con el **diagrama ER**, stack, instalación, tabla de endpoints, capturas y proceso Git.
- Evidencia de proceso Git local: ramas `feature/*` y commits descriptivos.
- `tasks/api-contract.md` como handoff congelado para el frontend de Ema.
- Documentación de aprendizaje en `docs/`: guías conceptuales, cuaderno de defensa oral y una nota por tarea ejecutada.

**Contexto del equipo:**

| Ítem | Detalle |
|---|---|
| Grupo | 2 personas, ambas principiantes en programación |
| Backend (100%) | Usuario (esta sesión): Django, API, admin, tests, Docker, documentación |
| Frontend | "Ema": Next.js + Tailwind + JavaScript puro, App Router |
| Estructura | Dos carpetas hermanas: `backend/` y `frontend/` |

## 2. Alcance reducido

El usuario pidió explícitamente un backend **no complejo, solo lo necesario para cumplir cada consigna**. El plan anterior (12 modelos, 5 apps, 12 endpoints, tests extensos, Docker multi-stage) era demasiado ambicioso para dos principiantes con dos semanas. El docente pide un mínimo explícito (≥10 modelos, ≥8 endpoints); el proyecto cumple ese mínimo con holgura y **nada más**.

| Qué SÍ hacemos | Qué NO hacemos | Motivo del recorte |
|---|---|---|
| Una única app `core` con los 10 modelos | 5 apps (`catalog`, `production`, `inventory`, `sales`, `customers`) bajo `apps/` | Con dos principiantes, 5 apps multiplican archivos, migraciones y permisos sin que el docente lo pida; una sola app se explica en una frase. |
| Exactamente 10 modelos | 12+ modelos (`Stock`, `MovimientoStock`, `Categoria`, `Usuario` custom) | El docente pide ≥10. Cada modelo extra arrastra serializer, viewset, admin, tests y migraciones. |
| `Cerveza.stock` y `MateriaPrima.stock` como campos numéricos | Entidad `Stock` separada + `MovimientoStock` + constraint "exactamente uno de dos FK" | Un `IntegerField` cubre la consigna; el módulo de movimientos de stock nadie lo pide y es el código más trabado del plan viejo. |
| `Cerveza.tipo` (`ENVASE`/`GRIFO`) para clasificar | Modelo `Categoria` separada con su endpoint | El `choices` ya clasifica; una tabla extra es otro serializer y otro ViewSet sin consigna que los pida. |
| `django.contrib.auth.User` nativo | Modelo `Usuario` heredando `AbstractUser` | Heredar obliga a `AUTH_USER_MODEL` antes de la primera migración; la consigna de auth se cubre con sesión + token nativos de DRF. |
| Dockerfile **single-stage** | Multi-stage con `--mount=type=cache` | Un solo `FROM` se lee y se debuggea de una pasada; el cache multi-stage ahorra segundos y complica el diagnóstico cuando algo falla. |
| ~12 tests en `core/tests.py` | 20+ tests repartidos en varios archivos | Cubren los requisitos (permisos, nested, actions, filtros) sin mantenimiento desproporcionado. |
| Permisos declarados: `IsAuthenticated` global, `IsAdminOrReadOnly` en 2 ViewSets, `IsAdminUser` en 1 acción | Clase de permisos custom que inspecciona `self.action` | Menos código, más fácil de auditar y de explicar en la defensa. |
| Sin Pillow ni `ImageField` | Imágenes de producto | Cada campo de imagen agrega dependencia, storage y validación; se cubre con texto. |
| Sin CI ni pipelines | Automatización de builds | El docente pide proceso Git (ramas y commits descriptivos), no pipelines. |
| Git **solo local** | Gestión de repositorios remotos y publicación | Esa parte la resuelve el usuario por su cuenta y no forma parte de este plan. |
| 10 endpoints con `DefaultRouter` | 12+ endpoints y acciones extra | El docente pide ≥8; 10 ViewSets dan CRUD completo de los 10 modelos. |

## 3. Cómo leer este plan

Si es la primera vez que tocás Django, leé en este orden: **Overview** (qué se entrega), **Alcance reducido** (qué NO vamos a hacer y por qué), **Estructura de carpetas** (dónde vive cada cosa) y **Modelo de datos**. Cuando aparezca un término que no conocés, buscalo en el glosario de abajo. Las secciones 8 a 12 son material de apoyo para la defensa oral: no hace falta memorizarlas, hace falta poder explicarlas.

**Glosario de conceptos clave:**

| Concepto | Qué es | Para qué lo usamos | Qué decir en la defensa |
|---|---|---|---|
| Framework | Un conjunto de herramientas y bibliotecas ya escritas que dan la base de una aplicación (servidor, formularios, seguridad) para no partir de cero. | Es la razón por la que dos principiantes pueden levantar un backend en dos semanas. | "Usamos un framework porque resuelve problemas genéricos (HTTP, sesiones, seguridad) y nosotros nos concentramos en la lógica de la cervecería." |
| Django | Framework web de Python, "full-stack": trae ORM, admin, plantillas y seguridad por defecto. | Estructura el backend: `manage.py`, `config/`, apps, modelos y migraciones. | "Django sigue el patrón 'convention over configuration': si seguimos sus convenciones, no hay que escribir código de infraestructura." |
| Django REST Framework (DRF) | Biblioteca sobre Django para construir APIs REST: ViewSets, serializers, permisos, paginación y browsable API. | Toda la capa `/api/`. | "DRF traduce modelos de Django a JSON y a la inversa, y aplica permisos y paginación de forma declarativa." |
| App | Un módulo dentro del proyecto Django con su propio `models.py`, `admin.py`, `views.py`. | Tenemos **una sola app**, `core`, con todo el dominio. | "Elegimos una app única a propósito: con 10 modelos y dos semanas, dividir en varias apps agregaba complejidad sin aportar." |
| Modelo | Clase de Python que Django mapea a una tabla de la base de datos (`class Cerveza(models.Model)`). | Los 10 modelos de la sección 7. | "El modelo es la fuente de verdad: define campos, tipos, restricciones y relaciones." |
| Migración | Archivo versionado que describe los cambios en los modelos para aplicarlos a la base de datos (`makemigrations` / `migrate`). | Evolucionar el esquema sin tocar datos a mano y poder recrear la DB desde cero. | "Las migraciones son el historial de la base de datos: permiten subir o bajar el esquema de forma reproducible." |
| Serializer | Clase que valida y convierte entre modelos/objetos y JSON (y viceversa). | `core/serializers.py`, incluidos los dos anidados. | "El serializer hace de traductor y de validador: si llega JSON inválido, devuelve 400 antes de tocar la base." |
| ViewSet | Clase que agrupa las operaciones CRUD de un recurso (list, create, retrieve, update, destroy) en un solo objeto. | Los 10 ViewSets de `core/views.py`. | "Un ViewSet por modelo nos da el CRUD completo reutilizando la lógica de DRF en lugar de escribir vistas una por una." |
| Router | Objeto (`DefaultRouter`) que genera las URLs de los ViewSets a partir de un prefijo. | `core/urls.py` montado en `/api/`. | "El router deriva las URLs desde el ViewSet; así las rutas y la documentación no se desincronizan." |
| Permiso | Clase que decide si una request puede ejecutarse (`IsAuthenticated`, `IsAdminOrReadOnly`, `IsAdminUser`). | `DEFAULT_PERMISSION_CLASSES` + permisos puntuales por ViewSet/acción. | "Los permisos son declarativos: primero preguntamos quién es, y recién después dejamos entrar al ViewSet." |
| Token | Cadena opaca que el frontend manda en el header `Authorization: Token <key>` para identificarse. | `POST /api/auth-token/` + `rest_framework.authtoken`. | "Usamos el token nativo de DRF en lugar de JWT porque la consigna pide sesión y token, y el token de DRF es una línea de configuración." |
| CORS | Mecanismo por el que el navegador permite que un sitio (el front en :3000) llame a otro origen (el back en :8000). | `corsheaders` con `CORS_ALLOWED_ORIGINS = http://localhost:3000`. | "Sin CORS el navegador bloquearía las requests del frontend; lo configuramos restrictivo, con el origen exacto." |
| Paginación | Dividir los listados en páginas (`count`, `next`, `previous`, `results`) para no devolver tablas enteras. | `PageNumberPagination`, `PAGE_SIZE=10`, tope 50. | "Paginar evita respuestas gigantes y es lo que cualquier API de producción hace." |
| `choices` (`TextChoices`) | Constantes de clase que definen los valores válidos de un campo (ej. `estado`). | Estados de Lote, Pedido, Etapa, etc. | "Los `choices` validan en el modelo y en el serializer, y documentan solos los valores posibles." |
| `on_delete` | Regla que dice qué pasa con las filas hijas al borrar una fila padre: `PROTECT`, `CASCADE`, `SET_NULL`. | Todas las FK de la sección 7. | "Elegimos la regla según el negocio: el histórico no se borra (`PROTECT`), lo dependiente desaparece con su padre (`CASCADE`), lo opcional se desengancha (`SET_NULL`)." |
| `@action` | Decorador de DRF que agrega un endpoint extra dentro de un ViewSet (ej. `/api/cervezas/en_grifo/`). | Las 2 acciones obligatorias + 1 opcional. | "Las acciones custom encapsulan lógica de negocio puntual sin inventar un modelo nuevo ni una vista suelta." |

## 4. Identidad de marca

| Atributo | Valor |
|---|---|
| Nombre | Cervecería Los Flacheros |
| Lema | *"Arte en cada trago, tradición en cada lote"* |
| Tono | Cálido, cercano, artesanal, orgulloso; informal pero profesional |
| Ámbar (primaria) | `#F5A623` |
| Lúpulo (secundaria) | `#4A7C59` |
| Malta tostada (acento) | `#8B4513` |
| Espuma (fondos) | `#F7F7F7` |
| Carbón (texto) | `#2B2B2B` |
| Público | Consumidores locales 18-45, bares/restaurantes (B2B), homebrewers y turistas cerveceros |

## 5. Stack y versiones

| Componente | Versión | Nota |
|---|---|---|
| Python | 3.13.5 | `uv python pin 3.13`, `requires-python = ">=3.13"` |
| Django | 5.2.18 LTS | Elegido por ser **LTS** (soporte largo) y porque `drf-spectacular` 0.30.0 declara soporte hasta Django 6.0 / DRF 3.17 |
| djangorestframework | 3.17.x | Fallback documentado: 3.18.3, validando siempre con `uv run python manage.py spectacular --validate` |
| drf-spectacular | 0.30.0 | OpenAPI 3 + Swagger UI + Redoc |
| django-filter | 26.2 | Filtros en endpoints |
| django-cors-headers | 4.9.0 | CORS para el frontend Next.js |
| django-environ | 0.14.0 | Settings 12-factor (lee `.env`) |
| psycopg[binary] | 3.3.6 | Driver de PostgreSQL |
| gunicorn | 26.2.0 | Solo Linux/Docker; en Windows local se usa `runserver` (gunicorn no corre en Windows nativo) |
| whitenoise | 6.12.0 | Sirve los static files dentro del contenedor, sin nginx |
| uv | 0.13.1 | Gestor de entornos (`uv init/add/sync/lock/run`) |
| pytest | 9.1.1 | Config TOML nativa |
| pytest-django | 4.14.0 | Requiere `DJANGO_SETTINGS_MODULE` |
| ruff | 0.17.1 | Lint + format (una sola herramienta) |
| Docker Compose | v5.6.0 (v2, sin guion) | Imagen `postgres:17`; el `version:` top-level del YAML está obsoleto, se omite |
| Git | 2.56.0 | Solo local (sección 11) |

**Qué falta instalar (verificado 19/10/2026):**

| Herramienta | Estado | Cómo instalarla |
|---|---|---|
| git 2.56 | Instalado | — |
| winget | Instalado | — |
| Python 3.13.5 | Instalado | — |
| `uv` | **Falta** | `winget install --id=astral-sh.uv -e` o `irm https://astral.sh/uv/install.ps1 | iex`; queda en `%USERPROFILE%\.local\bin` → **abrir terminal nueva** después |
| `docker` | **Falta** | Instalar Docker Desktop (parte de la Fase 0, Task 1) |

Comandos uv que vamos a usar: `uv init`, `uv add`, `uv add --dev`, `uv sync`, `uv lock`, `uv run`. En `pyproject.toml` va **`[tool.uv] package = false`** (el proyecto Django no es un paquete distribuible; sin eso, `uv sync` intenta construirlo y falla). Docker: se usa `docker compose` (v2, sin guion).

## 6. Estructura de carpetas

```
cerveceria_losflacheros/
├── backend/
│   ├── pyproject.toml, uv.lock, .python-version, .env.example, .gitignore, .dockerignore
│   ├── Dockerfile, compose.yaml, manage.py
│   ├── config/          # settings.py, urls.py, wsgi.py, asgi.py
│   ├── core/            # models.py, serializers.py, views.py, admin.py, urls.py, apps.py, tests.py
│   ├── templates/
│   └── static/
├── frontend/            # de Ema (no lo implementa el usuario)
├── tasks/
└── README.md
```

**Qué archivo hace qué:**

| Archivo | Qué hace |
|---|---|
| `backend/pyproject.toml` | Declara dependencias y configura uv (`[tool.uv] package = false`, ruff, pytest). |
| `backend/uv.lock` | Lockfile: congela la versión exacta de cada dependencia para que reproduzca igual en cualquier máquina. |
| `backend/.python-version` | Le dice a uv qué versión de Python usar (`3.13`). |
| `backend/.env.example` | Plantilla de variables de entorno; se copia a `.env` (que no se commitea). |
| `backend/.gitignore` / `.dockerignore` | Qué no llevar a git / qué no llevar al build de Docker. |
| `backend/Dockerfile` | Receta single-stage para construir la imagen del backend. |
| `backend/compose.yaml` | Levanta `db` (postgres:17) + `web` (backend) con un solo comando. |
| `backend/manage.py` | CLI de Django (`runserver`, `migrate`, `makemigrations`, `createsuperuser`, `spectacular`). |
| `backend/config/settings.py` | Configuración global: apps instaladas, middleware, DRF, CORS, base de datos. |
| `backend/config/urls.py` | Mapa de URLs del proyecto: `/`, `/admin/`, `/api/`, docs, token. |
| `backend/config/wsgi.py` / `asgi.py` | Puntos de entrada del servidor (gunicorn usa `config.wsgi:application`). |
| `backend/core/models.py` | Los 10 modelos + `TextChoices` + `on_delete` + `@property`. |
| `backend/core/serializers.py` | Serializers planos + `LoteNestedSerializer` + `PedidoNestedSerializer` + `EstadisticasPedidoSerializer`. |
| `backend/core/views.py` | Los 10 ViewSets + 2 `@action` + permisos + filtros. |
| `backend/core/admin.py` | Los 10 modelos registrados con `list_display`, `list_filter`, `search_fields` e inlines. |
| `backend/core/urls.py` | `DefaultRouter` con los 10 prefijos, montado en `/api/`. |
| `backend/core/tests.py` | ~12 tests: modelos, permisos, paginación, nested, actions y filtros. |
| `backend/templates/` | Template de bienvenida con la identidad de marca. |
| `backend/static/` | CSS/imágenes propias del template (el admin los resuelve con whitenoise + `collectstatic`). |
| `frontend/` | Carpeta de Ema; el usuario no la toca. |
| `tasks/` | `plan.md`, `todo.md`, `api-contract.md`. |
| `README.md` | Entregable final (sección 13). |

## 7. Modelo de datos

10 modelos, todos en `core/models.py`. `C` = CharField, `T` = TextField, `DT` = DateTimeField, `Dec` = DecimalField, `Int` = IntegerField. Los campos con opciones usan `TextChoices`.

| # | Modelo | Campos clave | Relaciones |
|---|---|---|---|
| 1 | `Estilo` | nombre C(100) unique · descripcion T blank · ibu Int null blank · color C(20) blank · orden Int def 0 | — |
| 2 | `Cerveza` | nombre C(150) unique · descripcion T blank · precio Dec(10,2) · volumen_ml Int def 330 · alcohol_pct Dec(4,1) null blank · stock Int def 0 · tipo choices(ENVASE/GRIFO) def ENVASE · activo Bool def True · fecha_creacion DT auto_now_add | `estilo`→Estilo `related_name='cervezas'` **PROTECT** |
| 3 | `Lote` | numero C(50) unique · fecha_inicio Date · fecha_fin Date null blank · volumen_litros Dec(8,2) · estado choices(PLANIFICADO/EN_PRODUCCION/FERMENTACION/MADURACION/LISTO/CANCELADO) def PLANIFICADO · notas T blank | `cerveza`→Cerveza `related_name='lotes'` **PROTECT** · `usuario`→User `related_name='lotes'` null blank **SET_NULL** |
| 4 | `EtapaFermentacion` | numero Int · tipo choices(PRIMARIA/SECUNDARIA/MADURADO) · fecha_inicio Date · fecha_fin Date null blank · temperatura Dec(4,1) null blank · estado choices(PENDIENTE/ACTIVA/COMPLETADA) def PENDIENTE | `lote`→Lote `related_name='etapas'` **CASCADE** |
| 5 | `Proveedor` | razon_social C(150) · cuit C(20) unique · email Email blank · telefono C(20) blank · activo Bool def True | — |
| 6 | `MateriaPrima` | nombre C(150) · tipo choices(MALTA/LUPULO/LEVADURA/OTROS) · unidad choices(KG/G/LT/UNIDAD) def KG · stock Dec(10,2) def 0 · stock_minimo Dec(10,2) def 0 · costo_unitario Dec(10,2) def 0 | `proveedor`→Proveedor `related_name='materias_primas'` null blank **SET_NULL** |
| 7 | `Cliente` | nombre C(100) · apellido C(100) · email Email unique · telefono C(20) blank · dni C(20) unique null blank · activo Bool def True · fecha_alta DT auto_now_add · **@property `nombre_completo`** | — |
| 8 | `Pedido` | fecha DT auto_now_add · estado choices(PENDIENTE/CONFIRMADO/EN_PREPARACION/LISTO_RETIRO/ENTREGADO/CANCELADO) def PENDIENTE · forma_pago choices(EFECTIVO/TARJETA/TRANSFERENCIA) def EFECTIVO · total Dec(10,2) def 0 · direccion_entrega C(255) blank · observaciones T blank | `cliente`→Cliente `related_name='pedidos'` **PROTECT** |
| 9 | `LineaPedido` | cantidad Int def 1 · precio_unitario Dec(10,2) · **@property `subtotal`** | `pedido`→Pedido `related_name='lineas'` **CASCADE** · `cerveza`→Cerveza `related_name='lineas_pedido'` **PROTECT** |
| 10 | `Opinion` | puntaje Int def 5 (validators Min 1 / Max 5) · comentario T blank · fecha DT auto_now_add | `cerveza`→Cerveza `related_name='opiniones'` **CASCADE** · `cliente`→Cliente `related_name='opiniones'` **CASCADE** |

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

### Orden de migraciones (por dependencia)

`Estilo` → `Cerveza` → `Lote` → `EtapaFermentacion` · `Proveedor` → `MateriaPrima` · `Cliente` → `Pedido` → `LineaPedido` → `Opinion`. (`User` no necesita migración: lo trae `django.contrib.auth`.)

### Por qué `PROTECT`, `CASCADE` o `SET_NULL` (una frase por caso)

- **PROTECT en `Cerveza` (desde Lote y LineaPedido):** no tiene sentido borrar una cerveza que ya se produjo o vendió; Django bloquea el borrado y protege el histórico.
- **PROTECT en `Cliente` (desde Pedido):** un pedido sin cliente pierde sentido comercial; no se puede borrar un cliente que tiene pedidos.
- **CASCADE en `EtapaFermentacion` (desde Lote):** una etapa de fermentación no existe sin su lote; al borrar el lote, sus etapas se borran con él.
- **CASCADE en `LineaPedido` (desde Pedido):** las líneas son parte del pedido; si desaparece el pedido, sus líneas quedan huérfanas.
- **CASCADE en `Opinion` (desde Cerveza y Cliente):** una opinión no sobrevive a lo que comenta ni a quien la escribió.
- **SET_NULL en `Lote.usuario`:** si se borra el usuario, el lote se queda sin responsable pero el lote se conserva (es información secundaria).
- **SET_NULL en `MateriaPrima.proveedor`:** la materia prima existe aunque el proveedor se dé de baja; solo desenganchamos el vínculo.

## 8. Contrato de API

Router `DefaultRouter` en `core/urls.py`, prefijo `/api/`. Los 10 endpoints son `ModelViewSet` (CRUD completo). Cada URL de colección tiene además su detalle en `{id}/` con `GET, PUT, PATCH, DELETE`.

| Método (colección) | URL | ViewSet | Serializer | Permiso | Filtros / búsqueda / orden | Anidado en list |
|---|---|---|---|---|---|---|
| GET, POST | `/api/estilos/` | EstiloViewSet | EstiloSerializer | IsAdminOrReadOnly | search: nombre · ordering: orden,nombre | No |
| GET, POST | `/api/cervezas/` | CervezaViewSet | CervezaSerializer | IsAuthenticated | filter: estilo,tipo,activo · search: nombre,descripcion · ordering: precio,nombre,-fecha_creacion | No |
| GET, POST | `/api/lotes/` | LoteViewSet | **LoteNestedSerializer en list** / LoteSerializer en detalle | IsAuthenticated | search: numero,cerveza__nombre · ordering: -fecha_inicio | **Sí** (`etapas`) |
| GET, POST | `/api/etapas/` | EtapaViewSet | EtapaSerializer | IsAuthenticated | filter: lote · ordering: numero | No |
| GET, POST | `/api/proveedores/` | ProveedorViewSet | ProveedorSerializer | IsAdminOrReadOnly | search: razon_social,cuit · ordering: razon_social | No |
| GET, POST | `/api/materias-primas/` | MateriaPrimaViewSet | MateriaPrimaSerializer | IsAuthenticated | filter: tipo,proveedor · search: nombre · ordering: tipo,nombre | No |
| GET, POST | `/api/clientes/` | ClienteViewSet | ClienteSerializer | IsAuthenticated | search: nombre,apellido,email,dni · ordering: -fecha_alta | No |
| GET, POST | `/api/pedidos/` | PedidoViewSet | **PedidoNestedSerializer en list** / PedidoSerializer en detalle | IsAuthenticated | filter: estado,forma_pago · search: cliente__nombre,cliente__apellido · ordering: -fecha | **Sí** (`lineas`) |
| GET, POST | `/api/lineas/` | LineaPedidoViewSet | LineaPedidoSerializer | IsAuthenticated | ordering: -pedido__fecha | No |
| GET, POST | `/api/opiniones/` | OpinionViewSet | OpinionSerializer | IsAuthenticated | ordering: -fecha | No |

**El requisito de "≥1 ViewSet con filtros y búsquedas" se cumple con creces:** `/api/cervezas/` tiene filtros (`?estilo=`, `?tipo=`, `?activo=`), búsqueda (`?search=`) y orden (`?ordering=`); el resto de los ViewSets también.

**Permisos base:** `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` en `settings.py`. `IsAdminOrReadOnly` se agrega solo en Estilo y Proveedor (catálogos que cualquiera lee y solo el staff edita). `IsAdminUser` solo en la acción `estadisticas`.

**Paginación global:** `PageNumberPagination`, `PAGE_SIZE=10`, `page_size_query_param='page_size'`, `max_page_size=50`.

### Nested serializers (solo en `list`) — patrón a explicar en la defensa

```python
def get_serializer_class(self):
    if self.action == "list":
        return LoteNestedSerializer   # o PedidoNestedSerializer
    return LoteSerializer             # plano
```

- `LoteNestedSerializer` = campos planos del lote + `etapas = EtapaSerializer(many=True, read_only=True)` + `cerveza_nombre` (`source='cerveza.nombre'`).
- `PedidoNestedSerializer` = campos planos del pedido + `lineas = LineaPedidoSerializer(many=True, read_only=True)` + `cliente_nombre` (`source='cliente.nombre_completo'`).

**Por qué solo en `list`:** el listado muestra de un vistazo el padre con sus hijos (la consigna pide "datos anidados SOLO en list"); el detalle y las escrituras van con el serializer plano para evitar payloads gigantes y escrituras anidadas accidentales.

### Endpoints `@action` (2 obligatorias + 1 opcional)

1. `GET /api/cervezas/en_grifo/` — `detail=False`, `url_path='en_grifo'`, en `CervezaViewSet`. Devuelve cervezas con `tipo='GRIFO'`, `activo=True` y `stock > 0`. Salida: `CervezaSerializer`. Permiso: `IsAuthenticated`.
2. `GET /api/pedidos/estadisticas/` — `detail=False`, `url_path='estadisticas'`, en `PedidoViewSet`. Salida: `EstadisticasPedidoSerializer` (`total_pedidos`, `monto_total`, `pedidos_por_estado`, `promedio_ticket`). Permiso: `IsAdminUser`. ORM: `Count`, `Sum`, `values()` + `annotate()`.
3. **Opcional (estirón, NO obligatorio):** `POST /api/lotes/{id}/avanzar/` — `detail=True`, avanza el estado del lote validando la transición. Solo si sobra tiempo después de la Fase 7.

### Códigos HTTP esperados

| Escenario | Código |
|---|---|
| GET list/retrieve sin token | 401 |
| GET con token pero sin permiso (ej. `estadisticas` sin staff) | 403 |
| GET list/retrieve OK | 200 |
| POST / PUT / PATCH / DELETE OK | 201 / 200 / 200 / 204 |
| Validación fallida (serializer) | 400 |
| Recurso inexistente | 404 |
| Preflight CORS sin origen permitido | 403 (respuesta del middleware, no de DRF) |

### URLs de documentación, token y panel

| URL | Descripción |
|---|---|
| `/` | Vista de bienvenida con template y marca |
| `/admin/` | Panel de administración |
| `/api/` | Índice navegable de la API (Browsable API) |
| `/api/schema/` | Esquema OpenAPI 3 (YAML/JSON) |
| `/api/schema/swagger-ui/` | Swagger UI |
| `/api/schema/redoc/` | ReDoc |
| `/api/auth-token/` | `POST {username, password}` → `{token}` (`rest_framework.authtoken.views.obtain_auth_token`) |

**Autenticación:** `POST /api/auth-token/` devuelve `{token}`; después cada request lleva `Authorization: Token <key>`. `SessionAuthentication` queda habilitada para el Browsable API y para el admin.

**Trampa a documentar (defensa oral):** las cookies **ignoran el puerto**, así que `localhost:3000` (front) y `localhost:8000` (back) comparten cookies en el mismo host. Si el SPA hiciera login por sesión, DRF exigiría CSRF en cada POST. **Decisión: el frontend usa SOLO `Authorization: Token <key>`, nunca cookies de sesión.**

**CORS:** `CorsMiddleware` siempre primero en `MIDDLEWARE`; `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`; nunca `CORS_ALLOW_ALL_ORIGINS` junto a `CORS_ALLOW_CREDENTIALS`.

## 9. Settings clave

Fragmento de `config/settings.py` (se implementa en la Task 4):

```python
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "rest_framework.authtoken", "drf_spectacular",
    "django_filters", "corsheaders",
    "core",
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   # SIEMPRE primero
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}
SPECTACULAR_SETTINGS = {"TITLE": "Cervecería Los Flacheros API", "DESCRIPTION": "API REST de gestión de cervecería artesanal.", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False}
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
```

Paginación (para que `?page_size=` funcione con tope 50) se declara una clase propia y se usa como `DEFAULT_PAGINATION_CLASS`:

```python
from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = "config.settings.DefaultPagination"
```

**`.env.example`:**

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

## 10. Docker

**`backend/Dockerfile` (single-stage, sin caches ni multi-stage):**

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**`backend/compose.yaml`:**

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
      retries: 10

  web:
    build: .
    env_file: .env
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER:-flacheros}:${POSTGRES_PASSWORD:-flacheros}@db:5432/${POSTGRES_DB:-flacheros}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    command: sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"

volumes:
  postgres_data:
```

**Notas:**

- El `version:` top-level del YAML está **obsoleto: se omite**. Se usa `docker compose` (v2, sin guion).
- **Docker Desktop NO está instalado** en la máquina del usuario → es parte del setup (Task 1). gunicorn no corre en Windows nativo → local `runserver`, Docker `gunicorn`.
- `COPY --from=ghcr.io/astral-sh/uv:0.13.1` copia solo los binarios `uv`/`uvx` (esa imagen es distroless: no trae Python ni shell); por eso la base es `python:3.13-slim`.
- `uv sync --frozen --no-install-project` + `[tool.uv] package = false`: el proyecto Django no es un paquete, sin esas flags `uv sync` intenta construirlo y falla.
- `.dockerignore` debe incluir `.venv/`, `__pycache__/`, `.env`, `*.sqlite3`, `staticfiles/`, `.git/`; si falta, el `COPY . .` arrastra el venv de Windows y rompe la imagen Linux.
- `collectstatic` corre en el `command` del compose: sin él, el admin se ve sin estilos dentro del contenedor.
- Antes del primer `docker compose up` hay que copiar `.env.example` a `.env`; si falta, `docker compose` falla al no encontrar el archivo.

## 11. Git local

| Qué SÍ | Qué NO |
|---|---|
| `git init` local en la raíz del proyecto, rama `main` | No configurar nada fuera del repositorio local |
| Ramas `feature/<tarea>`: `feature/estilos`, `feature/api-pedidos`, `feature/docker`, `feature/readme` | No commitear `.env`, `__pycache__/`, `.venv/`, `*.sqlite3`, `node_modules/`, `.next/` |
| Commits Conventional Commits en español: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:` | No commitear secretos ni credenciales |
| Merges a `main` con `git merge --no-ff feature/x` | — |
| Un commit chico y descriptivo por tarea | No dejar tareas enteras sin commitear ("WIP" al final de la semana) |

**Alcance:** esta sección cubre únicamente el trabajo con Git en local —ramas `feature/*`, commits descriptivos y merges a `main`—, que es la evidencia de proceso que pide el docente. Cualquier gestión de publicación del proyecto queda por fuera de este plan.

`.gitignore` de la raíz: `.venv/`, `__pycache__/`, `.env`, `*.sqlite3`, `staticfiles/`, `node_modules/`, `.next/`, `.pytest_cache/`, `__pypackages__/`.

## 12. Plan de pruebas

Un solo archivo `backend/core/tests.py`, **12 tests**:

| # | Test | Qué verifica |
|---|---|---|
| 1 | `test_cliente_nombre_completo` | `@property nombre_completo` de `Cliente` devuelve nombre + apellido |
| 2 | `test_linea_pedido_subtotal` | `@property subtotal` = cantidad × precio_unitario |
| 3 | `test_lote_estado_choices` | `Lote.estado` solo acepta los valores de `TextChoices` |
| 4 | `test_listado_sin_token_devuelve_401` | Sin `Authorization` → 401 |
| 5 | `test_listado_con_token_devuelve_200` | Con token válido → 200 |
| 6 | `test_paginacion_estructura` | La respuesta trae `count`, `next`, `previous`, `results` |
| 7 | `test_lotes_nested_solo_en_list` | `etapas` presente en `GET /api/lotes/` y ausente en `GET /api/lotes/{id}/` |
| 8 | `test_pedidos_nested_solo_en_list` | `lineas` presente en `GET /api/pedidos/` y ausente en `GET /api/pedidos/{id}/` |
| 9 | `test_en_grifo` | `GET /api/cervezas/en_grifo/` devuelve solo `GRIFO`, activas y con stock > 0 |
| 10 | `test_estadisticas_permisos` | `GET /api/pedidos/estadisticas/` → 403 sin staff, 200 con staff |
| 11 | `test_filtro_cervezas_tipo` | `GET /api/cervezas/?tipo=GRIFO` devuelve solo grifo |
| 12 | `test_busqueda_cervezas` | `GET /api/cervezas/?search=ipa` encuentra la IPA esperada |

Comandos:

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py spectacular --validate
```

## 13. README.md (entregable)

Estructura final del `README.md` de la raíz:

1. **Portada** con identidad de marca: nombre, lema, paleta (`#F5A623`, `#4A7C59`, `#8B4513`, `#F7F7F7`, `#2B2B2B`).
2. **Objetivo** del proyecto y alcance.
3. **Diagrama ER** (mermaid de la sección 7) — requisito literal: planificación de tablas y relaciones adjunta al README.
4. **Stack tecnológico** (tablas de backend y frontend).
5. **Instalación**: con `uv` (local, `runserver`) y con Docker Compose.
6. **Tabla de endpoints** (los 10 + las `@action` + `/api/auth-token/`).
7. **Capturas de pantalla** en `docs/capturas/`: Swagger, Redoc, Browsable API, admin con filtros y búsqueda, vista de bienvenida, frontend de Ema (si está listo).
8. **Credenciales de prueba** (usuario demo y superusuario).
9. **Comandos útiles** (`runserver`, `pytest`, `ruff`, `docker compose up --build`).
10. **Proceso del equipo**: ramas, commits, merges (lo evalúa la defensa oral).
11. Autores.

## 14. Cronograma

| Fecha | Hito | Tareas |
|---|---|---|
| Lun 19/10 – Mar 20/10 | Fase 0: uv + Docker Desktop, estructura, pyproject, git local | T1–T3 |
| Mar 20/10 – Mié 21/10 | Fase 1: Django base (`config` + `core`), settings, bienvenida, URLs y docs | T4–T6 |
| Mié 21/10 – Vie 23/10 | Fase 2: los 10 modelos + migraciones + `makemigrations --check` | T7–T11 |
| Vie 23/10 – Sáb 24/10 | Fase 3: admin con filtros, búsqueda, orden e inlines | T12–T13 |
| Sáb 24/10 – Lun 27/10 | Fase 4: serializers, ViewSets, router, nested, `@action`, filtros | T14–T18 |
| Lun 27/10 – Mar 28/10 | Fase 5: CORS final + handoff a Ema (`api-contract.md`) | T19–T20 |
| Mar 28/10 – Mié 29/10 | Fase 6: Docker single-stage + compose y verificación | T21–T22 |
| Mié 29/10 – Jue 30/10 | Fase 7: ~12 tests + ruff + calidad | T23–T24 |
| Jue 30/10 – Dom 2/11 | Fase 8: seed + capturas + README + checklist y ensayo | T25–T28 |
| **Lun 2/11** | **Entrega: `README.md` con diagrama ER y capturas, `main` al día** | — |
| Mar 3/11 | Defensa oral (backend + proceso) | — |

## 15. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| No tener `uv` o Docker instalados a tiempo | Alto | Task 1 verifica `uv --version` y `docker --version` en terminal nueva; la Fase 6 no arranca sin Docker. |
| WSL2 no instalado: el motor de Docker Desktop no levanta | Alto | El usuario ejecuta `wsl --install` como administrador y reinicia; mientras tanto el proyecto sigue desarrollándose con SQLite local y el entregable dockerizado (`Dockerfile` + `compose.yaml`) no depende de que el motor funcione. |
| Trampa CSRF/cookies entre `localhost:3000` y `localhost:8000` | Alto | Frontend SOLO con `Authorization: Token`; nunca login por sesión desde el SPA. Documentado en `api-contract.md`, README y ensayo. |
| drf-spectacular vs DRF 3.18 (soporte declarado hasta 3.17) | Medio | Pin DRF 3.17.x; fallback 3.18.3 validando siempre con `spectacular --validate`. |
| Quedarse sin tiempo para las capturas | Medio | Task 26 va después del seed y antes del README; si falta tiempo, capturar lo mínimo: Swagger, admin con filtros y bienvenida. |
| Olvidar `collectstatic` (admin sin estilos en Docker) | Medio | El `command` del compose lo ejecuta; la Task 22 verifica el admin con estilos en el contenedor. |
| `makemigrations --check` sucio al cerrar | Bajo | Lo corren la Task 11 y la Task 24; es parte de la triada de calidad. |
| No llegar con el README | Alto | La Task 27 arranca el 30/10 con la estructura ya definida en la sección 13; no se empieza de cero. |
| Ser principiante y trabarse con un concepto | Medio | Glosario de la sección 3, tareas chicas con verificación explícita y una sola dependencia por tarea; trabarse = volver al plan, no improvisar. |
| Que el README final quede sin el diagrama ER de tablas | Alto | El diagrama va como criterio de aceptación obligatorio de la Task 27 (requisito 2 del docente) |
| Ema no llega con el frontend a tiempo | Medio | El backend es autónomo (no depende del frontend); el contrato se congela en la Task 20. |

## 16. Preguntas abiertas

1. **Imágenes de producto:** ¿se agregan imágenes (Pillow + `ImageField`) o se omite? El alcance actual es **sin imágenes**; cambiar esto impacta modelos, admin y migraciones.
2. **Nivel de seed:** ¿cuántos datos de prueba realistas en el comando `seed_datos`? Se propone lo justo para las capturas (unos 5 estilos, 8 cervezas, 3 lotes con etapas, 10 clientes, 15 pedidos con líneas y opiniones).

## 17. Convención de documentación

### Por qué existe

El usuario se atrasó en clases y necesita dos cosas a la vez: **entender qué se está construyendo** y **poder defenderlo oralmente** ante el docente. Por eso la documentación no es un extra: es parte del entregable. Cada concepto que aparece en el código queda explicado con ejemplos de ESTE proyecto, y cada decisión queda registrada con su justificación.

### Las tres capas de documentación

1. **Guías conceptuales** — explicación de los conceptos con ejemplos de ESTE proyecto, cada una con un bloque "Para la defensa" (qué decir si el docente pregunta sobre ese tema):
   - `docs/01-django-esencial.md` — proyecto vs app, settings, modelos, migraciones, ORM, admin, vistas y templates.
   - `docs/02-drf-esencial.md` — serializers, ViewSets, router, permisos, paginación, filtros, `@action` y documentación OpenAPI.
   - `docs/03-http-json-cors.md` — métodos y códigos HTTP, JSON, token vs sesión, CORS y la trampa de cookies/CSRF.
   - `docs/04-nuestro-modelo.md` — los 10 modelos, relaciones, `on_delete` y el diagrama ER del proyecto.
   - `docs/05-stack-y-entorno.md` — uv, Docker, compose, pytest y ruff: por qué está cada herramienta del stack.
2. **Cuaderno de defensa** — `docs/06-cuaderno-de-defensa.md`: 30+ preguntas típicas del docente con la respuesta lista para decir, un guion de apertura de 2 minutos y un plan de repaso previo a la defensa.
3. **Notas de tarea** — una por cada tarea ejecutada, en `docs/tareas/T##-<slug>.md`: qué se hizo, qué conceptos aparecen, qué mirar en el código, qué responder y los errores que nos pasamos con su solución. Son el diario de aprendizaje.

### Índice de la carpeta `docs/`

| Archivo | Qué cubre | En qué fase leerlo |
|---|---|---|
| `docs/01-django-esencial.md` | Conceptos base de Django con ejemplos del proyecto | Fase 1 (al crear `config` y `core`) |
| `docs/02-drf-esencial.md` | DRF: serializers, ViewSets, permisos, filtros, `@action` | Fase 4 (al construir la API) |
| `docs/03-http-json-cors.md` | HTTP, JSON, token vs sesión, CORS y cookies/CSRF | Fase 5 (al cerrar CORS y el handoff) |
| `docs/04-nuestro-modelo.md` | Los 10 modelos, relaciones y el diagrama ER | Fase 2 (al implementar los modelos) |
| `docs/05-stack-y-entorno.md` | uv, Docker, compose, pytest y ruff | Fases 0 y 6 (entorno y Docker) |
| `docs/06-cuaderno-de-defensa.md` | 30+ preguntas de defensa con respuestas, guion y plan de repaso | Fase 8 (ensayo) y antes de la defensa |
| `docs/tareas/T##-<slug>.md` | Nota de cada tarea ejecutada | Al cerrar cada tarea |
| `docs/tareas/_plantilla.md` | Plantilla en blanco para las notas de tarea | Al escribir cada nota |
| `docs/capturas/` | Capturas del proyecto funcionando (entregable del README) | Fase 8 |

### Regla de oro

*Cada tarea del plan se documenta al terminarla.* La nota se escribe **antes** de dar la tarea por cerrada: sin nota, la tarea no está completa, aunque el código funcione. La Task 29 de `tasks/todo.md` formaliza esta obligación.

### Formato de la nota de tarea

Cada nota sigue la plantilla `docs/tareas/_plantilla.md` con estas secciones:

| Sección de la nota | Qué contiene |
|---|---|
| Qué se hizo | Resumen de lo implementado en la tarea |
| Conceptos que aparecen | Qué conceptos de Django/DRF toca la tarea |
| Archivos | Qué archivos se crearon o modificaron |
| Qué mirar en el código | Fragmentos o líneas que conviene releer |
| Para la defensa | Al menos una pregunta posible del docente con su respuesta de 2-4 frases |
| Errores que nos pasaron | Los errores reales de esa tarea y cómo se resolvieron (si no hubo: "Sin errores") |
| Verificación | Comandos ejecutados con su resultado esperado |

### Convención de nombres

Las notas viven en `docs/tareas/` y el número coincide con el número de tarea de `tasks/todo.md`: `docs/tareas/T01-instalar-uv-docker.md`, `docs/tareas/T07-modelos-catalog.md`, `docs/tareas/T29-documentar-cada-tarea.md`, etc.

## 18. Task List

Índice ordenado de las 29 tareas con criterios de aceptación y verificación: ver [`tasks/todo.md`](todo.md).

| Fase | Tasks | Fechas |
|---|---|---|
| 0 — Entorno | 1–3 | 19–20 oct |
| 1 — Django base | 4–6 | 20–21 oct |
| 2 — Modelos | 7–11 | 21–23 oct |
| 3 — Admin | 12–13 | 23–24 oct |
| 4 — API | 14–18 | 24–27 oct |
| 5 — Integración con Ema | 19–20 | 27–28 oct |
| 6 — Docker | 21–22 | 28–29 oct |
| 7 — Tests y calidad | 23–24 | 29–30 oct |
| 8 — Cierre y entrega | 25–28 | 30 oct – 2 nov |
| 9 — Documentación y defensa (continua) | 29 | 19 oct – 2 nov |
