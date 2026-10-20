# Todo — Cervecería Los Flacheros

31 tareas en 10 fases + 9 checkpoints (uno por fase; la Fase 9 es continua y no tiene checkpoint; las Tasks 30 y 31 tienen fecha fija fuera de fase). Convención: cada tarea se cierra con su checklist de verificación en verde. Tamaños: XS | S | M.

Cada tarea explica **qué concepto de Django se usa y por qué**: esa explicación es material de estudio para la defensa oral, no relleno. El alcance completo, el glosario y el modelo de datos están en [`tasks/plan.md`](plan.md).

---

## Fase 0 — Entorno (19-20 oct)

### Task 1: Instalar uv y Docker Desktop

**Descripción:** Verificar el estado real del entorno (estado verificado el 19/10/2026: **uv 0.13.1 instalado**; **Docker Desktop YA está instalado** — cliente `docker` 29.8.2 + `docker compose` v5.6.0 en `C:\Program Files\Docker\Docker\resources\bin\`) y confirmar que el **motor** de Docker levanta (WSL2). Concepto de Django implicado: ninguno todavía; es el requisito del docente de usar `uv` como gestor de entornos (requisito 12) y de dockerizar el proyecto (requisito 14).

Detalle práctico: `docker` **no está en el PATH de todas las consolas**: si un comando no lo encuentra, usar la ruta absoluta `C:\Program Files\Docker\Docker\resources\bin\docker.exe` o agregar esa carpeta al PATH del sistema.

**Criterios de aceptación:**
- [x] `uv` instalado (verificado: `uv --version` → `0.13.1`)
- [x] Docker Desktop instalado (verificado: `docker --version` → 29.8.2, `docker compose version` → v5.6.0)
- [ ] El **motor** responde: `docker info` devuelve el estado del daemon sin errores (esto es lo que falta confirmar; requiere WSL2 activo)
- [ ] Terminal NUEVA abierta: `uv --version` y `docker compose version` responden sin errores

**Plan B explícito (si el motor no levanta en esta máquina):** no dejar la tarea bloqueada. Verificar el build del stack en otra máquina/VM o en la del docente **antes del 1/11**, documentar el resultado en la nota de tarea (`docs/tareas/T01-...`) y seguir adelante: el `Dockerfile` y el `compose.yaml` se escriben igual (Tasks 21–22) y el resto del proyecto se desarrolla con SQLite local.

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv --version && docker --version && docker compose version` y `docker info`
- [ ] Manual: `uv python list` muestra Python 3.13 disponible; `docker info` responde (o queda documentado el plan B)

**Dependencias:** Ninguna
**Archivos probables:** — (solo instalación)
**Escala:** XS

### Task 2: Estructura de carpetas, pyproject.toml y archivos base

**Descripción:** Crear el árbol de carpetas del proyecto (sección 6 del plan), inicializar el proyecto Python en `backend/` con `uv init`, agregar las dependencias del stack y generar `uv.lock`, además de `.env.example`, `.gitignore` y `.dockerignore`. Concepto de Django implicado: aún no hay código Django; lo importante acá es que `pyproject.toml` declara **`[tool.uv] package = false`**, porque un proyecto Django no es un paquete distribuible y sin eso `uv sync` intenta construirlo y falla.

**Criterios de aceptación:**
- [ ] Árbol creado: `backend/`, `frontend/` (placeholder de Ema), `tasks/`, `README.md` raíz
- [ ] `pyproject.toml` con `requires-python = ">=3.13"`, `[tool.uv] package = false` y el grupo dev (pytest, pytest-django, ruff)
- [ ] `uv lock` ejecutado; `uv.lock` presente
- [ ] `.python-version` con `3.13` (`uv python pin 3.13`)
- [ ] `.env.example` con las variables del plan (DJANGO_SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, POSTGRES_*, CORS_ALLOWED_ORIGINS)
- [ ] `.gitignore` y `.dockerignore` con las listas de la sección 11 y 10 del plan

**Verificación:**
- [ ] Tests: N/A (aún sin tests)
- [ ] Arranque: `uv sync` termina sin errores y crea `.venv`
- [ ] Manual: `uv run python --version` muestra 3.13.x

**Dependencias:** Task 1
**Archivos probables:** `backend/pyproject.toml`, `backend/uv.lock`, `backend/.env.example`, `backend/.gitignore`, `backend/.dockerignore`
**Escala:** S

### Task 3: Git local: `git init`, rama main, primer commit y `.gitignore`

**Descripción:** Inicializar el repositorio git **local** en la raíz, con `main` como rama por defecto, y hacer el primer commit. Concepto de Django implicado: ninguno; es el requisito 15 (proceso Git: ramas y commits descriptivos).

**Criterios de aceptación:**
- [ ] `git init` con `main` como rama por defecto
- [ ] Primer commit con mensaje convencional en español (ej. `chore: inicializa proyecto con estructura base`)
- [ ] Convención definida: ramas `feature/<tarea>` y merges a `main` con `git merge --no-ff`

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `git log --oneline` muestra el commit; `git status` limpio
- [ ] Manual: `git branch` muestra solo `main`

**Dependencias:** Task 2
**Archivos probables:** `.gitignore`, `README.md`
**Escala:** XS

---

### Checkpoint: Fase 0

- [ ] `uv`, `docker` y `docker compose` responden en terminal nueva
- [ ] `uv sync` reproducible desde `uv.lock`; `.venv` creado
- [ ] `.env.example`, `.gitignore` y `.dockerignore` presentes
- [ ] Git local con `main` y primer commit

---

## Fase 1 — Django base (20-21 oct)

### Task 4: Proyecto `config`, app `core` y settings completos

**Descripción:** Crear el proyecto Django con `django-admin startproject config` y la única app del proyecto con `startapp core`; después completar `config/settings.py` con DRF, CORS, drf-spectacular y django-environ leyendo `.env`. Conceptos de Django en juego: **proyecto vs app** (el proyecto `config` es el esqueleto con settings y URLs; `core` es el módulo de negocio) y **settings** (la lista `INSTALLED_APPS` es lo que le dice a Django qué módulos cargar; `MIDDLEWARE` es la cadena de procesamiento de cada request).

**Criterios de aceptación:**
- [ ] `manage.py` y paquete `config/` (settings.py, urls.py, wsgi.py, asgi.py) existen
- [ ] App `core/` creada y agregada a `INSTALLED_APPS`
- [ ] `REST_FRAMEWORK` con TokenAuthentication + SessionAuthentication, `IsAuthenticated` global, `DEFAULT_PAGINATION_CLASS = "config.settings.DefaultPagination"` (clase propia con `page_size = 10`, `page_size_query_param = "page_size"` y `max_page_size = 50`; no la `PageNumberPagination` de fábrica, que no acepta `?page_size=`), filter backends y `DEFAULT_SCHEMA_CLASS` de drf-spectacular
- [ ] `SPECTACULAR_SETTINGS` con TITLE/DESCRIPTION/VERSION
- [ ] `CorsMiddleware` como primer middleware; `whitenoise` en su lugar (sección 9 del plan)
- [ ] Settings leen `.env` con django-environ (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, CORS_ALLOWED_ORIGINS)

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py check` sin errores
- [ ] Manual: `uv run python manage.py runserver` responde en `http://localhost:8000/`

**Dependencias:** Task 2
**Archivos probables:** `backend/config/settings.py`, `backend/core/apps.py`, `backend/.env`
**Escala:** M

### Task 5: Vista de bienvenida con template y static

**Descripción:** Crear la vista y el template HTML de bienvenida en `/` con la identidad de marca, configurar `templates/` y `static/` y dejar whitenoise listo para `collectstatic`. Conceptos de Django en juego: **vista + template** (Django renderiza HTML con contexto) y **static files** (whitenoise sirve los estáticos del admin y del template dentro del contenedor, sin nginx).

**Criterios de aceptación:**
- [ ] `/` renderiza un template (TemplateView)
- [ ] Template usa la paleta (`#F5A623`, `#4A7C59`, `#8B4513`, `#F7F7F7`, `#2B2B2B`) y el lema
- [ ] `STORAGES` con whitenoise configurado
- [ ] `collectstatic` corre sin errores

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py collectstatic --noinput`
- [ ] Manual: abrir `http://localhost:8000/` y ver la bienvenida con la marca

**Dependencias:** Task 4
**Archivos probables:** `backend/templates/bienvenida.html`, `backend/config/urls.py`, `backend/static/`
**Escala:** S

### Task 6: URLs del proyecto, documentación y token

**Descripción:** Definir el mapa de URLs del proyecto: `/`, `/admin/`, el router de la API en `/api/` (aún vacío), el schema con Swagger y ReDoc, el endpoint de token y el login de sesión en `/api-auth/`. Conceptos de Django en juego: **urls.py** (mapeo URL → vista) y **Browsable API** de DRF (DRF sirve una interfaz navegable en cada endpoint, que es la "API navegable" del requisito 9; con `rest_framework.urls` montado en `/api-auth/` esa interfaz tiene además botón de login/logout).

**Criterios de aceptación:**
- [ ] `/api/schema/` devuelve el schema OpenAPI
- [ ] `/api/schema/swagger-ui/` y `/api/schema/redoc/` cargan sus UIs
- [ ] `BrowsableAPIRenderer` en `DEFAULT_RENDERER_CLASSES`
- [ ] `path("api-auth/", include("rest_framework.urls"))` en `config/urls.py`: la Browsable API tiene botón de login/logout (autenticación por sesión, requisito literal)
- [ ] `POST /api/auth-token/` con `{username, password}` devuelve `{token}` (probar con un superusuario creado con `uv run python manage.py createsuperuser`)
- [ ] `uv run python manage.py spectacular --validate` sin errores

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: abrir Swagger y ReDoc; pedir un token en `/api/auth-token/`; abrir `/api-auth/login/` y loguearse desde la Browsable API

**Dependencias:** Task 4
**Archivos probables:** `backend/config/urls.py`, `backend/config/settings.py`
**Escala:** S

---

### Checkpoint: Fase 1

- [ ] `manage.py check` limpio
- [ ] `/` renderiza la bienvenida con la marca
- [ ] Swagger y ReDoc responden
- [ ] `/api/auth-token/` emite tokens y `/api-auth/` muestra el login de la Browsable API

---

## Fase 2 — Modelos (21-23 oct)

### Task 7: Modelos Estilo y Cerveza + migración

**Descripción:** Implementar `Estilo` y `Cerveza` con sus campos y la relación FK, y generar la primera migración. Concepto de Django en juego: **modelo y migración** — cada clase se convierte en una tabla; `makemigrations` genera el archivo y `migrate` lo aplica. Acá se ve la primera **relación ForeignKey** con `related_name='cervezas'` y `on_delete=PROTECT` (no se puede borrar un estilo que tiene cervezas).

**Criterios de aceptación:**
- [ ] `Estilo` y `Cerveza` con los campos exactos de la sección 7 del plan
- [ ] `Cerveza.estilo` → PROTECT, `related_name='cervezas'`
- [ ] `Cerveza.tipo` con `TextChoices` (ENVASE/GRIFO, default ENVASE)
- [ ] Migración generada y aplicada

**Verificación:**
- [ ] Tests: N/A aún
- [ ] Arranque: `uv run python manage.py migrate`
- [ ] Manual: `uv run python manage.py shell` — crear un Estilo y una Cerveza

**Dependencias:** Task 4
**Archivos probables:** `backend/core/models.py`, `backend/core/migrations/`
**Escala:** M

### Task 8: Modelos Lote y EtapaFermentacion + migración

**Descripción:** Implementar `Lote` y `EtapaFermentacion` con la máquina de estados del lote y la relación de etapas, y migrar. Concepto de Django en juego: **cascada de dependencias** — `EtapaFermentacion` depende de `Lote`, por eso se crea después y con `on_delete=CASCADE` (una etapa sin lote no existe). También se ve `SET_NULL` en `Lote.usuario` (el lote sobrevive si se borra el usuario).

**Criterios de aceptación:**
- [ ] `Lote` con `estado` de 6 valores (`TextChoices`), `cerveza` PROTECT, `usuario` SET_NULL null blank
- [ ] `EtapaFermentacion.lote` → CASCADE, `related_name='etapas'`
- [ ] Migración generada y aplicada

**Verificación:**
- [ ] Tests: N/A aún
- [ ] Arranque: `uv run python manage.py migrate`
- [ ] Manual: shell — crear un lote con 2 etapas

**Dependencias:** Task 7
**Archivos probables:** `backend/core/models.py`, `backend/core/migrations/`
**Escala:** M

### Task 9: Modelos Proveedor y MateriaPrima + migración

**Descripción:** Implementar `Proveedor` y `MateriaPrima` con sus choices y la relación, y migrar. Concepto de Django en juego: **`choices` con `TextChoices`** (valores válidos de `tipo` y `unidad`, validados por el modelo y documentados solos) y `SET_NULL` en `MateriaPrima.proveedor`.

**Criterios de aceptación:**
- [ ] `Proveedor` con `cuit` único y `activo`
- [ ] `MateriaPrima` con `tipo`, `unidad`, `stock`, `stock_minimo`, `costo_unitario`
- [ ] `MateriaPrima.proveedor` → SET_NULL, null blank, `related_name='materias_primas'`
- [ ] Migración generada y aplicada

**Verificación:**
- [ ] Tests: N/A aún
- [ ] Arranque: `uv run python manage.py migrate`
- [ ] Manual: shell — crear un Proveedor con 2 MateriasPrimas

**Dependencias:** Task 7
**Archivos probables:** `backend/core/models.py`, `backend/core/migrations/`
**Escala:** M

### Task 10: Modelos Cliente, Pedido, LineaPedido y Opinion + migración

**Descripción:** Implementar los cuatro modelos finales del dominio de ventas y opiniones, y migrar. Conceptos de Django en juego: **relación muchOS-a-muchos disfrazada** (`Pedido` tiene muchas `LineaPedido`; `Cerveza` y `Cliente` tienen muchas `Opinion`), **PROTECT** en `Pedido.cliente` y `LineaPedido.cerveza` (proteger el histórico) y **CASCADE** en `LineaPedido.pedido` y en `Opinion`.

**Criterios de aceptación:**
- [ ] `Cliente.email` y `dni` únicos; `@property nombre_completo`
- [ ] `Pedido.cliente` → PROTECT; `LineaPedido.pedido` → CASCADE (`related_name='lineas'`); `LineaPedido.cerveza` → PROTECT
- [ ] `Opinion` con `puntaje` y validators Min 1 / Max 5; CASCADE desde Cerveza y Cliente
- [ ] Migración generada y aplicada

**Verificación:**
- [ ] Tests: N/A aún
- [ ] Arranque: `uv run python manage.py migrate`
- [ ] Manual: shell — crear un cliente con un pedido de 2 líneas y una opinión

**Dependencias:** Task 7, Task 8
**Archivos probables:** `backend/core/models.py`, `backend/core/migrations/`
**Escala:** M

### Task 11: Cierre de modelos: properties, validators y makemigrations --check

**Descripción:** Revisar en conjunto `choices`, `@property` (`nombre_completo`, `subtotal`) y validators, y dejar las migraciones al día. Concepto de Django en juego: **`@property` expuesta por el serializer** — `nombre_completo` y `subtotal` no son campos de la base pero se leen como si lo fueran (solo lectura) y son el ejemplo más claro de "lógica de presentación en el modelo".

**Criterios de aceptación:**
- [ ] Los 10 modelos presentes en `core/models.py` con los campos de la sección 7 del plan
- [ ] `Cliente.nombre_completo` y `LineaPedido.subtotal` implementadas como `@property`
- [ ] `Opinion.puntaje` con `MinValueValidator(1)` y `MaxValueValidator(5)`
- [ ] `makemigrations --check --dry-run` sin cambios pendientes

**Verificación:**
- [ ] Tests: `uv run pytest`
- [ ] Arranque: `uv run python manage.py makemigrations --check --dry-run`
- [ ] Manual: shell — imprimir `cliente.nombre_completo` y `linea.subtotal`

**Dependencias:** Task 9, Task 10
**Archivos probables:** `backend/core/models.py`
**Escala:** S

---

### Checkpoint: Fase 2

- [ ] 10 modelos creados y migraciones aplicadas
- [ ] Orden de migraciones respetado (Estilo → Cerveza → Lote → Etapa · Proveedor → MateriaPrima · Cliente → Pedido → LineaPedido → Opinion)
- [ ] `makemigrations --check --dry-run` limpio
- [ ] `nombre_completo` y `subtotal` responden desde el shell

---

## Fase 3 — Admin (23-24 oct)

### Task 12: Registrar los 10 modelos en el admin

**Descripción:** Configurar un `ModelAdmin` por modelo con `list_display`, `list_filter`, `search_fields` y `ordering`. Concepto de Django en juego: **admin autogenerado** — registrando la clase en `admin.py` obtenemos una interfaz CRUD completa gratis; los cuatro atributos de arriba son exactamente lo que el docente pide mostrar en el panel (requisito 11: filtros, ordenamiento y búsqueda). Los tres atributos van en los **10 modelos**: el costo es cero (una línea por atributo) y el docente pide "control total" desde el panel.

**Criterios de aceptación:**
- [ ] Los 10 modelos registrados en `core/admin.py`
- [ ] `search_fields` con joins (ej. Lote: `numero`, `cerveza__nombre`; Pedido: `cliente__nombre`, `cliente__apellido`)
- [ ] `list_filter` en los **10 modelos** (tipo, estado, activo, etc.)
- [ ] `ordering` también en los 10 modelos
- [ ] Admin carga sin errores y filtros/búsqueda funcionan

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: entrar a `/admin/` y probar búsqueda y filtros en Cerveza, Lote y Pedido

**Dependencias:** Task 11
**Archivos probables:** `backend/core/admin.py`
**Escala:** M

### Task 13: Inlines en el admin y superusuario de prueba

**Descripción:** Agregar `EtapaFermentacionInline` en `Lote` y `LineaPedidoInline` en `Pedido`, y crear el superusuario de prueba. Concepto de Django en juego: **inlines** — editar un padre con sus hijos en la misma pantalla; es el equivalente del admin al "nested" de la API y un buen ejemplo para la defensa.

**Criterios de aceptación:**
- [ ] `EtapaFermentacionInline` (Tabular) en `LoteAdmin`
- [ ] `LineaPedidoInline` (Tabular) en `PedidoAdmin`
- [ ] Superusuario demo creado (`createsuperuser`); credenciales documentadas para la Task 25
- [ ] Abrir un Lote en admin y ver/editar sus etapas en la misma pantalla

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: abrir un Pedido en admin y ver sus líneas inline

**Dependencias:** Task 12
**Archivos probables:** `backend/core/admin.py`
**Escala:** S

---

### Checkpoint: Fase 3

- [ ] Los 10 modelos visibles en `/admin/` con filtros, orden y búsqueda
- [ ] Inlines funcionando en Lote y Pedido
- [ ] Superusuario demo accesible

---

## Fase 4 — API (24-27 oct)

### Task 14: Serializers simples de los 10 modelos

**Descripción:** Crear en `core/serializers.py` un `ModelSerializer` por modelo, más `EstadisticasPedidoSerializer`. Concepto de Django en juego: **serializer** — traductor y validador entre modelos y JSON; con `ModelSerializer` DRF infiere campos y validaciones desde el modelo, así que la mayoría del trabajo ya está hecho por Django.

**Criterios de aceptación:**
- [ ] 10 serializers planos (Estilo, Cerveza, Lote, Etapa, Proveedor, MateriaPrima, Cliente, Pedido, LineaPedido, Opinion)
- [ ] `LineaPedidoSerializer` expone `subtotal` como solo lectura
- [ ] `EstadisticasPedidoSerializer` con `total_pedidos`, `monto_total`, `pedidos_por_estado`, `promedio_ticket`
- [ ] Ningún campo de solo lectura acepta escritura (probar con un POST inválido)

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py check`
- [ ] Manual: revisar que los campos del serializer coinciden con la sección 7 del plan

**Dependencias:** Task 11
**Archivos probables:** `backend/core/serializers.py`
**Escala:** M

### Task 15: ViewSets, router y permisos globales

**Descripción:** Implementar los 10 `ModelViewSet` en `core/views.py`, registrarlos en un `DefaultRouter` montado en `/api/` y aplicar los permisos con la regla única del plan (sin `IsAdminOrReadOnly`): lectura = `IsAuthenticated` global (cualquier usuario autenticado); escritura = `IsAdminUser` (solo staff) en los 8 ViewSets que no son el mostrador; `Pedido` y `LineaPedido` se quedan con `IsAuthenticated` porque es el mostrador (cualquier autenticado crea y edita). Conceptos de Django/DRF en juego: **ViewSet + router** — un ViewSet por modelo da CRUD completo y el router genera las URLs y la documentación sin escribir vistas una por una; **permisos declarativos** — DRF chequea el permiso antes de entrar al ViewSet (el permiso por acción de escritura se aplica con `get_permissions()`, una línea por ViewSet).

**Criterios de aceptación:**
- [ ] 10 ViewSets registrados en `core/urls.py` con los prefijos de la sección 8 del plan
- [ ] Lectura: `IsAuthenticated` global — GET sin token → 401 en **todos** los endpoints (no hay lectura anónima)
- [ ] Escritura (`create`/`update`/`partial_update`/`destroy`) con `IsAdminUser` en estilos, cervezas, lotes, etapas, proveedores, materias-primas, clientes y opiniones
- [ ] `Pedido` y `LineaPedido`: cualquier usuario autenticado crea y edita (es el mostrador)
- [ ] Paginación visible: `GET /api/cervezas/` devuelve `count`, `next`, `previous`, `results`
- [ ] GET sin token → 401; POST con token de staff → 201; POST con token normal en `/api/pedidos/` → 201

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: `http://localhost:8000/api/` lista los 10 endpoints del router

**Dependencias:** Task 14
**Archivos probables:** `backend/core/views.py`, `backend/core/urls.py`, `backend/config/urls.py`
**Escala:** M

### Task 16: Nested serializers SOLO en list (Lote y Pedido)

**Descripción:** Crear `LoteNestedSerializer` y `PedidoNestedSerializer`, y seleccionarlos con `get_serializer_class()` únicamente cuando `self.action == "list"`. Concepto de DRF en juego: **polimorfismo de serializer por acción** — el mismo ViewSet responde distinto según la acción; es el patrón que el docente pide explícitamente (requisito 4) y hay que poder explicarlo con una frase: "en el listado traigo el padre con sus hijos; en el detalle y en las escrituras, el objeto plano".

**Criterios de aceptación:**
- [ ] `GET /api/lotes/` incluye `etapas` (array) y `cerveza_nombre`
- [ ] `GET /api/lotes/{id}/` NO incluye `etapas`
- [ ] `GET /api/pedidos/` incluye `lineas` (array) y `cliente_nombre`
- [ ] `GET /api/pedidos/{id}/` NO incluye `lineas`
- [ ] Campos anidados con `read_only=True`

**Verificación:**
- [ ] Tests: N/A (los tests van en la Task 23)
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: comparar el JSON de list vs detail de lotes y pedidos

**Dependencias:** Task 15
**Archivos probables:** `backend/core/serializers.py`, `backend/core/views.py`
**Escala:** M

### Task 17: @action en_grifo y estadisticas

**Descripción:** Implementar las dos acciones custom: `en_grifo` en `CervezaViewSet` y `estadisticas` en `PedidoViewSet` (esta última con `IsAdminUser`). Concepto de DRF en juego: **`@action`** — agrega un endpoint extra dentro de un ViewSet sin crear modelo ni vista nueva; `detail=False` lo monta en la colección. En `estadisticas` se usa el **ORM de Django** (`Count`, `Sum`, `values()` + `annotate()`) para agregar sin escribir SQL.

**Criterios de aceptación:**
- [ ] `GET /api/cervezas/en_grifo/` devuelve solo cervezas `GRIFO`, activas y con `stock > 0`
- [ ] `GET /api/pedidos/estadisticas/` devuelve `total_pedidos`, `monto_total`, `pedidos_por_estado`, `promedio_ticket`
- [ ] `estadisticas` sin staff → 403; con staff → 200
- [ ] Ambas acciones aparecen en Swagger

**Verificación:**
- [ ] Tests: N/A (la Task 23 los cubre)
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: probar las dos URLs con token de usuario normal y de staff

**Dependencias:** Task 15
**Archivos probables:** `backend/core/views.py`, `backend/core/serializers.py`
**Escala:** M

### Task 18: Filtros, búsqueda y ordenamiento + acciones `avanzar` y cierre de `estadisticas`

**Descripción:** Configurar `DjangoFilterBackend`, `SearchFilter` y `OrderingFilter` en los ViewSets, con el foco en `Cerveza` (el requisito 8 se cumple ahí) y el resto según la tabla de la sección 8 del plan. Además se cierran las acciones de negocio de la Fase 4: `avanzar` (comprometida, ya no es opcional) y el detalle del serializer de `estadisticas` con base vacía. Concepto de DRF en juego: **filter backends** — DRF aplica los query params (`?tipo=`, `?search=`, `?ordering=`) antes de serializar; `django-filter` valida los filtros de campos y FK, `SearchFilter` hace el `ILIKE` y `OrderingFilter` ordena.

**Criterios de aceptación:**
- [ ] Cerveza: filtros `estilo`, `tipo`, `activo`; search `nombre`, `descripcion`; ordering `precio`, `nombre`, `-fecha_creacion`
- [ ] Pedido: filtros `estado`, `forma_pago`; search `cliente__nombre`, `cliente__apellido`; ordering `-fecha`
- [ ] MateriaPrima: filtros `tipo`, `proveedor`; search `nombre`; ordering `tipo`, `nombre`
- [ ] Estilos, Proveedores, Clientes, Lotes, Etapas, Líneas y Opiniones con search u ordering según la sección 8
- [ ] `GET /api/cervezas/?tipo=GRIFO&search=ipa&ordering=-fecha_creacion` responde 200
- [ ] `POST /api/lotes/{id}/avanzar/` implementada (`@action(detail=True, url_path="avanzar")`, permiso `IsAdminUser`): avanza el estado validando la transición; un salto inválido responde 400; aparece en Swagger y la consume el frontend
- [ ] `EstadisticasPedidoSerializer` usa `allow_null=True` en `monto_total` y `promedio_ticket` (para no romper con base vacía) y el seed (Task 25) corre antes de las capturas (Task 26)

**Verificación:**
- [ ] Tests: N/A (la Task 23 los cubre)
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: probar filtros combinados y un `ordering` inválido (debe ignorarlo, no romper); probar `avanzar` con un lote en cada estado

**Dependencias:** Task 15, Task 16, Task 17
**Archivos probables:** `backend/core/views.py`, `backend/core/serializers.py`
**Escala:** M

---

### Checkpoint: Fase 4

- [ ] 10 endpoints responden paginados con token
- [ ] Nested (`etapas`/`lineas`) presente SOLO en list
- [ ] `en_grifo` y `estadisticas` funcionando con permisos correctos; `avanzar` funcionando en Task 18
- [ ] Filtros/búsqueda/orden funcionando, con `Cerveza` completo
- [ ] Swagger muestra las 10 rutas y las 3 acciones

---

## Fase 5 — Integración con Ema (27-28 oct)

### Task 19: CORS final y trampa de cookies/CSRF

**Descripción:** Cerrar la configuración CORS contra `http://localhost:3000`, verificar el preflight y documentar la trampa de cookies compartidas entre puertos. Concepto de Django en juego: **middleware** — `CorsMiddleware` intercepta las requests del navegador (incluido el preflight `OPTIONS`) y agrega los headers; por eso va primero en la lista.

**Criterios de aceptación:**
- [ ] `CORS_ALLOWED_ORIGINS` incluye `http://localhost:3000` (por defecto en settings)
- [ ] `CorsMiddleware` es el primer middleware
- [ ] Preflight `OPTIONS` con `Origin: http://localhost:3000` devuelve `Access-Control-Allow-Origin`
- [ ] Nunca `CORS_ALLOW_ALL_ORIGINS=True` junto a `CORS_ALLOW_CREDENTIALS=True`
- [ ] La trampa de cookies/CSRF queda escrita en `tasks/api-contract.md`

**Verificación:**
- [ ] Tests: N/A (la Task 23 no lo cubre; se verifica a mano)
- [ ] Arranque: `uv run python manage.py runserver`
- [ ] Manual: `curl -X OPTIONS -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" http://localhost:8000/api/cervezas/`

**Dependencias:** Task 18
**Archivos probables:** `backend/config/settings.py`
**Escala:** S

### Task 20: Handoff del contrato API a Ema

**Descripción:** Escribir y compartir `tasks/api-contract.md`: base URL, login por token, paginación, filtros por endpoint, list vs detail, las dos `@action` y un ejemplo de `fetch` en JavaScript puro. Concepto de Django en juego: ninguno nuevo; es el entregable que evita que Ema adivine la API (y que obliga a congelar el contrato antes de seguir).

**Criterios de aceptación:**
- [ ] `tasks/api-contract.md` completo y alineado con la API real
- [ ] Incluye login por token + ejemplo de `fetch` + manejo de `401`
- [ ] Incluye JSON de ejemplo de `GET /api/pedidos/` (con `lineas`) y `GET /api/pedidos/{id}/` (sin `lineas`)
- [ ] Sección "Qué necesito de tu lado" (CORS, solo token, sin cookies)
- [ ] Ema confirmó la recepción

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: N/A (documento)
- [ ] Manual: ejecutar el snippet de `fetch` contra el backend corriendo

**Dependencias:** Task 19
**Archivos probables:** `tasks/api-contract.md`
**Escala:** S

---

### Checkpoint: Fase 5

- [ ] Preflight CORS verde contra `http://localhost:3000`
- [ ] `api-contract.md` entregado a Ema
- [ ] Trampa cookies/CSRF documentada

---

## Fase 6 — Docker (28-29 oct)

### Task 21: Dockerfile single-stage y compose.yaml

**Descripción:** Escribir el Dockerfile single-stage con uv y el `compose.yaml` con Postgres 17, healthcheck y comando de arranque. Concepto de Django en juego: **punto de entrada WSGI** — el contenedor no usa `runserver` sino `gunicorn config.wsgi:application`, el servidor de producción que carga el `wsgi.py` del proyecto.

**Criterios de aceptación:**
- [ ] Dockerfile single-stage sobre `python:3.13-slim`, copiando `uv`/`uvx` desde `ghcr.io/astral-sh/uv:0.13.1`, sin `--mount=type=cache`
- [ ] `uv sync --frozen --no-install-project --no-dev` y después `uv sync --frozen --no-dev`
- [ ] `compose.yaml` con `db` (postgres:17 + healthcheck `pg_isready`) y `web` (`depends_on: condition: service_healthy`)
- [ ] Comando `web`: `migrate` + `collectstatic --noinput` + `gunicorn`
- [ ] Sin `version:` top-level; volumen `postgres_data` declarado

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: `uv run python manage.py check` (antes de build); `docker compose build` después
- [ ] Manual: revisar el build con `docker compose build` sin errores

**Dependencias:** Task 19
**Archivos probables:** `backend/Dockerfile`, `backend/compose.yaml`
**Escala:** S

### Task 22: Verificación del stack Docker

**Descripción:** Levantar el stack completo con `docker compose up --build` y verificar migraciones, admin con estilos y Swagger dentro del contenedor. Concepto de Django en juego: **migraciones en el arranque** — el `command` del compose corre `migrate` antes de gunicorn, que es como se despliega un Django real.

**Criterios de aceptación:**
- [ ] `docker compose up --build` levanta `db` y `web` sin errores
- [ ] Las migraciones aplican contra Postgres 17
- [ ] `http://localhost:8000/admin/` carga con estilos (collectstatic OK)
- [ ] `http://localhost:8000/api/schema/swagger-ui/` devuelve 200
- [ ] `docker compose down` limpia sin dejar procesos huérfanos

**Verificación:**
- [ ] Tests: `uv run pytest` (sigue en verde en local)
- [ ] Arranque: `docker compose up --build`
- [ ] Manual: admin + Swagger + una llamada autenticada vía el puerto 8000

**Dependencias:** Task 21
**Archivos probables:** `backend/compose.yaml`, `backend/.env.example`
**Escala:** S

---

### Checkpoint: Fase 6

- [ ] Stack Docker completo levanta de cero
- [ ] Admin con estilos dentro del contenedor
- [ ] Swagger responde 200 en el contenedor

---

## Fase 7 — Tests y calidad (29-30 oct)

### Task 23: core/tests.py con los 13 tests

**Descripción:** Escribir el único archivo de tests del proyecto con los 13 tests de la sección 12 del plan: modelos, permisos 401/403, sesión con `force_login`, paginación, nested solo en list, las acciones `@action` y filtros. Concepto de Django en juego: **`APIClient` de DRF + `pytest-django`** — los tests de API simulan requests HTTP reales contra las URLs, que es la forma honesta de verificar que la API hace lo que dice el contrato.

**Criterios de aceptación:**
- [ ] 13 tests en `core/tests.py` (los nombres de la sección 12 del plan)
- [ ] 401 sin token y 200 con token cubiertos
- [ ] `test_sesion_ya_autenticado_devuelve_200`: login con `django.test.Client` (`client.login(...)` o `force_login`) y `GET /api/cervezas/` → 200, mientras el mismo GET sin autenticar → 401
- [ ] `etapas`/`lineas` presentes en list y ausentes en detail
- [ ] `estadisticas` → 403 sin staff, 200 con staff
- [ ] Filtro `?tipo=GRIFO` y búsqueda `?search=ipa` cubiertos

**Verificación:**
- [ ] Tests: `uv run pytest`
- [ ] Arranque: N/A
- [ ] Manual: `uv run pytest -q` sin failures

**Dependencias:** Task 16, Task 17, Task 18
**Archivos probables:** `backend/core/tests.py`
**Escala:** M

### Task 24: Triada de calidad en verde

**Descripción:** Dejar ruff, pytest y migraciones en verde, más la validación del schema. Concepto de Django en juego: **`makemigrations --check`** detecta cambios en los modelos sin migración generada; es el guardia que evita que el entorno local y el contenedor tengan bases de datos distintas.

**Criterios de aceptación:**
- [ ] `uv run ruff check .` sin errores
- [ ] `uv run ruff format .` aplicado
- [ ] `uv run pytest` en verde
- [ ] `uv run python manage.py makemigrations --check --dry-run` limpio
- [ ] `uv run python manage.py spectacular --validate` sin errores

**Verificación:**
- [ ] Tests: `uv run pytest`
- [ ] Arranque: `uv run ruff check . && uv run ruff format --check .`
- [ ] Manual: los 5 comandos en verde

**Dependencias:** Task 23
**Archivos probables:** `backend/pyproject.toml` (config ruff/pytest)
**Escala:** XS

---

### Checkpoint: Fase 7

- [ ] `pytest` verde (13 tests)
- [ ] `ruff check` y `ruff format` limpios
- [ ] `makemigrations --check` limpio
- [ ] `spectacular --validate` limpio

---

## Fase 8 — Cierre y entrega (30/10-2/11)

### Task 25: Seed de datos y credenciales demo

**Descripción:** Crear un management command que inserte datos realistas de la cervecería y el superusuario demo. Concepto de Django en juego: **management command** — un script propio que corre dentro del contexto de Django (`python manage.py seed_datos`) y puede usar los modelos directamente; es la forma correcta de cargar datos de prueba, no tocar la base a mano.

**Criterios de aceptación:**
- [ ] Command `seed_datos` creado
- [ ] Datos coherentes: estilos, cervezas, lotes con etapas, proveedores, materias primas, clientes, pedidos con líneas y opiniones
- [ ] Superusuario demo creado por el command; credenciales anotadas para el README
- [ ] El command avisa si ya hay datos (evita duplicar)

**Verificación:**
- [ ] Tests: `uv run pytest`
- [ ] Arranque: `uv run python manage.py seed_datos`
- [ ] Manual: `GET /api/pedidos/` devuelve pedidos con `lineas`; admin muestra datos

**Dependencias:** Task 24
**Archivos probables:** `backend/core/management/commands/seed_datos.py`
**Escala:** S

### Task 26: Capturas de pantalla

**Descripción:** Tomar capturas del proyecto funcionando con los datos seed y guardarlas en `docs/capturas/`. Concepto de Django en juego: ninguno; es requisito de entrega (requisito 16: README con capturas). Si el frontend de Ema no está listo, se dejan los espacios reservados en el README.

**Criterios de aceptación:**
- [ ] Capturas en `docs/capturas/`: swagger, redoc, browsable-api, admin-filtros, bienvenida, frontend (si está)
- [ ] Imágenes legibles, sin datos sensibles
- [ ] Nombres consistentes (ej. `swagger-ui.png`)
- [ ] Se referencian desde el README

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: backend corriendo con datos seed
- [ ] Manual: abrir cada imagen y confirmar que muestra el proyecto real

**Dependencias:** Task 25, Task 22
**Archivos probables:** `docs/capturas/*.png`
**Escala:** S

### Task 27: README.md final

**Descripción:** Escribir el README raíz siguiendo la estructura de la sección 13 del plan, incluyendo el diagrama ER. Concepto de Django en juego: ninguno nuevo; es el entregable que el docente lee primero y donde vive el requisito 2 (planificación de tablas adjunta).

**Criterios de aceptación:**
- [ ] Portada con nombre, lema y paleta
- [ ] Diagrama ER (mermaid) — requisito literal
- [ ] Instalación con `uv` y con Docker Compose
- [ ] Tabla de endpoints completa (10 + 2 `@action` + auth-token)
- [ ] Capturas embebidas, credenciales demo y comandos útiles
- [ ] Sección de proceso del equipo (ramas, merges, commits)

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: N/A
- [ ] Manual: seguir las instrucciones de instalación en una terminal limpia

**Dependencias:** Task 26
**Archivos probables:** `README.md`
**Escala:** M

### Task 28: Checklist de requisitos y ensayo de defensa

**Descripción:** Recorrer el checklist de los **21 requisitos (R1–R21)** de abajo, hacer el merge final a `main`, publicar el repo en GitHub (Task 31) y ensayar la defensa oral. Concepto de Django en juego: ninguno nuevo; el ensayo cubre DRF, ViewSets, serializers anidados, `@action`, permisos, CORS y por qué una app única.

**Criterios de aceptación:**
- [ ] Checklist de los 21 requisitos (R1–R21) en verde o con justificación explícita; la matriz completa con evidencia vive en `docs/08-trazabilidad-requisitos.md`
- [ ] Última versión en `main` vía merge `--no-ff` de la última feature y repo publicado en GitHub (Task 31)
- [ ] Ensayo de defensa: explicar framework, modelos/relaciones, ViewSets, nested, `@action`, permisos, token vs sesión, CORS y el proceso Git

**Verificación:**
- [ ] Tests: `uv run pytest` en `main`
- [ ] Arranque: `docker compose up --build` en `main`
- [ ] Manual: recorrer el README como si se fuera un docente

**Dependencias:** Task 27
**Archivos probables:** `README.md`, `tasks/plan.md`
**Escala:** S

---

### Checkpoint: Fase 8 / Entrega

- [ ] Datos seed cargados y credenciales demo documentadas
- [ ] Capturas en `docs/capturas/` y embebidas en el README
- [ ] `main` al día con merges `--no-ff`
- [ ] Repositorio de GitHub publicado con `main` al día (Task 31)
- [ ] Checklist de los 21 requisitos (R1–R21) en verde y ensayo de defensa hecho

---

## Fase 9 — Documentación y preparación de la defensa (continua, 19/10 - 2/11)

> Esta fase no es un bloque de días: se ejecuta **en paralelo** con todas las demás. Cada vez que se cierra una tarea, se escribe su nota en `docs/tareas/` (Task 29).

### Task 29: Documentar cada tarea al ejecutarla

**Descripción:** Escribir en `docs/tareas/` la nota de cada tarea del plan al terminarla, usando la plantilla `docs/tareas/_plantilla.md`. Concepto de Django implicado: ninguno; es la documentación de aprendizaje que permite entender el proyecto y defenderlo oralmente. Cada nota queda versionada en el repo, así que el historial de commits cuenta la historia del trabajo.

**Criterios de aceptación:**
- [ ] Existe una nota `docs/tareas/T##-<slug>.md` por cada tarea completada, con el número de tarea y el slug correctos
- [ ] La nota tiene las 7 secciones de la plantilla: qué se hizo, conceptos, archivos, qué mirar en el código, para la defensa, errores y soluciones, verificación
- [ ] La sección "Para la defensa" tiene al menos una pregunta con su respuesta de 2-4 frases
- [ ] La sección "Errores que nos pasaron" registra los errores reales de esa tarea (si no hubo, se escribe "Sin errores")
- [ ] La sección "Verificación" lista los comandos ejecutados con su resultado esperado

**Verificación:**
- [ ] Tests: N/A (es documentación)
- [ ] Arranque: N/A
- [ ] Manual: releer la nota y comprobar que alcanza para explicar la tarea sin mirar el código

**Dependencias:** Task 28
**Archivos probables:** `docs/tareas/T##-<slug>.md`, `docs/tareas/_plantilla.md`
**Escala:** S

---

## Tareas con fecha fija (fuera de fase)

### Task 30: Crear el README.md raíz (esqueleto §13 + diagrama ER)

**Fecha:** 25/10 · **Responsable:** usuario (backend) · **Escala:** S

**Descripción:** Crear el `README.md` raíz con el esqueleto de la sección 13 del plan: portada con la identidad de marca (nombre "Cervecería Los Flacheros", lema "Arte en cada trago, tradición en cada lote", paleta `#F5A623` `#4A7C59` `#8B4513` `#F7F7F7` `#2B2B2B`), objetivo, **diagrama ER en mermaid copiado de `tasks/plan.md` §7**, stack, instalación, tabla de endpoints, sección de capturas con placeholders, credenciales de prueba, comandos útiles, proceso del equipo y autores. Es el esqueleto que la Task 27 completa en la Fase 8 (capturas reales, credenciales exactas y cierre de texto); se crea temprano para que el requisito "planificación de tablas adjunta al README" exista en el repo desde la primera semana.

**Criterios de aceptación:**
- [ ] `README.md` raíz creado con la portada de marca (nombre, lema y paleta)
- [ ] Diagrama ER (mermaid) copiado de `tasks/plan.md` §7 y renderizado
- [ ] Secciones de la §13 presentes: objetivo, stack, instalación, tabla de endpoints, capturas (placeholders), credenciales (placeholders), comandos útiles, proceso del equipo y autores
- [ ] Marcadores claros de lo que se completa en la Task 27

**Verificación:**
- [ ] Tests: N/A (documento)
- [ ] Arranque: N/A
- [ ] Manual: abrir el README en el repo y ver el diagrama ER renderizado

**Dependencias:** Task 3
**Archivos probables:** `README.md`
**Escala:** S

### Task 31: Publicar el proyecto en GitHub y dejar main al día

**Fecha:** 1/11 · **Responsable:** el usuario (crea la cuenta y el repo si hace falta) · **Escala:** S

**Descripción:** Publicar el proyecto en un repositorio remoto de GitHub (privado o público, a decisión del equipo) con la última versión de `main`, y subir cada rama `feature/*` como **pull request** hacia `main` (el docente pide "pull requests" explícitamente). Es el requisito de entrega R19/R18 de `docs/08-trazabilidad-requisitos.md`.

Pasos concretos:
1. Crear el repo en GitHub (cuenta del usuario; `gh repo create` o desde la web).
2. `git remote add origin <url-del-repo>`
3. `git push -u origin main`
4. Por cada rama `feature/*` viva: `git push -u origin feature/<tarea>` y abrir un pull request hacia `main`; cerrarlo con merge (merge commit, no squash, para conservar la historia).

**Criterios de aceptación:**
- [ ] Repo remoto creado y `origin` configurado (`git remote -v`)
- [ ] `git push -u origin main` hecho; el `main` del remoto igual al local (`git log` coincide)
- [ ] Cada rama `feature/*` publicada como pull request hacia `main`
- [ ] La URL del repo queda registrada (en el README o en la nota de tarea) para el docente
- [ ] Sin secretos en el remoto (el `.env` nunca se pushea)

**Verificación:**
- [ ] Tests: N/A
- [ ] Arranque: N/A
- [ ] Manual: abrir el repo en GitHub y confirmar `main` al día y los PRs cerrados

**Dependencias:** Task 28 (merge final a `main`)
**Archivos probables:** — (solo git/GitHub) + `README.md` (URL del repo)
**Escala:** S

---

## Checklist contra requisitos del docente

La matriz completa (**R1–R21**, con evidencia detallada y estado) vive en [`docs/08-trazabilidad-requisitos.md`](../docs/08-trazabilidad-requisitos.md). Este es el checklist accionable de la entrega (se recorre en la Task 28):

- [ ] **R1** ≥10 modelos con relaciones — Tasks 7–11 (10 modelos en `core/models.py`)
- [ ] **R2** Modelos relevantes para la temática de la cervecería — Tasks 7–11
- [ ] **R3** Relaciones entre modelos (`on_delete` según el negocio) — Tasks 7–10
- [ ] **R4** Planificación de tablas adjunta al README (diagrama ER) — Task 30 (esqueleto) y Task 27 (cierre)
- [ ] **R5** API REST para el frontend (DRF + router en `/api/`) — Tasks 4, 14, 15
- [ ] **R6** ≥8 de los 10 modelos con endpoint vía ViewSet — Task 15 (los 10)
- [ ] **R7** ≥2 ViewSets con datos anidados SOLO en `list` — Task 16 (Lote y Pedido)
- [ ] **R8** Autenticación por sesión y por token — Tasks 4 y 6 (token + `/api-auth/`)
- [ ] **R9** ≥2 funciones personalizadas con `@action` — Tasks 17 y 18 (`en_grifo`, `estadisticas`, `avanzar`)
- [ ] **R10** Endpoints de get all paginados — Tasks 4 y 15 (`DefaultPagination`, tope 50)
- [ ] **R11** ≥1 ViewSet con filtros y búsquedas — Task 18 (Cerveza completo + el resto)
- [ ] **R12** Documentación OpenAPI/Swagger/ReDoc + API navegable — Task 6
- [ ] **R13** Vista principal con template de bienvenida — Task 5
- [ ] **R14** Panel de admin con filtros, ordenamiento y búsqueda (control total en los 10 modelos) — Tasks 12 y 13
- [ ] **R15** uv como gestor de entornos — Tasks 1 y 2
- [ ] **R16** CORS configurado para el frontend — Tasks 4 y 19
- [ ] **R17** Proyecto dockerizado — Tasks 21 y 22
- [ ] **R18** Proceso Git: ramas `feature/*`, pull requests y commits descriptivos — Tasks 3, 28 y 31
- [ ] **R19** Repositorio de GitHub publicado con `main` al día — Task 31
- [ ] **R20** `README.md` con diagrama ER y capturas — Tasks 26, 27 y 28 (esqueleto en Task 30)
- [ ] **R21** Entrega el lunes 2/11; defensa el martes 3/11 — Task 28 (cierre) y Task 31
