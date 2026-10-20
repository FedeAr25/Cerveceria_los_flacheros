# 03 — HTTP, JSON y CORS: el idioma entre nuestro backend y el frontend

> Guía de autoaprendizaje. Equipo: Cervecería Los Flacheros — EFI Ingeniería de Software 2026.
> Backend Django 5.2 + DRF en `localhost:8000`. Frontend Next.js de Ema en `localhost:3000`.
> Leé con calma, hacé los ejercicios y marcá lo que no entendiste. Vas a tener que explicar esto en la defensa.

---

## Qué es HTTP

**HTTP** son las siglas de *HyperText Transfer Protocol* (protocolo de transferencia de hipertexto). Un **protocolo** es un conjunto de reglas que dos computadoras se ponen de acuerdo para hablar. HTTP define cómo un navegador (o cualquier cliente) le pide cosas a un servidor y cómo el servidor le responde.

La regla más importante de HTTP: **la comunicación ocurre en mensajes de ida y vuelta**.

- La ida se llama **request** (petición). La hace el cliente: el navegador, o en nuestro caso el frontend de Next.js.
- La vuelta se llama **response** (respuesta). La hace el servidor: nuestro backend Django.

Un dato clave: **la conexión se corta después de cada intercambio**. El servidor responde y se olvida de quién le pidió. Para "acordarse" existen las cookies (las vemos más abajo).

### Las 4 piezas de una request

Toda request tiene, como mínimo, estas cuatro cosas:

| Pieza | Qué es | Ejemplo real nuestro |
|---|---|---|
| **Método** | La acción que querés hacer | `GET` |
| **URL** | A qué recurso (dirección) le pedís algo | `/api/cervezas/` |
| **Headers** | Metadatos: información *sobre* el pedido, no el pedido en sí | `Authorization: Token 9f8e7d...` |
| **Body** (cuerpo) | Los datos que mandás (solo en POST, PUT, PATCH) | `{"nombre": "IPA del Flachero", ...}` |

Y la response también tiene sus cuatro piezas:

| Pieza | Qué es | Ejemplo real nuestro |
|---|---|---|
| **Código de estado** | Número de 3 dígitos que dice si salió bien o mal | `200 OK` |
| **Headers** | Metadatos de la respuesta | `Content-Type: application/json` |
| **Body** | El contenido: en nuestra API, siempre JSON | `{"count": 3, "results": [...]}` |
| --- | --- | --- |

> **Para la defensa:** "HTTP es un protocolo de ida y vuelta: el cliente manda una *request* con método, URL, headers y opcionalmente un body, y el servidor devuelve una *response* con un código de estado, headers y un body que en nuestra API es JSON."

---

## Los métodos HTTP

El **método** le dice al servidor qué querés hacer con un recurso. Hay más, pero nosotros usamos cinco.

| Método | Qué hace | Ejemplo real en Los Flacheros | Éxito |
|---|---|---|---|
| `GET` | **Leer**. No modifica nada. Es seguro repetirlo. | `GET /api/cervezas/` → lista todas las cervezas | `200` |
| `POST` | **Crear** algo nuevo (o mandar un formulario de login). | `POST /api/pedidos/` con body `{"cliente": 3, ...}` → crea un pedido | `201` |
| `PUT` | **Reemplazar** un recurso completo. Hay que mandar todos los campos. | `PUT /api/cervezas/1/` con todos los campos de la cerveza 1 | `200` |
| `PATCH` | **Actualizar** campos parciales. Mandás solo lo que cambia. | `PATCH /api/pedidos/1/` con `{"estado": "CONFIRMADO"}` → el pedido 1 pasa a CONFIRMADO | `200` |
| `DELETE` | **Borrar** un recurso. | `DELETE /api/opiniones/3/` → borra la opinión 3 | `204` |

Dos reglas prácticas:

- **GET no debería modificar nada.** Si un GET cambia datos, es una señal de que está mal diseñado.
- **PATCH es el que más usamos para cambios chicos.** En nuestra API, marcar un pedido como CONFIRMADO es un `PATCH` con un solo campo. No hace falta reenviar la fecha ni el total.

Otras dos cosas que vas a ver:

- **`POST /api/auth-token/`** es un `POST` que no crea un recurso visible: manda usuario y contraseña y devuelve un token. Es la excepción típica de un POST "de login".
- **`OPTIONS`** es el método que usa el navegador para preguntar "¿me dejás hacer esto?" antes de mandar request "de verdad". Es la base de CORS, que explicamos más abajo.

> **Para la defensa:** "Usamos GET para leer, POST para crear, PATCH para actualizar campos puntuales, PUT para reemplazar completo y DELETE para borrar. Por ejemplo, confirmar un pedido es `PATCH /api/pedidos/1/` con `{"estado": "CONFIRMADO"}`."

---

## Códigos de estado

Cuando el servidor responde, arranca con un número de tres dígitos. No es burocracia: **es la forma en que el frontend se entera de qué pasó** sin tener que leer el body.

| Código | Significado | Cuándo lo devuelve nuestro backend | Qué hace el frontend |
|---|---|---|---|
| `200` | OK | Respuesta normal: `GET /api/cervezas/`, un `PATCH` exitoso, `/api/pedidos/estadisticas/` | Muestra los datos |
| `201` | Created | `POST /api/pedidos/` creó un pedido | Muestra "pedido creado" y actualiza la lista |
| `204` | No Content | `DELETE /api/opiniones/3/` borró y no hay nada que devolver | Saca el elemento de la pantalla |
| `301` | Moved Permanently | Una URL vieja que redirige a otra (raro en nuestra API) | Sigue la redirección automáticamente |
| `400` | Bad Request | El JSON llegó mal: falta un campo, `puntaje` es 9 cuando el rango es 1-5 | Muestra el error de validación campo por campo |
| `401` | Unauthorized | No mandaste token, o el token es inválido. Te falta **identificarte** | Pide el token de nuevo: `POST /api/auth-token/` |
| `403` | Forbidden | Estás identificado pero **no podés**: un usuario sin sesión escribiendo, o falto el token CSRF | Muestra "no tenés permiso"; no insiste con pedir token |
| `404` | Not Found | `GET /api/cervezas/99/` y la cerveza 99 no existe | Muestra "no encontrado" |
| `405` | Method Not Allowed | Mandás `DELETE /api/estilos/` cuando el recurso no admite borrar por esa ruta, o `GET` a una acción que solo acepta `POST` | Error de programación del frontend: revisar el método |
| `409` | Conflict | Conflicto con el estado actual: intentar crear un `Estilo` con un nombre que ya existe, o un `Cerveza` con un `stock` negativo | Muestra el conflicto y no duplica el recurso |
| `500` | Internal Server Error | Se rompió el código del servidor: una excepción no atrapada en una vista | Muestra "algo salió mal" y lo reporta; el equipo revisa el log del backend |

La regla que conviene memorizar: **4xx = culpa del pedido, 5xx = culpa del servidor**. `4xx` dice "lo que mandaste está mal o no podés"; `5xx` dice "nosotros nos caímos".

La diferencia `401` vs `403` es la que más preguntan:

- `401`: **no sé quién sos**. Mandá credenciales.
- `403`: **sé quién sos, pero no podés**. O, en nuestro caso, mandaste la request desde el puerto 3000 sin el token de sesión correcto y Django la frenó por CSRF.

> **Para la defensa:** "Los 2xx son éxitos: 200 al leer, 201 al crear, 204 al borrar. Los 4xx son errores del cliente: 400 por datos inválidos, 401 sin identificar, 403 sin permiso, 404 inexistente. Los 5xx son errores nuestros. El frontend decide qué mostrar según el número, así que devolver el código correcto es parte de la API."

---

## Headers

Los **headers** son pares `nombre: valor` que viajan tanto en la request como en la respuesta. No son el contenido: son **información sobre el contenido**.

Los cuatro que nos importan:

| Header | Dónde | Qué dice | Ejemplo nuestro |
|---|---|---|---|
| `Content-Type` | Request y response | Qué tipo de dato es el body | `Content-Type: application/json` → "el body es JSON" |
| `Accept` | Request | Qué tipo de dato querés recibir | `Accept: application/json` |
| `Authorization` | Request | Credencial para identificarse | `Authorization: Token 9f8e7d6c5b4a3210...` |
| `Origin` | Request | Desde qué sitio (protocolo + host + puerto) viene la request | `Origin: http://localhost:3000` |

Ese último es el que Django ve cuando le llega una request del frontend, y es la clave de CORS.

Dos detalles útiles:

- Si el backend manda `Content-Type: application/json` y el frontend manda `Accept: text/html`, algo está desalineado.
- El header `Authorization` es lo que hace que DRF sepa quién sos cuando usás token. **El token va ahí y no en la URL**: en una URL se guarda en historiales y logs.

> **Para la defensa:** "Los headers son metadatos de la request o la respuesta. Nosotros usamos `Content-Type` para decir que mandamos JSON, `Accept` para pedir JSON, `Authorization: Token <key>` para autenticar y `Origin` es el que Django revisa para aplicar CORS."

---

## JSON

**JSON** (*JavaScript Object Notation*) es un formato de texto para representar datos. Es el idioma que habla nuestra API: DRF recibe JSON, lo convierte en objetos de Python, y devuelve objetos de Python convertidos en JSON.

### Los 6 tipos de valor de JSON

| Tipo | Ejemplo | Equivalente en Python | Dónde lo usamos |
|---|---|---|---|
| Número | `12`, `4.85` | `int`, `float` | `ibu`, `alcohol_pct` |
| Texto (string) | `"IPA del Flachero"` | `str` | `nombre`, `comentario` |
| Booleano | `true`, `false` | `bool` | `activo` |
| Nulo | `null` | `None` | `estilo` cuando el FK quedó en `SET_NULL` |
| Lista | `[1, 2, 3]` | `list` | `results` de la paginación |
| Objeto | `{"nombre": "..."}` | `dict` | una cerveza, un pedido |

Tres reglas de sintaxis que caen mal al principio:

1. Los textos van entre **comillas dobles**.
2. Las **claves** van entre comillas dobles.
3. No se aceptan comas colgantes (`{"a": 1,}` es error) ni comentarios.

### Por qué JSON y no XML

- Es más chico: `{"stock": 10}` en vez de `<stock>10</stock>`.
- Lo parsea cualquier lenguaje con una línea.
- JavaScript lo entiende de fábrica, y el frontend es Next.js (JavaScript).

### Ejemplo real: respuesta de `GET /api/cervezas/?search=ipa`

Con la paginación global de 10 por página (clase `DefaultPagination`), toda respuesta de listado tiene esta forma. Fijate los cuatro campos fijos:

```json
{
    "count": 3,
    "next": "http://localhost:8000/api/cervezas/?search=ipa&page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "nombre": "IPA del Flachero",
            "descripcion": "Con lúpulo americano y amargor firme.",
            "estilo": 2,
            "precio": "12500.00",
            "volumen_ml": 473,
            "alcohol_pct": "6.50",
            "stock": 48,
            "tipo": "ENVASE",
            "activo": true,
            "fecha_creacion": "2026-10-21T14:03:00-03:00"
        }
    ]
}
```

Claves del ejemplo:

- **`count`**: total de resultados (no el tamaño de la página).
- **`next` / `previous`**: URL de la página siguiente o anterior, o `null` si no hay. El frontend sigue esas URLs a mano; no tiene que inventar la lógica de paginación.
- **`results`**: la lista real, de a lo sumo 10 elementos.
- **`precio` y `alcohol_pct` llegan como texto** (`"12500.00"`): los `DecimalField` de Django se serializan como string para no perder precisión. Un error clásico del frontend es sumarlos sin convertir.
- **`estilo` es un número**: por defecto DRF manda el `id` del FK. Si el serializer lo declara anidado, en cambio verías el objeto completo.

> **Para la defensa:** "JSON es texto con 6 tipos de valor: número, string, booleano, nulo, lista y objeto. Nuestras respuestas de listado siempre traen `count`, `next`, `previous` y `results` porque usamos una clase de paginación propia con `page_size = 10`; así el frontend pagina sin reimplementar la lógica."

---

## El viaje completo de una request autenticada

Este es el recorrido que tenés que poder dibujar en la defensa. Arranca en el navegador de Ema y termina en el JSON.

```
 Frontend (:3000)                              Backend Django (:8000)
------------------------------------------------+-------------------------------------
 1. El usuario pide "listar cervezas"
    fetch("http://localhost:8000/api/cervezas/")
                                                |
 2. ¿El origen es distinto? SÍ (:3000 != :8000)
    -> el navegador manda primero un OPTIONS   ->
    <- 200 con Access-Control-Allow-Origin:    <-
       http://localhost:3000  (preflight)
                                                |
 3. El navegador deja pasar la request real    ->
                                                | 4. Middleware: CORS deja entrar
                                                | 5. Rutas: /api/cervezas/ -> CervezaViewSet
                                                | 6. Autenticación:
                                                |    lee Authorization: Token 9f8e...
                                                |    -> DRF busca el token -> user "fede"
                                                | 7. Permiso: IsAuthenticated -> OK
                                                | 8. Vista: list() de los Cervezas
                                                | 9. Serializer: valida y traduce
                                                |    cada instancia a dict
                                                | 10. Select related estilo (1 query,
                                                |     no N)
                                                | 11. Paginación: corta a 10 y arma
                                                |     count/next/previous
                                                | 12. Render a JSON -> 200 OK
 <-- response 200 con Content-Type: application/json
    {"count": 12, "next": ..., "results": [...]}
                                                |
 13. El navegador aplica CORS y entrega el     |
     JSON al código de Next.js                 |
 14. React renderiza las tarjetas de cerveza   |
```

Y el paso previo, el de obtener el token:

```
POST /api/auth-token/
Content-Type: application/json

{"username": "fede", "password": "secreto123"}

-> 200 OK
{"token": "9f8e7d6c5b4a3210aa..."}

Desde ahí, TODA request autenticada lleva:

GET /api/pedidos/
Authorization: Token 9f8e7d6c5b4a3210aa...
```

Si falta el `Authorization`, DRF devuelve `401` (o `403` según la configuración de autenticación). Si el token existe pero el permiso dice `IsAdminUser` y el usuario no es admin, devuelve `403`. La distinción importa: **la autenticación responde "quién sos", el permiso responde "¿podés?"**.

> **Para la defensa:** "Una request autenticada pasa por CORS (preflight OPTIONS si el origen es distinto), luego por las rutas, luego la autenticación lee `Authorization: Token ...` y resuelve el usuario, después el permiso decide si entra, la vista arma la respuesta, el serializer valida y traduce, y DRF renderiza a JSON. Si cualquier paso falla, ahí corta con un 4xx."

---

## CORS a fondo

### La misma política de origen (same-origin policy)

El navegador tiene una regla de seguridad por defecto: **un sitio solo puede leer lo que pide su mismo origen**. El *origen* es la combinación de **protocolo + host + puerto**.

- `http://localhost:3000` y `http://localhost:8000` son **orígenes distintos** (cambia el puerto).
- `http://localhost:8000` y `https://localhost:8000` también (cambia el protocolo).

Nuestro frontend corre en `:3000` y el backend en `:8000`. Son orígenes distintos. Sin CORS, el navegador **bloquea** la respuesta: la request hasta puede salir, pero el JavaScript de Next.js no puede leer el resultado. En la consola verías algo como:

```
Access to fetch at 'http://localhost:8000/api/cervezas/' from origin
'http://localhost:3000' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Qué resuelve django-cors-headers

Es una app de Django que se suma a los middlewares y **agrega los headers CORS correctos a las respuestas**. En `config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

Con eso, cuando llega una request con `Origin: http://localhost:3000`, el backend responde con `Access-Control-Allow-Origin: http://localhost:3000` y el navegador suelta el JSON.

Ojo con un detalle: **ponemos los orígenes exactos, no `*`**. Con `*` cualquier sitio podría leer nuestra API desde un navegador. En producción eso sería un problema serio.

### El preflight

Para requests "simples" (como un `GET` con solo `Accept`) el navegador manda la request y listo. Pero si la request es "complicada" —por ejemplo un `POST` con `Content-Type: application/json` o un header `Authorization`— el navegador manda **primero** un ensayo:

```
OPTIONS /api/pedidos/ HTTP/1.1
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization,content-type
```

Eso es el **preflight**: "¿me dejás hacer un POST con esos headers?". El backend responde con los headers `Access-Control-Allow-*` y recién entonces va la request real. Si el preflight falla, **el navegador ni siquiera manda el POST**.

Por eso la primera llamada de la API a veces tarda un poquito más: viajaron dos requests.

### CORS vs CSRF

Acá se confunde todo el mundo, porque los dos protegen cosas distintas y los dos usan el navegador.

| | **CORS** | **CSRF** |
|---|---|---|
| Qué es | Restricción del **navegador** sobre leer respuestas de otro origen | Ataque en el que un sitio logueado es engañado para que mande una acción a nuestro backend |
| Quién lo aplica | El navegador, leyendo headers | El servidor (Django, con el token CSRF) |
| Qué protege | Que otro sitio **lea** nuestra API desde el browser | Que otro sitio **actúe** en nombre del usuario logueado |
| Quién lo configura | Nosotros, con `django-cors-headers` y `CORS_ALLOWED_ORIGINS` | Django, con `CsrfViewMiddleware` y el token en formularios |
| Qué pasa si falla | `Access-Control blocked` en la consola del navegador | `403 Forbidden` con "CSRF cookie not set" o "CSRF token missing" |

La consecuencia práctica de la fila de CSRF: las `SessionAuthentication` de DRF **exigen token CSRF** para cualquier request que no sea `GET`. Como el frontend en `:3000` no tiene esa cookie emparejada, recibe `403`. Por eso nuestro frontend usa **solo token**.

### CORS no es seguridad del servidor

Frase para la defensa, porque es la que más valoran:

> **Para la defensa:** "CORS no es una medida de seguridad del servidor: es una restricción que aplica el navegador para proteger al usuario final. Un atacante con `curl` o con Python ignora CORS por completo. Nuestro backend igual valida permisos y autenticación en cada request; CORS solo habilita o no al navegador de localhost:3000 a leer las respuestas."

---

## Cookies

Una **cookie** es un texto chico que el servidor le pide al navegador que guarde y que el navegador le devuelve **automáticamente** en cada request a ese servidor. Es el parche que HTTP, que se olvida de todo, necesita para "recordar".

Tres reglas que conviene tener claras:

1. Las cookies pertenecen a un **origen** y el navegador las manda solo a ese origen.
2. **Las cookies ignoran el puerto.** Una cookie creada para `localhost` se manda a `localhost:3000` *y* a `localhost:8000`. Esto contrae la regla general de orígenes y es justamente el motivo de los problemas de abajo.
3. Se puede marcar `HttpOnly` (el JavaScript no puede leerla, contra ataques XSS) y `SameSite` (cuándo se manda en requests cross-site).

### La sessionid de Django

Cuando alguien hace login en Django (por ejemplo desde el panel de admin en `localhost:8000/admin/`), Django:

1. Crea una sesión en la base de datos.
2. Manda una cookie llamada **`sessionid`** al navegador.
3. En cada request, el navegador la devuelve y Django sabe quién es.

Eso es `SessionAuthentication` de DRF.

### Por qué el login por sesión desde el front en :3000 termina en 403 CSRF

Acá se arma el lío. Supongamos que Ema intenta loguearse con sesión desde el puerto 3000:

```
1. El front hace POST a http://localhost:8000/api/... con credenciales.
2. La cookie sessionid SÍ viaja (las cookies ignoran el puerto).
3. DRF con SessionAuthentication ve la cookie: "este es fede".
4. PERO: SessionAuthentication exige además el token CSRF para
   cualquier POST/PATCH/DELETE.
5. El front nunca tuvo el par de cookies csrftoken + sessionid del
   backend, porque esa pareja se crea en el dominio/puerto del back
   y el front no la puede leer (HttpOnly / same-origin).
6. Resultado: 403 Forbidden, "CSRF Failed".
```

La solución que usamos: **el frontend no usa sesión, usa token**.

```
POST /api/auth-token/       -> devuelve {"token": "9f8e..."}
GET  /api/pedidos/           con  Authorization: Token 9f8e...
PATCH /api/pedidos/1/        con  Authorization: Token 9f8e...
```

`TokenAuthentication` no lee cookies, así que no hay relación con el puerto ni con CSRF. Es simple, es stateless (el servidor no guarda nada por request) y es lo que cualquiera entiende en la defensa.

¿Y para qué dejamos `SessionAuthentication` habilitado? Para vos mismo, cuando probás desde la **browsable API** de DRF en `http://localhost:8000/api/` haciendo login en el navegador. En local, contra el backend directo, eso funciona bien.

> **Para la defensa:** "La cookie `sessionid` de Django viaja entre localhost:3000 y localhost:8000 porque las cookies ignoran el puerto, pero `SessionAuthentication` exige además el token CSRF y el frontend no lo tiene, así que recibe 403. Por eso el frontend se autentica únicamente con `Authorization: Token <key>`; la sesión la usamos solo para la browsable API en :8000."

---

## HTTPS en producción

**HTTPS** es HTTP dentro de un túnel cifrado con TLS. Mientras que HTTP viaja en texto plano (cualquiera en la red lee los headers y el body), HTTPS lo encripta de punta a punta.

En producción es obligatorio por tres motivos:

1. Sin TLS, el token de `Authorization` viaja legible para cualquiera que esté en la red.
2. Los navegadores marcan como "No seguro" los sitios HTTP.
3. Cookies sin HTTPS pueden ser interceptadas (session hijacking).

**En local HTTP alcanza, y es a propósito.** `localhost` no pasa por la red de la empresa ni por routers intermedios: es la propia máquina. Además, TLS local implica certificados autofirmados y un proxy extra, que para dos principiantes con entrega el lunes es complejidad sin valor.

Lo que sí dejamos previsto: `CORS_ALLOWED_ORIGINS` apunta a `http://localhost:3000`, y si algún día se despliega, ahí se cambia por `https://...` y se termina el asunto.

> **Para la defensa:** "En local usamos HTTP porque `localhost` no sale de la máquina; en producción usaríamos HTTPS para que el header `Authorization` no viaje en claro. La única referencia al protocolo está en `CORS_ALLOWED_ORIGINS`, que es una lista de orígenes exactos."

---

## Ejercicios

### 1. Métodos y endpoints

Para cada acción, escribí el método y la URL exactos:

a) Ver todas las materias primas.
b) Crear un cliente nuevo.
c) Cambiar el precio de la cerveza 7.
d) Borrar la opinión 3.
e) Saber qué cervezas tenemos en grifo.

<details>
<summary>Respuestas</summary>

a) `GET /api/materias-primas/`
b) `POST /api/clientes/`
c) `PATCH /api/cervezas/7/` con body `{"precio": "14000.00"}`
d) `DELETE /api/opiniones/3/`
e) `GET /api/cervezas/en_grifo/` (es una `@action` del ViewSet de Cerveza)

</details>

### 2. Códigos de estado

Decí qué código devuelve el backend en cada caso y por qué:

a) `POST /api/pedidos/` con todos los campos válidos.
b) `GET /api/lotes/42/` y el lote 42 no existe.
c) `POST /api/estilos/` con nombre "IPA" ya existente.
d) `PATCH /api/pedidos/1/` sin mandar ningún header de autenticación.
e) `POST /api/opiniones/` con `puntaje: 9`.
f) El backend lanza una excepción por un bug en `views.py`.

<details>
<summary>Respuestas</summary>

a) `201 Created`
b) `404 Not Found`
c) `409 Conflict` (o `400` si la validación del serializer lo deja caer como error de campo; en cualquier caso, es un 4xx y no se crea el registro)
d) `401 Unauthorized` — falta identificarse
e) `400 Bad Request` — el `choices`/rango de `puntaje` es 1-5
f) `500 Internal Server Error`

</details>

### 3. El viaje de una request

El frontend de Ema hace `POST /api/pedidos/` con `Content-Type: application/json` y `Authorization: Token ...`. Escribí, en orden, los pasos que ocurren desde que se aprieta el botón hasta que se pinta el pedido en pantalla.

<details>
<summary>Respuesta</summary>

1. El navegador ve que el origen (`http://localhost:3000`) es distinto del destino (`http://localhost:8000`) y la request no es "simple": manda un preflight `OPTIONS`.
2. `django-cors-headers` responde con `Access-Control-Allow-Origin: http://localhost:3000` y `Access-Control-Allow-Methods: POST`.
3. El navegador manda el `POST` real con los headers `Content-Type` y `Authorization`.
4. El middleware de CORS deja pasar la request.
5. `config/urls.py` la deriva a `/api/pedidos/` → `PedidoViewSet.create`.
6. `TokenAuthentication` lee el header, busca el token y resuelve el usuario; si no existe, corta con 401.
7. El permiso decide si puede escribir: `IsAdminUser` exige staff, salvo en el mostrador (`Pedido` y `LineaPedido`), donde basta estar identificado; si no, 403.
8. El `PedidoSerializer` valida el JSON: si hay un campo mal, corta con 400 antes de tocar la base.
9. La vista crea el `Pedido` (y sus `LineaPedido`) en la base de datos.
10. El serializer convierte la instancia a dict, DRF renderiza a JSON y responde `201 Created`.
11. El navegador entrega el JSON al código de Next.js, que muestra el pedido.

</details>

### 4. CORS y cookies

a) El frontend de Ema manda `GET /api/cervezas/` sin token y le sale `403` en la consola con un texto de CSRF. ¿Qué pasó y cómo se arregla?
b) ¿Por qué `CORS_ALLOWED_ORIGINS = ["*"]` sería mala idea?
c) El backend corre en `:8000`, abrís el admin en `:8000/admin/` y te logueás. ¿Se ve el login en el frontend de `:3000`? Justificá.

<details>
<summary>Respuestas</summary>

a) El `GET` lo hizo con cookies de sesión (o con `SessionAuthentication` activo sin par de cookies CSRF), y DRF exige el token CSRF. Se arregla autenticando con `Authorization: Token <key>` obtenido en `POST /api/auth-token/`, que no depende de cookies.
b) Cualquier sitio podría leer nuestras respuestas desde el navegador de un usuario. CORS restringe *el navegador*, pero lo mínimo es dejar solo el origen del front: `["http://localhost:3000"]`.
c) No. Aunque las cookies ignoran el puerto y `sessionid` viajaría a `:3000`, el frontend no lee cookies ajenas ni llama al admin; además, para escribir necesitaría el token CSRF. El login de sesión sirve para la browsable API en `:8000`, no para el front.

</details>

### 5. JSON

Corregí este JSON, que el frontend mandó mal a `POST /api/opiniones/`:

```json
{
    "cerveza": 1,
    "cliente": 4,
    "puntaje": 5,
    "comentario": "Muy buena,
}
```

<details>
<summary>Respuesta</summary>

Hay tres errores: el string de `comentario` está sin cerrar y tiene una coma adentro, y sobra la coma final antes del `}`. JSON correcto:

```json
{
    "cerveza": 1,
    "cliente": 4,
    "puntaje": 5,
    "comentario": "Muy buena"
}
```

El backend respondería `400 Bad Request` con los detalles de validación.

</details>

---

> **Para la defensa:** "HTTP es request/response, JSON es el formato de los bodies, los códigos de estado le dicen al frontend qué hacer, CORS le permite al navegador de :3000 leer el backend de :8000, y el token en el header `Authorization` evita depender de cookies y de CSRF. Todo eso es lo que sostiene la API."
