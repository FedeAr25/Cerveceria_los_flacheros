# T08 — Modelos Lote y Etapa de fermentación

**Fase:** 2
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Agregamos los dos modelos de producción en `backend/core/models.py`: `Lote` (la producción concreta de una cerveza: número único, fecha de inicio y fin, volumen en litros, estado, notas, la cerveza que se produce y el usuario responsable) y `EtapaFermentacion` (cada fase dentro de un lote: número, tipo PRIMARIA/SECUNDARIA/MADURADO, fechas, temperatura, estado y el lote al que pertenece). La migración `0002_lote_etapafermentacion` los crea en el orden correcto: primero `lote`, después `etapafermentacion`, porque la etapa tiene una FK a lote y las migraciones respetan las dependencias.

El corazón de esta tarea es la **máquina de estados** de `Lote`: el diccionario `TRANSICIONES` declara, para cada estado, cuál es el único siguiente estado válido (PLANIFICADO → EN_PRODUCCION → FERMENTACION → MADURACION → LISTO; CANCELADO es terminal y no aparece porque no tiene salida), y el método `puede_avanzar_a(estado)` responde si el salto pedido es legal. Ese método no lo usa todavía ninguna vista: lo dejó listo la `@action` "avanzar" de la Fase 4 (Task 18), que va a devolver 400 cuando la transición no cumpla la regla.

## Conceptos que aparecen acá
- **Máquina de estados** — un modelo cuyo campo `estado` sólo puede moverse por transiciones predefinidas, no a libre albedrío. Acá está implementada con el diccionario de clase `TRANSICIONES` (cada clave apunta a su único próximo estado) y el método `puede_avanzar_a()`, que compara el estado pedido contra `TRANSICIONES.get(self.estado)`. CANCELADO no está en el diccionario: al no tener clave, ningún salto desde ahí es válido.
- **`CASCADE` vs `PROTECT` vs `SET_NULL`** — las tres reglas `on_delete` con casos concretos de esta migración: `EtapaFermentacion.lote` es `CASCADE` (la etapa no existe sin su lote; si se borra el lote, sus etapas se borran con él), `Lote.cerveza` es `PROTECT` (no se borra la cerveza que ya se produjo) y `Lote.usuario` es `SET_NULL` (si se borra el usuario, el lote queda sin responsable pero se conserva: el responsable es un dato secundario y el histórico de producción no se pierde). Como `SET_NULL` requiere que la columna admita NULL, ese FK lleva `null=True, blank=True`.
- **`DateField` vs `DateTimeField`** — `DateField` guarda sólo el día (fecha de inicio del lote) y `DateTimeField` día + hora + minuto (por eso `fecha_creacion` de `Cerveza` es `DateTimeField` con `auto_now_add`): si el campo no necesita la hora, no se le pide. `fecha_fin` es `DateField(null=True, blank=True)` porque el lote se planifica sin saber cuándo termina.
- **`DecimalField` para el volumen** — `volumen_litros = DecimalField(max_digits=8, decimal_places=2)`: los lotes se miden en litros con decimales (200,50 L) y aplica la misma razón del precio: con dinero o con medidas que después se multiplican, se usa decimal exacto y no float.
- **`estado` como `CharField` con `choices` y no como booleano** — un booleano sólo alcanza para dos estados; la producción tiene seis (PLANIFICADO, EN_PRODUCCION, FERMENTACION, MADURACION, LISTO, CANCELADO) y el pedido otros seis distintos. `choices` además habilita `get_estado_display()`, el filtro del admin y la validación de que entre un valor de la lista. Es `CharField` y no un ENUM de la base para que el esquema siga siendo portable y el listado de valores quede en el código, versionado con git.
- **Dos `related_name` iguales sin pisarse** — `Lote.cerveza` y `Lote.usuario` ambos se llaman `related_name="lotes"` y no hay conflicto, porque cada uno cuelga de un modelo distinto: el reverso queda en `cerveza.lotes` y en `usuario.lotes`. Sí se pisaría (y Django tiraría error) si dos FK apuntaran al **mismo** modelo con el mismo `related_name`.

## Archivos
- `backend/core/models.py` — las clases `Lote` (con `Estado`, `TRANSICIONES`, `puede_avanzar_a`) y `EtapaFermentacion` (con `Tipo` y `Estado`), más sus tres FK (`cerveza` PROTECT, `usuario` SET_NULL, `lote` CASCADE).
- `backend/core/migrations/0002_lote_etapafermentacion.py` — la migración generada: `CreateModel` de `Lote` y después de `EtapaFermentacion`, con dependencia implícita sobre `0001_initial` (necesita las tablas `core_cerveza` y `core_estilo`).

## Lo que hay que mirar en el código
- `backend/core/models.py::Lote.TRANSICIONES` — el diccionario entero con la flecha de cada estado y el comentario que aclara que CANCELADO es terminal.
- `backend/core/models.py::Lote.puede_avanzar_a` — tres líneas: `TRANSICIONES.get(self.estado) == estado`. Es toda la lógica de validación que va a usar la `@action` "avanzar" de la Fase 4.
- `backend/core/models.py::Lote.usuario` — el `SET_NULL` con su comentario y el `null=True, blank=True` que lo acompaña (el patrón completo de una FK opcional).
- `backend/core/models.py::EtapaFermentacion.__str__` — el único `__str__` que combina una propiedad calculada por display (`get_tipo_display()`) con otra FK (`self.lote`): muestra el patrón de encadenar.

## Para la defensa
> **Pregunta:** ¿Cómo garantizan que un lote no salte de PLANIFICADO a LISTO?
> **Respuesta:** Con el diccionario `TRANSICIONES`: cada estado declara solo su próximo estado válido, y `puede_avanzar_a()` compara el estado pedido contra lo que dice ese diccionario. PLANIFICADO sólo tiene flecha a EN_PRODUCCION, así que "PLANIFICADO → LISTO" no está en la lista y devuelve `False`. Cuando llegue la `@action` "avanzar" de la Fase 4, si la transición no es válida responde 400 y no guarda nada.

> **Pregunta:** ¿Por qué `Lote.usuario` es `SET_NULL` y no `CASCADE`?
> **Respuesta:** Porque el lote es histórico de producción y el responsable es un dato secundario: si mañana se da de baja un usuario, no queremos perder los lotes que produjo. Con `SET_NULL` el lote queda sin responsable (la columna pasa a NULL) pero se conserva; con `CASCADE` se borraría el lote junto con el usuario.

## Errores que nos pasaron y cómo los resolvimos
- Sin errores: la migración se generó y aplicó a la primera, respetando el orden de dependencias.

## Verificación
- [x] `uv run python manage.py makemigrations` → `Migrations for 'core': core/migrations/0002_lote_etapafermentacion.py` (Lote + EtapaFermentacion)
- [x] `uv run python manage.py migrate` → `Applying core.0002_lote_etapafermentacion... OK`
- [x] `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- [x] `uv run python manage.py makemigrations --check --dry-run` → `No changes detected`
- [x] En el shell: `lote.puede_avanzar_a("EN_PRODUCCION")` con estado PLANIFICADO → `True`; `lote.puede_avanzar_a("LISTO")` → `False` (la máquina de estados corta el salto).
