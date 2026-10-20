# T06 — URLs del proyecto, documentación OpenAPI y endpoint de token

**Fase:** 1
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Montamos el mapa de URLs completo del proyecto en `backend/config/urls.py`: la bienvenida en `/`, el panel en `/admin/`, el router de la API en `/api/`, el schema en `/api/schema/`, Swagger UI en `/api/schema/swagger-ui/`, ReDoc en `/api/schema/redoc/`, el endpoint de token en `/api/auth-token/` y el login/logout de sesión de la Browsable API en `/api-auth/` (`rest_framework.urls`, que es lo que le da botón de login a la API navegable y demuestra que la autenticación por sesión no es solo teórica).

En los settings activamos la API navegable agregando `BrowsableAPIRenderer` a `DEFAULT_RENDERER_CLASSES` (JSON para las máquinas, HTML navegable para los humanos) y configuramos `SPECTACULAR_SETTINGS` con el título "Cervecería Los Flacheros API", descripción y versión. El schema se genera con drf-spectacular recorriendo las URLs: cada vista DRF que encuentre aporta su operación a un único documento OpenAPI 3 del que después se sirven tres vistas distintas (el JSON/YAML crudo, Swagger UI y ReDoc).

El router (`DefaultRouter` en `core/urls.py`) quedó vacío a propósito: los ViewSets son Fase 4. Igual expone `/api/` con la API navegable de DRF (con el permiso global, responde 401 sin sesión/token y 200 autenticado).

## Conceptos que aparecen acá
- **OpenAPI** — un archivo (JSON o YAML) que describe toda la API: endpoints, métodos, parámetros, cuerpos y respuestas. Es un estándar, no de Django: sirve para generar documentación, clientes y tests desde cualquier herramienta.
- **Swagger UI y ReDoc** — dos interfaces web que leen el mismo schema OpenAPI y lo pintan. Son tres vistas de lo mismo: `/api/schema/` (el documento), `/api/schema/swagger-ui/` (interactiva, permite probar requests) y `/api/schema/redoc/` (más legible, para documentar).
- **API navegable de DRF** — el renderer HTML que DRF sirve en cada endpoint: muestra el JSON junto con un formulario para probarlo, el botón de login y el historial de requests. Es la "API navegable habilitada" que pide el docente; con `rest_framework.urls` montado en `/api-auth/` tiene además login/logout con sesión.
- **`DefaultRouter`** — clase de DRF que genera las URLs de un ViewSet (colección, detalle, acciones) a partir de `router.register(...)`. Ahora está vacío: `/api/` responde con la raíz de la API (sin endpoints registrados) porque los ViewSets llegan en la Fase 4.
- **`manage.py spectacular`** — el comando de drf-spectacular que genera el schema por línea de comandos: `--file schema.yml` lo escribe y `--validate` lo chequea. Sirve para validar en CI sin levantar el server y para commitear el contrato.
- **Serializer como fuente del schema** — drf-spectacular no adivina: lee los serializers de cada vista (los campos, tipos, requeridos) y de ahí arma los ` requestBody` y `responses` del schema. Por eso un serializer mal declarado se documenta mal; el serializer es, en la práctica, el contrato de la API.

## Archivos
- `backend/config/urls.py` — el mapa completo: `/`, `/admin/`, `/api/`, las tres vistas de documentación, `/api/auth-token/` y `/api-auth/`.
- `backend/core/urls.py` — `DefaultRouter()` vacío, montado desde `config/urls.py` en `/api/`.
- `backend/config/settings.py` — `DEFAULT_RENDERER_CLASSES` (JSON + Browsable API) y `SPECTACULAR_SETTINGS` (título, descripción, versión).

## Lo que hay que mirar en el código
- `backend/config/urls.py::urlpatterns` — las siete rutas y el orden: home, admin, api, schema, swagger, redoc, token, api-auth.
- `backend/core/urls.py::router` — el `DefaultRouter()` vacío con su comentario: es la evidencia de que la API navegable funciona aun sin endpoints (y de que los ViewSets son la Fase 4).
- `backend/config/settings.py::REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]` — dónde se activa la Browsable API.
- `backend/config/settings.py::SPECTACULAR_SETTINGS` — el título que aparece en Swagger y ReDoc.

## Para la defensa
> **Pregunta:** ¿Qué diferencia hay entre Swagger y ReDoc?
> **Respuesta:** Ninguna en el contenido: los dos renderizan el mismo schema OpenAPI que genera drf-spectacular; Swagger UI es más interactivo y sirve para probar requests desde el navegador, ReDoc es más legible y sirve más para documentar. Nosotros exponemos los dos porque el docente pidió "openapi, swagger y/o redoc" y tener los tres cubre cualquier interpretación.

## Errores que nos pasaron y cómo los resolvimos
- **Error:** `GET /api/schema/` devolvía 500 con `AssertionError: Incompatible AutoSchema used on View <class 'rest_framework.authtoken.views.ObtainAuthToken'>. Is DRF's DEFAULT_SCHEMA_CLASS pointing to "drf_spectacular.openapi.AutoSchema"...`.
  **Causa:** DRF y drf-spectacular tienen clases `AutoSchema` distintas, y drf-spectacular verifica con `isinstance` que cada vista termine con una **instancia** de la suya. DRF resuelve el schema de cada vista mediante un descriptor (`DefaultSchema`) que instancia `DEFAULT_SCHEMA_CLASS`; el error aparece cuando esa cadena se rompe. En DRF anterior a 3.12 pasaba porque `ObtainAuthToken` inyectaba a mano el `AutoSchema` de DRF (bug propio de DRF, documentado por drf-spectacular). A nosotros nos pasó por dos vías: (1) un import de un módulo de DRF **arriba** de `settings.py` hacía que DRF cachee sus settings a medio cargar y pierda `DEFAULT_SCHEMA_CLASS` (vuelve el de DRF y todas las vistas quedan "incompatibles"); (2) el parche que probamos —una subclase `SpectacularTokenObtainAuthView(ObtainAuthToken)` con `schema = AutoSchema` (la clase)— **no** arregla nada y reproduce el mismo 500 con el nombre de la subclase, porque `isinstance` exige una instancia y `schema = AutoSchema` deja la clase a secas (verificado con un script en el shell: una vista normal devuelve una *instancia* resuelta por el descriptor; con el atributo de clase devolvía la clase y fallaba).
  **Solución:** dejar la vista de DRF tal cual (`obtain_auth_token`, que con DRF 3.17.2 ya respeta el schema class global), el import de DRF movido después de `REST_FRAMEWORK` en los settings (con su comentario) y `DEFAULT_SCHEMA_CLASS = "drf_spectacular.openapi.AutoSchema"`. Con eso `/api/schema/` responde 200 y el schema se genera entero.
- **Error:** probamos usar `drf_spectacular.contrib.rest_framework.authtoken.views` (la extensión que drf-spectacular trae para el viejo bug de `ObtainAuthToken`) y dio `ModuleNotFoundError: 'drf_spectacular.contrib.rest_framework' is not a package`.
  **Causa:** verificado con un import directo: en drf-spectacular 0.30.0 ese módulo **no existe** como paquete; hay un archivo plano `drf_spectacular/contrib/rest_framework.py` con la extensión `ObtainAuthTokenView`, que para DRF ≥ 3.12 devuelve la vista sin tocar (no hace falta) y cuya importación automática no resuelve nada que nosotros necesitemos.
  **Solución:** no usarlo; la subclase innecesaria se descartó y se quedó la vista simple de DRF.

## Verificación
- [x] Las URLs responden 200: `/`, `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/`, `/admin/login/`, `/api-auth/login/`; `/api/` responde 401 sin credenciales (permiso global `IsAuthenticated`, a diseño) y **200 con `Authorization: Token <key>`**
- [x] `POST /api/auth-token/` con `{"username", "password"}` → 200 y devuelve `{"token": ...}`
- [x] `GET /api/schema/` devuelve OpenAPI válido (`application/vnd.oai.openapi`, arranca con `openapi: 3.0.3`); `GET /api/schema/?format=json` → JSON con `"openapi": "3.0.3"` y `info.title` "Cervecería Los Flacheros API"
- [x] El log del server no tira `AssertionError` ni ningún 500 en `/api/schema/`
- [x] `uv run python manage.py spectacular --file schema.yml --validate` → exit 0, sin errores (el `schema.yml` generado se borró)
