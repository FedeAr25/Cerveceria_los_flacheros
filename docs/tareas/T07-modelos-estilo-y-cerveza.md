# T07 — Modelos Estilo y Cerveza

**Fase:** 2
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Arrancamos la Fase 2 escribiendo los dos primeros modelos del dominio en `backend/core/models.py`: `Estilo` (la categoría de cerveza: IPA, Stout, APA, Weizen, con nombre único, IBU, color y un `orden` para mostrarlos en un orden fijo) y `Cerveza` (el producto vendible: nombre único, descripción, precio, volumen en ml, alcohol, stock, tipo ENVASE o GRIFO, si está activo, fecha de creación y el estilo al que pertenece).

Con `makemigrations` Django tradujo las dos clases a la migración `0001_initial`, que crea las tablas `core_estilo` y `core_cerveza` en el SQLite del proyecto; con `migrate` quedaron aplicadas. Esa migración es `initial = True` porque no depende de ninguna otra: es la primera piedra del esquema. Ahí también quedó registrada la primera relación del proyecto: `Cerveza.estilo`, un `ForeignKey` con `on_delete=PROTECT` (no se puede borrar un estilo que ya tiene cervezas cargadas) y `related_name="cervezas"` (que nos deja hacer `estilo.cervezas.all()` desde el shell).

## Conceptos que aparecen acá
- **Modelo y tabla** — un modelo de Django es una clase Python que describe una entidad del negocio; cada modelo se convierte en una tabla de la base (una clase = una tabla, cada atributo = una columna). Django genera el `CREATE TABLE` en la migración, así que no escribimos SQL a mano.
- **`CharField` vs `TextField` vs `IntegerField` vs `DecimalField`** — `CharField` es texto corto con `max_length` (nombre, color); `TextField` es texto largo sin límite razonable (descripción); `IntegerField` es un número entero (IBU, stock, volumen en ml); `DecimalField` es un número con decimales exactos (precio, alcohol). Elegir el tipo correcto importa: la base de datos valida lo que entra.
- **`DecimalField` y no `FloatField` para el precio** — los flotantes son binarios y no representan exactamente 3500,50 ni 0,1: a la larga aparecen errores de redondeo y la suma de ítems no da. Con dinero eso es inaceptable, por eso el precio es `DecimalField(max_digits=10, decimal_places=2)`.
- **`DecimalField(max_digits, decimal_places)`** — `decimal_places` es la cantidad de decimales que guarda (2 en el precio: centavos); `max_digits` es el total de dígitos incluyendo los decimales (10 dígitos con 2 decimales = hasta 99.999.999,99). En `alcohol_pct` usamos `max_digits=4, decimal_places=1` (hasta 99,9 %).
- **`unique=True`** — impone restricción única en la columna: la base rechaza dos filas con el mismo valor (dos estilos llamados "IPA" o dos cervezas con el mismo nombre). Es un garantismo de base de datos, no una validación de Python.
- **`null` vs `blank`** — es la diferencia clave: `null=True` es a nivel de base de datos (la columna admite el valor NULL) y `blank=True` es a nivel de validación (el formulario o validador acepta el campo vacío). Un campo puede ser `blank=True` sin `null=True` (texto vacío en vez de NULL) y viceversa.
- **`default`** — valor que toma el campo si no se pasa ninguno: `orden=0`, `stock=0`, `tipo=Tipo.ENVASE`. Evita que la columna quede indefinida y deja el modelo instanciable sin argumentos.
- **`auto_now_add`** — en `fecha_creacion`: pone la fecha/hora del momento del INSERT y no se toca nunca más. Es el "cuándo se creó"; para "cuándo se modificó" existe `auto_now`.
- **`TextChoices` anidado (`Cerveza.Tipo`)** — una clase dentro del modelo que declara las opciones permitidas ("ENVASE", "GRIFO"). Se usa con `choices=Tipo.choices`, y además habilita dos cosas: `get_tipo_display()` (el texto legible) y el default como `Tipo.ENVASE` en vez de un string suelto.
- **`verbose_name` en español** — el nombre legible del campo/modelo para el admin, los formularios y los mensajes de error. Si no se pasa, Django muestra el nombre del atributo; nosotros los escribimos en español desde el primer modelo.
- **`__str__`** — qué imprime `print(objeto)`: en `Estilo` y `Cerveza` devolvemos `self.nombre`. Sin él, el shell y el admin muestran algo ilegible como `<Cerveza: Cerveza object (3)>`.
- **`Meta.verbose_name_plural`** — el bloque `Meta` configura el modelo; `verbose_name` y `verbose_name_plural` son cómo se llama la cosa en singular y plural ("estilo"/"estilos", "cerveza"/"cervezas") en el admin y en las etiquetas.
- **`ForeignKey` con `PROTECT` y `related_name`** — `ForeignKey` es la columna de relación (una cerveza tiene un estilo). `on_delete=PROTECT` hace que borrar el estilo con cervezas cargadas reviente con un error en vez de borrar en cascada. `related_name="cervezas"` agrega el reverso: `estilo.cervezas.all()`.

## Archivos
- `backend/core/models.py` — las clases `Estilo` y `Cerveza` con sus campos, `Meta`, `__str__` y la relación `Cerveza.estilo`.
- `backend/core/migrations/0001_initial.py` — la migración generada por `makemigrations`: `CreateModel` de `Estilo` y `Cerveza`, con `initial = True` y sin dependencias.

## Lo que hay que mirar en el código
- `backend/core/models.py::Estilo` — el modelo más chico del proyecto: cinco campos, `Meta` con plural y `__str__`; sirve de plantilla para entender la estructura de todos.
- `backend/core/models.py::Cerveza.precio` — el `DecimalField(max_digits=10, decimal_places=2)` que justifica la charla entera de precisión decimal.
- `backend/core/models.py::Cerveza.estilo` — la primera FK: fijarse en el `PROTECT`, el `related_name="cervezas"` y el comentario que explica por qué se protege.
- `backend/core/migrations/0001_initial.py::operations` — cómo cada atributo del modelo aparece traducido a los argumentos del campo en la migración.

## Para la defensa
> **Pregunta:** ¿Por qué el precio es `DecimalField` y no `IntegerField` o `FloatField`?
> **Respuesta:** Porque el precio tiene centavos: con enteros no se puede representar 3500,50. Y con `FloatField` tampoco sirve, porque los flotantes son binarios y redondean (0,1 no existe exacto en coma flotante), lo que con dinero produce diferencias de centavos en las sumas. `DecimalField` guarda decimales exactos, que es lo que pide cualquier sistema de cobro.

> **Pregunta:** ¿Qué significa `null=True, blank=True`?
> **Respuesta:** Son dos capas distintas. `null` controla si la columna admite NULL en la base de datos; `blank` controla si el formulario o el validador acepta el campo vacío. En este proyecto van juntos (`null=True, blank=True`) en los campos opcionales: que la base acepte la nada y que la validación también, para no tener que mandar un valor inventado.

## Errores que nos pasaron y cómo los resolvimos
- Sin errores: la primera migración se generó y aplicó a la primera.

## Verificación
- [x] `uv run python manage.py check` → `System check identified no issues (0 silenced).`
- [x] `uv run python manage.py makemigrations` → `Migrations for 'core': core/migrations/0001_initial.py` (Estilo + Cerveza)
- [x] `uv run python manage.py migrate` → `Applying core.0001_initial... OK`
- [x] `uv run python manage.py makemigrations --check --dry-run` → `No changes detected`
- [x] En el shell: `Estilo(nombre="IPA")` imprime `IPA` (el `__str__` funciona) y una cerveza se puede crear apuntando a un estilo existente.
