# T04 — Proyecto Django `config`, app `core` y settings completos

**Fase:** 1
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Creamos el proyecto Django (el paquete `config/` con `settings.py`, `urls.py`, `wsgi.py` y `asgi.py`) y la app `core/`, que es la única app del dominio de la cervecería y va a concentrar modelos, serializers, ViewSets, admin y tests. La parte importante de esta tarea no fue el `startproject`, que es un esqueleto automático, sino escribir los `settings.py` completos: DRF con autenticación por token y por sesión, permiso global `IsAuthenticated`, paginación, filter backends, la schema class que conecta DRF con drf-spectacular y los renderers (JSON + Browsable API); drf-spectacular con su `SPECTACULAR_SETTINGS`; django-filter; `corsheaders` con `CorsMiddleware` primero en el `MIDDLEWARE`; `django-environ` para leer todo lo sensible o por-entorno del `.env`; whitenoise para servir los estáticos dentro del contenedor; y `DATABASES` con `DATABASE_URL` (SQLite en local, PostgreSQL cuando levante Docker).

También quedó definida la clase propia `DefaultPagination` (10 por página, `page_size` consultable hasta 50) como `DEFAULT_PAGINATION_CLASS`. La paginación vive en una clase propia y no en un `PAGE_SIZE` suelto: queda en un solo lugar y no se pisan los dos valores.

## Conceptos que aparecen acá
- **Proyecto vs. app en Django** — el *proyecto* (`config/`) es el contenedor de la configuración: settings, URLs raíz, puntos de entrada WSGI/ASGI. Una *app* (`core/`) es un módulo del negocio que se puede (en teoría) mover a otro proyecto; Django los separa para que la configuración quede en un lugar y el dominio en otro. En este proyecto hay una sola app a propósito: no somos una plataforma multi-app.
- **`INSTALLED_APPS`** — lista de apps y paquetes que Django carga. Van las de `django.contrib` (admin, auth, sesiones, staticfiles, contenttypes), las de la API (`rest_framework`, `rest_framework.authtoken`, `drf_spectacular`, `django_filters`, `corsheaders`) y `core`. Sin declarar una app acá, Django no le lee sus modelos, sus migraciones ni su admin.
- **Bloques de `settings.py`** — cada sección resuelve una decisión: `MIDDLEWARE` (cadena de plugins por la que pasa cada request/response), `TEMPLATES` (dónde buscar templates y con qué context processors), `DATABASES` (qué base), `REST_FRAMEWORK` (defaults globales de la API) y `STORAGES` (cómo se guardan y sirven los archivos estáticos y de media).
- **`django-environ`** — librería que lee variables de entorno y las tipa (`env.bool`, `env.list`, `env.db`). La usamos en vez de parsear el `.env` a mano porque ya trae los conversores y las validaciones: si `DEBUG` viene mal escrito o falta `DATABASE_URL`, explota en el arranque con un mensaje claro.
- **`CorsMiddleware` primero** — el middleware es una pila y el orden es el orden de ejecución. El navegador manda el preflight `OPTIONS` y la respuesta con `Access-Control-Allow-Origin` tiene que salir antes de que cualquier otro middleware decida algo; por eso `CorsMiddleware` va primero de todos.
- **Renderers de DRF** — el renderer decide en qué formato se empaqueta la respuesta. `JSONRenderer` para las máquinas (el frontend) y `BrowsableAPIRenderer` para los humanos: es la API navegable que DRF sirve en HTML en cada endpoint, que es lo que pide el requisito de "API navegable habilitada".
- **`DEFAULT_SCHEMA_CLASS`** — es literalmente el cable que conecta DRF con drf-spectacular: le dice a DRF qué clase usar cuando alguien le pida el esquema de una vista. DRF trae la suya; drf-spectacular reemplaza ese default con `drf_spectacular.openapi.AutoSchema`, y todas las vistas quedan documentables. Si este valor no llega a aplicarse, `/api/schema/` revienta (lo vivimos en carne propia: sección de errores).
- **`DEFAULT_AUTO_FIELD`** — qué tipo de campo primario usa Django para los modelos que declaremos sin clave explícita. `BigAutoField` (entero grande) es el default moderno; fijarlo ahora evita los warnings de Django 3.2+ y la sorpresa de que aparezcan `id` chiquitos en los modelos nuevos.
- **whitenoise** — middleware que sirve los archivos estáticos desde el propio proceso de Python, sin nginx. En Docker nos ahorra un servicio entero: `collectstatic` junta los estáticos en `staticfiles/` y whitenoise los sirve (con compresión y caché) desde ahí.
- **`DATABASE_URL`** — una sola variable con toda la conexión a la base (`sqlite:///db.sqlite3` en local, `postgres://...` en el compose). `env.db()` la parsea a la configuración de Django; el mismo código corre contra SQLite o PostgreSQL según el entorno, sin tocar el archivo.

## Archivos
- `backend/manage.py` — script de consola: ejecuta comandos de Django (`check`, `migrate`, `runserver`, `spectacular`).
- `backend/config/settings.py` — todos los ajustes del proyecto, con el `.env` leído por django-environ; incluye `DefaultPagination`.
- `backend/config/urls.py` / `wsgi.py` / `asgi.py` — mapa de URLs raíz y puntos de entrada del servidor.
- `backend/core/` — app del dominio: `models.py` (todavía sin modelos, es Fase 2), `admin.py`, `apps.py`, `views.py`, `urls.py`, `tests.py`.
- `backend/.env` (no commiteado) y `backend/.env.example` (plantilla) — secretos y configuración por entorno.

## Lo que hay que mirar en el código
- `backend/config/settings.py::REST_FRAMEWORK` — el bloque que define toda la política de la API: autenticación (token + sesión), permiso global, paginación, filtros, schema class y renderers.
- `backend/config/settings.py::DefaultPagination` — la clase de paginación global (`page_size=10`, `page_size_query_param="page_size"`, `max_page_size=50`).
- `backend/config/settings.py::MIDDLEWARE` — el comentario "CorsMiddleware SIEMPRE primero" y su posición #1 de la lista.
- `backend/config/settings.py` (final del archivo) — el import de `PageNumberPagination` está DESPUÉS de `REST_FRAMEWORK`, con el comentario que explica por qué el orden importa (errores de abajo).
- `backend/config/settings.py::DATABASES` y `CORS_ALLOWED_ORIGINS` — ambos leídos del `.env` con valores por defecto locales.

## Para la defensa
> **Pregunta:** ¿Por qué configurás CORS en el backend y no en el frontend?
> **Respuesta:** Porque CORS es una cabecera que **emite el servidor**. El navegador del frontend recibe la respuesta y es el que chequea el header `Access-Control-Allow-Origin`; el backend tiene que decir explícitamente qué orígenes puede llamar (en nuestro caso `http://localhost:3000`). Del lado del frontend no se puede configurar: un fetch cross-origin no tiene forma de agregarse sus propias cabeceras de autorización del navegador.

> **Pregunta:** ¿Por qué leés la configuración del `.env` en vez de escribirla en el código?
> **Respuesta:** Para no commitear secretos (`SECRET_KEY`, credenciales de la base) y para poder cambiar el comportamiento por entorno sin tocar el código: el mismo `settings.py` corre en local con SQLite, en Docker con PostgreSQL y en producción con otros orígenes de CORS, solo cambiando el `.env` de cada máquina. El `.env.example` documenta qué variables hacen falta sin valores reales.

## Errores que nos pasaron y cómo los resolvimos
- **Error:** `AssertionError: Incompatible AutoSchema used on View <class 'rest_framework.authtoken.views.ObtainAuthToken'>. Is DRF's DEFAULT_SCHEMA_CLASS pointing to "drf_spectacular.openapi.AutoSchema"...` al abrir `/api/schema/` (500).
  **Causa:** drf-spectacular, al recorrer las URLs para armar el schema, exige que cada vista tenga un `schema` que sea **instancia** de su `AutoSchema` (`isinstance(view.schema, AutoSchema)`). DRF entrega el schema de cada vista por un descriptor (`DefaultSchema`) que instancia `DEFAULT_SCHEMA_CLASS` en cada acceso. Tres cosas pudieron fallar acá y una nos comió un buen rato: (1) en DRF anterior a 3.12, `ObtainAuthToken` inyectaba su propio `AutoSchema` de DRF y no respetaba `DEFAULT_SCHEMA_CLASS` (bug reportado y citado por la propia doc de drf-spectacular); con DRF 3.17.2 ese bug ya no existe. (2) El que sí nos pasó: un `from rest_framework.pagination import PageNumberPagination` **arriba** de `settings.py` importa un módulo de DRF mientras los settings se están ejecutando a medio cargar; DRF cachea sus settings en ese momento, todavía sin `REST_FRAMEWORK`, y pierde `DEFAULT_SCHEMA_CLASS` (vuelve al de DRF). Todas las vistas quedan con el AutoSchema equivocado y el schema revienta. (3) Intentamos parchear la vista de token con una subclase `SpectacularTokenObtainAuthView(ObtainAuthToken)` que sobrescribía `schema = AutoSchema` (la **clase**): no funciona, porque `isinstance` de una clase contra sí misma es `False`; DRF necesita una instancia (lo verificamos con un script: `view.schema` de una vista normal devuelve una *instancia* de `drf_spectacular.openapi.AutoSchema` resuelta por el descriptor, y con el atributo de clase devolvía la clase y fallaba igual). Además, la extensión que drf-spectacular trae para viejas versiones de DRF (`ObtainAuthTokenView`) es automática e inofensiva en 3.17.2: devuelve la vista sin tocar.
  **Solución:** la combinación que queda en el repo y que dejó `/api/schema/` en 200: `DEFAULT_SCHEMA_CLASS = "drf_spectacular.openapi.AutoSchema"` en los settings, el import de DRF movido **después** de `REST_FRAMEWORK` (con el comentario que lo explica) y la vista de token de DRF usada tal cual (`obtain_auth_token`), que con 3.17.2 ya respeta el schema class global. Verificado con el server vivo y con `manage.py spectacular --validate`.
- **Error:** locale y zona horaria de Uruguay en un proyecto argentino: `LANGUAGE_CODE = "es-uys"` y `TIME_ZONE = "America/Montevideo"`.
  **Causa:** se copió una plantilla de un proyecto uruguayo y nadie lo corrigió; afecta los mensajes del admin, los formatos de fecha y los nombres de zonas horarias.
  **Solución:** `LANGUAGE_CODE = "es-ar"` y `TIME_ZONE = "America/Argentina/Cordoba"` (ITEC Río Cuarto, Córdoba), con el comentario de país corregido.

## Verificación
- [x] `uv run python manage.py check` → "System check identified no issues (0 silenced)"
- [x] `uv run python manage.py showmigrations` → todas las migraciones de `django.contrib` y `authtoken` con `[X]` (aplicadas)
- [x] `uv run python -c "import django; print(django.get_version())"` → `5.2.18`
- [x] `uv run python manage.py spectacular --file schema.yml --validate` → exit 0, sin errores (el `schema.yml` se borró después)
