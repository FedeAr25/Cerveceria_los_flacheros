# Resumen de Defensa - Cervecería Los Flacheros

## 1. Presentación del Proyecto (2 minutos)

**¿Qué es?** API REST para gestión de una cervecería artesanal.

**Identidad:** Cervecería Los Flacheros  
**Lema:** "Arte en cada trago, tradición en cada lote"

**Stack tecnológico:**
- Backend: Django 5.2 LTS + Django REST Framework 3.17
- Python 3.13
- Base de datos: PostgreSQL 17 (producción) / SQLite (desarrollo)
- Gestor de dependencias: uv 0.13.1
- Servidor: Gunicorn (producción), runserver (desarrollo)
- Documentación: drf-spectacular (OpenAPI/Swagger/ReDoc)

**Alcance:** 10 modelos, 1 app core, 10 endpoints CRUD, 3 acciones personalizadas

---

## 2. Cumplimiento de Requisitos

| Requisito | Evidencia | Ubicación |
|-----------|-----------|-----------|
| **≥10 modelos** | 10 modelos: Estilo, Cerveza, Lote, EtapaFermentacion, Proveedor, MateriaPrima, Cliente, Pedido, LineaPedido, Opinion | ackend/core/models.py |
| **Relaciones** | 8 FK con elated_name + on_delete justificado (PROTECT/CASCADE/SET_NULL) | ackend/core/models.py |
| **Planificación** | Diagrama ER + tabla de 10 tablas | README.md §3 |
| **API REST** | 10 ViewSets + DefaultRouter bajo /api/ | ackend/core/views.py, ackend/core/urls.py |
| **≥8 ViewSets** | Los 10 con CRUD completo | ackend/core/views.py |
| **Nested solo en list** | Lote→etapas, Pedido→lineas (verificado con tests 7 y 8) | ackend/core/serializers.py, ackend/core/tests.py |
| **Sesión + Tokens** | /api/auth-token/ + /api-auth/ (tests 4, 5, 13) | ackend/config/urls.py |
| **≥2 @action** | 3: en_grifo, estadisticas, vanzar | ackend/core/views.py |
| **Paginación** | DefaultPagination (10, page_size, tope 50) | ackend/config/settings.py |
| **Filtros/búsqueda** | Cerveza: filtros estilo/tipo/activo, search nombre/descripcion, ordering | ackend/core/views.py |
| **OpenAPI/Swagger/ReDoc** | Los 3 funcionando, spectacular --validate sin errores | ackend/config/urls.py |
| **Vista bienvenida** | HomeView con bienvenida.html (paleta de marca) | ackend/core/views.py, ackend/templates/bienvenida.html |
| **Admin completo** | 10 modelos con list_display/list_filter/search_fields/ordering + inlines + autocomplete | ackend/core/admin.py |
| **uv** | pyproject.toml + uv.lock + .python-version | ackend/pyproject.toml |
| **CORS** | Preflight real verificado (6 escenarios) | ackend/config/settings.py |
| **Docker** | Dockerfile single-stage + compose.yaml + compose.sqlite.yaml (build bloqueado por red) | ackend/Dockerfile, ackend/compose.yaml |
| **Git** | 31 commits, 3 merges --no-ff, ramas feature/* | Historial de git |

---

## 3. Decisiones Técnicas Clave

### 3.1 Nested solo en list
**Qué:** get_serializer_class() devuelve nested solo si ction == 'list'.  
**Por qué:** 
- Requisito de consigna
- Evita payloads gigantes en detalle
- Previene escrituras anidadas accidentales

### 3.2 Permisos
**Qué:** lectura = IsAuthenticated (global), escritura = IsAdminUser (staff), excepto mostrador (Pedido/LineaPedido) donde cualquier autenticado escribe.  
**Por qué:** Regla única sin excepciones raras, fácil de defender.

### 3.3 CORS sin credenciales
**Qué:** CORS_ALLOW_CREDENTIALS = False  
**Por qué:** Frontend usa solo Authorization: Token, sin cookies. Evita CSRF por cookies compartidas (mismo host, distinto puerto).

### 3.4 DecimalField con coerce_to_string=False
**Qué:** Precios como números JSON ("precio": 4500.00), no strings ("4500.00").  
**Por qué:** Contrato con frontend congela formato numérico.

### 3.5 ReDoc pineado a versión UMD
**Qué:** SPECTACULAR_SETTINGS["REDOC_DIST"] = "https://cdn.jsdelivr.net/npm/redoc@2.5.0"  
**Por qué:** CDN pasó a servir @latest como ESM-only, rompiendo el script clásico.

---

## 4. Bugs Reales Encontrados y Resueltos

### 4.1 Opinion.__str__
**Problema:** Invocaba get_puntaje_display() que Django solo genera para campos con choices. puntaje es IntegerField con validators → AttributeError al listar opiniones en admin.  
**Fix:** Usar self.puntaje directo.

### 4.2 ReDoc en blanco
**Problema:** CDN de @latest servía bundle ESM-only → Cannot use 'import.meta' outside a module.  
**Fix:** Pin a edoc@2.5.0 (UMD) vía SPECTACULAR_SETTINGS["REDOC_DIST"].

---

## 5. Proceso de Trabajo

| Fase | Fechas | Entregable |
|------|--------|------------|
| Fase 0 | 19-20/10 | Entorno (uv, Docker, git) |
| Fase 1 | 20-21/10 | Django base (config, core, settings, bienvenida, OpenAPI) |
| Fase 2 | 21-23/10 | 10 modelos + 4 migraciones |
| Fase 3 | 23-24/10 | Admin con filtros/búsqueda/orden + inlines |
| Fase 4 | 24-27/10 | API REST (serializers, ViewSets, nested, @action, filtros) |
| Fase 5 | 27-28/10 | CORS verificado con preflight real |
| Fase 6 | 28-29/10 | Docker (Dockerfile + compose + validación) |
| Fase 7 | 29-30/10 | 17 tests automatizados |
| Fase 8 | 30/10-2/11 | Seed, capturas, README, cierre |

**Estadísticas:** 31 commits, 3 merges --no-ff, 3 ramas feature/*, 17 tests passing

---

## 6. Preguntas Típicas del Docente

### ¿Por qué Django?
Framework full-stack: ORM, admin, plantillas, seguridad. Convention over configuration.

### ¿Por qué una sola app?
10 modelos + 2 semanas: dividir en apps agrega complejidad sin aportar.

### ¿Qué es un ViewSet?
Clase que agrupa CRUD (list, create, retrieve, update, destroy). Un ViewSet por modelo.

### ¿Por qué nested solo en list?
Requisito de consigna + evita payloads grandes en detalle.

### ¿Cómo protegés los endpoints?
IsAuthenticated (lectura) + IsAdminUser (escritura), excepto mostrador.

### ¿Por qué no JWT?
Consigna pide sesión + token. Token nativo de DRF es una línea. JWT agrega complejidad.

### ¿Qué hace @action?
Endpoint custom dentro de ViewSet sin crear modelo nuevo. Usamos 3: en_grifo, estadisticas, avanzar.

### ¿Cómo paginás?
DefaultPagination (10, page_size query param, tope 50). Evita respuestas gigantes.

### ¿Por qué PROTECT en Cerveza.estilo?
No se puede borrar un estilo con cervezas: protege histórico.

### ¿Qué es CORS?
Mecanismo para que frontend (localhost:3000) llame a backend (localhost:8000). Sin CORS, navegador bloquea.

---

## 7. Lo Que Queda Pendiente (Honesto)

- **Build de Docker con Postgres:** compose.yaml listo, pendiente de verificar en red abierta (Docker Hub no alcanzable en esta red)
- **Publicación en GitHub:** repo local listo, pendiente de push remoto
- **Captura frontend.png:** depende del frontend de Ema

---

## 8. Evidencia de Calidad

**Triada de verificación:**
- uv run pytest -v → 17 passed
- uv run ruff check . → All checks passed
- uv run python manage.py check → 0 issues
- uv run python manage.py spectacular --validate → 0 errores, 0 warnings

**Capturas:** 9 imágenes del backend funcionando (bienvenida, Swagger, ReDoc, API navegable, admin con filtros, admin con inlines, API JSON nested, API JSON detalle, estadísticas)

---

*Documento preparado para la defensa oral - 3 de noviembre de 2026*
