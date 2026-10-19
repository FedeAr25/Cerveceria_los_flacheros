# Contrato API — Cervecería Los Flacheros (handoff frontend)

Documento para Ema (frontend). La fuente de verdad en vivo es **Swagger** (`http://localhost:8000/api/schema/swagger-ui/`); este contrato se mantiene sincronizado con la API real. Si algo cambia, se avisa antes de seguir programando contra eso.

## Base URL

```
http://localhost:8000/api/
```

## Autenticación

### Login por token

```
POST /api/auth-token/
Content-Type: application/json

{ "username": "demo", "password": "flacheros2026" }
```

Respuesta:

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```

### Uso del token

Todas las peticiones a `/api/...` deben llevar el header:

```
Authorization: Token <token>
```

### Por qué NO usar cookies de sesión

- Las cookies **ignoran el puerto**: `localhost:3000` (tu frontend) y `localhost:8000` (el backend) comparten cookies porque están en el mismo host.
- Si hicieras login con sesión (`SessionAuthentication`), DRF exigiría **CSRF** en cada POST/PUT/PATCH/DELETE, lo que complica el flujo de un SPA.
- **Decisión del equipo:** el frontend usa SOLO `Authorization: Token <key>` y **nunca** login por sesión. Esto queda documentado en el README y se defiende en la defensa oral.

Si el backend responde `401`, el token es inválido o ausente. Si responde `403`, el token es válido pero el usuario no tiene permiso (ej. `estadisticas` requiere usuario staff).

## Paginación

Los listados devuelven:

```json
{
  "count": 137,
  "next": "http://localhost:8000/api/pedidos/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

| Parámetro | Efecto |
|---|---|
| `?page=2` | Página (arranca en 1) |
| `?page_size=50` | Tamaño de página (default 10, tope 50; más de 50 se trunca a 50) |

`next`/`previous` pueden ser `null` en los extremos. No asumas que todas las respuestas traen menos de 10 items.

## Tabla de endpoints

Todos los recursos son `ModelViewSet`: cada URL de colección tiene además su detalle en `{id}/` con `GET`, `PUT`, `PATCH` y `DELETE`.

| Método | URL | Auth | Params | Respuesta resumida |
|---|---|---|---|---|
| POST | `/api/auth-token/` | No | — | `{token}` |
| GET, POST | `/api/estilos/` | Token (lectura; admin para escribir) | page, page_size, search, ordering | paginado |
| GET, POST | `/api/cervezas/` | Token | page, page_size, filtros, search, ordering | paginado |
| GET | `/api/cervezas/en_grifo/` | Token | — | cervezas en grifo con stock |
| GET, POST | `/api/lotes/` | Token | page, page_size, search, ordering | paginado **con `etapas`** |
| GET | `/api/lotes/{id}/` | Token | — | lote plano (sin `etapas`) |
| GET, POST | `/api/etapas/` | Token | page, page_size, filtros, ordering | paginado |
| GET, POST | `/api/proveedores/` | Token (lectura; admin para escribir) | page, page_size, search, ordering | paginado |
| GET, POST | `/api/materias-primas/` | Token | page, page_size, filtros, search, ordering | paginado |
| GET, POST | `/api/clientes/` | Token | page, page_size, search, ordering | paginado |
| GET, POST | `/api/pedidos/` | Token | page, page_size, filtros, search, ordering | paginado **con `lineas`** |
| GET | `/api/pedidos/{id}/` | Token | — | pedido plano (sin `lineas`) |
| GET | `/api/pedidos/estadisticas/` | Token **admin** | — | métricas de pedidos |
| GET, POST | `/api/lineas/` | Token | page, page_size, ordering | paginado |
| GET, POST | `/api/opiniones/` | Token | page, page_size, ordering | paginado |

Códigos: `200` OK · `201` creado · `204` borrado · `400` validación · `401` sin token o inválido · `403` sin permiso · `404` no existe.

## Filtros, búsqueda y orden por endpoint

| Endpoint | Filtros (`?campo=valor`) | Búsqueda (`?search=`) | Orden (`?ordering=`) |
|---|---|---|---|
| `/api/estilos/` | — | nombre | `orden`, `nombre` |
| `/api/cervezas/` | estilo, tipo, activo | nombre, descripcion | `precio`, `nombre`, `-fecha_creacion` |
| `/api/lotes/` | — | numero, cerveza__nombre | `-fecha_inicio` |
| `/api/etapas/` | lote | — | `numero` |
| `/api/proveedores/` | — | razon_social, cuit | `razon_social` |
| `/api/materias-primas/` | tipo, proveedor | nombre | `tipo`, `nombre` |
| `/api/clientes/` | — | nombre, apellido, email, dni | `-fecha_alta` |
| `/api/pedidos/` | estado, forma_pago | cliente__nombre, cliente__apellido | `-fecha` |
| `/api/lineas/` | — | — | `-pedido__fecha` |
| `/api/opiniones/` | — | — | `-fecha` |

Notas:

- `ordering` acepta varios campos separados por coma y el prefijo `-` para descendente. Un `ordering` inválido se ignora (no rompe).
- Los valores de `estado`, `tipo`, `forma_pago`, etc. son los `choices` exactos, en mayúsculas: `ENVASE`, `GRIFO`, `PLANIFICADO`, `EN_PRODUCCION`, `FERMENTACION`, `MADURACION`, `LISTO`, `CANCELADO`, `PENDIENTE`, `CONFIRMADO`, `EN_PREPARACION`, `LISTO_RETIRO`, `ENTREGADO`, `EFECTIVO`, `TARJETA`, `TRANSFERENCIA`, `PRIMARIA`, `SECUNDARIA`, `MADURADO`, `ACTIVA`, `COMPLETADA`, `MALTA`, `LUPULO`, `LEVADURA`, `OTROS`, `KG`, `G`, `LT`, `UNIDAD`.
- Ejemplo: `GET /api/cervezas/?tipo=GRIFO&search=ipa&ordering=-fecha_creacion`.

## List vs detail: nesting en Pedidos y Lotes

Solo `list` trae los hijos anidadas. `retrieve` (`{id}/`) y todas las escrituras usan el serializer plano. Esto es a propósito (requisito de la consigna): en el listado ves el padre con sus hijos de un vistazo; el detalle es liviano.

### `GET /api/pedidos/` (con `lineas` anidadas)

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

### `GET /api/pedidos/1/` (sin `lineas`)

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

### `GET /api/lotes/` (con `etapas` anidadas)

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero": "LOTE-2026-007",
      "fecha_inicio": "2026-10-01",
      "fecha_fin": null,
      "volumen_litros": 500.00,
      "estado": "FERMENTACION",
      "notas": "Lupulo Citra en whirlpool",
      "cerveza": 1,
      "cerveza_nombre": "IPA del Lote 7",
      "usuario": 1,
      "etapas": [
        {
          "id": 1,
          "numero": 1,
          "tipo": "PRIMARIA",
          "fecha_inicio": "2026-10-01",
          "fecha_fin": "2026-10-08",
          "temperatura": 20.5,
          "estado": "COMPLETADA",
          "lote": 1
        },
        {
          "id": 2,
          "numero": 2,
          "tipo": "SECUNDARIA",
          "fecha_inicio": "2026-10-08",
          "fecha_fin": null,
          "temperatura": 19.0,
          "estado": "ACTIVA",
          "lote": 1
        }
      ]
    }
  ]
}
```

### `GET /api/lotes/1/` (sin `etapas`)

```json
{
  "id": 1,
  "numero": "LOTE-2026-007",
  "fecha_inicio": "2026-10-01",
  "fecha_fin": null,
  "volumen_litros": 500.00,
  "estado": "FERMENTACION",
  "notas": "Lupulo Citra en whirlpool",
  "cerveza": 1,
  "usuario": 1
}
```

**Implicancia para el frontend:** si en una vista puntual necesitás las líneas de un solo pedido o las etapas de un solo lote, usá el listado (por ahora el detalle no trae hijos). Si eso te complica, avisá: es un cambio chico del backend.

## Endpoints `@action` (extras)

| Método | URL | Auth | Descripción |
|---|---|---|---|
| GET | `/api/cervezas/en_grifo/` | Token | Cervezas con `tipo='GRIFO'`, activas y con `stock > 0`. Misma forma que cualquier listado de cervezas (paginado, `CervezaSerializer`). |
| GET | `/api/pedidos/estadisticas/` | Token **admin** | `{ "total_pedidos": 25, "monto_total": 350000.00, "pedidos_por_estado": { "PENDIENTE": 4, "CONFIRMADO": 10, ... }, "promedio_ticket": 14000.00 }` |

(Posible tercer action, **opcional y aún no comprometido**: `POST /api/lotes/{id}/avanzar/`. Si se implementa, se agrega a este contrato antes de usarlo.)

## Ejemplo de cliente en JavaScript puro

```javascript
const API = "http://localhost:8000/api";
let token = null;

async function login(username, password) {
  const res = await fetch(`${API}/auth-token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Login falló");
  const data = await res.json();
  token = data.token; // guardalo donde prefieras (localStorage, memoria)
  return token;
}

async function apiGet(path) {
  if (!token) throw new Error("No hay token: hacé login primero");
  const res = await fetch(`${API}${path}`, {
    headers: { Authorization: `Token ${token}` },
  });
  if (res.status === 401) {
    token = null; // token ausente o inválido → volver a login
    throw new Error("Sesión expirada, volvé a iniciar sesión");
  }
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

// Uso: listado paginado de pedidos (en list, cada pedido trae `lineas` y `cliente_nombre`)
async function listarPedidos(page = 1, pageSize = 10) {
  const data = await apiGet(`/pedidos/?page=${page}&page_size=${pageSize}`);
  console.log(`Total: ${data.count}`);
  data.results.forEach((p) => {
    console.log(p.id, p.cliente_nombre, p.total, p.lineas.length, "líneas");
  });
  if (data.next) console.log("Hay más páginas:", data.next);
}

// Uso: cervezas en grifo
async function listarEnGrifo() {
  const data = await apiGet("/cervezas/en_grifo/");
  return data.results;
}

// Arranque
// await login("demo", "flacheros2026");
// await listarPedidos();
```

## Qué necesito de tu lado

1. **CORS:** el backend ya permite `http://localhost:3000`. Si cambiás el puerto o el host del dev server de Next.js, avisá para ajustar `CORS_ALLOWED_ORIGINS` en el `.env` del backend.
2. **Token:** guardalo y mandalo en `Authorization: Token <key>` en **cada** request. Manejá `401` como "volver a login" y `403` como "no tenés permiso" (no es sesión expirada).
3. **No mandes cookies de sesión:** no uses `credentials: "include"` ni cookies de autenticación; todo el login es por header (evitamos el problema de CSRF con cookies compartidas entre puertos).
4. **Paginación:** respetá `count/next/previous`; el default son 10 items por página (tope 50 con `?page_size=`).
5. **Nesting:** los hijos (`lineas`, `etapas`) solo vienen en `list`; si implementás una vista de detalle y necesitás los hijos, usá el listado o avisame.
6. **Credenciales de prueba:** usuario demo con permisos de lectura/escritura normal; para `GET /api/pedidos/estadisticas/` necesitás un usuario staff (las credenciales exactas quedan en el `README.md` final).
