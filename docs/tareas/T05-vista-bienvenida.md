# T05 — Vista de bienvenida en `/`

**Fase:** 1
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Creamos la página que ve cualquiera que entre a `http://localhost:8000/`: una vista `HomeView` (subclase de `TemplateView`) montada en la raíz del mapa de URLs, que renderiza `templates/bienvenida.html`. El template lleva la identidad de la marca: nombre "Cervecería Los Flacheros", lema "Arte en cada trago, tradición en cada lote" y la paleta (ámbar `#F5A623`, lúpulo `#4A7C59`, malta tostada `#8B4513`, espuma `#F7F7F7`, carbón `#2B2B2B`) aplicada con variables CSS en `static/css/estilos.css`.

Además del branding, la página es el mapa de entrada del proyecto: enlaces a la API navegable (`/api/`), a Swagger (`/api/schema/swagger-ui/`), a ReDoc (`/api/schema/redoc/`) y al panel de administración (`/admin/`), más una sección que explica cómo pedir el token (`POST /api/auth-token/` con `{"username", "password"}` y usarlo como `Authorization: Token <key>`). No hay lógica de negocio en la vista: solo dice qué template renderizar.

## Conceptos que aparecen acá
- **Qué es una vista** — el pedazo de código que recibe una `HttpRequest` y devuelve una `HttpResponse`. Es el eslabón entre una URL y el contenido que ve el usuario (HTML, JSON, un redirect…).
- **Vista función vs. vista de clase** — una vista función es una función Python a secas; una vista de clase (`View`, `TemplateView`, y más adelante los `ModelViewSet`) agrupa lógica reutilizable en métodos (`get`, `post`, `get_context_data`). Nosotros usamos `TemplateView` porque la página de bienvenida no tiene lógica: hereda todo el comportamiento y solo declara `template_name`.
- **Template** — archivo HTML con marcas del lenguaje de templates de Django. Se separa la vista (qué hacer) del template (cómo se ve), y el HTML lo puede retocar alguien que no programa Python.
- **`{% load static %}` y `{% static %}`** — `{% load %}` importa librerías de tags al template; `{% static 'css/estilos.css' %}` devuelve la URL correcta del archivo estático según los settings. La ventaja clave: si más adelante cambiamos a un CDN o a whitenoise con nombres hasheados, no tocamos el HTML.
- **`TEMPLATES` con `DIRS` y `APP_DIRS`** — `DIRS` son carpetas de templates del proyecto (`backend/templates/`); `APP_DIRS` busca también dentro de `templates/` de cada app instalada. `bienvenida.html` vive en `DIRS` porque no pertenece a ninguna app en particular: es del proyecto.
- **Estáticos aparte** — Django no sirve CSS/JS "mágicamente": hay que declarar `STATIC_URL`, `STATIC_ROOT` y `STATICFILES_DIRS`. El admin de Django trae sus propios CSS y JS, y `staticfiles` es la app que los localiza; en desarrollo `runserver` los sirve y en producción los sirve whitenoise desde `STATIC_ROOT`.
- **whitenoise** — el middleware ya configurado en la T04: comprime y sirve los estáticos desde el propio proceso, con caché. En local `runserver` alcanza; en Docker es lo que va a darle servicio al admin y a este template.

## Archivos
- `backend/core/views.py` — `HomeView(TemplateView)` con `template_name = "bienvenida.html"`.
- `backend/templates/bienvenida.html` — la página: identidad de marca, enlaces útiles y explicación del token.
- `backend/static/css/estilos.css` — la paleta como variables CSS (`:root`) y los estilos de la página.
- `backend/config/settings.py` — bloques `TEMPLATES` (con `DIRS`) y de estáticos (`STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`, `STORAGES` con whitenoise).
- `backend/config/urls.py` — `path("", HomeView.as_view(), name="home")`.

## Lo que hay que mirar en el código
- `backend/core/views.py::HomeView` — la vista entera: seis líneas, cero lógica. Es el ejemplo más limpio de "vista de clase sin lógica de negocio".
- `backend/templates/bienvenida.html` — `{% load static %}` arriba, la etiqueta `{% static 'css/estilos.css' %}` en el `<head>`, y la lista de enlaces a API, Swagger, ReDoc y admin.
- `backend/static/css/estilos.css` — el bloque `:root` con los cinco colores de la marca; es lo que hay que mostrar cuando preguntan "¿dónde está la identidad visual?".
- `backend/config/urls.py::urlpatterns` — el primer patrón del mapa: `""` → `HomeView`.

## Para la defensa
> **Pregunta:** ¿Qué es una vista en Django y qué devuelve?
> **Respuesta:** Es el código que recibe la `HttpRequest` de una URL y devuelve una respuesta HTTP. En nuestro caso es una `TemplateView`, que no tiene lógica de negocio: solo declara qué template renderizar (`bienvenida.html`), y Django se encarga de armar la página completa con los context processors (por eso el template puede usar `request`, `user` y `messages` sin que nosotros los pasemos a mano).

## Errores que nos pasaron y cómo los resolvimos
Sin errores.

## Verificación
- [x] `GET /` → 200; el HTML contiene el nombre, el lema y los 4 enlaces (`/api/`, Swagger UI, ReDoc, `/admin/`)
- [x] `GET /static/css/estilos.css` → 200 (`text/css`, 1576 bytes)
