# T11 — Integridad del modelo y migraciones limpias

**Fase:** 2
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Antes de cerrar la Fase 2 hicimos una pasada de consistencia sobre los 10 modelos de `backend/core/models.py` y dejamos el repo en un estado verificable: todos los campos de estado usan `TextChoices` anidado con `choices=` y `default=`, todas las `FK` llevan `related_name` y `on_delete` explícito con el criterio del negocio (PROTECT para histórico, CASCADE para dependientes, SET_NULL para opcionales), todos los campos llevan `verbose_name` en español, los 10 modelos tienen `__str__` y `Meta` con `verbose_name` y `verbose_name_plural`, los campos opcionales usan `null=True, blank=True` y los puntajes/rangos usan `validators`.

El cierre práctico fue dejar la triada de verificación de modelos en verde: `manage.py check` sin problemas, las cuatro migraciones aplicadas (`showmigrations` con todo en `[X]`) y `makemigrations --check --dry-run` diciendo `No changes detected`, que es la garantía de que el código de los modelos y las migraciones commiteadas dicen lo mismo. Además corrimos un smoke test que instancia los 10 modelos y les llama `str()`; ése es el que descubrió (y con el que quedó verificado) el bug de `Opinion.__str__` de la Task 10.

## Conceptos que aparecen acá
- **`makemigrations --check --dry-run`** — es el comando que hay que correr antes de commitear. No escribe nada (`--dry-run`) y sólo devuelve distinto de cero si hay modelos que todavía no tienen su migración (`--check`). Detecta el olvido clásico: alguien agregó un campo, lo commiteó y no generó la migración; sin ése comando, otro compañero que clona el repo tiene el código pero la base le queda vieja y el error aparece recién en runtime.
- **`showmigrations`** — lista las migraciones de cada app y su estado: `[ ]` = generada pero sin aplicar, `[X]` = aplicada en esa base. Es la forma rápida de ver "¿la base de esta máquina tiene lo que dice el código?".
- **`makemigrations` vs `migrate`** — son dos pasos distintos: `makemigrations` **escribe el archivo** de migración comparando los modelos con la última migración (queda en el repo, versionado con git); `migrate` **la aplica** a la base de datos concreta (cada máquina la ejecuta). Por eso la migración se commitea y la base no: el archivo es el contrato, `migrate` es cómo cada entorno lo cumple.
- **`check`** — el saneamiento de Django: recorre modelos, settings, urls y declaraciones y reporta problemas de configuración (campos mal declarados, dependencias rotas). No toca la base; corre en segundos y es el primer filtro.
- **Criterios de consistencia del modelo** — `TextChoices` para todo valor con lista fija (nunca strings sueltos), `@property` para lo que se calcula y no se guarda, `validators` para rangos numéricos (1-5 en `Opinion.puntaje`), `verbose_name` en español para que admin y errores se lean en nuestro idioma, `__str__` en los 10 modelos para que el shell y el admin muestren algo legible, y `Meta.verbose_name`/`verbose_name_plural` para singular y plural.

## Archivos
- `backend/core/models.py` — los 10 modelos ya unificados bajo los mismos criterios; único archivo tocado en el fix de `Opinion.__str__` (una línea + comentario).
- `backend/core/migrations/0001_initial.py` … `0004_cliente_opinion_pedido_lineapedido.py` — las cuatro migraciones, commiteadas y aplicadas; su existencia es lo que hace que `--check` pase.
- `docs/tareas/T07-*` a `T11-*` — las notas de esta fase (incluida ésta).

## Lo que hay que mirar en el código
- `backend/core/models.py` (entero) — recorrer los 10 buscando el patrón repetido: `class Meta`, `__str__`, `verbose_name` en español, `TextChoices` para estados/tipos. La repetición es la evidencia de la consistencia.
- `backend/core/models.py::Opinion.__str__` — el fix del bug con su comentario de dos líneas: queda documentado por qué `puntaje` no tiene `get_puntaje_display()`.
- `backend/core/models.py::Lote.TRANSICIONES` y `puede_avanzar_a` — la única lógica de negocio "activa" del modelo hasta ahora (todo lo demás es estructura).
- `backend/core/migrations/` — el orden de los cuatro archivos y cómo cada uno depende del anterior por las FK.

## Para la defensa
> **Pregunta:** ¿Cómo saben que el modelo y la base están sincronizados?
> **Respuesta:** Con `makemigrations --check --dry-run`, que devuelve `No changes detected` si están alineados. Si alguien agrega un campo y no genera la migración, ese comando falla, así que lo corremos antes de commitear (y va a correr en CI en la Task 24): es la forma de que el olvido se detecte acá y no en la máquina de otro compañero.

> **Pregunta:** ¿Cuál es la diferencia entre `makemigrations` y `migrate`?
> **Respuesta:** `makemigrations` escribe el archivo de migración comparando los modelos con la última migración; `migrate` aplica ese archivo a la base de datos. El archivo se commitea y viaja con el repo; la base se genera en cada entorno corriendo `migrate`, que por eso es el primer paso del `compose.yaml`.

## Errores que nos pasaron y cómo los resolvimos
- **Error:** `AttributeError: 'Opinion' object has no attribute 'get_puntaje_display'` (mismo que el detalle en la Task 10).
  **Causa:** lo detectó un smoke test que instancia los 10 modelos y les llama `str()`: `Opinion.__str__` usaba `get_puntaje_display()`, método que Django sólo genera para campos con `choices`, y `puntaje` es un `IntegerField` con `validators`. Ningún `check` de Django ni ninguna migración lo hubieran visto: el error sólo aparece al imprimir una opinión.
  **Solución:** el `__str__` pasa a usar `self.puntaje` directo, con un comentario de dos líneas al lado que explica la causa. El smoke test quedó como verificación obligatoria del cierre de fase y ahora pasa sin ningún `AttributeError`.

## Verificación
- [x] `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- [x] `uv run python manage.py makemigrations --check --dry-run` → `No changes detected`
- [x] `uv run python manage.py showmigrations core` → `0001`, `0002`, `0003` y `0004` todos en `[X]`
- [x] Smoke test (10 modelos instanciados + `str()`): ningún `AttributeError`; `Lote`, `EtapaFermentacion`, `Pedido`, `LineaPedido` y `Opinion` devuelven `RelatedObjectDoesNotExist` sin guardar (normal de Django, el resto imprime bien)
- [x] `git status` → limpio después de commitear el fix y las notas de esta fase
