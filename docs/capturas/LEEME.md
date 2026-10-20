# Capturas de pantalla — qué capturar, cómo y con qué comando

Guía de la **Task 26** (Fase 8). Estas imágenes son el requisito **R20**: "README.md trabajado con capturas del proyecto en funcionamiento". Se toman **después** del seed (Task 25) y se referencian desde la sección 10 del [`README.md`](../../README.md).

Convención: archivos **PNG**, nombres en minúscula con guiones, ventana completa, datos legibles y **sin credenciales a la vista**.

## Preparación (una sola vez)

```bash
cd backend
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py seed_datos        # datos de prueba (idempotente)
uv run python manage.py createsuperuser    # usuario staff para admin y acciones admin
uv run python manage.py runserver
```

Base URL: `http://localhost:8000`. Para las capturas de API con curl, pedí primero el token:

```bash
curl -X POST http://localhost:8000/api/auth-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<usuario>", "password": "<contraseña>"}'
```

y usalo en cada request como `Authorization: Token <clave>`.

## Las 10 capturas

| # | Archivo | Qué muestra | Cómo obtenerlo |
|---|---|---|---|
| 1 | `bienvenida.png` | Vista de bienvenida con paleta y lema | Abrir <http://localhost:8000/> en el navegador |
| 2 | `swagger-ui.png` | Swagger UI con los 10 endpoints y las 3 acciones | Abrir <http://localhost:8000/api/schema/swagger-ui/> |
| 3 | `redoc.png` | ReDoc con el esquema OpenAPI | Abrir <http://localhost:8000/api/schema/redoc/> |
| 4 | `browsable-api.png` | API navegable logueada por sesión | Abrir <http://localhost:8000/api/>, entrar con sesión en `/api-auth/` y expandir un endpoint |
| 5 | `admin-filtros.png` | Admin de cervezas con filtros, búsqueda y orden | Entrar en <http://localhost:8000/admin/> → Cervezas; aplicar un filtro (ej.: `tipo = GRIFO`) y una búsqueda |
| 6 | `admin-pedidos-inline.png` | Admin de un pedido con el inline de líneas | Admin → Pedidos → un pedido con líneas: se ven editadas en la misma pantalla |
| 7 | `api-pedidos-nested.png` | `GET /api/pedidos/` **con** `lineas` anidadas | `curl -s -H "Authorization: Token <clave>" "http://localhost:8000/api/pedidos/?page_size=5"` (o abrir la URL en el navegador con sesión) |
| 8 | `api-lote-detalle.png` | `GET /api/lotes/{id}/` **sin** anidar (contraste) | `curl -s -H "Authorization: Token <clave>" "http://localhost:8000/api/lotes/1/"` |
| 9 | `api-estadisticas.png` | Acción `estadisticas` con los datos del seed | `curl -s -H "Authorization: Token <clave>" "http://localhost:8000/api/pedidos/estadisticas/"` con usuario **staff** (sin staff responde `403`) |
| 10 | `frontend.png` | Frontend de Ema (si está listo) | `npm run dev` en `frontend/` → <http://localhost:3000/> |

Para JSON legibles en terminal: `curl -s ... | python -m json.tool` (o el botón "Pretty print" del navegador).

## Reglas

1. **Orden:** primero el seed (Task 25), después las capturas (Task 26): `estadisticas` y los listados necesitan datos.
2. **Legibilidad:** resolución suficiente para leer el texto; recortar lo que sobre (barra del navegador, escritorio).
3. **Sin datos sensibles:** nada de contraseñas, tokens completos ni `.env` visible.
4. **Nombres exactos:** los 10 archivos de la tabla, tal cual, porque el README ya los referencia con esos nombres.
5. **Mínimo vital** si falta tiempo (según el plan): `swagger-ui.png`, `admin-filtros.png` y `bienvenida.png`.
6. Al terminar, abrir el README y comprobar que las imágenes se ven (Fase 8, Task 26–27).
