# T09 — Modelos Proveedor y Materia Prima

**Fase:** 2
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Sumamos el bloque de insumos en `backend/core/models.py`: `Proveedor` (quién nos vende materia prima: razón social, CUIT único, email, teléfono y un `activo` para darlo de baja sin borrarlo) y `MateriaPrima` (lo que entra al depósito: nombre, tipo MALTA/LUPULO/LEVADURA/OTROS, unidad KG/G/LT/UNIDAD, stock actual, stock mínimo, costo unitario y el proveedor del que se compra). La migración `0003_proveedor_materiaprima` los crea en ese orden, porque `MateriaPrima` tiene una FK a `Proveedor`.

La decisión de diseño de esta tarea es el `on_delete` de `MateriaPrima.proveedor`: `SET_NULL`. Un proveedor se puede dar de baja y las materias primas que nos vendió siguen existiendo en el depósito, así que la relación se desengancha (`null=True, blank=True`) y no se borra nada. También aparece el primer `EmailField` del proyecto (valida el formato de mail antes de mandarlo a la base) y la primera diferencia de tipos de `stock`: acá es `DecimalField`, no `IntegerField` como en `Cerveza`.

## Conceptos que aparecen acá
- **`SET_NULL` aplicado a `MateriaPrima.proveedor`** — la materia prima sobrevive al proveedor: si el proveedor se da de baja o se elimina, la columna `proveedor` pasa a NULL y el insumo queda igual, sólo sin vínculo. Por eso el FK lleva `null=True, blank=True` (necesita que la columna admita NULL) y no es `CASCADE`, que borraría la malta junto con el proveedor.
- **`EmailField`** — un `CharField` que además valida que lo que entre parezca un mail (`email` de `Proveedor` y de `Cliente`). Es validación de Django, previa a la base; no manda nada a un servidor de correo.
- **`stock` y `stock_minimo` como `DecimalField`** — los insumos se miden en kilos o litros con decimales: se puede tener 2,5 kg de lúpulo o 12,75 L de wort, y con `IntegerField` eso no se guarda. `stock_minimo` es el umbral de reorden: sirve para filtrar "lo que está por debajo del mínimo" y no es un número entero por la misma razón.
- **`choices` anidados (`Tipo` y `Unidad`)** — `MateriaPrima.Tipo` (MALTA, LUPULO, LEVADURA, OTROS) y `MateriaPrima.Unidad` (KG, G, LT, UNIDAD) son dos `TextChoices` dentro de la misma clase, cada uno con su `choices=` y su `default`. Dos listas distintas en un modelo mismo: cada campo se sirve de la que le corresponde.
- **`default` en campos de negocio** — `stock=0`, `stock_minimo=0`, `costo_unitario=0`, `unidad=Unidad.KG`, `activo=True`: valores de partida razonables para un alta rápida; no son "lo que siempre va a ser", son el punto de arranque.
- **`unique=True` en `cuit`** — igual que `nombre` en `Estilo`: la base impide dos proveedores con el mismo CUIT, aunque dos hilos lo escriban a la vez.

## Archivos
- `backend/core/models.py` — las clases `Proveedor` y `MateriaPrima` con sus `TextChoices`, `Meta`, `__str__` y la FK `proveedor` con `SET_NULL`.
- `backend/core/migrations/0003_proveedor_materiaprima.py` — la migración generada: `CreateModel` de `Proveedor` y después de `MateriaPrima`.

## Lo que hay que mirar en el código
- `backend/core/models.py::MateriaPrima.proveedor` — el `SET_NULL` con el comentario ("la materia prima sigue existiendo aunque el proveedor se dé de baja") y el par `null=True, blank=True` que va siempre de la mano con esta regla.
- `backend/core/models.py::MateriaPrima.stock` y `stock_minimo` — los dos `DecimalField(default=0)`; compararlos con `Cerveza.stock = IntegerField(default=0)` de la Task 7.
- `backend/core/models.py::MateriaPrima.Tipo` y `Unidad` — dos `TextChoices` anidados en la misma clase, con `default=Unidad.KG` en el campo.
- `backend/core/models.py::Proveedor.cuit` — `unique=True` y `EmailField("email", blank=True)` juntos.

## Para la defensa
> **Pregunta:** ¿Por qué `Cerveza.stock` es entero y `MateriaPrima.stock` es decimal?
> **Respuesta:** Porque miden cosas distintas: las cervezas se cuentan en unidades o botellas (330, no 330,5), en cambio la malta y el lúpulo se pesan en kilos con fracciones y con enteros no se puede guardar 2,5 kg. El tipo del campo sigue la naturaleza del dato, no un criterio estético.

> **Pregunta:** ¿Qué pasa si borro un proveedor que tiene materias primas cargadas?
> **Respuesta:** No se borra nada: `MateriaPrima.proveedor` es `SET_NULL`, así que el proveedor se elimina (o se da de baja con `activo=False`) y las materias primas quedan sin vínculo, con la columna en NULL. La materia prima es el dato importante y el vínculo es secundario.

## Errores que nos pasaron y cómo los resolvimos
- Sin errores: la migración se generó y aplicó a la primera.

## Verificación
- [x] `uv run python manage.py makemigrations` → `Migrations for 'core': core/migrations/0003_proveedor_materiaprima.py` (Proveedor + MateriaPrima)
- [x] `uv run python manage.py migrate` → `Applying core.0003_proveedor_materiaprima... OK`
- [x] `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- [x] `uv run python manage.py makemigrations --check --dry-run` → `No changes detected`
- [x] En el shell: `MateriaPrima()` instanciada sin argumentos toma `stock=0` y `unidad="KG"` por los `default`.
