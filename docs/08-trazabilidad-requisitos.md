# 08 — Matriz de trazabilidad de requisitos (EFI)

Matriz formal que cruza cada requisito del docente con la respuesta concreta del proyecto: qué modelo, endpoint, archivo o tarea lo cumple, dónde está documentado y en qué estado está. Sirve para dos cosas: que el equipo la use como guion en la defensa oral (sección de evidencia) y que el docente verifique de un vistazo que no falta nada (tabla matriz + checklist final).

**Convención de estados** (verificados contra el repo el 19/10/2026): ✅ Implementado = el código o archivo existe y está commiteado · ⏳ Planificado (Task N) = el diseño está definido en `tasks/plan.md` pero **el código todavía no se escribió**; la Task N de `tasks/todo.md` es la que lo va a producir · ⏳ Pendiente = falta ejecutar la tarea y/o una acción externa al plan. A fin del 19/10/2026 están completas la Fase 0 (Tasks 1–3), las Tasks 4–6 (proyecto, settings, bienvenida, documentación) y las Tasks 7–11 (los 10 modelos con sus migraciones). Todavía no hay ViewSets, ni admin configurado, ni Docker.

## Tabla matriz principal

| N° | Requisito del docente | Cómo lo cumple el proyecto | Dónde se documenta | Estado |
|---|---|---|---|---|
| R1 | Al menos 10 modelos en la base de datos | 10 modelos en `backend/core/models.py`: `Estilo`, `Cerveza`, `Lote`, `EtapaFermentacion`, `Proveedor`, `MateriaPrima`, `Cliente`, `Pedido`, `LineaPedido`, `Opinion` | `tasks/plan.md` §7 (Modelo de datos) + `docs/04-nuestro-modelo.md` | ✅ Implementado (Tasks 7–10) — 10 modelos en `backend/core/models.py` |
| R2 | Los modelos deben ser relevantes para la temática elegida | Dominio completo de una cervecería artesanal: catálogos de estilos y cervezas, producción (lotes y etapas de fermentación), insumos (proveedores y materias primas) y ventas/opiniones (clientes, pedidos, líneas, opiniones) | `tasks/plan.md` §7 + `docs/04-nuestro-modelo.md` | ✅ Implementado (Tasks 7–10) |
| R3 | Deben existir relaciones entre los modelos | 8 relaciones FK con `related_name` y reglas `on_delete` según el negocio: PROTECT (histórico: `Cerveza.estilo`, `Lote.cerveza`, `Pedido.cliente`, `LineaPedido.cerveza`), CASCADE (dependientes: `EtapaFermentacion.lote`, `LineaPedido.pedido`, `Opinion.*`), SET_NULL (opcionales: `Lote.usuario`, `MateriaPrima.proveedor`) | `tasks/plan.md` §7 (tabla de relaciones + justificación de `on_delete`) + `docs/01-django-esencial.md` §5 | ✅ Implementado (Tasks 7–10) — 8 FK con related_name y on_delete según el negocio |
| R4 | Planificación de las tablas y relaciones antes de desarrollar, adjunta al README.md (diagrama o escrito) | Diagrama ER en Mermaid ya diseñado en el plan, con el orden de migraciones por dependencia; se pega en el README raíz como criterio de aceptación obligatorio de la Task 27 | `tasks/plan.md` §7 (Diagrama ER); destino final: `README.md` raíz | ⏳ Planificado (Task 27) — el diseño existe en el plan, falta embeberlo en el README |
| R5 | El proyecto Django debe habilitar una API REST para comunicarse con un frontend | Backend Django 5.2 + DRF 3.17 con `ModelViewSet` por recurso, `DefaultRouter` montado en `/api/`, renderers JSON + Browsable API y settings completos (Task 4) | `tasks/plan.md` §8 (Contrato de API) + `docs/02-drf-esencial.md` | ⏳ Planificado (Tasks 4, 14, 15) |
| R6 | Al menos 8 de los 10 modelos con endpoint mediante un ViewSet (CRUD o solo lectura) | Los **10** modelos (el mínimo pedido, con holgura) con `ModelViewSet` y CRUD completo: `/api/estilos/`, `/api/cervezas/`, `/api/lotes/`, `/api/etapas/`, `/api/proveedores/`, `/api/materias-primas/`, `/api/clientes/`, `/api/pedidos/`, `/api/lineas/`, `/api/opiniones/` en `backend/core/views.py` + `core/urls.py` | `tasks/plan.md` §8 (tabla de endpoints) + `tasks/api-contract.md` (tabla de endpoints) | ⏳ Planificado (Tasks 14–15) |
| R7 | Como mínimo 2 de los ViewSets CRUD deben mostrar datos anidados sólo en list, usando NestedSerializers | `LoteViewSet` (`LoteNestedSerializer` con `etapas` + `cerveza_nombre`) y `PedidoViewSet` (`PedidoNestedSerializer` con `lineas` + `cliente_nombre`); `get_serializer_class()` devuelve el nested únicamente cuando `self.action == "list"`, el detalle y las escrituras usan el serializer plano | `tasks/plan.md` §8 (sección "Nested serializers") + `tasks/api-contract.md` ("List vs detail") + `docs/02-drf-esencial.md` | ⏳ Planificado (Task 16) |
| R8 | Los endpoints deben estar protegidos con autenticación de Sesión y por Tokens | `DEFAULT_AUTHENTICATION_CLASSES` con `TokenAuthentication` + `SessionAuthentication` en `config/settings.py`; emisión de tokens en `POST /api/auth-token/` (`rest_framework.authtoken`); login de sesión para la Browsable API en `/api-auth/` (`rest_framework.urls`); permiso global `IsAuthenticated` para lectura (401 sin token en todos los endpoints) e `IsAdminUser` para la escritura, excepto `Pedido` y `LineaPedido` (el mostrador) | `tasks/plan.md` §8–9 + `tasks/api-contract.md` (sección "Autenticación") + `docs/03-http-json-cors.md` (token vs sesión) | ✅ Implementado (Tasks 4 y 6) |
| R9 | Al menos 2 funciones personalizadas en el viewset usando `@action` | `GET /api/cervezas/en_grifo/` (`CervezaViewSet`, `detail=False`: cervezas GRIFO, activas, con stock) y `GET /api/pedidos/estadisticas/` (`PedidoViewSet`, `IsAdminUser`, agregados con `Count`/`Sum`/`annotate`, con `allow_null=True` en `monto_total` y `promedio_ticket`); más un tercer action **comprometido**: `POST /api/lotes/{id}/avanzar/` (`LoteViewSet`, `detail=True`, `IsAdminUser`, valida la transición de estado) | `tasks/plan.md` §8 (sección "Endpoints `@action`") + `tasks/api-contract.md` (sección "`@action`") | ⏳ Planificado (Tasks 17–18) |
| R10 | Los endpoints de get all deben traer datos paginados | Paginación global con la clase propia `DefaultPagination` (`PageNumberPagination` en `config/settings.py`): `page_size=10`, `page_size_query_param="page_size"` y `max_page_size=50`; todas las respuestas de listado traen `count`/`next`/`previous`/`results` | `tasks/plan.md` §9 (settings + clase `DefaultPagination`) + `tasks/api-contract.md` (sección "Paginación") | ✅ Implementado (Task 4) |
| R11 | Por lo menos 1 viewset debe permitir filtros y búsquedas | Se cumple con creces: `CervezaViewSet` tiene filtros `?estilo=`, `?tipo=`, `?activo=` (django-filter), búsqueda `?search=` y orden `?ordering=`; el resto de los 10 ViewSets también lleva search u ordering según la tabla del contrato | `tasks/plan.md` §8 (tabla de filtros) + `tasks/api-contract.md` (sección "Filtros, búsqueda y orden por endpoint") | ⏳ Planificado (Task 18) |
| R12 | Endpoints de documentación de API (openapi, swagger y/or redoc) + API navegable habilitada | drf-spectacular: `/api/schema/` (OpenAPI 3), `/api/schema/swagger-ui/`, `/api/schema/redoc/` en `config/urls.py`; la API navegable es la Browsable API de DRF en `/api/` (`BrowsableAPIRenderer`) | `tasks/plan.md` §8 (tabla "URLs de documentación, token y panel") + `docs/02-drf-esencial.md` | ✅ Implementado (Task 6) |
| R13 | Vista principal que renderice un template de bienvenida | `TemplateView` en `/` que renderiza `backend/templates/bienvenida.html` con la identidad de marca (paleta y lema) | `tasks/plan.md` §4 (identidad) y §6 (archivos) + `docs/01-django-esencial.md` §9 | ✅ Implementado (Task 5) |
| R14 | Control total con el panel de administración; modelos relevantes con filtros, ordenamiento y búsqueda desde el panel | Los 10 modelos registrados en `backend/core/admin.py` con `list_display`, `list_filter` (en los 10 modelos: costo cero, "control total" pedido), `search_fields` con joins (ej. `cerveza__nombre`, `cliente__nombre`) y `ordering`; más `EtapaFermentacionInline` en Lote y `LineaPedidoInline` en Pedido | `tasks/plan.md` §6 (fila `admin.py`) + `docs/01-django-esencial.md` §8 | ⏳ Planificado (Tasks 12–13) |
| R15 | Usar uv como gestor de entornos virtuales | `uv` 0.13.1 instalado e integrado: `uv init` en `backend/`, `[tool.uv] package = false`, `uv.lock` commiteado (30 paquetes), `.python-version` con 3.13, todo el workflow del proyecto pasa por `uv run` | `tasks/plan.md` §5 (stack) + `docs/05-stack-y-entorno.md` + notas `docs/tareas/T01-instalar-uv-docker.md` y `T02-estructura-y-dependencias.md` | ✅ Implementado (Tasks 1–2) |
| R16 | Configurar CORS para permitir la conexión hacia un frontend | `django-cors-headers` 4.9.0 ya instalado (uv.lock); la configuración (`CorsMiddleware` primero en `MIDDLEWARE`, `CORS_ALLOWED_ORIGINS=["http://localhost:3000"]`) va en los settings de la Task 4 y se cierra y verifica el preflight en la Task 19 | `tasks/plan.md` §9 (settings) y §8 (apéndice CORS) + `tasks/api-contract.md` ("Qué necesito de tu lado") + `docs/03-http-json-cors.md` | ✅ Implementado (Task 4) |
| R17 | El proyecto de Django debe estar dockerizado | `backend/Dockerfile` single-stage sobre `python:3.13-slim` con `uv sync --frozen` y `gunicorn config.wsgi:application`; `backend/compose.yaml` con servicios `db` (postgres:17 + healthcheck) y `web` (`migrate` + `collectstatic` + gunicorn) | `tasks/plan.md` §10 (Docker) + `docs/05-stack-y-entorno.md` | ⏳ Planificado (Tasks 21–22) — Docker Desktop instalado en la Task 1; falta escribir el Dockerfile y el compose |
| R18 | Buen trabajo organizacional con Git (ramas, pull requests, commits descriptivos) | Repo git local en la raíz con `main` como rama por defecto y primer commit convencional ya hecho; convención definida: ramas `feature/<tarea>`, un commit chico por tarea en Conventional Commits en español, merges a `main` con `--no-ff` y publicación de cada `feature/*` como **pull request** hacia `main` en el repo de GitHub (Task 31) | `tasks/plan.md` §11 (Git local + remoto) + `docs/tareas/T03-git-local.md` | ⏳ Parcial: Task 3 ✅ (init + primer commit); las ramas, PRs y merges se generan con cada feature (Tasks 7–28, publicación en 31) |
| R19 | Entrega a través de un repositorio de Github con la última versión en main/master | El proceso Git del plan produce la historia limpia en `main` y la publicación está planificada: repo remoto en GitHub, `git remote add origin`, `git push -u origin main` y un PR por cada `feature/*`; se verifica abriendo el remoto | `tasks/plan.md` §11 (Git local + remoto) + Task 31 de `tasks/todo.md` | ⏳ Planificado (Task 31 — 1/11) |
| R20 | README.md trabajado con capturas del proyecto en funcionamiento | README raíz con portada de marca, diagrama ER, stack, instalación (uv y Docker), tabla de endpoints, credenciales demo, comandos útiles, proceso Git y capturas embebidas de `docs/capturas/` (Swagger, ReDoc, Browsable API, admin con filtros, bienvenida, frontend si está) | `tasks/plan.md` §13 (estructura del README) + Tasks 26–27 | ⏳ Planificado (Tasks 26–27) |
| R21 | Fecha límite: lunes 2 de noviembre (2026); defensas desde el martes 3 de noviembre | Cronograma con hitos por fase hasta el cierre (Fase 8: Tasks 25–28, 30/10–2/11): seed + capturas + README + checklist y ensayo de defensa antes de la entrega | `tasks/plan.md` §14 (Cronograma) + `docs/07-plan-de-aprendizaje.md` | ⏳ Hito de calendario — Task 28 cierra la entrega el 2/11 |

## Requisitos que exceden lo pedido

El docente pide un mínimo; el plan va más allá en cinco puntos, siempre con justificación y sin desviarse del alcance:

1. **10 ViewSets en vez de los 8 pedidos (R6).** Los 10 modelos tienen endpoint con CRUD completo: como el router de DRF deriva las URLs desde los ViewSets, exponer los dos que sobran (líneas y opiniones) cuesta lo mismo que exponer los otros ocho y deja el modelo entero navegable desde la API.
2. **Tests automatizados (13 con pytest-django).** El docente no los pide, pero son la única forma honesta de verificar permisos (401/403), nesting solo-en-list, paginación y filtros sin depender de la demo manual; viven en un solo archivo `core/tests.py` (Task 23, incluido el test de sesión ya autenticada → 200) y corren en la triada de calidad con ruff y `makemigrations --check` (Task 24).
3. **Documentación de estudio en `docs/`.** Siete guías conceptuales con ejemplos de ESTE proyecto, un cuaderno de defensa oral con 30+ preguntas y una nota de tarea por cada tarea ejecutada (Task 29). No es un requisito de la consigna: es lo que permite que dos principiantes entiendan y defiendan lo que escribieron.
4. **`tasks/api-contract.md` como contrato congelado para el frontend.** Handoff con base URL, login por token, paginación, filtros por endpoint, ejemplos de JSON list-vs-detail y un cliente `fetch` en JavaScript puro (Task 20). Evita que el frontend de Ema adivine la API y obliga a congelar el contrato antes de seguir.
5. **whitenoise + gunicorn dentro de Docker.** El contenedor no corre `runserver`: corre el servidor WSGI de producción (`gunicorn config.wsgi:application`) y sirve sus static files con whitenoise, sin nginx (Tasks 5 y 21). Es más allá de "que esté dockerizado" y muestra criterio de despliegue real.

## Cómo lo demuestra el equipo

Evidencia concreta por requisito, para la defensa oral o para las capturas:

| N° | Evidencia que se muestra |
|---|---|
| R1 | Se abre `core/models.py` y se cuentan las 10 clases; en el shell se listan con `python manage.py shell -c "from django.apps import apps; print(len(apps.get_models()))"`. |
| R2 | Se recorre el flujo real del negocio en una frase: "un estilo clasifica cervezas, una cerveza se produce en lotes, un lote tiene etapas de fermentación, un cliente hace pedidos con líneas y escribe opiniones". |
| R3 | Se muestra el diagrama ER y se responde "¿qué pasa si borro esta cerveza?": PROTECT porque ya se produjo o vendió (se demostró con un intento de borrado bloqueado). |
| R4 | Se muestra el diagrama ER embebido en el README raíz (idéntico al de `tasks/plan.md` §7). |
| R5 | Se abre `http://localhost:8000/api/` y se ven los 10 endpoints respondiendo JSON. |
| R6 | Se muestra el índice de `/api/` (o Swagger) con los 10 prefijos del router y se hace un POST/GET/PUT/DELETE de punta a punta en un recurso. |
| R7 | Se comparan en vivo dos respuestas: `GET /api/pedidos/` con el array `lineas` y `GET /api/pedidos/1/` sin `lineas` (lo mismo con `lotes/` y `etapas`). |
| R8 | Se pide un GET sin token → 401 (en cualquier endpoint, incluso de lectura); se hace `POST /api/auth-token/` con las credenciales demo y se repite con `Authorization: Token <key>` → 200; en el Browsable API se loguea por sesión con el botón de `/api-auth/`. |
| R9 | Se muestran en Swagger las 3 acciones custom y se ejecutan `GET /api/cervezas/en_grifo/`, `GET /api/pedidos/estadisticas/` (esta última con usuario sin staff → 403) y `POST /api/lotes/{id}/avanzar/` (con un lote en un estado de prueba). |
| R10 | Se muestra el JSON de `GET /api/cervezas/` con `count`, `next`, `previous`, `results` y se navega `?page=2&page_size=50`. |
| R11 | Se corre en vivo `GET /api/cervezas/?tipo=GRIFO&search=ipa&ordering=-fecha_creacion` y se ve el resultado filtrado. |
| R12 | Se abre Swagger UI (`/api/schema/swagger-ui/`), ReDoc (`/api/schema/redoc/`) y la API navegable (`/api/`), con las 10 rutas y las 3 acciones documentadas. |
| R13 | Se abre `http://localhost:8000/` y se ve la bienvenida con la paleta y el lema de la cervecería. |
| R14 | Se muestra el admin de Lotes con `list_filter` por estado y búsqueda por número, y un Pedido con sus líneas editadas inline en la misma pantalla. |
| R15 | Se muestra `uv --version`, el `pyproject.toml` con `[tool.uv] package = false` y se arranca la app con `uv run python manage.py runserver`. |
| R16 | Se muestra el `curl -X OPTIONS` con `Origin: http://localhost:3000` devolviendo `Access-Control-Allow-Origin`, más la línea de settings correspondiente. |
| R17 | Se levanta de cero con `docker compose up --build` y se entra al admin con estilos y a Swagger dentro del contenedor. |
| R18 | Se muestra `git log --graph` con ramas `feature/*` y merges `--no-ff` a `main`, y se abre un commit para ver su mensaje convencional descriptivo. |
| R19 | Se muestra el repo en GitHub con `main` como rama por defecto y el último commit de la rama main igual al del `git log` local. |
| R20 | Se recorre el README como lo haría el docente: diagrama ER, tabla de endpoints y capturas clicables del proyecto funcionando con datos seed. |
| R21 | En la defensa (3/11) se cita el cronograma cumplido: 31 tareas, checkpoints por fase y entrega del 2/11. |

## Riesgos de cumplimiento

| # | Riesgo | Probabilidad / Impacto | Mitigación ya en el plan |
|---|---|---|---|
| 1 | El calendario es apretado: 31 tasks en 14 días y dos principiantes | Alta / Alto | Cronograma por fases con checkpoint al cierre de cada una (`tasks/plan.md` §14); el README no arranca de cero: la Task 30 (25/10) crea el esqueleto con el diagrama ER y la Task 27 (30/10) lo completa, con las capturas (Task 26) antes y mínimo vital si falta tiempo (Swagger, admin y bienvenida). |
| 2 | Docker no levanta por WSL2 faltante y la Fase 6 se trabaja | Media / Alto | `tasks/plan.md` §15: ejecutar `wsl --install` como administrador y reiniciar (Task 1); mientras tanto el desarrollo sigue en local con SQLite (ya elegido en T02) y el entregable dockerizado (`Dockerfile` + `compose.yaml`) no depende de que el motor funcione en la máquina de desarrollo. |
| 3 | R19: la publicación a GitHub se descuida y se llega sin remoto publicado | Media / Alto | La publicación quedó incorporada al plan como **Task 31 (1/11)**: repo remoto, `git push -u origin main` y un pull request por cada `feature/*`. Se verifica abriendo el repo en GitHub antes de dar por entregado (checklist final). **No dar la entrega por hecha sin abrir el repo en GitHub con `main` al día.** |
| 4 | El frontend de Ema no llega a tiempo y no hay demo integral | Media / Medio | `tasks/plan.md` §15: el backend es autónomo (no depende del frontend) y el docente evalúa backend y proceso; el contrato se congela en la Task 20 para no bloquear a Ema. En las capturas se dejan espacios reservados si el front no está (Task 26). |
| 5 | Quedarse sin tiempo para las capturas (R20) | Media / Medio | `tasks/plan.md` §15: la Task 26 va después del seed (Task 25) y antes del README (Task 27); si falta tiempo se captura lo mínimo: Swagger, admin con filtros y vista de bienvenida. |
| 6 | incompatibilidad drf-spectacular con DRF 3.18 (soporte declarado hasta 3.17) | Baja / Medio | Ya mitigado de entrada: el `uv.lock` de la Task 2 fijó DRF 3.17.2; queda el fallback documentado en `tasks/plan.md` §15 (probar 3.18.3 validando siempre con `uv run python manage.py spectacular --validate`). |

## Checklist final de entrega (Fase 8 — Task 28)

El equipo lo recorre el domingo 1/11 y el lunes 2/11 antes de dar por entregado:

**Documentación y repo**
- [ ] `README.md` raíz con el **diagrama ER** (Mermaid) embebido
- [ ] `README.md` con **capturas del proyecto funcionando** en `docs/capturas/` embebidas
- [ ] `README.md` con stack, instalación (uv y Docker), tabla de endpoints, credenciales demo y comandos útiles
- [ ] Una nota en `docs/tareas/` por cada tarea completada (Task 29)
- [ ] **`main` al día**: último merge `--no-ff` hecho y `git status` limpio
- [ ] **Repositorio de GitHub publicado con `main` al día** (Task 31: `git remote add origin`, `git push -u origin main` y un pull request cerrado por cada `feature/*`)

**Entorno e infraestructura**
- [ ] **`uv` como gestor**: el proyecto se instala y corre con `uv sync` / `uv run` desde `uv.lock`
- [ ] **CORS** configurado: `CorsMiddleware` primero y `CORS_ALLOWED_ORIGINS` con `http://localhost:3000` (preflight devolviendo `Access-Control-Allow-Origin`)
- [ ] **Dockerfile + compose.yaml** presentes y verificados: `docker compose up --build` levanta `db` y `web` de cero

**API**
- [ ] **≥10 modelos** en `core/models.py` con sus relaciones y migraciones aplicadas (`makemigrations --check` limpio)
- [ ] **≥8 ViewSets** con endpoint (el proyecto tiene los 10) respondiendo en `/api/`
- [ ] **2 ViewSets con nested SOLO en list**: `etapas` en `GET /api/lotes/` y `lineas` en `GET /api/pedidos/`, ausentes en los detalles
- [ ] **3 `@action`**: `/api/cervezas/en_grifo/`, `/api/pedidos/estadisticas/` y `/api/lotes/{id}/avanzar/` (las dos últimas con permiso admin)
- [ ] **Paginación** en todos los GET de listado (`count`/`next`/`previous`/`results`, `page_size` tope 50)
- [ ] **Sesión + token**: `POST /api/auth-token/` emite token; `Authorization: Token` y login por sesión (`/api-auth/`) funcionan
- [ ] **Swagger + ReDoc + API navegable**: `/api/schema/swagger-ui/`, `/api/schema/redoc/` y `/api/` responden

**Vistas, admin y proceso**
- [ ] **Vista de bienvenida** renderizando el template con la identidad de marca en `/`
- [ ] **Panel admin** con los 10 modelos, filtros, ordenamiento, búsqueda e inlines (Lote y Pedido)
- [ ] **Proceso Git visible**: `git log --graph` con ramas `feature/*` y merges a `main`
- [ ] **Triada de calidad en verde**: `uv run pytest`, `uv run ruff check .` y `makemigrations --check --dry-run`
- [ ] **Entrega en repo GitHub con la última versión en `main`** (Task 31; verificado abriendo el remoto, no solo el local)
- [ ] **Ensayo de defensa** hecho: framework, modelos/relaciones, ViewSets, nested, `@action`, permisos, token vs sesión, CORS y proceso Git
- [ ] **Fecha**: entrega el **lunes 2/11**; defensa el **martes 3/11**
