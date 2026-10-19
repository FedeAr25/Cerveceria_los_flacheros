# Documentación de estudio — Cervecería Los Flacheros

Material de estudio del backend Django de la EFI. Esta carpeta no es documentación de usuario: es el cuaderno de clase del equipo.

## Qué es esta carpeta

Acá vive todo lo que leemos, escribimos y anotamos mientras construimos el backend de Cervecería Los Flacheros. Las guías (`01-...`, `02-...`) explican los conceptos con el código **de este** proyecto, y las notas de tarea (`tareas/`) guardan lo que hicimos y lo que entendimos de cada paso. Sirven para estudiar y para tener a mano las respuestas cuando el docente pregunta en la defensa oral.

## Cómo estudiar con este proyecto

El método es siempre el mismo, en tres pasos:

1. **Leer la guía de la fase** (15 a 20 minutos, una sola vez por fase). No hace falta memorizar: hace falta entender las palabras.
2. **Ejecutar la tarea** que está en `tasks/todo.md`. Manos a la tecla: escribir el código, correr el comando, ver el resultado.
3. **Escribir la nota de la tarea** en `docs/tareas/T##-<slug>.md`, con tus palabras, antes de cerrar la tarea. Cinco minutos alcanzan si el paso anterior salió bien.

**Por qué no alcanza con leer el código ajeno:** leer el código de alguien más (o el que escribimos nosotros hace tres días) genera la ilusión de entender, porque todo te parece obvio cuando está resuelto. En la defensa no te van a pedir que recites sintaxis: te van a pedir que **expliques por qué** algo está así. Esa explicación solo aparece si la escribiste vos después de hacerlo. Por eso la regla de oro de esta carpeta es: *si no lo podés explicar con una frase propia, todavía no lo entendiste; volvé al paso 1 y hacé el 3 igual*.

Un detalle práctico: los errores también son material de estudio. Cuando algo truena, antes de pegar el traceback en el chat, mirá la sección 13 de `01-django-esencial.md`. Casi seguro está ahí.

## Mapa de las guías

| Archivo | Qué cubre | Cuándo se lee | Estado |
|---|---|---|---|
| [`01-django-esencial.md`](01-django-esencial.md) | Framework, anatomía del proyecto, apps, modelos y campos, relaciones y `on_delete`, migraciones, ORM, admin, plantillas, secretos, SQLite→Postgres, comandos de `manage.py`, cómo leer errores | **Antes de arrancar la Fase 1.** Consultar durante las Fases 2 y 3 (modelos y admin) | Escrita |
| [`02-drf-esencial.md`](02-drf-esencial.md) | Serializers, ViewSets, router, permisos, paginación, nested solo en `list`, `@action`, filtros | Antes de la Fase 4 | Escrita |
| [`03-http-json-cors.md`](03-http-json-cors.md) | HTTP, JSON y CORS: el idioma entre nuestro backend y el frontend | Fase 5 (integración con Ema); conviene leerla antes de la Fase 4 | Escrita |
| [`04-nuestro-modelo.md`](04-nuestro-modelo.md) | Los 10 modelos explicados uno por uno, con sus campos y relaciones | Fase 2 (modelos) y Fase 8 (ensayo de defensa) | Escrita |
| [`05-stack-y-entorno.md`](05-stack-y-entorno.md) | `uv`, Docker, PostgreSQL, `gunicorn`, `pytest` y `ruff` | Fases 0, 6 y 7 | Escrita |
| [`06-cuaderno-de-defensa.md`](06-cuaderno-de-defensa.md) | Cuaderno de defensa oral | Fase 8 | Escrita |
| [`07-plan-de-aprendizaje.md`](07-plan-de-aprendizaje.md) | Plan de aprendizaje de 15 días para entender el backend y defenderlo | Para ordenar las semanas; consultar siempre | Escrita |

## Cómo están armadas las guías (4 capas)

Todas las guías (`01-` a `07-`) repiten la misma estructura de 4 capas, en este orden:

1. **Explicación en lenguaje llano** — el concepto contado sin jerga, como si lo explicaras a un compañero principiante.
2. **Ejemplo con el código de nuestro proyecto** — el fragmento real de `backend/`, no un ejemplo genérico de internet.
3. **Bloque `> **Para la defensa:**`** — la respuesta lista para decir, de 2 a 4 frases, por si el docente pregunta sobre ese tema.
4. **Ejercicio con la respuesta tapada en `<details>`** — primero lo intentás vos; después abrís la respuesta y te autoevaluás.

Con esas 4 capas se puede estudiar solo: leés la explicación, mirás el ejemplo del proyecto, hacés el ejercicio con la respuesta tapada y recién ahí la abrís. Si un concepto no queda claro, igual tenés la frase de la defensa a mano.

## Orden de lectura sugerido por día

La regla es una sola: **leé la guía de la fase justo antes de empezar esa fase**, no todo el capítulo de una vez.

| Fase | Fecha | Qué leer antes de arrancar | Qué ejecutás | Qué anotás |
|---|---|---|---|---|
| 0 — Entorno | 19–20 oct | Este README (nada de Django todavía) | Tasks 1–3: `uv`, Docker, estructura, git | `T01` a `T03` |
| 1 — Django base | 20–21 oct | `01-django-esencial.md` §§1, 2, 3, 9, 10 | Tasks 4–6: proyecto, settings, bienvenida, URLs | `T04` a `T06` |
| 2 — Modelos | 21–23 oct | `01-django-esencial.md` §§4, 5, 6, 7, 12 (releer) + `04-nuestro-modelo.md` | Tasks 7–11: los 10 modelos + migraciones | `T07` a `T11` |
| 3 — Admin | 23–24 oct | `01-django-esencial.md` §8 | Tasks 12–13: admin + inlines | `T12`, `T13` |
| 4 — API | 24–27 oct | `02-drf-esencial.md` (+ `03-http-json-cors.md`) | Tasks 14–18 | `T14` a `T18` |
| 5 — Integración | 27–28 oct | `03-http-json-cors.md` (sección CORS) | Tasks 19–20 | `T19`, `T20` |
| 6 — Docker | 28–29 oct | `05-stack-y-entorno.md` | Tasks 21–22 | `T21`, `T22` |
| 7 — Tests | 29–30 oct | Sección de tests de `05-stack-y-entorno.md` | Tasks 23–24 | `T23`, `T24` |
| 8 — Cierre | 30 oct–2 nov | `06-cuaderno-de-defensa.md` | Tasks 25–28 | `T25` a `T28` |

Si un día no llegás a leer la guía, **no saltees la nota de tarea**: es la que te salva la semana de la defensa.

## Convención de notas de tarea

Cada tarea ejecutada deja **un solo archivo** en `docs/tareas/`, con este nombre:

```
docs/tareas/T##-<slug>.md
```

Ejemplos reales: `T04-proyecto-config-y-core.md`, `T07-modelos-estilo-y-cerveza.md`, `T16-nested-solo-en-list.md`. El número es el de la Task en `tasks/todo.md` (con dos dígitos) y el slug es corto y en minúscula.

La plantilla vive en [`docs/tareas/_plantilla.md`](tareas/_plantilla.md). Se usa copiando ese archivo y renombrándolo: sus secciones son `Qué se hizo`, `Conceptos que aparecen acá`, `Archivos`, `Lo que hay que mirar en el código`, `Para la defensa` (la pregunta y tu respuesta), `Errores que nos pasaron y cómo los resolvimos` y `Verificación`.

**Para qué sirve:** esa nota es el diario de aprendizaje y, sobre todo, la fuente de las respuestas de la defensa. Dos semanas después no te vas a acordar por qué `Lote.usuario` es `SET_NULL` y no `CASCADE`, pero sí te vas a acordar lo que escribiste el día que lo hiciste. Si la nota queda en blanco, en la defensa vas a tener que adivinar. Y se escriben **en el momento**, no todas juntas el domingo: "después las escribo juntas" nunca pasa.

## Dónde está la respuesta a cada pregunta del docente

Índice rápido. Si la pregunta es "explicame X", mirá acá y abrí ese archivo:

| Si te preguntan sobre... | Mirá |
|---|---|
| ¿Qué es un framework? ¿Por qué Django? | `01-django-esencial.md` §1 |
| ¿Cómo está armado el proyecto? ¿Qué es `settings.py`? | `01-django-esencial.md` §2 |
| ¿Por qué una sola app? | `01-django-esencial.md` §3 |
| Explicame un modelo, los tipos de campo, `unique`/`blank`/`choices` | `01-django-esencial.md` §4 + `04-nuestro-modelo.md` |
| Explicame esta cerveza, este lote, este pedido en particular | `04-nuestro-modelo.md` |
| Relaciones, `on_delete`, `related_name`, "¿qué pasa si borro esto?" | `01-django-esencial.md` §5 |
| ¿Qué es una migración? ¿Cómo se revierte? | `01-django-esencial.md` §6 |
| Consultas, ORM, el problema de las N+1 | `01-django-esencial.md` §7 |
| Mostrame el admin con filtros, búsqueda e inlines | `01-django-esencial.md` §8 |
| La vista de bienvenida y los templates | `01-django-esencial.md` §9 |
| ¿Dónde están los secretos? ¿Qué hace `DEBUG`? | `01-django-esencial.md` §10 |
| ¿Por qué PostgreSQL y no SQLite? | `01-django-esencial.md` §11 + `05-stack-y-entorno.md` |
| Comandos de Django que usan | `01-django-esencial.md` §12 |
| "Te falló algo, ¿cómo lo debugueás?" | `01-django-esencial.md` §13 |
| Serializers, ViewSets, nested, `@action`, permisos, paginación, filtros | `02-drf-esencial.md` |
| ¿Qué es HTTP? ¿Qué es JSON? ¿Qué es CORS? | `03-http-json-cors.md` |
| Cookies, token vs sesión, CSRF | `03-http-json-cors.md` + `tasks/api-contract.md` |
| uv, Docker, Compose, `gunicorn`, `collectstatic` | `05-stack-y-entorno.md` |
| Tests, cobertura, `ruff`, triada de calidad | `05-stack-y-entorno.md` (secciones de pytest y ruff) |
| ¿Qué le respondo si me pregunta X? / Ensayo de defensa | `06-cuaderno-de-defensa.md` |
| El diagrama ER y el modelo de datos completo | `tasks/plan.md` §7 |
| El contrato con el frontend de Ema | `tasks/api-contract.md` |
| ¿Cumplen los 17 requisitos? | `tasks/todo.md` (checklist final) + `README.md` de la raíz |
| ¿Cómo organizo los días y por dónde sigo? | `07-plan-de-aprendizaje.md` |
| Proceso Git: ramas, commits, merges | `tasks/plan.md` §11 + `git log --oneline` |
