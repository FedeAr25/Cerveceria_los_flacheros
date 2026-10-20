# DRF esencial: guía de estudio y de defensa

**Proyecto:** Cervecería Los Flacheros (EFI 2026). Backend Django 5.2 LTS + Django REST Framework (DRF) 3.17, documentación con drf-spectacular, filtros con django-filter y CORS con django-cors-headers.

**Para quién es:** para vos, que estás arrancando con programación y tenés que construir una API REST y después **defenderla oralmente** frente al docente.

**Cómo usarla:**

1. Leé una sección completa.
2. Hacé el ejercicio del final sin mirar las respuestas.
3. Ensayá en voz alta el bloque `> **Para la defensa:**`. Ahí está la respuesta lista para decir.

**Convención:** todos los ejemplos salen de nuestro backend: la única app `core` (`models.py`, `serializers.py`, `views.py`, `admin.py`, `urls.py`) dentro del proyecto `config`. Los fragmentos de código son de estudio: muestran la idea aplicada al archivo que corresponde.

**Índice:**

1. Qué es una API REST y qué es JSON
2. El flujo de una request
3. Serializers: el traductor
4. ViewSets: CRUD en una clase
5. El Router
6. El patrón de datos anidados (el corazón del proyecto)
7. `@action`: endpoints dentro de un ViewSet
8. Filtros, búsqueda y ordenamiento
9. Paginación
10. Autenticación y permisos
11. Renderers y la API navegable
12. Documentación automática (drf-spectacular)
13. CORS visto desde DRF
14. Errores comunes de DRF y cómo debuggearlos
15. Resumen: qué memorizar para la defensa

---

## 1. Qué es una API REST y qué es JSON

### Explicación en lenguaje llano

Una **API** (interfaz de programación de aplicaciones) es la puerta que abre un sistema para que **otro programa** le pida cosas. No es una pantalla para una persona: es una ventana para otra computadora.

**REST** es un estilo de armar esa puerta, con reglas simples:

- Cada cosa del negocio es un **recurso** (una cerveza, un lote, un pedido) y tiene su propia **URL**, su dirección.
- Para saber qué querés hacer se usa el **verbo HTTP**: `GET` para leer, `POST` para crear, `PUT` y `PATCH` para modificar, `DELETE` para borrar.
- El servidor no se acuerda de vos entre request y request. Cada request se explica sola (por eso el token viaja en cada una).

Un **endpoint** es una URL + un método. Por ejemplo, `GET /api/cervezas/` es un endpoint: "listame las cervezas".

**JSON** (Notación de Objetos JavaScript) es un formato de texto para datos. Se ve así: llaves `{}`, corchetes `[]`, claves entre comillas y valores separados por coma. Ni más ni menos que eso.

**¿Por qué JSON y no objetos de Python?** Porque el frontend está escrito en JavaScript. Python y JavaScript no se entienden entre sí: uno corre en nuestro servidor con Django, el otro corre en el navegador. JSON es el idioma del medio, texto puro que los dos entienden. Además se lee a simple vista en el navegador, lo cual ayuda un montón cuando algo falla.

### Ejemplo con nuestro proyecto

El frontend de Ema pide `GET http://localhost:8000/api/cervezas/` y DRF le contesta con JSON paginado:

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "IPA del Lote 7",
      "descripcion": "IPA con lúpulo Citra en whirlpool",
      "precio": 4500.00,
      "volumen_ml": 473,
      "alcohol_pct": 6.5,
      "stock": 12,
      "tipo": "GRIFO",
      "activo": true,
      "fecha_creacion": "2026-10-01T18:30:00-03:00",
      "estilo": 2,
      "estilo_nombre": "IPA"
    },
    {
      "id": 3,
      "nombre": "Amber de la Casa",
      "descripcion": "Malta tostada y equilibrio",
      "precio": 3800.00,
      "volumen_ml": 330,
      "alcohol_pct": 5.0,
      "stock": 40,
      "tipo": "ENVASE",
      "activo": true,
      "fecha_creacion": "2026-09-12T10:00:00-03:00",
      "estilo": 1,
      "estilo_nombre": "Amber Ale"
    }
  ]
}
```

Traducción al lenguaje llano: "hay 2 cervezas en total, no hay más páginas, y acá están". Cada objeto del array `results` es una fila de la tabla `core_cerveza` traducida a JSON.

Los códigos de respuesta (el "estado" que devuelve el servidor) que vamos a ver todo el tiempo:

| Código | Qué significa | Ejemplo nuestro |
|---|---|---|
| 200 | Todo bien, acá tenés | `GET /api/cervezas/` |
| 201 | Creado | `POST /api/cervezas/` con JSON válido |
| 204 | Borrado, sin contenido | `DELETE /api/cervezas/1/` |
| 400 | El dato que mandaste es inválido | `POST` con `precio: "caro"` |
| 401 | No me dijiste quién sos | `GET /api/cervezas/` sin token |
| 403 | Sos quién decís ser, pero no podés | `GET /api/pedidos/estadisticas/` sin ser staff |
| 404 | Eso no existe | `GET /api/cervezas/999/` |
| 405 | Ese método no va en esa URL | `POST /api/pedidos/1/` |
| 500 | Se rompió algo del servidor | Error con traceback |

> **Para la defensa:**
> "Una API es la interfaz que expone el sistema para que otro programa, en este caso el frontend Next.js, le pida datos. REST es un estilo donde cada cosa del negocio es un recurso con su URL, y se maneja con los verbos HTTP: GET para leer, POST para crear, PATCH para modificar parcialmente y DELETE para borrar. JSON es el formato en el que viajan los datos porque el frontend es JavaScript y no entiende objetos de Python: JSON es texto neutro que lo entienden los dos. Ejemplo: `GET /api/cervezas/` devuelve un listado paginado de cervezas en JSON."

### Ejercicio para comprobar que lo entendiste

1. El frontend quiere crear un pedido nuevo. ¿Qué método y qué URL usa?
2. ¿Por qué el backend no le manda un archivo `.py` con las cervezas al frontend?
3. Mandaste `GET /api/cervezas/999/` y llegaste 404. ¿Qué significa?

<details>
<summary>Respuesta</summary>

1. `POST /api/pedidos/`, con el pedido en el body en formato JSON. La respuesta correcta sería 201.
2. Porque el frontend corre en JavaScript en el navegador y no puede "importar" ni ejecutar Python. JSON es texto que ambos lenguajes entienden, y además se lee a mano para debuggear.
3. Que la cerveza con id 999 no existe en la base. El recurso pedido no está, y eso está bien: el backend contestó 404 en lugar de inventar datos o devolver un 500.

</details>

---

## 2. El flujo de una request

### Explicación en lenguaje llano

Una **request** (o petición) es el pedido que hace el frontend al backend, y la **response** es la respuesta. Cuando el navegador o el `fetch` piden una URL, Django no adivina: sigue una cadena de pasos en un orden fijo. Entender ese orden es la diferencia entre "sé usar DRF" y "sé explicar DRF".

Los pasos, en orden:

1. **Routing**: Django mira la URL y decide qué vista la atiende. Acá manda `config/urls.py` y después `core/urls.py` con el `DefaultRouter`.
2. **Autenticación**: DRF mira los headers de la request e intenta descubrir quién sos. Si mandaste `Authorization: Token 9944...`, sos un usuario concreto. Si no mandaste nada, sos anónimo.
3. **Permisos**: recién ahora se decide si ese usuario puede hacer eso. Si no puede, corta de entrada con 401 o 403 y la vista nunca se ejecuta.
4. **Serializer de entrada**: para un `POST` o `PUT`, DRF arma el serializer y valida el body JSON contra el modelo. Si algo está mal, devuelve 400 y tampoco toca la base.
5. **Vista**: corre la acción (`list`, `create`, etc.), que arma el `queryset` y aplica filtros, búsqueda, orden y paginación.
6. **Serializer de salida**: convierte los objetos Django en diccionarios y después en JSON.
7. **Renderer**: alguien tiene que escribir el texto final. Si el cliente pidió JSON, lo escribe `JSONRenderer`; si pidió HTML (el navegador), lo escribe `BrowsableAPIRenderer`.

Un detalle fino que conviene tener listo: **en DRF se autentica antes de permisar**. Los permisos necesitan saber quién sos (`request.user`) para responder. A veces se dice "primero permisos" como atajo conceptual, pero el orden real es autenticación, después permisos.

### Ejemplo con nuestro proyecto

Diagrama completo de lo que pasa cuando el frontend pide pedidos con token:

```
  Frontend Next.js (localhost:3000)  o  el navegador
        |
        |  GET http://localhost:8000/api/pedidos/
        |  Header: Authorization: Token 9944b0...
        v
 [1] Django recibe la request y ejecuta el MIDDLEWARE
        |      (CorsMiddleware, SessionMiddleware, ...)
        v
 [2] ROUTING: config/urls.py  ->  core/urls.py (DefaultRouter)
        |      matchea: /api/pedidos/  ->  PedidoViewSet, accion "list"
        v
 [3] AUTENTICACION: se lee el header  ->  nace request.user
        |      token valido -> user real
        |      sin token    -> user anonimo
        v
 [4] PERMISOS: IsAuthenticated (global)
        |      si NO pasa -> 401 o 403 y aca termina el viaje
        v
 [5] SERIALIZER de entrada: get_serializer_class()
        |      accion "list"    -> PedidoNestedSerializer (solo lectura)
        |      accion "create"  -> PedidoSerializer (valida el body)
        v
 [6] VISTA: get_queryset() + filtros + busqueda + orden + pagina
        |
        v
 [7] SERIALIZER de salida: objetos Django -> dict -> JSON
        |
        v
 [8] RENDERER: JSONRenderer (o BrowsableAPIRenderer si pediste HTML)
        |
        v
 200 OK   { "count": 2, "next": null, "previous": null, "results": [...] }
```

Dos cosas que valen la pena remarcar de nuestro `settings.py`:

- El `MIDDLEWARE` es la cadena de procesos que atraviesa cada request antes de llegar a DRF. Por eso `CorsMiddleware` va primero: si no, no puede responder los pedidos de CORS.
- `DEFAULT_PERMISSION_CLASSES` y las demás claves de `REST_FRAMEWORK` son el **valor por defecto** de todo el proyecto: cada ViewSet arranca con esas reglas y solo las cambia si declara las suyas.

### Ejercicio para comprobar que lo entendiste

1. Poner en orden: serialización, permisos, routing, autenticación, vista.
2. El frontend pide `GET /api/pedidos/` sin token. ¿En qué paso se corta el viaje y con qué código?
3. El frontend manda un `POST /api/pedidos/` con `estado: "NO_EXISTE"`. ¿En qué paso se detecta y con qué código?

<details>
<summary>Respuesta</summary>

1. Routing, autenticación, permisos, vista, serialización. (Si dijiste "permisos antes que autenticación", aclará en la defensa que los permisos necesitan a `request.user`, que nace en la autenticación.)
2. Se corta en el paso 4 (permisos): `IsAuthenticated` ve un usuario anónimo y devuelve **401**.
3. Se corta en el paso 4 o 5, según el caso: DRF valida el `choices` del campo y devuelve **400** con algo como `{"estado": ["\"NO_EXISTE\" is not a valid choice."]}`. La base no se toca.

</details>

---

## 3. Serializers: el traductor

### Explicación en lenguaje llano

Un **serializer** es la clase que traduce en las dos direcciones:

- **Salida**: objeto Django (`Cerveza`) -> diccionario -> JSON.
- **Entrada**: JSON -> diccionario validado -> objeto Django.

Y valida en el medio. Si llega JSON malo, el serializer devuelve **400** antes de que se escriba una sola fila en la base. Ese es su superpoder: no es un simple conversor, es un filtro con autoridad.

**`ModelSerializer`** es el atajo de DRF: le pasás el modelo y él solo infiere los campos, los tipos y las validaciones. Sin él, habría que declarar campo por campo a mano.

Para qué sirve aparte de traducir:

| Trabajo del serializer | Ejemplo nuestro |
|---|---|
| Controlar qué campos se exponen | No exponer campos internos o sensibles |
| Marcar campos de solo lectura | `id`, `fecha_creacion`, `subtotal` |
| Renombrar o aplanar | `cliente_nombre` desde `cliente.nombre_completo` |
| Validar | precio positivo, `puntaje` entre 1 y 5, nombre único |
| Anidar | `etapas` dentro de un lote, `lineas` dentro de un pedido |

**`fields = "__all__"` contra una lista explícita.** La primera opción incluye todos los campos del modelo de una. Es rápida, pero expone todo lo que el modelo tenga, aunque no lo quieras. La lista explícita tarda dos minutos más y deja a la vista qué expone la API. Para una defensa, la lista explícita se explica sola: "expongo estos campos y ninguno más".

| | `fields = "__all__"` | Lista explícita |
|---|---|---|
| Velocidad de escritura | Inmediata | Hay que escribir los campos |
| Control | Ninguno | Total |
| Riesgo | Exponés un campo sin querer | Casi nulo |
| Documentación Swagger | Muestra todo | Muestra exactamente lo que la API devuelve |

**`read_only=True`** dice "esto se muestra pero no se acepta del cliente". Lo usamos para lo que calcula Django: `id` lo pone la base, `fecha_creacion` es `auto_now_add`, y `subtotal` lo calcula el modelo. Si alguien manda `subtotal` en un `POST`, DRF lo ignora. Si un campo es solo lectura, además no figura como obligatorio al crear.

**`source=`** dice "este campo sale de otro lado". Ejemplos: `source="estilo.nombre"` trae el nombre del estilo asociado, y `source="cliente.nombre_completo"` trae un `@property` del modelo `Cliente` (más abajo lo vemos completo).

**`many=True` y `read_only=True` juntos.** Para relaciones que son varias (un lote tiene muchas etapas, un pedido tiene muchas líneas) se declara el serializer hijo con `many=True` (son muchos) y `read_only=True` (el padre no crea hijos desde ahí). Lo vemos entero en la sección 6.

**`PrimaryKeyRelatedField`, `SlugRelatedField` y por qué el `id` es más simple.** Cuando un modelo tiene una FK, `ModelSerializer` la convierte solo en un `PrimaryKeyRelatedField`: acepta el `id` y verifica que exista. Es lo más liviano posible: el JSON manda `"estilo": 2` y listo. Alternativas:

| Campo | Ejemplo de JSON | Cuándo conviene |
|---|---|---|
| `PrimaryKeyRelatedField` (por defecto) | `"estilo": 2` | Siempre, y para el frontend es lo más simple |
| `SlugRelatedField` | `"estilo": "IPA"` | Cuando el cliente prefiere mandar un nombre legible |
| Serializer anidado | `"estilo": {"id": 2, "nombre": "IPA"}` | Solo para lectura, cuando el cliente necesita ver el objeto |

**`extra_kwargs`** es un diccionario para ajustar campos sin declararlos a mano: poner `read_only`, un mínimo, o reemplazar los validadores que DRF puso solo.

**Validación, de menor a mayor:**

| Nivel | Cómo se declara | Ejemplo nuestro |
|---|---|---|
| Validador de campo | `validators` (del modelo o del serializer) | `Opinion.puntaje` con `MinValueValidator(1)` y `MaxValueValidator(5)` |
| `UniqueValidator` | DRF lo agrega solo si el campo es `unique=True` | `Cerveza.nombre`, `Cliente.email`, `Lote.numero` |
| `validate_<campo>` | Método por campo, valida un solo campo | `validate_precio`: "el precio tiene que ser mayor a cero" |
| `validate()` | Método general, valida campos entre sí | `validate`: "fecha_fin no puede ser anterior a fecha_inicio" |

Si el campo es `unique=True` en el modelo, el `ModelSerializer` ya agrega un `UniqueValidator` automáticamente. Podés reemplazarlo con `extra_kwargs` para personalizar el mensaje.

### Ejemplo con nuestro proyecto

El serializer completo de `Cerveza`, en `core/serializers.py`:

```python
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Cerveza


class CervezaSerializer(serializers.ModelSerializer):
    # source: no es un campo del modelo, lo calculo desde la FK estilo
    estilo_nombre = serializers.CharField(source="estilo.nombre", read_only=True)

    class Meta:
        model = Cerveza
        fields = [
            "id", "nombre", "descripcion", "precio", "volumen_ml",
            "alcohol_pct", "stock", "tipo", "activo",
            "fecha_creacion", "estilo", "estilo_nombre",
        ]
        extra_kwargs = {
            # la pone Django con auto_now_add: no se puede escribir
            "fecha_creacion": {"read_only": True},
            # mínimo en el stock, sin escribir un método entero
            "stock": {"min_value": 0},
            # personalizo el mensaje del validador único que DRF agrega
            "nombre": {
                "validators": [
                    UniqueValidator(
                        queryset=Cerveza.objects.all(),
                        message="Ya existe una cerveza con ese nombre.",
                    )
                ]
            },
        }

    def validate_precio(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("El precio tiene que ser mayor a cero.")
        return valor
```

Lectura de ese código, paso a paso:

- `fields` es una lista explícita: expongo estos campos y ninguno más. `estilo` queda como `id` numérico porque lo pone `ModelSerializer` solo, y `estilo_nombre` es un extra de lectura para que el frontend no tenga que hacer otra request.
- `fecha_creacion` es `auto_now_add` en el modelo, así que es de solo lectura.
- `validate_precio` corre cuando llega un `precio` en el JSON. Si no pasa, DRF devuelve 400 con `{"precio": ["El precio tiene que ser mayor a cero."]}`.

El serializer de `LineaPedido`, con `subtotal` tomado del `@property` del modelo:

```python
class LineaPedidoSerializer(serializers.ModelSerializer):
    # El modelo tiene @property subtotal (cantidad * precio_unitario).
    # ModelSerializer no incluye properties: hay que declararla a mano,
    # y como es calculada, solo lectura.
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = LineaPedido
        fields = ["id", "cantidad", "precio_unitario", "subtotal", "pedido", "cerveza"]
```

Puntos clave de `LineaPedidoSerializer`:

- `subtotal` **no** es un campo de la tabla: es un `@property` de `LineaPedido`. `ModelSerializer` solo infiere campos del modelo, por eso se declara a mano como `DecimalField` de solo lectura. Al serializar, DRF lee `instance.subtotal` y ejecuta el property.
- Como `subtotal` es `read_only`, nadie puede mandar un subtotal trucho en un `POST`. Siempre sale de `cantidad * precio_unitario`.
- `pedido` y `cerveza` son FK, así que llegan como `id`. Un `POST /api/lineas/` se ve así:

```json
{
  "pedido": 1,
  "cerveza": 2,
  "cantidad": 3,
  "precio_unitario": 5000.00
}
```

La respuesta, con el subtotal calculado por el backend:

```json
{
  "id": 12,
  "cantidad": 3,
  "precio_unitario": 5000.00,
  "subtotal": 15000.00,
  "pedido": 1,
  "cerveza": 2
}
```

Si querés ver cómo quedaría un `SlugRelatedField` (no lo usamos en el contrato, es una variante para entender la diferencia):

```python
class CervezaSerializerVariant(serializers.ModelSerializer):
    estilo = serializers.SlugRelatedField(slug_field="nombre", read_only=True)

    class Meta:
        model = Cerveza
        fields = ["id", "nombre", "precio", "estilo"]
```

Ahí `"estilo"` saldría como `"IPA"` en lugar de `2`. El que manda el JSON es el backend, y nosotros elegimos el `id` porque para el frontend es más simple de guardar y de mandar.

Y el serializer que **no** es de modelo, el de las estadísticas (lo usamos en la sección 7):

```python
class EstadisticasPedidoSerializer(serializers.Serializer):
    total_pedidos = serializers.IntegerField()
    monto_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    pedidos_por_estado = serializers.DictField()
    promedio_ticket = serializers.DecimalField(max_digits=12, decimal_places=2)
```

Un `Serializer` común sirve para respuestas que no salen de una tabla: DRF serializa lo que le pases (hasta un diccionario) y la documentación lo muestra igual.

> **Para la defensa:**
> "El serializer es el traductor y el validador entre el mundo Django y el mundo JSON. En salida convierte objetos del modelo en JSON; en entrada convierte JSON en datos validados, y si el JSON está mal devuelve 400 antes de tocar la base. Además controla qué campos se exponen: por ejemplo `fecha_creacion` es de solo lectura porque la pone Django, `subtotal` es un `@property` del modelo `LineaPedido` que declaro a mano como solo lectura para que nadie mande un subtotal falso, y las FK como `estilo` o `cliente` viajan como `id` porque es lo más simple para el frontend."

### Ejercicio para comprobar que lo entendiste

1. ¿Por qué hay que escribir `subtotal = serializers.DecimalField(...)` a mano si el modelo ya tiene el `@property`?
2. Mandás `POST /api/lineas/` con `"subtotal": 99999`. ¿Qué pasa?
3. ¿Cuál es la diferencia entre `fields = "__all__"` y una lista explícita? ¿Cuál prefieren explicar en la defensa y por qué?
4. ¿Qué hace `source="cliente.nombre_completo"`?

<details>
<summary>Respuesta</summary>

1. Porque `ModelSerializer` infiere desde los campos de la tabla, y un `@property` no es un campo de tabla: es un cálculo de Python. Hay que declararlo a mano y como es calculado, `read_only=True`.
2. DRF lo ignora, porque `subtotal` es de solo lectura. El `subtotal` de la respuesta sale de `cantidad * precio_unitario`, siempre.
3. `"all__"` expone todo lo que tenga el modelo, incluso lo que no querés; la lista explícita expone exactamente lo que declarás. Prefieren la lista porque se puede defender con una frase: "esta API expone estos campos y ninguno más".
4. Que el campo `cliente_nombre` del JSON no está en la tabla: sale del objeto `cliente` asociado, y de ahí del `@property nombre_completo` (nombre + apellido).

</details>

---

## 4. ViewSets: CRUD en una clase

### Explicación en lenguaje llano

Un **ViewSet** es una clase que agrupa todas las operaciones de un recurso en un solo lugar. En lugar de escribir una vista para leer, otra para crear, otra para borrar, escribís una clase y DRF ya trae las acciones armadas.

El más usado es **`ModelViewSet`**, que es un combo de mixins (trozos de código reutilizables) que ya saben leer, crear, modificar y borrar sobre un modelo. Es como una plantilla de CRUD (Crear, Leer, Actualizar, Borrar).

Las acciones que trae armadas son estas. A veces se cuentan 6 acciones de fábrica, y 7 si sumás la acción propia que agregamos con `@action` (sección 7):

| Acción | Método y URL en nuestro proyecto | Qué hace | Código de salida |
|---|---|---|---|
| `list` | `GET /api/pedidos/` | Devuelve la colección, paginada | 200 |
| `create` | `POST /api/pedidos/` | Valida el JSON y crea | 201 |
| `retrieve` | `GET /api/pedidos/1/` | Devuelve un objeto | 200 |
| `update` | `PUT /api/pedidos/1/` | Reemplaza el objeto completo (pide todos los campos) | 200 |
| `partial_update` | `PATCH /api/pedidos/1/` | Modifica solo los campos que mandás | 200 |
| `destroy` | `DELETE /api/pedidos/1/` | Borra | 204 |
| acción propia (`@action`) | `GET /api/pedidos/estadisticas/` | Lógica de negocio que vos definís | 200 |

Dos atributos hacen todo el trabajo pesado:

- **`queryset`**: qué objetos maneja ese ViewSet. `Pedido.objects.all()` o, mejor, con `select_related` para no hacer queries de más.
- **`serializer_class`**: con qué serializer traduce.

Y dos métodos para cambiar eso en caliente:

- **`get_queryset()`**: para devolver un `queryset` distinto según la request (por ejemplo, "solo los pedidos del usuario logueado").
- **`get_serializer_class()`**: para devolver un serializer distinto según la acción. Es el corazón del patrón anidado de la sección 6.

**¿Por qué no escribir vistas a mano?** Porque son 10 modelos. Con vistas a mano serían unas 60 funciones repetidas (list, create, retrieve, update, partial_update, destroy por cada uno). Con ViewSets son 10 clases de pocas líneas, y DRF se encarga del resto: permisos, validación, paginación, códigos de salida y documentación.

### Ejemplo con nuestro proyecto

```python
# core/views.py
from rest_framework import viewsets

from .models import Pedido
from .serializers import PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related("cliente").all()
    serializer_class = PedidoSerializer
    filterset_fields = ["estado", "forma_pago"]
    search_fields = ["cliente__nombre", "cliente__apellido"]
    ordering_fields = ["fecha"]
    ordering = ["-fecha"]
```

Con esas seis líneas tenemos: `GET /api/pedidos/` paginado, `POST`, `GET /api/pedidos/{id}/`, `PUT`, `PATCH`, `DELETE`, permisos globales de `IsAuthenticated`, filtros por `estado` y `forma_pago`, búsqueda por nombre y apellido del cliente, y orden por fecha. Nada de eso se escribió: se declaró.

`get_queryset()` y `get_serializer_class()` se usan cuando la respuesta depende de algo que no sabés al escribir la clase:

```python
class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.select_related("cerveza", "usuario").all()

    def get_serializer_class(self):
        # cambia de serializer según la acción que se esté ejecutando
        if self.action == "list":
            return LoteNestedSerializer
        return LoteSerializer
```

Conviene saber que `get_queryset()` se ejecuta **en cada request**, no una vez al arrancar. Por eso adentro se puede usar `self.request.user` o cualquier dato de la request.

> **Para la defensa:**
> "Un ViewSet agrupa todas las operaciones CRUD de un recurso en una sola clase. `ModelViewSet` trae las acciones armadas: list, create, retrieve, update, partial_update y destroy, y con `@action` agregamos una séptima propia. Con `queryset` declaro qué objetos maneja y con `serializer_class` con qué serializer traduce, y si necesito variarlos por request uso `get_queryset()` y `get_serializer_class()`. Con 10 modelos tenemos 10 ViewSets en lugar de unas 60 vistas sueltas."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué acción atiende `PATCH /api/pedidos/1/` y en qué se diferencia de `PUT`?
2. ¿Qué atributo le dice al ViewSet qué objetos maneja?
3. ¿Por qué conviene un ViewSet por modelo en lugar de vistas escritas a mano?

<details>
<summary>Respuesta</summary>

1. `partial_update`. `PATCH` modifica solo los campos que mandás; `PUT` espera el objeto completo y reemplaza todo.
2. `queryset` (por ejemplo `Pedido.objects.all()`), o `get_queryset()` si cambia según la request.
3. Porque son 6 acciones repetidas por cada modelo: con 10 modelos serían unas 60 funciones. Con ViewSets son 10 clases chicas y DRF hace el trabajo repetido (validación, permisos, paginación, códigos y documentación).

</details>

---

## 5. El Router

### Explicación en lenguaje llano

Un ViewSet no es una vista con URL propia: es una clase con varias acciones. Entonces, ¿quién decide que `GET /api/pedidos/1/` llama a `retrieve` y no a `list`? El **router**.

El router es un objeto que recibe los ViewSets y **genera las URLs solo**, siguiendo convenciones. Nosotros usamos `DefaultRouter`, que además de las URLs crea un índice en `/api/` que lista todos los recursos (eso ayuda mucho al principio de la defensa).

Convenciones del router:

- Cada ViewSet registrado con un prefijo (`r"pedidos"`) produce `/api/pedidos/` para la colección.
- El detalle va con el id al final: `/api/pedidos/1/`.
- **Todas las URLs terminan en barra** (`/api/pedidos/`, no `/api/pedidos`). Si falta la barra, Django redirige, y en un `POST` mal redirigido se puede perder el body. Regla simple: siempre la barra final.
- El `@action` también genera su URL automáticamente (sección 7).

**¿Por qué el router y no escribir `path()` a mano?** Porque las URLs, la documentación y el código no se desincronizan: si registro un ViewSet, aparece en las URLs, en el índice de `/api/` y en Swagger sin tocar nada más. Agregar un recurso nuevo es una línea.

### Ejemplo con nuestro proyecto

Dos archivos trabajando juntos. Primero `core/urls.py`, con el router:

```python
# core/urls.py
from rest_framework.routers import DefaultRouter

from .views import (
    CervezaViewSet,
    ClienteViewSet,
    EstiloViewSet,
    EtapaViewSet,
    LineaPedidoViewSet,
    LoteViewSet,
    MateriaPrimaViewSet,
    OpinionViewSet,
    PedidoViewSet,
    ProveedorViewSet,
)

router = DefaultRouter()
router.register(r"estilos", EstiloViewSet)
router.register(r"cervezas", CervezaViewSet)
router.register(r"lotes", LoteViewSet)
router.register(r"etapas", EtapaViewSet)
router.register(r"proveedores", ProveedorViewSet)
router.register(r"materias-primas", MateriaPrimaViewSet)
router.register(r"clientes", ClienteViewSet)
router.register(r"pedidos", PedidoViewSet)
router.register(r"lineas", LineaPedidoViewSet)
router.register(r"opiniones", OpinionViewSet)

urlpatterns = router.urls
```

Después `config/urls.py`, que le pone el prefijo `/api/` al incluir esas URLs:

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),      # el router (con su índice) queda bajo /api/
    path("api/auth-token/", obtain_auth_token),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
```

Lo importante: el **`include()` en `config/urls.py`** es el que monta las URLs del router bajo `/api/`. El router no sabe nada de `/api/`: lo sabemos nosotros.

Tabla de lo que el router genera a partir de `router.register(r"pedidos", PedidoViewSet)`:

| URL generada | Acción del ViewSet | Métodos |
|---|---|---|
| `/api/pedidos/` | `list` | GET |
| `/api/pedidos/` | `create` | POST |
| `/api/pedidos/{id}/` | `retrieve` | GET |
| `/api/pedidos/{id}/` | `update` | PUT |
| `/api/pedidos/{id}/` | `partial_update` | PATCH |
| `/api/pedidos/{id}/` | `destroy` | DELETE |
| `/api/pedidos/estadisticas/` | `estadisticas` (nuestra, con `@action`) | GET |

Fijate que la acción nuestra (`estadisticas`) compite con `{id}`: el router la resuelve porque `estadisticas` está declarada con `url_path` y DRF la prioriza. Por eso es importante no usar `@action` con `detail=True` y un nombre que podría confundirse con un id.

> **Para la defensa:**
> "El router convierte los ViewSets en URLs por convención: con `DefaultRouter` registramos cada ViewSet con su prefijo y él genera la colección en `/api/pedidos/`, el detalle en `/api/pedidos/{id}/` y las acciones propias. Elegimos el router porque así las URLs, la documentación automática y el código no se desincronizan: registrar un ViewSet lo hace aparecer en el índice de `/api/` y en Swagger sin tocar más nada."

### Ejercicio para comprobar que lo entendiste

1. `router.register(r"cervezas", CervezaViewSet)`. ¿Qué URL tiene el detalle de la cerveza con id 7?
2. ¿Qué pasa si el `fetch` manda `/api/cervezas` sin la barra final?
3. ¿En qué archivo se le pone el prefijo `/api/`?

<details>
<summary>Respuesta</summary>

1. `http://localhost:8000/api/cervezas/7/`, y atiende `retrieve`.
2. Django redirige a la versión con barra. En navegadores a veces pasa, pero en un `POST` puede perderse el body o fallar. Mejor mandar siempre la URL con barra final.
3. En `config/urls.py`, con `path("api/", include("core.urls"))`.

</details>

---

## 6. El patrón de datos anidados (el corazón del proyecto)

### Explicación en lenguaje llano

Esta es la sección que más vas a explicar en la defensa, porque es la que pidió el docente de forma literal: **los datos anidados van SOLO en `list`**. Es decir: en el listado, cada pedido trae sus líneas adentro; en el detalle (`{id}/`), el pedido va plano, sin líneas.

Antes de entender el patrón, hay que entender tres piezas.

**(a) `self.action`.** DRF guarda en la vista, en el atributo `self.action`, el nombre de la acción que está ejecutando: `"list"`, `"retrieve"`, `"create"`, `"update"`, `"partial_update"`, `"destroy"` o el nombre de tu `@action`. Es un string. Con eso, una misma vista puede preguntarse "¿en qué estoy? y responder distinto.

**(b) `get_serializer_class()` y quién lo llama.** DRF, cuando necesita un serializer, no usa `serializer_class` directamente: llama a `self.get_serializer_class()`. Si nosotros sobreescribimos ese método, DRF recibe el que le devolvamos. Y lo llama en cada acción: en `list` llama a `get_serializer()`, en `retrieve` también, en `create` también. Eso significa que **si cambiamos lo que devuelve `get_serializer_class()`, la misma URL cambia de serializer según la acción**.

**(c) El patrón completo.** El corazón es esto:

```python
def get_serializer_class(self):
    if self.action == "list":
        return PedidoNestedSerializer   # con lineas anidadas
    return PedidoSerializer             # plano, para todo lo demás
```

Traducido: "cuando listo, muestro el padre con sus hijos; en el detalle y en las escrituras, el objeto plano".

**¿Por qué anidar en todos lados rompe?** Tres motivos, y los tres valen puntos en la defensa:

1. **Recursión infinita.** Nuestros modelos se referencian entre sí. `EtapaFermentacion` tiene FK a `Lote`, y `Lote` tiene muchas etapas. Si `EtapaFermentacionSerializer` incluyera el lote completo con sus etapas, y el serializer de lote incluyera las etapas... cada etapa traería un lote con etapas con un lote con etapas, hasta que Python revienta con `RecursionError`. Lo mismo con `Pedido` y `LineaPedido`: si la línea trae el pedido completo con sus líneas, y el pedido trae las líneas... ciclo. Y si encima `Cerveza` trajera sus opiniones, y cada opinión su cliente, y el cliente sus pedidos... el ciclo es todavía más fácil de armar.
2. **Payload gigante.** Un listado de 10 pedidos con todas sus líneas, y cada línea con su cerveza y su cliente, puede pesar muchísimo más que lo que el frontend necesita. En una tabla con 500 pedidos, la respuesta se vuelve inservible.
3. **Validaciones cruzadas no deseadas.** Si los hijos anidados fueran escribibles, DRF intentaría crear o modificar hijos desde el padre, con validaciones cruzadas, borrados accidentales y respuestas confusas. Por eso los hijos van con `read_only=True`: se leen, no se escriben desde ahí.

**¿Por qué el `retrieve` va plano?** Porque la consigna lo pide y porque tiene sentido: el listado ya trajo el padre con sus hijos de un vistazo, y el detalle sirve para ver o editar el objeto liviano, sin arrastrar todo. Las escrituras (`POST`, `PUT`, `PATCH`) usan el serializer plano: para crear un pedido se manda `cliente: 3`, y las líneas se crean aparte con `POST /api/lineas/`.

### Ejemplo con nuestro proyecto

Primero los serializers anidados, en `core/serializers.py`:

```python
class LoteNestedSerializer(serializers.ModelSerializer):
    etapas = EtapaFermentacionSerializer(many=True, read_only=True)
    cerveza_nombre = serializers.CharField(source="cerveza.nombre", read_only=True)

    class Meta:
        model = Lote
        fields = [
            "id", "numero", "fecha_inicio", "fecha_fin", "volumen_litros",
            "estado", "notas", "cerveza", "cerveza_nombre", "usuario", "etapas",
        ]


class PedidoNestedSerializer(serializers.ModelSerializer):
    lineas = LineaPedidoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(
        source="cliente.nombre_completo", read_only=True
    )

    class Meta:
        model = Pedido
        fields = [
            "id", "fecha", "estado", "forma_pago", "total",
            "direccion_entrega", "observaciones",
            "cliente", "cliente_nombre", "lineas",
        ]
```

Detalle por detalle:

- `etapas = EtapaFermentacionSerializer(many=True, read_only=True)`: "traé todas las etapas de este lote, como lista, y no las escribas desde acá". `many=True` porque son varias; `read_only=True` porque no queremos escritura anidada.
- `cerveza_nombre` con `source="cerveza.nombre"`: un nombre legible sin obligar al frontend a cruzar datos.
- `cliente_nombre` con `source="cliente.nombre_completo"`: un `@property` del modelo `Cliente`, no un campo de tabla.
- Los campos `cerveza`, `cliente` y `usuario` siguen siendo `id`, para que el frontend pueda mandarlos de vuelta tal cual.

Y el ViewSet que elige el serializer, en `core/views.py`:

```python
class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.select_related("cerveza", "usuario").all()

    def get_serializer_class(self):
        if self.action == "list":
            return LoteNestedSerializer
        return LoteSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related("cliente").all()

    def get_serializer_class(self):
        if self.action == "list":
            return PedidoNestedSerializer
        return PedidoSerializer
```

**Respuesta real de `GET /api/pedidos/`** (el listado, con `lineas` anidadas):

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "fecha": "2026-10-26T18:30:00-03:00",
      "estado": "CONFIRMADO",
      "forma_pago": "TRANSFERENCIA",
      "total": 11000.00,
      "direccion_entrega": "Av. Principal 123",
      "observaciones": "Entrega en el local",
      "cliente": 3,
      "cliente_nombre": "Lucía Fernández",
      "lineas": [
        {
          "id": 10,
          "cantidad": 2,
          "precio_unitario": 5000.00,
          "subtotal": 10000.00,
          "pedido": 1,
          "cerveza": 1
        },
        {
          "id": 11,
          "cantidad": 1,
          "precio_unitario": 2000.00,
          "subtotal": 2000.00,
          "pedido": 1,
          "cerveza": 2
        }
      ]
    }
  ]
}
```

**Respuesta real de `GET /api/pedidos/1/`** (el detalle, plano, sin `lineas`):

```json
{
  "id": 1,
  "fecha": "2026-10-26T18:30:00-03:00",
  "estado": "CONFIRMADO",
  "forma_pago": "TRANSFERENCIA",
  "total": 11000.00,
  "direccion_entrega": "Av. Principal 123",
  "observaciones": "Entrega en el local",
  "cliente": 3
}
```

Comparalas: la primera trae `cliente_nombre` y `lineas` (cada una con su `subtotal` calculado); la segunda es el objeto plano. Lo mismo pasa con lotes: `GET /api/lotes/` trae `etapas` y `cerveza_nombre`, y `GET /api/lotes/1/` va sin `etapas`.

También queda claro qué serializer se usa para escribir: `POST /api/pedidos/` usa `PedidoSerializer` (plano), porque `self.action` es `"create"`, no `"list"`. Y `POST /api/lineas/` crea las líneas una por una.

> **Para la defensa:** (este es el bloque a ensayar más veces)
> "El docente pidió que los datos anidados aparezcan solo en el listado. Lo resolvemos con polimorfismo de serializer: DRF llama a `get_serializer_class()` en cada acción, y nosotros devolvemos `PedidoNestedSerializer` cuando `self.action == "list"` y `PedidoSerializer` en el resto. El nested trae los campos planos del pedido más `lineas` con `many=True, read_only=True` y `cliente_nombre` con `source='cliente.nombre_completo'`. Anidar en todos lados no sirve: por un lado hay recursión, porque nuestros modelos se referencian entre sí (`Pedido` con `LineaPedido`, `Lote` con `EtapaFermentacion`) y entrar en un ciclo infinito rompería la request; por otro el payload se agranda de más, y por otro se abren escrituras anidadas que no queremos. El detalle va plano porque la consigna lo pide y porque así el objeto es liviano; las escrituras también usan el serializer plano."

### Ejercicio para comprobar que lo entendiste

1. En `get_serializer_class()`, ¿qué valor tiene `self.action` cuando el frontend pide `GET /api/pedidos/`? ¿Y en `POST /api/pedidos/`?
2. ¿Qué dos líneas del serializer anidado hacen el trabajo de anidar?
3. Si `LineaPedidoSerializer` incluyera `pedido = PedidoSerializer()`, ¿qué problema aparecería?
4. ¿Qué serializer se usa para `PUT /api/pedidos/1/`?

<details>
<summary>Respuesta</summary>

1. `"list"` en el `GET` del listado; `"create"` en el `POST`.
2. `lineas = LineaPedidoSerializer(many=True, read_only=True)` y `cliente_nombre = serializers.CharField(source="cliente.nombre_completo", read_only=True)`.
3. Recursión infinita: el pedido traería sus líneas, y cada línea traería el pedido con sus líneas, hasta que Python revienta con `RecursionError` y la request cae en 500.
4. `PedidoSerializer`, el plano, porque `self.action` es `"update"`.

</details>

---

## 7. `@action`: endpoints dentro de un ViewSet

### Explicación en lenguaje llano

A veces necesitás una URL que no es CRUD. No querés listar ni crear pedidos: querés las estadísticas de los pedidos. No querés listar cervezas de cualquier tipo: querés las que están en grifo con stock. Esas son operaciones de negocio, no operaciones genéricas sobre un modelo.

El decorador **`@action`** hace exactamente eso: agrega un endpoint extra dentro de un ViewSet, sin crear un modelo nuevo ni una vista suelta. Un **decorador** es la "@" que se pone arriba de un método para agregarle un comportamiento.

Dos modos principales:

| | `detail=False` | `detail=True` |
|---|---|---|
| URL que genera | `/api/cervezas/en_grifo/` | `/api/lotes/1/avanzar/` |
| ¿Pide id en la URL? | No | Sí, va después del prefijo y antes de la acción |
| Para qué sirve | Consulta sobre la colección | Operación sobre un objeto concreto |
| Ejemplos nuestros | `en_grifo`, `estadisticas` | `avanzar` (comprometida, Fase 4 / Task 18) |

Dos atributos que conviene distinguir:

- **`url_path`**: la parte de la URL. Lo escribimos en **snake_case** (`en_grifo`, `estadisticas`) porque es la convención que ya usamos en los query params (`page_size`, `search_fields`) y porque es lo que quedó escrito en el contrato con el frontend. Nunca `enGrifo`, que es estilo JavaScript y mezclaría convenciones.
- **`url_name`**: el nombre interno para reversar la URL (lo usa DRF en la documentación). Si no lo pasás, DRF usa el nombre del método.

Dos detalles prácticos:

- **Serializer de salida propio.** `en_grifo` devuelve cervezas normales, así que usa `CervezaSerializer`. `estadisticas` no devuelve filas de una tabla: devuelve números calculados, así que usa `EstadisticasPedidoSerializer` (un `Serializer` común, no un `ModelSerializer`).
- **`permission_classes` por acción.** Se puede poner permisos solo para esa acción, y reemplazan a los globales para ella. `estadisticas` usa `IsAdminUser`: cualquier usuario autenticado puede listar pedidos, pero solo el staff ve los números agregados.

**¿Por qué no crear un modelo nuevo para cada caso?** Porque `estadisticas` no son datos que se guardan: son un cálculo sobre los pedidos que ya existen. Un modelo `Estadistica` obligaría a migración, admin, serializer, ViewSet y CRUD para datos derivados que en cada request estarían desactualizados. `@action` devuelve el cálculo en vivo con una query.

### Ejemplo con nuestro proyecto

**1. `GET /api/cervezas/en_grifo/`** (obligatoria):

```python
# core/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cerveza
from .serializers import CervezaSerializer


class CervezaViewSet(viewsets.ModelViewSet):
    queryset = Cerveza.objects.select_related("estilo").all()
    serializer_class = CervezaSerializer
    filterset_fields = ["estilo", "tipo", "activo"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["precio", "nombre", "fecha_creacion"]

    @action(detail=False, url_path="en_grifo")
    def en_grifo(self, request):
        queryset = self.get_queryset().filter(
            tipo="GRIFO", activo=True, stock__gt=0
        )
        # paginate_queryset y get_paginated_response respetan la paginación global
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

Dos cosas de ese método:

- `self.get_queryset()` reutiliza el queryset del ViewSet y le agrega el filtro de negocio: `tipo='GRIFO'`, `activo=True` y `stock > 0`.
- `self.paginate_queryset(...)` y `self.get_paginated_response(...)` son métodos de DRF que aplican la paginación global. Así la respuesta tiene la misma forma que cualquier listado: `count`, `next`, `previous`, `results`.

Respuesta JSON:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "IPA del Lote 7",
      "descripcion": "IPA con lúpulo Citra en whirlpool",
      "precio": 4500.00,
      "volumen_ml": 473,
      "alcohol_pct": 6.5,
      "stock": 12,
      "tipo": "GRIFO",
      "activo": true,
      "fecha_creacion": "2026-10-01T18:30:00-03:00",
      "estilo": 2,
      "estilo_nombre": "IPA"
    }
  ]
}
```

**2. `GET /api/pedidos/estadisticas/`** (obligatoria, solo staff):

Primero el serializer de salida, en `core/serializers.py`:

```python
class EstadisticasPedidoSerializer(serializers.Serializer):
    total_pedidos = serializers.IntegerField()
    monto_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    pedidos_por_estado = serializers.DictField()
    promedio_ticket = serializers.DecimalField(max_digits=12, decimal_places=2)
```

Y la acción en `core/views.py`:

```python
from django.db.models import Avg, Count, Sum
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

from .serializers import EstadisticasPedidoSerializer, PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related("cliente").all()
    serializer_class = PedidoSerializer

    @action(detail=False, url_path="estadisticas", permission_classes=[IsAdminUser])
    def estadisticas(self, request):
        queryset = self.get_queryset()
        totales = queryset.aggregate(monto=Sum("total"), promedio=Avg("total"))
        por_estado = {
            fila["estado"]: fila["n"]
            for fila in queryset.values("estado").annotate(n=Count("id"))
        }
        data = {
            "total_pedidos": queryset.count(),
            "monto_total": totales["monto"],
            "pedidos_por_estado": por_estado,
            "promedio_ticket": totales["promedio"],
        }
        serializer = EstadisticasPedidoSerializer(instance=data)
        return Response(serializer.data)
```

Lo que hace esa acción, en lenguaje llano: cuenta los pedidos, suma los totales, calcula el promedio y agrupa por estado, todo con el ORM de Django (`aggregate`, `values`, `annotate`), sin escribir una línea de SQL. El resultado se pasa al serializer como si fuera un objeto, y DRF lo serializa igual.

Respuesta JSON:

```json
{
  "total_pedidos": 25,
  "monto_total": 350000.00,
  "pedidos_por_estado": {
    "PENDIENTE": 4,
    "CONFIRMADO": 10,
    "EN_PREPARACION": 6,
    "LISTO_RETIRO": 2,
    "ENTREGADO": 2,
    "CANCELADO": 1
  },
  "promedio_ticket": 14000.00
}
```

Si un usuario normal (no staff) pide esa URL, la respuesta es **403**, porque `IsAdminUser` se aplica solo a esa acción.

**3. La tercera, `POST /api/lotes/{id}/avanzar/`** (`detail=True`, comprometida en el plan para la Fase 4):

```python
class LoteViewSet(viewsets.ModelViewSet):
    TRANSICIONES = {
        "PLANIFICADO": "EN_PRODUCCION",
        "EN_PRODUCCION": "FERMENTACION",
        "FERMENTACION": "MADURACION",
        "MADURACION": "LISTO",
    }

    @action(detail=True, url_path="avanzar", methods=["POST"])
    def avanzar(self, request, pk=None):
        lote = self.get_object()
        siguiente = self.TRANSICIONES.get(lote.estado)
        if siguiente is None:
            return Response(
                {"detail": f"El lote {lote.numero} no se puede avanzar desde {lote.estado}."},
                status=400,
            )
        lote.estado = siguiente
        lote.save(update_fields=["estado"])
        return Response(LoteSerializer(lote).data)
```

Acá `detail=True` genera `/api/lotes/1/avanzar/` (el `1` es el `pk`), y `methods=["POST"]` deja afuera a `GET`. `self.get_object()` busca el lote con ese id y responde 404 si no existe.

> **Para la defensa:**
> "El decorador `@action` agrega un endpoint de negocio dentro de un ViewSet, sin crear modelos ni vistas nuevas. Con `detail=False` la URL queda en la colección, como `/api/cervezas/en_grifo/` y `/api/pedidos/estadisticas/`; con `detail=True` queda sobre un objeto, como `/api/lotes/1/avanzar/`. Usamos `url_path` en snake_case porque es la convención que ya usamos en los query params y la que quedó en el contrato. `en_grifo` filtra el queryset con `tipo='GRIFO', activo=True, stock > 0` y devuelve cervezas normales paginadas; `estadisticas` devuelve un cálculo con el ORM (`Count`, `Sum`, `Avg`) usando un `Serializer` común, y tiene `permission_classes=[IsAdminUser]` solo para esa acción, porque los números agregados no los ve cualquiera. No creamos un modelo `Estadistica` porque no son datos que se guardan: son un cálculo en vivo."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué URL genera `@action(detail=False, url_path="en_grifo")` en `CervezaViewSet`? ¿Y `@action(detail=True, url_path="avanzar")` en `LoteViewSet`?
2. ¿Por qué `estadisticas` necesita un serializer que no es `ModelSerializer`?
3. ¿Por qué `en_grifo` usa `url_path="en_grifo"` y no `urlPath="enGrifo"` ni `url_path="enGrifo"`?

<details>
<summary>Respuesta</summary>

1. `GET /api/cervezas/en_grifo/` (sin id) y `POST /api/lotes/{id}/avanzar/`, por ejemplo `POST /api/lotes/1/avanzar/`.
2. Porque no devuelve filas de una tabla: devuelve cuatro valores calculados (`total_pedidos`, `monto_total`, `pedidos_por_estado`, `promedio_ticket`). Un `ModelSerializer` traduce un modelo; acá usamos un `Serializer` común que serializa un diccionario.
3. Porque `url_path` es la parte de la URL, y una URL es un recurso: se escribe en snake_case, igual que los query params (`page_size`). `enGrifo` sería convención JavaScript y mezclaría estilos en la misma API.

</details>

---

## 8. Filtros, búsqueda y ordenamiento

### Explicación en lenguaje llano

Los tres sirven para que el frontend pida **parte** de la colección en lugar de la colección entera. Los tres se configuran en el ViewSet y los tres actúan sobre el `queryset`, antes de paginar.

| Backend | Query param | Qué hace | Ejemplo |
|---|---|---|---|
| `DjangoFilterBackend` | `?campo=valor` | Filtra por igualdad en campos concretos | `?tipo=GRIFO` |
| `SearchFilter` | `?search=texto` | Busca "como si contuviera" en los campos de búsqueda | `?search=ipa` |
| `OrderingFilter` | `?ordering=campo` | Ordena, con `-` para descendente | `?ordering=precio` |

Los tres están en `DEFAULT_FILTER_BACKENDS` de `settings.py`, así que están disponibles en todos los ViewSets; a cada ViewSet le falta declarar **qué** campos filtra, busca y ordena.

**`filterset_fields` (atajo) contra `filterset_class` (FilterSet propio).**

- `filterset_fields = ["estilo", "tipo", "activo"]` es el atajo: por cada campo, django-filter arma un filtro que compara por igualdad.
- `filterset_class = CervezaFiltros` es el camino largo: una clase `FilterSet` propia, para cuando querés reglas más ricas (mínimos, máximos, rangos de fechas).

**No se pueden usar los dos juntos.** Si los declarás en el mismo ViewSet, django-filter levanta `ImproperlyConfigured`: no sabe cuál de los dos mandó. Elegí uno.

**Cómo busca DRF.** `SearchFilter` compara con "contiene" por defecto, y respeta prefijos en los campos de búsqueda:

| Prefijo | Significado | Ejemplo |
|---|---|---|
| (sin prefijo) | Contiene | `nombre` encuentra "IPA del Lote 7" con `?search=ipa` |
| `^` | Empieza con | `^I` encontraría solo lo que empieza con I |
| `=` | Igual exacto | `=IPA` |
| `@` | Búsqueda de texto completo (full-text) | `@lupulo` |
| `$` | Termina con | `$ale` |

También se puede buscar en un campo de otra tabla con `__`: por eso `/api/pedidos/` tiene `search_fields = ["cliente__nombre", "cliente__apellido"]`.

**`ordering_fields` y por qué hay que restringirlo.** Si no lo declarás, DRF deja ordenar por cualquier campo del serializer. Conviene restringirlo por tres motivos: controlar qué puede pedir el cliente, evitar ordenar por campos de texto enormes que son lentos en la base, y dejarle al frontend un menú claro de opciones ordenables. Un `ordering` que no esté en la lista **se ignora**, no rompe.

### Ejemplo con nuestro proyecto

El ViewSet de `Cerveza`, completo:

```python
class CervezaViewSet(viewsets.ModelViewSet):
    queryset = Cerveza.objects.select_related("estilo").all()
    serializer_class = CervezaSerializer

    filterset_fields = ["estilo", "tipo", "activo"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["precio", "nombre", "fecha_creacion"]
    ordering = ["-fecha_creacion"]   # orden por defecto si no mandan ?ordering=
```

Y la variante con un `FilterSet` propio (mismo resultado que el atajo, para ver la diferencia):

```python
# core/filters.py
import django_filters

from .models import Cerveza


class CervezaFiltros(django_filters.FilterSet):
    class Meta:
        model = Cerveza
        fields = ["estilo", "tipo", "activo"]
```

```python
from .filters import CervezaFiltros

class CervezaViewSet(viewsets.ModelViewSet):
    queryset = Cerveza.objects.select_related("estilo").all()
    serializer_class = CervezaSerializer
    filterset_class = CervezaFiltros      # en vez de filterset_fields
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["precio", "nombre", "fecha_creacion"]
```

En el proyecto real usamos el atajo `filterset_fields`; el `FilterSet` propio queda como la opción para filtros más expresivos.

Query strings reales contra nuestro backend:

| Query string | Qué hace | Endpoint |
|---|---|---|
| `?tipo=GRIFO` | Solo cervezas de tipo GRIFO | `/api/cervezas/` |
| `?estilo=2` | Solo las cervezas del estilo con id 2 | `/api/cervezas/` |
| `?search=ipa` | Cuy nombre o descripción contenga "ipa" | `/api/cervezas/` |
| `?ordering=precio` | De menor a mayor precio | `/api/cervezas/` |
| `?ordering=-precio` | De mayor a menor precio | `/api/cervezas/` |
| `?tipo=GRIFO&search=ipa&ordering=-fecha_creacion` | Los tres a la vez | `/api/cervezas/` |
| `?estado=CONFIRMADO` | Pedidos confirmados | `/api/pedidos/` |
| `?search=fernandez` | Pedidos cuyo cliente tenga "fernandez" en nombre o apellido | `/api/pedidos/` |
| `?lote=1` | Las etapas del lote 1 | `/api/etapas/` |
| `?proveedor=3` | Las materias primas del proveedor 3 | `/api/materias-primas/` |
| `?page=2&page_size=5` | Página 2, 5 elementos por página | Cualquiera |

Dos detalles que se preguntan seguido:

- Los filtros por FK se mandan con el **id**: `?estilo=2`, no `?estilo=IPA`. Para los campos con `choices` se mandan los valores exactos, en mayúsculas: `?estado=CONFIRMADO`, `?tipo=GRIFO`, `?forma_pago=TARJETA`.
- El `search` no distingue mayúsculas, pero tampoco normaliza acentos: `?search=fernandez` no encuentra "Fernández". Si el frontend busca por nombres de clientes, conviene tenerlo en cuenta.
- El orden de aplicación es: filtros, después búsqueda, después orden, y recién después paginar. Todos actúan sobre el mismo `queryset`, así que se pueden combinar.

> **Para la defensa:**
> "Tenemos tres filter backends declarados en `DEFAULT_FILTER_BACKENDS`: `DjangoFilterBackend` para filtros de igualdad con `filterset_fields`, `SearchFilter` con `search_fields` y `OrderingFilter` con `ordering_fields`. El requisito de filtros y búsquedas se cumple en `/api/cervezas/`: filtra por `estilo`, `tipo` y `activo`, busca en `nombre` y `descripcion`, y ordena por `precio`, `nombre` y `-fecha_creacion`. Los tres backends actúan sobre el `queryset` antes de paginar, y se pueden combinar, por ejemplo `?tipo=GRIFO&search=ipa&ordering=-fecha_creacion`. `ordering_fields` lo restringimos a propósito: un orden que no está en la lista se ignora, y así evitamos que el cliente pida ordenar por cualquier campo."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué hace `GET /api/cervezas/?estilo=2&ordering=-precio`?
2. ¿Por qué `search_fields` de `/api/puedidos/` usa `cliente__nombre` con dos guiones bajos?
3. ¿Qué pasa si mandás `?ordering=descripcion` y `descripcion` no está en `ordering_fields`?
4. ¿Por qué no se puede usar `filterset_fields` y `filterset_class` en el mismo ViewSet?

<details>
<summary>Respuesta</summary>

1. Trae solo las cervezas del estilo con id 2, ordenadas de mayor a menor precio.
2. Porque el campo está en otra tabla: `cliente__nombre` significa "el nombre del cliente asociado". Los guiones bajos cruzan relaciones.
3. DRF lo ignora: devuelve la respuesta con el orden por defecto, sin error.
4. Porque django-filter no sabe cuál de los dos es la fuente de verdad y levanta `ImproperlyConfigured`. Se usa uno u otro.

</details>

---

## 9. Paginación

### Explicación en lenguaje llano

**Paginación** es partir un listado en trozos. Si el backend tuviera 500 pedidos y `GET /api/pedidos/` devolviera los 500 juntos, la respuesta sería enorme, lenta y probablemente se colgara el navegador. Con paginación, el frontend pide una página por vez.

Nosotros usamos **`PageNumberPagination`**: paginación por número de página. Pedís la página 1, la 2, la 3, y el backend te devuelve un trozo con el número total de resultados.

La respuesta no es un array pelado: es un objeto con cuatro claves.

```json
{
  "count": 137,
  "next": "http://localhost:8000/api/pedidos/?page=2",
  "previous": null,
  "results": []
}
```

| Clave | Qué es |
|---|---|
| `count` | Total de elementos en toda la colección, no de esta página |
| `next` | URL de la página siguiente, o `null` si es la última |
| `previous` | URL de la página anterior, o `null` si es la primera |
| `results` | El array con los elementos de esta página |

Tres configuraciones que conviene poder explicar:

| Config | Valor nuestro | Qué hace |
|---|---|---|
| `page_size` | 10 | Cuántos elementos por página, por defecto |
| `page_size_query_param` | `"page_size"` | Nombre del query param con el que el cliente puede pedir otro tamaño |
| `max_page_size` | 50 | Tope: si alguien pide `?page_size=1000`, se trunca a 50 |

**¿Por qué el docente la exige?** Porque es lo que hace cualquier API de producción. Paginar evita respuestas gigantes, protege la base de datos y hace el frontend más rápido. Una API sin paginación es una de las primeras cosas que un evaluador nota.

**¿Qué le implica al frontend?** Que no piense en "el array de pedidos", sino en "la página de pedidos". Tiene que leer `count` para saber cuántas páginas hay, usar `next` y `previous` para navegar, y respetar el tope de 50.

### Ejemplo con nuestro proyecto

La clase de paginación propia que usamos en `config/settings.py`:

```python
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


REST_FRAMEWORK = {
    # ... el resto de la config ...
    "DEFAULT_PAGINATION_CLASS": "config.settings.DefaultPagination",
}
```

(`DEFAULT_PAGINATION_CLASS` le dice a DRF qué clase usar en todos los ViewSets. El tamaño no se configura con la clave `"PAGE_SIZE"` del dict: vive únicamente en la clase, `page_size = 10`, junto a `page_size_query_param` y `max_page_size`.)

Ejemplo real: `GET /api/pedidos/?page=2&page_size=5`.

```json
{
  "count": 137,
  "next": "http://localhost:8000/api/pedidos/?page=3&page_size=5",
  "previous": "http://localhost:8000/api/pedidos/?page=1&page_size=5",
  "results": []
}
```

Traducción: "hay 137 pedidos en total; con 5 por página serían 28 páginas; esta es la segunda". Y si el frontend manda `?page_size=500`, el backend trunca a 50 y no rompe nada.

Un caso que conviene conocer: `GET /api/pedidos/?page=999` responde **404** con `{"detail": "Invalid page."}`, porque esa página no existe. No es un error del frontend de "no encontró el endpoint": es "esa página no tiene elementos".

> **Para la defensa:**
> "Usamos una clase propia de paginación, `DefaultPagination` (en `config/settings.py`), con `page_size = 10`, `page_size_query_param = "page_size"` y `max_page_size = 50`. La respuesta no es un array sino un objeto con `count`, `next`, `previous` y `results`. La clase propia le permite al cliente pedir otro tamaño con `?page_size=` pero con tope de 50, así nadie nos pide la tabla entera. Es lo que hace cualquier API de producción: sin paginación, una tabla grande devolvería una respuesta enorme y lenta."

### Ejercicio para comprobar que lo entendiste

1. Con `count = 137` y `page_size = 10`, ¿cuántas páginas hay?
2. ¿Qué significa que `next` sea `null`?
3. ¿Qué pasa con `?page_size=1000`?
4. Mandaste `?page=999` y llegaste 404. ¿Está bien o es un bug?

<details>
<summary>Respuesta</summary>

1. 14 páginas: 13 de 10 y una última con 7.
2. Que no hay página siguiente: estás en la última.
3. El backend trunca el pedido a `max_page_size = 50`.
4. Está bien: esa página no existe. DRF responde 404 con `{"detail": "Invalid page."}`.

</details>

---

## 10. Autenticación y permisos

### Explicación en lenguaje llano

Dos cosas distintas que se confunden todo el tiempo:

- **Autenticación** = ¿quién sos? DRF mira los headers y arma `request.user`.
- **Permiso** = ¿te dejo hacer esto? DRF mira `request.user` y decide.

Nuestro `settings.py` declara dos formas de autenticarse, y un permiso global:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # ...
}
```

`DEFAULT_PERMISSION_CLASSES` es el permiso por defecto de todo el proyecto: sin identificarse, no se entra a ningún endpoint. Un ViewSet puede reemplazarlo con `permission_classes = [...]`, y una `@action` puede reemplazarlo solo para sí misma.

**Sesión contra token, la comparación que hay que tener clara:**

| | Sesión (`SessionAuthentication`) | Token (`TokenAuthentication`) |
|---|---|---|
| Qué usa el cliente | La cookie de sesión (`sessionid`) | Una cadena opaca en el header |
| Dónde lo guarda el cliente | En las cookies del navegador | En localStorage o en memoria del SPA |
| Cómo viaja | El navegador manda la cookie solo | El frontend manda `Authorization: Token <key>` a mano |
| ¿Pide CSRF? | Sí, DRF exige token CSRF en POST, PUT, PATCH y DELETE | No |
| ¿Para qué lo usamos? | El admin y la API navegable | El frontend Next.js |
| Sin credenciales, DRF responde | 403 | 401 (porque `TokenAuthentication` va primero en la lista) |

**¿Qué hace el servidor en cada caso?** Con sesión, DRF lee la cookie `sessionid`, la busca en la base y con eso identifica al usuario. Con token, lee el header `Authorization`, verifica que empiece con `Token `, busca esa clave en la tabla `authtoken_token` y con eso identifica al usuario.

**Los dos permisos que usamos:**

| Permiso | Qué permite | Dónde lo usamos |
|---|---|---|
| `IsAuthenticated` | Cualquier usuario identificado | Lectura: es el permiso global y aplica a todos los endpoints (sin token, ninguno responde) |
| `IsAdminUser` | Solo el staff | Escritura (crear, editar, borrar) en los catálogos, y la acción `estadisticas` |

La única excepción de la escritura es el mostrador: en `PedidoViewSet` y `LineaPedidoViewSet` no reemplazamos el permiso global, así que cualquier usuario autenticado puede escribir (el bar toma pedidos); en el resto de los catálogos, escribir es cosa del staff.

**Por qué `SessionAuthentication` devuelve 403 y no 401 (la pregunta clásica).** DRF devuelve 401 solo si puede decirle al cliente **cómo autenticarse**, mandando un header `WWW-Authenticate`. Ese header lo aporta la clase de autenticación: `TokenAuthentication` aporta `"Token"`, pero `SessionAuthentication` no aporta nada, porque las cookies no se piden con ese mecanismo. Si DRF no tiene con qué desafiar, baja el código de 401 a 403 para no mentirle al cliente.

Ojo, matiz importante para no trabarse en la defensa: en **nuestro** proyecto `TokenAuthentication` va **primero** en la lista, así que `get_authenticate_header` devuelve `"Token"` y una request sin credenciales responde **401**. El 403 "de sesión" aparece en setups donde la sesión es la única autenticación, y también aparece (en cualquier setup) cuando **sos quién decís ser pero no tenés permiso**: por ejemplo `GET /api/pedidos/estadisticas/` con token de un usuario normal.

Regla práctica para interpretar códigos en nuestro backend:

| Código | Significado |
|---|---|
| 401 | No me dijiste quién sos: falta el token o es inválido |
| 403 | Sos quién decís ser, pero no podés hacer eso (o falló CSRF con sesión) |

**El flujo del login por token.** DRF trae `obtain_auth_token`: una vista que recibe usuario y contraseña y devuelve un token.

1. El frontend hace `POST /api/auth-token/` con `{"username": "demo", "password": "..."}`.
2. El backend responde `{"token": "9944b0..."}`.
3. El frontend guarda ese token (localStorage o memoria) y lo manda en **cada** request: `Authorization: Token 9944b0...`.
4. Si recibe 401, el token ya no sirve: vuelve al login. Si recibe 403, el token sirve pero ese usuario no tiene permiso.

**La trampa de las cookies compartidas entre puertos.** Las cookies **ignoran el puerto**: `localhost:3000` (el frontend) y `localhost:8000` (el backend) son el mismo host, así que comparten cookies. Consecuencia práctica: si el SPA hiciera login por sesión, el navegador mandaría la cookie solo al backend, y DRF exigiría un token CSRF en cada POST o PUT; si el frontend no lo manda, cada escritura responde 403 con "CSRF Failed". Por eso la **decisión del equipo** es simple y se defiende fácil: el frontend usa **solo** `Authorization: Token <key>`, nunca cookies de sesión, y nunca `credentials: "include"`.

### Ejemplo con nuestro proyecto

Login y uso del token con `fetch`, tal cual lo usa Ema:

```javascript
const API = "http://localhost:8000/api";
let token = null;

async function login(username, password) {
  const res = await fetch(`${API}/auth-token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  token = data.token; // guardado en memoria o localStorage
}

async function apiGet(path) {
  const res = await fetch(`${API}${path}`, {
    headers: { Authorization: `Token ${token}` },
  });
  if (res.status === 401) throw new Error("Volvé a iniciar sesión");
  if (res.status === 403) throw new Error("No tenés permiso para esto");
  return res.json();
}

await login("demo", "flacheros2026");
await apiGet("/pedidos/");
```

Lo que pasa por dentro de `GET /api/pedidos/estadisticas/` con un usuario normal:

1. Routing hasta `PedidoViewSet`, acción `estadisticas`.
2. `TokenAuthentication` lee el header y arma `request.user` con el usuario demo. Ahí no hay 401: la autenticación funcionó.
3. La acción declara `permission_classes=[IsAdminUser]`; el usuario demo no es staff.
4. DRF corta con **403**: `{"detail": "You do not have permission to perform this action."}`.

Con un superusuario (staff) los mismos pasos terminan en 200 con las estadísticas.

> **Para la defensa:**
> "Autenticación es quién sos y permiso es si te dejo. Tenemos dos autenticadores: `TokenAuthentication` para el frontend y `SessionAuthentication` para el admin y la API navegable. El frontend solo usa token: `POST /api/auth-token/` devuelve `{token}` y después cada request lleva `Authorization: Token <key>`. Si la respuesta es 401, faltó o falló el token; si es 403, el token es válido pero el usuario no tiene permiso, como en `estadisticas` que usa `IsAdminUser`. Sobre el 403 de sesión: DRF devuelve 401 solo si puede mandar el header `WWW-Authenticate` con el desafío; `SessionAuthentication` no lo manda, entonces DRF baja a 403. En nuestro caso `TokenAuthentication` va primero, así que sin credenciales respondemos 401. Y sobre las cookies: las cookies ignoran el puerto, entonces `localhost:3000` y `localhost:8000` comparten cookies; si el SPA hiciera login por sesión, DRF exigiría CSRF en cada escritura. Por eso el frontend usa solo token y nunca cookies."

### Ejercicio para comprobar que lo entendiste

1. Mandás `GET /api/cervezas/` sin header. ¿401 o 403, y por qué?
2. Mandás `GET /api/pedidos/estadisticas/` con token de un usuario normal. ¿401 o 403?
3. ¿Por qué `SessionAuthentication` responde 403 y no 401?
4. ¿Por qué el frontend no debe loguearse con sesión?

<details>
<summary>Respuesta</summary>

1. **401**: nadie se identificó y `TokenAuthentication`, que va primero, sí aporta el header `WWW-Authenticate: Token`.
2. **403**: la autenticación funcionó, pero `IsAdminUser` pide staff y el usuario no lo es.
3. Porque DRF solo devuelve 401 si puede decirle al cliente cómo autenticarse con `WWW-Authenticate`, y la sesión no se pide con ese header: DRF baja el código a 403.
4. Porque las cookies ignoran el puerto: `localhost:3000` y `localhost:8000` comparten cookies, y DRF exigiría CSRF en cada POST, PUT y DELETE. Con token, todo el viaje se resuelve con el header y no hay CSRF.

</details>

---

## 11. Renderers y la API navegable

### Explicación en lenguaje llano

Un **renderer** es quien escribe el texto final de la respuesta. DRF primero arma los datos y después el renderer los vuelca en el formato que corresponde.

Nuestros settings declaran dos:

```python
"DEFAULT_RENDERER_CLASSES": [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
],
```

| Renderer | Formato | Para quién | Cuándo se activa |
|---|---|---|---|
| `JSONRenderer` | JSON, texto plano | El frontend | Cuando el cliente pide JSON (o no pide nada raro) |
| `BrowsableAPIRenderer` | HTML con interfaz | Una persona | Cuando el navegador pide HTML |

DRF elige según el header `Accept` de la request (eso se llama **negociación de contenido**). El navegador al navegar pide `text/html`, así que recibe la API navegable. Un `fetch` del frontend manda `Accept: */*` y, como `JSONRenderer` va primero en la lista, recibe JSON. Para estar seguros, el frontend puede mandar `Accept: application/json` de forma explícita.

**¿Qué es la API navegable?** Una página HTML que DRF genera en cada endpoint: te muestra los campos, te deja mandar requests con un formulario, te deja cambiar los headers, ver el JSON crudo y hasta loguearte con usuario y contraseña. Es la herramienta de prueba más cómoda que tenemos, y es la que vas a usar para mostrar cosas en la defensa.

**¿Por qué el frontend NO debe usarla?** Porque es HTML para una persona. El frontend necesita JSON. Si en algún fetch terminara recibiendo la página HTML de la API navegable, `res.json()` explotaría. Además, esa página se arma con sesión de navegador, no con token: es el camino del admin, no el del SPA.

### Ejemplo con nuestro proyecto

Abrí `http://localhost:8000/api/pedidos/` en el navegador: ves la lista de campos, el formulario de "POST /api/pedidos", los botones de "GET", "PUT", "DELETE" y la respuesta con su JSON. Eso es `BrowsableAPIRenderer`.

Y esto es lo que hace el mismo endpoint con `fetch` (JSON, silencioso, para la máquina):

```javascript
const res = await fetch("http://localhost:8000/api/pedidos/", {
  headers: {
    Authorization: `Token ${token}`,
    Accept: "application/json",
  },
});
const data = await res.json(); // { count, next, previous, results }
```

Mismo endpoint, dos renderers distintos, según quién pregunte.

> **Para la defensa:**
> "El renderer escribe la respuesta final. Tenemos `JSONRenderer`, que devuelve JSON para el frontend, y `BrowsableAPIRenderer`, que devuelve una interfaz HTML que DRF arma sola en cada endpoint. DRF elige según el header `Accept`: el navegador pide HTML y recibe la API navegable; el `fetch` del frontend pide JSON y recibe JSON. La API navegable la usamos para probar endpoints y para mostrar la API en vivo, pero el frontend nunca la usa porque necesita JSON, no HTML."

### Ejercicio para comprobar que lo entendiste

1. Abrís `/api/cervezas/` en el navegador y ves una página con formularios. ¿Qué renderer la dibujó?
2. ¿Qué le manda el frontend para asegurarse de recibir JSON?
3. ¿Por qué la API navegable no reemplaza a Swagger?

<details>
<summary>Respuesta</summary>

1. `BrowsableAPIRenderer`, porque el navegador pidió HTML con `Accept: text/html`.
2. El header `Accept: application/json`. (Aunque no lo mande, `JSONRenderer` va primero en la lista y termina ganando con `Accept: */*`.)
3. Porque la navegable es una herramienta para probar un endpoint puntual desde el navegador; Swagger es la documentación de toda la API, con todos los endpoints, parámetros y respuestas, pensada para leer y para compartir.

</details>

---

## 12. Documentación automática (drf-spectacular)

### Explicación en lenguaje llano

**OpenAPI** es un archivo que describe una API de forma automática y legible por máquinas: qué endpoints hay, qué parámetros aceptan, qué devuelven y qué códigos pueden devolver. Ese archivo se genera desde el código, así que no se desincroniza.

**Swagger UI** y **ReDoc** son dos lectores de ese archivo: dos formas de ver la documentación con interfaz bonita. Swagger UI es la más conocida y la que vas a mostrar.

El paquete que hace esto en nuestro proyecto es **drf-spectacular**. Él mira nuestros ViewSets, serializers y permisos, y arma el esquema solo.

Las tres URLs que quedaron armadas en `config/urls.py`:

| URL | Qué es |
|---|---|
| `/api/schema/` | El esquema OpenAPI en sí (YAML) |
| `/api/schema/swagger-ui/` | Swagger UI: la interfaz para leerlo |
| `/api/schema/redoc/` | ReDoc: otra interfaz para leerlo |

Para validar que el esquema esté bien formado, desde la terminal:

```bash
uv run python manage.py spectacular --file schema.yml --validate
```

`--file schema.yml` guarda el esquema en un archivo (útil para versionarlo o para pasarlo a herramientas), y `--validate` chequea que sea un esquema OpenAPI válido. Si falla ahí, la documentación está mal armada y hay que arreglarla antes de la entrega.

**Cómo leer un endpoint en Swagger.** Cada endpoint aparece con:

- **Método y path**: `GET /api/pedidos/`.
- **Query parameters**: `page`, `page_size`, `estado`, `forma_pago`, `search`, `ordering`.
- **Request body**: solo en `POST`, `PUT` y `PATCH`, con un ejemplo que se puede copiar y pegar.
- **Responses**: los códigos posibles (`200`, `201`, `400`, `401`, `403`) y el shape de cada uno, incluida la paginación con `count`, `next`, `previous` y `results`.
- **Authorize**: el candadito de arriba a la derecha para cargar el header `Authorization: Token <key>` y probar los endpoints protegidos directamente desde ahí.

**¿Por qué el docente lo pide?** Porque la documentación automática es un requisito de la EFI, y porque demuestra la API completa sin tener que leer el código: con Swagger se ve que existen los 10 endpoints, las 3 acciones, los filtros y los permisos. Es la mejor evidencia para una defensa oral.

### Ejemplo con nuestro proyecto

La configuración que le pone título y versión a Swagger:

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "Cervecería Los Flacheros API",
    "DESCRIPTION": "API REST de gestión de cervecería artesanal.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
```

Y en `settings.py`, la clave que hace que todo funcione:

```python
"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
```

Sin esa clave, DRF usaría su propio esquema y drf-spectacular no podría generar la documentación correcta (sección 14 explica el error típico).

En Swagger, al abrir `GET /api/pedidos/estadisticas/`, vas a ver algo así:

| Qué ves en Swagger | Qué significa |
|---|---|
| `GET /api/pedidos/estadisticas/` | Es una acción propia del ViewSet, no un CRUD |
| Sin query parameters | No acepta filtros ni paginación |
| `200` con `total_pedidos`, `monto_total`, `pedidos_por_estado`, `promedio_ticket` | La forma exacta de la respuesta |
| `403` | Si no sos staff, te responde eso |
| Candadito "Authorize" | Ahí cargás `Token <tu-key>` y lo probás |

> **Para la defensa:**
> "OpenAPI es la descripción automática de la API en un archivo generado desde el código; Swagger UI y ReDoc son dos formas de leerla. Con drf-spectacular generamos `/api/schema/`, la Swagger UI en `/api/schema/swagger-ui/` y ReDoc en `/api/schema/redoc/`. Validamos el esquema con `manage.py spectacular --file schema.yml --validate`. Es un requisito porque deja ver la API completa sin leer el código: los 10 endpoints, las 3 acciones, los parámetros de filtrado, los códigos de respuesta y la autenticación."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué archivo genera `spectacular --file schema.yml` y para qué sirve `--validate`?
2. ¿Dónde se carga el token para probar un endpoint protegido desde Swagger?
3. ¿Qué clave de `settings.py` necesita drf-spectacular para funcionar bien?

<details>
<summary>Respuesta</summary>

1. Genera el esquema OpenAPI en YAML. `--validate` chequea que ese esquema sea válido; si falla, hay que arreglar la documentación.
2. En el candadito "Authorize" de Swagger UI, cargando `Token <tu-key>`.
3. `"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"` dentro de `REST_FRAMEWORK`.

</details>

---

## 13. CORS visto desde DRF

### Explicación en lenguaje llano

El frontend corre en `http://localhost:3000` y el backend en `http://localhost:8000`. Para el navegador, eso son **dos orígenes distintos** (el origen es protocolo + host + puerto), y el navegador tiene una regla de seguridad llamada **política del mismo origen**: un sitio no puede leer respuestas de otro origen, salvo que ese otro origen lo permita explícitamente.

Sin CORS, el `fetch` del frontend a `localhost:8000` falla y en la consola aparece un error del navegador (no del backend) diciendo que el origen está bloqueado por CORS. Detalle importante: el pedido **sí llega** al backend; lo que el navegador hace es **no entregar la respuesta** al JavaScript del frontend.

**`django-cors-headers`** es el paquete que resuelve esto. Es un **middleware**, o sea un proceso que atraviesa cada request antes de llegar a las vistas. Cuando ve que la request viene de un origen permitido, le agrega los headers `Access-Control-Allow-*` que el navegador estaba esperando.

**El preflight `OPTIONS`.** Para pedidos "no simples" (cualquier `POST`, `PUT`, `PATCH` o `DELETE`, y cualquier request que lleva el header `Authorization`), el navegador manda **antes** un pedido de prueba `OPTIONS` preguntando: "¿me dejás mandar este método y estos headers?". El backend responde con los `Access-Control-Allow-*` y recién ahí el navegador manda la request de verdad. Como el frontend usa `Authorization: Token`, **todas** sus requests hacen preflight.

**`CORS_ALLOWED_ORIGINS` contra `CORS_ALLOW_ALL_ORIGINS`.**

| Setting | Qué hace | Cuándo usarlo |
|---|---|---|
| `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]` | Solo ese origen puede llamarnos | Producción y desarrollo en serio: es lo que usamos |
| `CORS_ALLOW_ALL_ORIGINS = True` | Cualquier sitio del mundo puede llamarnos | Solo para una prueba rápida descartable |

Nunca combines `CORS_ALLOW_ALL_ORIGINS = True` con `CORS_ALLOW_CREDENTIALS = True`: el navegador directamente rechaza esa combinación, porque no se puede permitir "todos los orígenes" junto con cookies.

**CORS y CSRF son problemas distintos.** Se confunden porque los dos tocan al navegador, pero atacan cosas opuestas:

| | CORS | CSRF |
|---|---|---|
| Qué protege | De quién se **lee** la respuesta | Que nadie **escriba** haciéndose pasar por el usuario |
| Quién lo aplica | El navegador, con headers del servidor | El servidor, con un token en el body o header |
| Falla visible como | Request bloqueada en la consola del navegador | 403 "CSRF Failed" |
| Nuestro caso | `CorsMiddleware` permite `http://localhost:3000` | No aplica, porque el frontend usa token y no cookies |

### Ejemplo con nuestro proyecto

La configuración en `config/settings.py`:

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",   # SIEMPRE primero
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ...
]

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)
```

Dos reglas de oro:

- `CorsMiddleware` va **primero** en `MIDDLEWARE`. Si va después de `CommonMiddleware`, el preflight `OPTIONS` no llega a timepo y el navegador ve un error de CORS.
- `CORS_ALLOWED_ORIGINS` se lee del `.env`, así que si Ema levanta el frontend en otro puerto, se cambia un archivo de configuración y no se toca código.

Cómo verificarlo con `curl`, sin instalar nada:

```bash
curl -i -X OPTIONS http://localhost:8000/api/cervezas/ ^
  -H "Origin: http://localhost:3000" ^
  -H "Access-Control-Request-Method: POST" ^
  -H "Access-Control-Request-Headers: Authorization"
```

Si está bien configurado, la respuesta trae `Access-Control-Allow-Origin: http://localhost:3000`, `Access-Control-Allow-Methods` y `Access-Control-Allow-Headers` (que debe incluir `Authorization`). Si el origen no está permitido, el preflight responde **403**, pero ese 403 lo manda el middleware de CORS, no DRF: no tiene nada que ver con permisos de usuario.

Si querés ver el problema de un navegador, la forma más rápida es abrir DevTools, pestaña Network, y buscar el request bloqueado con el mensaje de CORS.

> **Para la defensa:**
> "CORS es una política del navegador: `localhost:3000` y `localhost:8000` son orígenes distintos, así que sin permiso explícito el navegador bloquea la lectura de la respuesta. Usamos `django-cors-headers` con `CorsMiddleware` primero en `MIDDLEWARE` y `CORS_ALLOWED_ORIGINS` con el origen exacto del frontend, nunca `CORS_ALLOW_ALL_ORIGINS`. Como el frontend manda `Authorization`, el navegador hace un preflight `OPTIONS` antes de cada request; ese preflight lo responde el middleware, y si el origen no está permitido responde 403 desde ahí. Aclaro que CORS y CSRF son cosas distintas: CORS decide quién puede leer respuestas, CSRF protege escrituras falsificadas; como nuestro frontend usa token y no cookies, no tenemos problema de CSRF."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué es el origen en `http://localhost:3000` y por qué no coincide con el del backend?
2. ¿Qué es el preflight `OPTIONS` y por qué lo dispara el frontend?
3. Mandaste `GET /api/cervezas/` desde el frontend y ves un error de CORS en la consola. ¿El problema está en DRF, en el navegador o en el middleware?
4. ¿Por qué no conviene `CORS_ALLOW_ALL_ORIGINS = True`?

<details>
<summary>Respuesta</summary>

1. El origen es protocolo + host + puerto: `http://localhost:3000`. El backend es `http://localhost:8000`, y cambia el puerto, así que es otro origen.
2. Es un pedido de prueba que el navegador manda antes de un request "no simple" para preguntar si puede usar ese método y esos headers. Se dispara porque el frontend manda `Authorization` en cada request.
3. Está en la configuración del middleware: falta incluir `http://localhost:3000` en `CORS_ALLOWED_ORIGINS` (o `CorsMiddleware` no está primero). DRF no tiene la culpa: el navegador ni entrega la respuesta al JavaScript.
4. Porque cualquiera podría llamar a la API, y además no se puede combinar con `CORS_ALLOW_CREDENTIALS = True`, que el navegador rechaza.

</details>

---

## 14. Errores comunes de DRF y cómo debuggearlos

### Explicación en lenguaje llano

La mayoría de los errores de DRF se diagnostican leyendo **dos cosas**: el código de estado y el cuerpo de la respuesta. Casi siempre el JSON trae una clave `detail` que lo explica.

Flujo de debug corto:

1. Mirá el código (400, 401, 403, 404, 405, 500).
2. Mirá el `detail` de la respuesta.
3. Compará la URL con la de Swagger (es la fuente de verdad).
4. Si es 500, mirá la consola de `runserver`: ahí está el traceback completo.
5. Reproducilo en la API navegable, que te deja cambiar método, body y headers sin escribir código.

Tabla de los errores que vamos a tener, con causa, detección y arreglo:

| Error | Causa típica | Cómo lo detectás | Cómo lo arreglás |
|---|---|---|---|
| **401** | Falta el header o el token es inválido o mal escrito (`Token` con mayúscula y espacio) | `{"detail": "Authentication credentials were not provided."}` con header `WWW-Authenticate: Token` | Pedir token en `POST /api/auth-token/` y mandar `Authorization: Token <key>` en cada request |
| **403** | Autenticado pero sin permiso (`IsAdminUser` sin staff), o CSRF con sesión | `{"detail": "You do not have permission to perform this action."}` | Usar un usuario staff, o token en lugar de sesión |
| **404** | URL mal escrita: falta la barra final, mal prefijo, id inexistente, o `?page=999` | `{"detail": "Not found."}` o `{"detail": "Invalid page."}` | Copiar la URL de Swagger exacta, con la barra final y con un id que exista |
| **405** | Método que esa URL no soporta: `DELETE /api/pedidos/`, `POST /api/pedidos/1/`, `GET /api/lotes/1/avanzar/` | `{"detail": "Method \"DELETE\" not allowed."}` | Mirar en Swagger qué métodos acepta esa URL y usar uno correcto |
| **400** | El serializer rechazó el body: campo obligatorio faltante, tipo mal, `choices` inválido, número negativo | `{"precio": ["Ensure this value is greater than or equal to 0."]}` | Leer el error campo por campo y corregir el JSON |
| **500 con `AttributeError`** | Un `source` mal escrito, o una cadena que pasa por un `None` (por ejemplo `source="cliente.nombre_completo"` con un `cliente` nulo) | Traceback con `AttributeError` o mensaje de DRF sobre el `source` | Revisar el `source`, o declarar el campo con `required=False` y `default=""`, o no atravesar objetos nulos |
| **500 con `ImproperlyConfigured`** | Falta `"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"` en `REST_FRAMEWORK`, o `filterset_fields` y `filterset_class` juntos | El comando `spectacular` o `/api/schema/` revienta al arrancar | Agregar la clave de schema, o elegir uno de los dos métodos de filtrado |
| **404 de `get_object()`** | El objeto no existe, o `get_queryset()` lo filtró y no lo encontró (por ejemplo, pedido de otro usuario) | `{"detail": "Not found."}` viniendo de una acción de detalle | Revisar el `id`, el `lookup_field` y los filtros de `get_queryset()` |

Dos detalles que suelen quedar mal explicados:

- **`404` en un endpoint "mal escrito".** Si el ViewSet no está registrado en el router, o está registrado con otro prefijo (`r"cerveza"` y no `r"cervezas"`), la URL no matchea y Django responde 404 de "no encontré esa ruta". Por eso conviene entrar a `/api/` (el índice del router) y copiar la URL desde ahí o desde Swagger.
- **`405` contra `404`.** Si la URL existe pero el método no: 405. Si ni la URL existe: 404. Por ejemplo `POST /api/pedidos/1/` es 405 (el detalle no crea), y `POST /api/pedidos/` es 201 (la colección sí crea).

### Ejemplo con nuestro proyecto

Algunos escenarios reales y su salida:

**400 por validación**, al crear una cerveza con precio trucho:

```json
{
  "precio": ["Ensure this value is greater than or equal to 0."],
  "estilo": ["Invalid pk \"99\" - object does not exist."]
}
```

Dos errores distintos en la misma respuesta: el precio no pasa el `validate_precio`, y el `estilo` con id 99 no existe en la base. DRF devuelve todos los errores juntos, campo por campo.

**403 en la acción de estadísticas**, con token de usuario normal:

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 de `get_object()`** en `GET /api/lotes/999/`: el router matcheó la URL y la acción `retrieve` corrió, pero `Lote.objects.get(pk=999)` no encontró nada, así que DRF devolvió 404.

**500 por `AttributeError`**, el clásico: escribiste `source="cervezaa.nombre"` (una "a" de más). DRF revienta al serializar con un mensaje que menciona que ese `source` no existe. Se arregla corrigiendo el `source`.

Tres comandos que te salvan antes de la defensa:

```bash
uv run python manage.py check                 # revisa la config sin levantar el server
uv run python manage.py spectacular --file schema.yml --validate
uv run pytest
```

> **Para la defensa:**
> "Ante un error, miro el código y el `detail` de la respuesta. 401 es que no me autentiqué; 403 es que me autentiqué pero no tengo permiso; 400 es que el serializer rechazó el JSON, y ahí DRF me devuelve campo por campo qué falló; 404 es recurso o página inexistente; 405 es un método que esa URL no soporta. Si es 500, miro el traceback en la consola de `runserver`: los más comunes son un `AttributeError` por un `source` mal escrito o por atravesar un objeto nulo, y un `ImproperlyConfigured` por faltar `DEFAULT_SCHEMA_CLASS` en los settings. Y para debuggear uso la API navegable y Swagger como fuente de verdad de las URLs."

### Ejercicio para comprobar que lo entendiste

1. Mandás `DELETE /api/pedidos/` (a la colección) y llegás 405. ¿Por qué?
2. Mandás `GET /api/pedidos/1/` sin el token y llegás 401; con token pero el objeto no existe llegás 404. ¿En qué paso se corta cada uno?
3. `{"detail": "Invalid page."}` con código 404. ¿Qué hiciste mal?
4. ¿Qué mirás primero cuando DRF te devuelve un error?

<details>
<summary>Respuesta</summary>

1. Porque la colección solo acepta `GET` (list) y `POST` (create); `DELETE` no está permitido en `/api/pedidos/`, solo en el detalle `/api/pedidos/{id}/`.
2. El 401 se corta en los permisos, antes de tocar la base: nadie se identificó. El 404 se corta en la vista: la autenticación y los permisos pasaron, pero `get_object()` no encontró el pedido.
3. Mandaste un número de página que no existe, por ejemplo `?page=999`.
4. El código de estado y el campo `detail`. Después comparo la URL con Swagger y, si es 500, miro el traceback de la consola.

</details>

---

## 15. Resumen: qué memorizar para la defensa

### Explicación en lenguaje llano

No hace falta memorizar el código. Hace falta poder decir estas quince frases con seguridad, porque son las que el docente va a perseguir.

### Checklist para la defensa

1. **API REST + JSON.** API = interfaz para que otro programa pida datos; REST = recursos con URL y verbos HTTP; JSON = el formato neutro en el que viajan porque el frontend es JavaScript.
2. **El flujo de una request.** Routing, autenticación, permisos, vista con filtros y paginación, serializer de salida y renderer. Si algo falla antes, corta con 401, 403 o 400.
3. **El serializer es traductor y validador.** Convierte modelos a JSON y JSON a modelos, y si el JSON está mal devuelve 400 antes de tocar la base.
4. **Campos de solo lectura y `source`.** `id` y `fecha_creacion` los pone Django; `subtotal` es un `@property` declarado a mano; `cliente_nombre` sale de `source="cliente.nombre_completo"`.
5. **Relaciones.** Las FK viajan como `id` (`PrimaryKeyRelatedField`), que es lo más simple para el frontend; el anidado es para lectura y con `many=True, read_only=True`.
6. **ViewSets.** `ModelViewSet` da el CRUD completo con 6 acciones armadas; con `queryset` y `serializer_class` declaro qué maneja y cómo traduce, y con `get_queryset()` y `get_serializer_class()` lo varío por request.
7. **Router.** `DefaultRouter` genera las URLs por convención: `/api/prefijo/` y `/api/prefijo/{id}/`, siempre con barra final, y registra todo en el índice y en Swagger.
8. **Anidado SOLO en `list`.** `get_serializer_class()` devuelve `PedidoNestedSerializer` o `LoteNestedSerializer` cuando `self.action == "list"`, y el serializer plano para el resto. Motivos: recursión entre modelos referenciados, payload gigante y escrituras anidadas no deseadas.
9. **`@action`.** Agrega endpoints de negocio: `GET /api/cervezas/en_grifo/` (filtra `tipo='GRIFO'`, `activo=True`, `stock > 0`), `GET /api/pedidos/estadisticas/` (`IsAdminUser`, con `Count`, `Sum` y `Avg`) y `POST /api/lotes/{id}/avanzar/`. No hace falta un modelo nuevo porque son cálculos, no datos guardados.
10. **Filtros, búsqueda y orden.** `filterset_fields`, `search_fields` y `ordering_fields` se aplican al `queryset` antes de paginar, y se pueden combinar en un mismo query string.
11. **Paginación.** Clase propia `DefaultPagination` con `page_size = 10`, `?page_size=` y tope de 50; respuesta con `count`, `next`, `previous` y `results`.
12. **Token y códigos.** `POST /api/auth-token/` devuelve el token; después viaja en `Authorization: Token <key>`. 401 = sin credenciales, 403 = sin permiso.
13. **Sesión, CSRF y la trampa de las cookies.** La sesión pide CSRF; las cookies ignoran el puerto, así que `localhost:3000` y `localhost:8000` comparten cookies; por eso el frontend usa solo token.
14. **CORS.** `CorsMiddleware` primero en `MIDDLEWARE`, `CORS_ALLOWED_ORIGINS` con el origen exacto, preflight `OPTIONS` porque mandamos `Authorization`, y CORS no es CSRF.
15. **Documentación.** drf-spectacular genera `/api/schema/`, Swagger UI y ReDoc, y la validamos con `manage.py spectacular --file schema.yml --validate`.

### Las cinco preguntas que más se repiten

| Pregunta | Respuesta corta |
|---|---|
| ¿Por qué un solo serializer no alcanza? | Porque el listado tiene que traer los hijos y el detalle no: son dos formas distintas de mostrar el mismo modelo. |
| ¿Por qué el anidado solo en `list`? | Recursión, payload gigante y escrituras anidadas no deseadas. |
| ¿Por qué el frontend no usa sesión? | Cookies comparten puerto y DRF exigiría CSRF en cada escritura. |
| ¿401 o 403? | 401: no me dijiste quién sos. 403: sos quién decís ser pero no podés. |
| ¿Por qué un `@action` y no un modelo nuevo? | Porque las estadísticas y el grifo son consultas y cálculos sobre datos que ya existen. |

> **Para la defensa:**
> "Si tengo que resumir el backend en un minuto: 10 modelos en una sola app `core`, 10 ViewSets registrados en un `DefaultRouter` bajo `/api/`, paginación de 10 con tope 50, filtros y búsquedas en los endpoints, autenticación por token con `IsAuthenticated` global (sin token no se lee nada), escritura con `IsAdminUser` salvo en el mostrador (`Pedido` y `LineaPedido`, donde cualquier autenticado escribe), datos anidados solo en el listado con `get_serializer_class()`, tres acciones propias (`en_grifo`, `estadisticas` con `IsAdminUser` y `avanzar`), documentación OpenAPI con drf-spectacular y CORS restrictivo para el frontend de Next.js."

### Ejercicio final para comprobar que lo entendiste

Explicá, en voz alta y sin mirar, estas cuatro situaciones. Si podés, ya estás listo para la defensa.

1. El frontend pide `GET /api/pedidos/` y trae `lineas` adentro. ¿Por qué?
2. Un compañero te dice "hagamos que `/api/cervezas/` traiga sus lotes con sus etapas". ¿Qué le respondés?
3. Un usuario normal pide `/api/pedidos/estadisticas/` y recibe 403. ¿Está roto?
4. Abrís `http://localhost:8000/api/pedidos/` en el navegador y ves HTML con formularios, pero el mismo URL con `fetch` devuelve JSON. ¿Por qué?

<details>
<summary>Respuesta</summary>

1. Porque `get_serializer_class()` devuelve `PedidoNestedSerializer` cuando `self.action == "list"`, y ese serializer trae `lineas` con `many=True, read_only=True` más `cliente_nombre` con `source="cliente.nombre_completo"`.
2. Que no conviene: si cada cerveza trae sus lotes y cada lote sus etapas, el payload del listado crece muchísimo, y si encadenamos relaciones que se referencian entre sí podemos caer en recursión infinita. Para eso está el detalle o el endpoint de lotes, que filtra por cerveza.
3. No. La autenticación funcionó (por eso no es 401), pero `estadisticas` declara `permission_classes=[IsAdminUser]` y ese usuario no es staff. Con un superusuario responde 200.
4. Porque hay dos renderers: el navegador pide `text/html` y `BrowsableAPIRenderer` le devuelve la interfaz HTML; el `fetch` pide JSON (o nada especial, y `JSONRenderer` va primero en la lista) y recibe JSON. Es el mismo endpoint con dos respuestas distintas según quién pregunta.

</details>

