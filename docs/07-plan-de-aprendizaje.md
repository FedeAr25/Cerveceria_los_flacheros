# 07 — Plan de aprendizaje: 15 días para entender el backend y defenderlo

> Guía de autoaprendizaje. Equipo: Cervecería Los Flacheros — EFI Ingeniería de Software 2026.
> Para alguien que se atrasó en clases y tiene que ponerse al día mientras el proyecto avanza.
> Este plan no reemplaza al proyecto: lo acompaña. Cada día tenés que terminar con algo **hecho** y algo **entendido**.

---

## Cómo usar el plan

El error clásico de quien se pone al día es leer ocho horas seguidas y no tocar nada. No funciona. La proporción que sí funciona, día por día:

| Bloque | Tiempo | Qué hacés |
|---|---|---|
| Lectura | 25 min | Leés la guía y la tarea del `tasks/todo.md` que toca ese día |
| Práctica | 20 min | Corrés un comando, rompés algo, lo mirás fallar, lo arreglás |
| Nota | 15 min | Completan una nota en `docs/tareas/` con la plantilla `_plantilla.md` |

Cuatro reglas:

1. **Si el día no llega, recortá la lectura, no la práctica.** Ver `runserver` andando vale más que dos capítulos leídos.
2. **La nota del día es obligatoria.** Es tu diario de aprendizaje y además es la fuente de respuestas de la defensa: si no lo escribiste ayer, no lo recordás el martes.
3. **No te saltees el protocolo "me trabé"** (más abajo). Es la diferencia entre quedarte dos horas trabiado y resolver en quince minutos.
4. **Completá los hitos de comprensión con honestidad.** Un "no" tachado a tiempo vale más que tres "sí" inflados.

---

## Tabla día por día (19/10 al 2/11)

Las "guías" son los documentos de `docs/`. Las "tareas" son las de `tasks/todo.md`.

| Fecha | Fase | Qué leer | Qué practicar | Cómo compruebo que lo entendí |
|---|---|---|---|---|
| **lun 19/10** | Fase 0 — Entorno | `docs/05-stack-y-entorno.md`: "Entorno virtual", "uv" e "instalación en Windows". Tarea 1 | `winget install --id=astral-sh.uv -e`, cerrar y abrir terminal nueva, `uv --version`, `docker --version` | Los tres comandos responden sin errores en una **terminal nueva** |
| **mar 20/10** | Fase 0 → 1 | `docs/05-stack-y-entorno.md`: "`pyproject.toml`" y "`uv.lock`". Tarea 2 y 3 | `uv init`, `uv add` del stack, `uv lock`, `uv sync`, `uv python pin 3.13`, `git init` y primer commit | Existe `.venv/`, existe `uv.lock`, y `uv run python --version` muestra 3.13.x |
| **mié 21/10** | Fase 1 — Base Django | `docs/03-http-json-cors.md`: "Qué es HTTP", "Los métodos HTTP", "Códigos de estado". Tarea 4 | `uv run python manage.py startapp core`, `startproject config .`, primer `runserver` y primera `check` | Abrís `http://127.0.0.1:8000/` y ves la pantalla de Django; `manage.py check` no tiene errores |
| **jue 22/10** | Fase 2 — Modelos | `docs/04-nuestro-modelo.md`: "El negocio en una página", "El diagrama ER", "cómo leer un diagrama ER" | Dibujá el ER a mano en una hoja sin mirar. Tarea 7: modelos `Estilo` y `Cerveza` + primera migración | Podés explicar en voz alta qué es una FK y qué significa `ESTILO \|\|--o{ CERVEZA` |
| **vie 23/10** | Fase 2 → 3 | `docs/04-nuestro-modelo.md`: "Los 10 modelos" (completo) y "Las relaciones y sus `on_delete`". Tareas 8, 9, 10 | Creá los 8 modelos que faltan, `makemigrations` y `migrate`. Probá en el shell un `PROTECT` | `uv run python manage.py showmigrations` muestra todo aplicado; podés predecir qué modelo se borra primero |
| **sáb 24/10** | Fase 3 → 4 | `docs/04-nuestro-modelo.md`: "Estados como máquinas simples". `docs/03-http-json-cors.md`: "JSON". Tareas 11 y 12 | `@property nombre_completo` y `subtotal`; registrar los 10 modelos en `admin.py` | Creás una cerveza desde el admin y `nombre_completo` aparece en la lista |
| **dom 25/10** | Fase 4 — API | `docs/03-http-json-cors.md`: "Headers" y "El viaje completo de una request autenticada". Tarea 14 | Escribí los 10 serializers simples y probá `GET /api/cervezas/` en el navegador | Ves un JSON con `count`, `next`, `previous` y `results` |
| **lun 26/10** | Fase 4 — API | Repasá "El viaje completo" entero (el diagrama ASCII). Tarea 15 | ViewSets + `DefaultRouter` + permisos globales; probá `POST /api/auth-token/` | Tenés un token y con `Authorization: Token ...` el `POST` deja de dar 401 |
| **mar 27/10** | Fase 4 → 5 | `docs/04-nuestro-modelo.md`: "De modelo a endpoint". Tareas 16, 17, 18 | Anidado solo en `list` con `get_serializer_class()`, `@action en_grifo`, `estadisticas` y `avanzar`, filtros | `GET /api/lotes/` trae `etapas` adentro y `GET /api/lotes/1/` no |
| **mié 28/10** | Fase 5 → 6 | `docs/03-http-json-cors.md`: "CORS a fondo", "Cookies", "HTTPS en producción". Tarea 19 | `CORS_ALLOWED_ORIGINS`, probá una llamada con `fetch` desde un HTML en :3000 | Sin CORS el fetch falla; con CORS devuelve JSON. Podés explicar 401 vs 403 |
| **jue 29/10** | Fase 6 → 7 | `docs/05-stack-y-entorno.md`: "Docker", "Dockerfile", "Docker Compose", "PostgreSQL". Tareas 21 y 22 | `docker compose up --build`, mirá el healthcheck, entrá con `psql` | `docker compose ps` muestra `db` (healthy) y `web` (running); `GET /api/cervezas/` responde desde :8000 contenedorizado |
| **vie 30/10** | Fase 7 → 8 | `docs/05-stack-y-entorno.md`: "gunicorn vs runserver", "whitenoise y collectstatic", "pytest y pytest-django", "ruff". Tareas 23 y 24 | Escribí los 13 tests (incluido el de sesión ya autenticada), corré `pytest`, `ruff check .` y `ruff format .` | La triada en verde: `uv run pytest`, `uv run ruff check .` y `uv run ruff format --check .` sin errores |
| **sáb 31/10** | Fase 8 — Cierre | Plan de repaso final (más abajo). Tarea 25 | Seed de datos y credenciales demo; probá el flujo completo de un pedido end-to-end | Con el seed cargado, el front de Ema puede crear un pedido de punta a punta |
| **dom 1/11** | Fase 8 — Cierre | Releé tus notas de `docs/tareas/`. Tareas 26 y 27 | Capturas para el README y el `README.md` final | El README se lee solo: stack, ER, endpoints, instalación y capturas |
| **lun 2/11** | Fase 8 — Entrega | Ensayo completo (abajo). Tarea 28 y 29 | Ensayá la defensa en voz alta con las preguntas de "Para la defensa" de cada guía | Podés explicar los 10 modelos, el viaje de una request y por qué Docker sin mirar notas |

---

## Hitos de comprensión

Escala de autoevaluación, usala siempre igual:

| Nivel | Significado | Qué hacer |
|---|---|---|
| 2 | Lo explico sin mirar nada y entiendo los "por qué" | Pasá al siguiente ítem |
| 1 | Lo explico mirando un poco el código o mis notas | Releé esa sección de la guía y repetí mañana |
| 0 | No lo explico o lo que digo está mal | Es tu prioridad de mañana; si no sale, preguntá |

### Fase 0 — Entorno

- [ ] Explico qué es un entorno virtual y por qué existe `.venv/`
- [ ] Explico qué hace `uv sync` y por qué usa `uv.lock`
- [ ] Explico por qué `[tool.uv] package = false` está en nuestro `pyproject.toml`
- [ ] Digo por qué `uv.lock` va commiteado a git

### Fase 1 — Base Django

- [ ] Digo qué hace Django y cuál es la convención "sobre configuración"
- [ ] Explico qué es una app y por qué tenemos una sola (`core`)
- [ ] Digo qué hace `manage.py check` y cuándo lo corro
- [ ] Explico la diferencia entre `config/settings.py` y `core/apps.py`

### Fase 2 — Modelos

- [ ] Explico qué es un modelo y cómo se convierte en tabla
- [ ] Leo un diagrama ER: `||`, `o{`, `|{`, `PK`, `UK`, `FK`
- [ ] Digo los campos de los 10 modelos y qué representa cada uno en el negocio
- [ ] Explico la diferencia entre `PROTECT`, `CASCADE` y `SET_NULL` con un ejemplo nuestro
- [ ] Explico por qué los `choices` son mejores que texto libre
- [ ] Explico qué hace una migración y por qué se commitea

### Fase 3 — Admin

- [ ] Explico para qué sirve el admin y cómo se registra un modelo
- [ ] Explico qué es un inline y por qué `EtapaFermentacion` va como inline de `Lote`
- [ ] Digo por qué el admin también es una herramienta de prueba para nosotros

### Fase 4 — API

- [ ] Explico qué hace un serializer (traductor y validador)
- [ ] Explico qué hace un ViewSet y cómo `DefaultRouter` genera las URLs
- [ ] Recito los 10 endpoints y qué hace cada uno
- [ ] Explico el patrón `get_serializer_class()` del anidado en `list`
- [ ] Explico qué hace una `@action` con el ejemplo de `/api/cervezas/en_grifo/`
- [ ] Explico cómo se obtiene y se usa el token (`POST /api/auth-token/`)

### Fase 5 — CORS e integración

- [ ] Explico la same-origin policy y por qué :3000 y :8000 son orígenes distintos
- [ ] Explico qué hace `django-cors-headers` y qué header agrega
- [ ] Explico el preflight `OPTIONS`
- [ ] Explico la diferencia entre CORS y CSRF
- [ ] Explico por qué el frontend usa solo token y no sesión

### Fase 6 — Docker

- [ ] Explico qué es imagen, contenedor y volumen
- [ ] Leo nuestro Dockerfile instrucción por instrucción
- [ ] Explico por qué el orden `COPY`/`RUN uv sync` ahorra caché
- [ ] Explico qué hacen `depends_on` + `condition: service_healthy` y el `pg_isready`
- [ ] Explico por qué el backend se conecta a `db:5432` y no a `localhost:5432`

### Fase 7 — Tests y calidad

- [ ] Explico la estructura arrange-act-assert con un test nuestro
- [ ] Explico qué es una fixture y para qué sirve
- [ ] Digo por qué `@pytest.mark.django_db` es necesario
- [ ] Explico la diferencia entre `ruff check` y `ruff format`
- [ ] Digo qué cubren nuestros tests y qué queda sin cubrir

### Fase 8 — Cierre

- [ ] Explico el seed y por qué tiene credenciales demo
- [ ] Recito el stack completo con versiones
- [ ] Explico el flujo end-to-end: cliente hace un pedido y el sistema lo gestiona
- [ ] Ensayé la defensa completa al menos dos veces en voz alta

---

## Protocolo "me trabé"

Cuando algo falla, la tentación es preguntar de inmediato o reescribir todo. Hacé esta lista **en orden**, sin saltarte pasos:

1. **Leé el traceback completo**, de arriba a abajo. El error útil casi nunca está en la última línea: está donde dice "During handling of the above exception" o en la primera fila con un archivo tuyo (`core/models.py`, no la librería).
2. **Corré `uv run python manage.py check`.** Django valida settings, apps, URLs y modelos en segundos. Si el problema es de configuración, lo dice ahí.
3. **Probá la consulta suelta en el shell**: `uv run python manage.py shell`. Escribí la misma query que hace la vista y mirá qué devuelve. Con `Lote.objects.filter(...)` sabés si el problema es el modelo o la vista.
4. **Buscá el error exacto**, copiando el mensaje entre comillas. Primero en la documentación (Django y DRF), después en Stack Overflow. Buscá el texto **tal cual**, con el número de versión si hace falta.
5. **Recién ahí pedí ayuda.** Y pedila bien.

Formato para pedir ayuda (a tu compañero, al foro o al docente):

```
Estoy en: Fase 4, Task 15 (ViewSet de Pedido)
Quiero que: GET /api/pedidos/ devuelva 200
Pasa que: devuelve 500
Error exacto: <pegá el traceback completo>
Ya probé: correr manage.py check (en verde), probar el query en el shell
(funciona), buscar el texto del error en la doc de DRF (no encontré)
```

Con ese formato, cualquiera te ayuda en cinco minutos. Sin traceback y sin "ya probé", la respuesta es "pegame el traceback".

---

## Ejercicios extra

Para practicar por tu cuenta, en tres niveles de dificultad.

### Nivel 1 — Leer y responder

a) Abrí `backend/config/settings.py` y listá tres paquetes de terceros que aparezcan en `INSTALLED_APPS` o `MIDDLEWARE`.
b) En `core/models.py`, contá cuántos campos tiene `Pedido` **sin contar** el `id` ni la FK `cliente`.
c) Buscá en el proyecto dónde se define el tamaño de página y explicá qué cambia si lo pasás a 5.

<details>
<summary>Respuestas</summary>

a) `corsheaders` (en `INSTALLED_APPS` y `MIDDLEWARE`), `rest_framework` y `drf_spectacular` (en `INSTALLED_APPS`), `whitenoise` (en `MIDDLEWARE`) o `django_filters`. Cualquiera de estas sirve.
b) Seis: `fecha`, `estado`, `forma_pago`, `total`, `direccion_entrega` y `observaciones`.
c) En `config/settings.py`, en la clase `DefaultPagination` (`page_size = 10`). Si lo pasás a 5, cada página del listado trae 5 resultados y aparecen más páginas en `next`/`previous`.

</details>

### Nivel 2 — Modificar algo existente

a) Agregá al serializer de `Estilo` un filtro para buscar por `nombre` y comprobá con `GET /api/estilos/?search=ipa`.
b) Cambiá temporalmente `CORS_ALLOWED_ORIGINS` a lista vacía, llamá al API desde un `fetch` en el navegador y anotá el error exacto. Volvé a poner el origen y comprobá que funciona.
c) Creá un test nuevo que verifique que `GET /api/cervezas/en_grifo/` devuelve solo cervezas con `tipo="GRIFO"`. Corré `uv run pytest` y mirá que pase.

<details>
<summary>Respuestas orientativas</summary>

a) Con `django-filter` se usa `filterset_fields = ["nombre"]` en el ViewSet (o `search_fields` con el buscador de DRF). Comprobación: `curl` o el navegador contra `/api/estilos/?search=ipa` con un `200` y `count` menor al total.
b) Con la lista vacía el navegador bloquea la respuesta y aparece en la consola el error de CORS: falta el header `Access-Control-Allow-Origin`. Es el error que `django-cors-headers` está para evitar.
c) Esquema del test: crear dos cervezas (una `ENVASE`, una `GRIFO`), llamar con `client.get("/api/cervezas/en_grifo/")` y assertar que el `count` es 1 y que el resultado tiene `tipo == "GRIFO"`.

</details>

### Nivel 3 — Crear algo nuevo

a) Pensá un modelo `Reserva` para el bar (cliente, fecha, cantidad de personas, estado). Escribí sus campos con tipos y `choices`, y el `on_delete` de su FK a `Cliente`. Justificá cada decisión en una línea.
b) ¿Qué endpoint tendría `Reserva` y qué `@action` le agregarías? Escribí la lista de rutas.
c) Escribí un test de un `POST` inválido a ese endpoint: ¿qué código esperás y por qué?

<details>
<summary>Respuesta orientativa</summary>

a) Campos posibles: `cliente` FK a `Cliente` con `PROTECT` (la reserva es historial del bar: no puede desaparecer si se borra el cliente), `fecha` (obligatoria), `cantidad_personas` entero positivo, `estado` con `choices` (`PENDIENTE`, `CONFIRMADA`, `CANCELADA`), `observaciones` opcional.
b) `GET/POST /api/reservas/`, detalle en `/api/reservas/{id}/`, y por ejemplo `@action` `POST /api/reservas/{id}/confirmar/`.
c) Un `400 Bad Request` si falta `cliente` o `fecha`, o si `cantidad_personas` es 0 o negativo. El serializer valida antes de tocar la base.

</details>

---

## Plan de repaso final (últimos 3 días antes de la defensa)

El 31/10, 1/11 y 2/11, además de cerrar tareas:

### Día 1 — Repaso de contenido

1. Releé `docs/04-nuestro-modelo.md` entero. Es el documento más importante de la defensa.
2. Dibujá el diagrama ER de memoria. Si te trabás en una relación, mirá y volvé a intentar.
3. Recitá los 10 endpoints de `De modelo a endpoint`.

### Día 2 — Repaso de respuestas

1. Abrí tus notas de `docs/tareas/` y releé solo las secciones "Para la defensa".
2. Releé en `docs/03-http-json-cors.md` los bloques `> **Para la defensa:**` y las tablas de códigos de estado y CORS vs CSRF.
3. Releé en `docs/05-stack-y-entorno.md` los bloques de defensa sobre uv, Dockerfile, compose y whitenoise.

### Día 3 — Ensayo

1. Ensayá la defensa **en voz alta**, cronometrada, sin mirar nada: qué es el proyecto, el stack con versiones, los modelos, el viaje de una request, cómo se despliega.
2. Grabá la explicación del "viaje de una request autenticada" (el diagrama de `docs/03-http-json-cors.md`). Si te sale en voz alta, te sale en la defensa.
3. Dejá anotadas las 3 cosas que más se te travaron. Esas son las que hay que releer el lunes por la mañana.

Y el día de la defensa: llevá el proyecto corriendo (o el `docker compose up` listo), tus notas a mano y la humildad de decir "eso no lo sé, lo buscaría" cuando no lo sepas. Un "no lo sé pero lo buscaría así" bien acompañado suma más que inventar.

---

> **Para la defensa:** "Tuvimos un plan de estudio de dos semanas alineado a las fases, con lectura, práctica y una nota por día, hitos de autoevaluación y un protocolo de diagnóstico antes de pedir ayuda. Las notas de cada tarea en `docs/tareas/` son el registro de ese proceso."
