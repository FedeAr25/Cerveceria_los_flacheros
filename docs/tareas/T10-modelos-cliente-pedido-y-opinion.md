# T10 — Modelos Cliente, Pedido, Línea de pedido y Opinión

**Fase:** 2
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Cerramos el modelo con los cuatro modelos de ventas y feedback en `backend/core/models.py`: `Cliente` (ficha con nombre, apellido, email único, DNI, teléfono y fecha de alta), `Pedido` (cabecera de la venta: fecha, estado, forma de pago, total, dirección, observaciones y el cliente), `LineaPedido` (cada renglón: cantidad, precio unitario, el pedido y la cerveza) y `Opinion` (reseña 1-5 estrellas con comentario, de un cliente sobre una cerveza). La migración `0004_cliente_opinion_pedido_lineapedido` los crea en ese orden, que es el de las dependencias: `Pedido` necesita a `Cliente`, `LineaPedido` necesita a `Pedido` y `Cerveza`, y `Opinion` necesita a `Cliente` y a `Cerveza`.

Aparecen dos ideas nuevas que no estaban en los modelos anteriores. La primera es el **precio como snapshot**: `LineaPedido.precio_unitario` no lee el precio de la cerveza, guarda una copia del precio al momento de la venta; así, si mañana subimos el precio de la cerveza, el histórico de los pedidos viejos no se mueve (y `Pedido.total` es un campo guardado por la misma razón: lo calcula la capa de API al crear el pedido y queda congelado). La segunda son las **`@property`**: `Cliente.nombre_completo` y `LineaPedido.subtotal` no son columnas, se calculan cada vez que se los piden y el serializer los va a exponer como campos de solo lectura.

## Conceptos que aparecen acá
- **`PROTECT` en `Pedido.cliente`** — un pedido sin cliente pierde sentido comercial: no se puede borrar un cliente que tiene pedidos; hay que darlo de baja (`activo=False`) o borrar primero sus pedidos. Igual criterio en `LineaPedido.cerveza` (`PROTECT`): no se reescribe una venta borrando la cerveza que se vendió.
- **`CASCADE` en `LineaPedido.pedido`** — las líneas son parte del pedido: si desaparece el pedido, sus renglones quedan huérfanos, así que se borran con él. Mismo criterio en `Opinion.cerveza` y `Opinion.cliente`: una opinión no sobrevive a la cerveza que comenta ni a quien la escribió. Es el patrón "dependiente CASCADE / histórico PROTECT" que usan todos los modelos del proyecto.
- **`@property` (`nombre_completo`, `subtotal`)** — métodos que se leen como si fueran atributos (`cliente.nombre_completo`, `linea.subtotal`) pero no son columnas: no ocupan lugar en la base y se recalculan cada vez que se accede. `nombre_completo` concatena nombre + apellido; `subtotal` multiplica `cantidad * precio_unitario`. El serializer los expone como campos normales de solo lectura.
- **`MinValueValidator` / `MaxValueValidator`** — validadores que Django ejecuta en `full_clean()` y que DRF ejecuta al validar el serializer: en `Opinion.puntaje` rechazan cualquier valor fuera de 1-5. Sin ellos, un 0 o un 9 entraría silenciosamente a la base porque `IntegerField` sólo exige que sea un entero. Es validación (aplica al serializar/validar), no `choices` (que además limita los valores en el admin y da `get_*_display`).
- **`precio_unitario` como snapshot** — la foto del precio al momento de la venta: se copia en la línea y después no se consulta más `Cerveza.precio`. Si el precio se lee de la cerveza, todos los pedidos viejos "revisan" su precio con el de hoy y el histórico miente sobre lo que realmente se cobró.
- **`total` como campo guardado y no recalculado** — `Pedido.total` es un `DecimalField(default=0)` persistido: lo calcula la capa de API (serializers, Fase 4) al crear el pedido y queda congelado. No es un `@property` que sume las líneas en cada lectura, porque esa suma cambiaría si cambian los precios después.
- **`auto_now_add` en dos formatos distintos** — `Pedido.fecha` y `Opinion.fecha` son `DateTimeField` (día y hora: cuándo se concretó la venta / se escribió la reseña) y `Cliente.fecha_alta` también; en `Cerveza` usamos lo mismo para `fecha_creacion`. El patrón es siempre el mismo: se pone solo en el alta y no se toca más.

## Archivos
- `backend/core/models.py` — las clases `Cliente` (con la `@property nombre_completo`), `Pedido`, `LineaPedido` (con la `@property subtotal`) y `Opinion` (con los validators de puntaje).
- `backend/core/migrations/0004_cliente_opinion_pedido_lineapedido.py` — la migración generada: `CreateModel` de `Cliente`, `Pedido`, `LineaPedido` y `Opinion`, en orden de dependencias.

## Lo que hay que mirar en el código
- `backend/core/models.py::LineaPedido.precio_unitario` — el snapshot del precio con su `DecimalField`; ver también `Pedido.total` con el comentario largo que explica por qué es un campo guardado.
- `backend/core/models.py::Cliente.__str__` y `Cliente.nombre_completo` — el `__str__` devuelve una `@property`: ésa es la prueba de que la propiedad existe aunque no sea columna.
- `backend/core/models.py::LineaPedido.subtotal` — la propiedad de dos líneas (`cantidad * precio_unitario`) con el docstring que aclara que el serializer la expone de solo lectura.
- `backend/core/models.py::Opinion.puntaje` — los dos validators y el comentario que dice por qué no es `choices` (acá está la semilla del bug de la sección siguiente).
- `backend/core/models.py::Pedido.cliente` / `LineaPedido.cerveza` / `LineaPedido.pedido` — las tres FK juntas: PROTECT, PROTECT y CASCADE en tres líneas de distancia.

## Para la defensa
> **Pregunta:** ¿Por qué `LineaPedido` guarda el precio si ya está en `Cerveza`?
> **Respuesta:** Es una foto del precio al momento de la venta: si subimos el precio mañana, los pedidos viejos tienen que seguir mostrando lo que realmente se cobró. Por eso el precio se copia en la línea y no se lee de la cerveza; de lo contrario, el histórico de ventas cambiaría retroactivamente cada vez que tocamos el catálogo.

> **Pregunta:** ¿Qué es una `@property`?
> **Respuesta:** Un atributo calculado por Python que no ocupa columna en la base: se recalcula cada vez que se accede (por ejemplo `linea.subtotal` multiplica cantidad por precio en el momento). Como se lee igual que un campo, el serializer puede exponerlo como un campo normal, y en el JSON aparece junto a los demás pero de solo lectura.

## Errores que nos pasaron y cómo los resolvimos
- **Error:** `AttributeError: 'Opinion' object has no attribute 'get_puntaje_display'` al llamar a `str()` sobre una instancia de `Opinion`.
  **Causa:** el `__str__` original usaba `self.get_puntaje_display()`, pero `puntaje` es un `IntegerField` con `validators=[MinValueValidator(1), MaxValueValidator(5)]` y **no** es un campo con `choices`. Django sólo genera los métodos `get_<campo>_display()` para campos que declaran `choices` (por eso `get_tipo_display()` y `get_estado_display()` funcionan en los demás modelos y `get_puntaje_display()` no existe). El error no salta al importar el modelo ni al migrar: sólo aparece cuando algo imprime la opinión (el admin, el shell, el serializer).
  **Solución:** el `__str__` usa el valor directo — `return f"{self.puntaje}★ — {self.cerveza}"` — y se agregó un comentario de dos líneas al lado que documenta la causa, para que no se reintroduzca. Verificado con el smoke test de los 10 modelos: ningún `AttributeError`.

## Verificación
- [x] `uv run python manage.py makemigrations` → `Migrations for 'core': core/migrations/0004_cliente_opinion_pedido_lineapedido.py` (Cliente + Pedido + LineaPedido + Opinion)
- [x] `uv run python manage.py migrate` → `Applying core.0004_cliente_opinion_pedido_lineapedido... OK`
- [x] `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- [x] `uv run python manage.py makemigrations --check --dry-run` → `No changes detected`
- [x] Smoke test (instancia los 10 modelos y llama a `str()`): ningún `AttributeError`; `Estilo`, `Cerveza`, `Proveedor`, `MateriaPrima` y `Cliente` imprimen; `Lote`, `EtapaFermentacion`, `Pedido`, `LineaPedido` y `Opinion` tiran `RelatedObjectDoesNotExist` al instanciarse sin guardar (comportamiento normal de Django con una FK a un objeto que todavía no existe, no un bug).
