# 01 — Django esencial

Guía para entender el Django de **este** proyecto: Cervecería Los Flacheros, backend Django 5.2 LTS + DRF, Python 3.13, base PostgreSQL 17.

**Cómo usarla:** leé una sección, hacé el ejercicio de esa sección y recién después pasá a la siguiente. No hace falta que leas todo de una: es la guía de las Fases 1, 2 y 3, y vas a volver a ella. Todas las explicaciones usan los modelos reales del proyecto (`Estilo`, `Cerveza`, `Lote`, `Pedido`, etc.), nada de blogs genéricos.

**Sobre el código de ejemplo:** los fragmentos están recortados para que se lean. El código completo del proyecto vive en `backend/config/` y `backend/core/`.

---

## 1. Qué es un framework y qué te ahorra

### La explicación en lenguaje llano

Programar un backend es, en el fondo, responder preguntas todo el tiempo: alguien me pidió algo por HTTP, ¿qué hago con eso? ¿Cómo sé quién es? ¿Cómo guardo y leo datos? ¿Cómo valido que lo que me mandó no esté mal?

Un **framework** es un montón de código ya escrito que responde esas preguntas genéricas por vos. Vos solo escribís la parte que es propia de tu negocio.

El ciclo básico es siempre el mismo, y es el que tenés que poder dibujar de memoria:

```
1. Alguien (navegador, frontend de Ema, curl) manda un HTTP request
2. Django recibe la request
3. MIDDLEWARE la procesa (CORS, sesión, CSRF, autenticación)
4. urls.py decide a qué vista corresponde esa URL
5. La vista hace su trabajo (lee/escribe la base de datos)
6. Django arma el HTTP response (JSON o HTML)
7. El cliente recibe la respuesta
```

Lo que Django resuelve por vos, sin que escribas una línea:

| Django resuelve | Con qué herramienta |
|---|---|
| Mapear URLs a código | `urls.py` |
| Generar HTML con datos | plantillas + `render()` |
| Recordar quién es el usuario | sesiones |
| Hablar con la base de datos sin SQL | ORM |
| Un panel de administración | `django.contrib.admin` |
| Protegerse de ataques CSRF y clickjacking | `MIDDLEWARE` |
| Evolucionar la base de datos sin romper datos | migraciones |

### El ejemplo de nuestro proyecto

Cuando arrancamos con `uv run python manage.py runserver` y alguien pide `GET /api/cervezas/` con token, Django hace todo el ciclo del punto anterior: el middleware de CORS chequea el origen, TokenAuthentication lee el header, el router de DRF manda al `CervezaViewSet`, el serializer traduce las `Cerveza` a JSON y devuelve un `200`. Nosotros escribimos el modelo, el serializer y el ViewSet: el resto ya venía.

Y cuando pedís `GET /`, Django busca `templates/bienvenida.html` y te devuelve HTML con la identidad de la marca. Tampoco escribimos servidor HTTP ni manejo de sockets.

### ¿Por qué dos principiantes pueden con esto?

Porque el framework absorbe las partes difíciles y genéricas (HTTP, seguridad, base de datos, servidor), y lo que queda —nombrar entidades, sus campos y sus reglas— es exactamente lo que ya modelamos en `tasks/plan.md`. La dificultad pasa de "programar un servidor" a "traducir el negocio a modelos".

> **Para la defensa:** "Usamos Django porque es un framework con baterías incluidas: resuelve lo genérico (HTTP, sesiones, seguridad, base de datos, admin) y nosotros escribimos solo la lógica de la cervecería: 10 modelos, el admin y la API."

### Ejercicio para comprobar que lo entendiste

1. Alguien hace `GET /api/pedidos/`. ¿La respuesta es HTML o JSON? ¿Y quién decide eso?
2. Nombrá tres cosas que Django resuelve por vos de la tabla de arriba y una que tuvimos que escribir nosotros.

<details>
<summary>Respuesta</summary>

1. **JSON.** La API de DRF devuelve JSON por defecto (el `BrowsableAPIRenderer` además ofrece una vista HTML si la request viene de un navegador con `Accept: text/html`, pero el contenido real es JSON). Quién lo decide: la configuración `DEFAULT_RENDERER_CLASSES` de `REST_FRAMEWORK` en `config/settings.py`, más lo que pida el cliente con el header `Accept`.
2. Lo que Django resuelve: CSRF, sesiones, migraciones, el ORM, el admin. Lo nuestro: `core/models.py` (los 10 modelos y sus reglas), `core/serializers.py`, `core/views.py`.

</details>

---

## 2. Anatomía de un proyecto Django

### La explicación en lenguaje llano

Cuando corrés `django-admin startproject config` y `startapp core`, Django crea una estructura de carpetas fija. No es un estilo: es la convención ("convention over configuration") y seguirla ahorra pelearse con el framework.

| Pieza | Qué es |
|---|---|
| `manage.py` | La terminal del proyecto. Todos los comandos (`runserver`, `migrate`, `shell`) pasan por acá. |
| `config/` | El **proyecto**: la configuración y el esqueleto. No tiene lógica de negocio. |
| `config/settings.py` | El cerebro: qué apps hay, qué base de datos usa, cómo se procesa cada request. |
| `config/urls.py` | El mapa: qué URL va a qué vista. |
| `config/wsgi.py` | El punto de entrada del servidor: `gunicorn config.wsgi:application` carga ese archivo. |
| `core/` | La **app**: acá vive todo lo de la cervecería (modelos, serializers, views, admin). |

Cinco claves de `settings.py` que hay que conocer de nombre:

| Clave | Qué hace |
|---|---|
| `INSTALLED_APPS` | La lista de módulos que Django carga al arrancar. Sin registrarla acá, una app no existe para Django. |
| `MIDDLEWARE` | Cadena de procesamiento que cada request recorre antes y después de la vista. **El orden importa.** |
| `DATABASES` | Con qué base de datos se habla y con qué credenciales. |
| `TEMPLATES` | Dónde busca Django los archivos `.html`. |
| `STATIC_URL` | Prefijo para archivos estáticos (CSS, imágenes). |

### El ejemplo de nuestro proyecto

Este es el `config/settings.py` del proyecto, recortado a lo que importa. Léelo con calma: es el archivo que más se explica solo en una defensa.

```python
from pathlib import Path
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# django-environ: lee el archivo .env que está en backend/
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    # --- de Django ---
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # --- de terceros ---
    "rest_framework",             # DRF: ViewSets, serializers, permisos
    "rest_framework.authtoken",   # token nativo para /api/auth-token/
    "drf_spectacular",            # genera el esquema OpenAPI
    "django_filters",             # filtros por query param (?tipo=GRIFO)
    "corsheaders",                # permite las requests del frontend
    # --- nuestra app ---
    "core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",       # SIEMPRE primero
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # sirve los static dentro del contenedor
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # nuestras plantillas
        "APP_DIRS": True,                   # también mira dentro de cada app
        "OPTIONS": {"context_processors": []},  # recortado
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Una sola línea decide la base de datos entera. Ver sección 11.
DATABASES = {"default": env.db("DATABASE_URL")}

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"      # a dónde va collectstatic

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "config.settings.DefaultPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Cervecería Los Flacheros API",
    "DESCRIPTION": "API REST de gestión de cervecería artesanal.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
```

Qué hace cada bloque "nuestro" del settings, en una línea por uno:

| Qué agregamos | Para qué |
|---|---|
| `rest_framework` + `rest_framework.authtoken` | La capa `/api/` y el endpoint `POST /api/auth-token/`. |
| `drf_spectacular` + `DEFAULT_SCHEMA_CLASS` | Genera el esquema OpenAPI que ves en `/api/schema/swagger-ui/` y `/api/schema/redoc/`. |
| `django_filters` + `DEFAULT_FILTER_BACKENDS` | Filtros (`?tipo=`), búsqueda (`?search=`) y orden (`?ordering=`). |
| `corsheaders` + `CorsMiddleware` primero | Sin esto, el navegador de Ema en `localhost:3000` no podría llamar a `localhost:8000`. |
| `whitenoise` en `STORAGES` y en `MIDDLEWARE` | Sirve los CSS del admin dentro del contenedor, sin instalar nginx. |
| `django-environ` (`env(...)`) | Nada hardcodeado: todo sale de `.env`. Ver sección 10. |
| `IsAuthenticated` global | Ningún endpoint abierto por defecto: primero te identificás. |

> **Para la defensa:** "`settings.py` es la configuración central: `INSTALLED_APPS` le dice a Django qué módulos cargar, `MIDDLEWARE` es la cadena que recorre cada request —con CORS primero a propósito—, `DATABASES` define la conexión y el bloque `REST_FRAMEWORK` configura DRF de forma global."

### Ejercicio para comprobar que lo entendiste

1. Si borrás `"core"` de `INSTALLED_APPS`, ¿qué se rompe? (Pensá en `models.py`, `admin.py` y las migraciones).
2. ¿Por qué `CorsMiddleware` va primero en `MIDDLEWARE` y no al final?

<details>
<summary>Respuesta</summary>

1. Django deja de ver la app: no carga sus modelos ni su `admin.py`, y `makemigrations core` falla porque no hay app que inspeccionar. Se nota rápido: el panel de admin deja de mostrar Cerveza, Pedido, etc.
2. Porque el middleware actúa como filtros apilados que se ejecutan en orden. Si CORS va al final, una request rechazada por seguridad o por la sesión ya ni llega a él, y el navegador no recibe los headers `Access-Control-Allow-Origin`. Por eso la documentación de `django-cors-headers` pide que sea el primero de la lista.

</details>

---

## 3. Qué es una app y por qué usamos una sola

### La explicación en lenguaje llano

Django mezcla dos palabras que suenan igual y son distintas:

- **Proyecto** (`config/`): el contenedor general. Hay uno solo por repositorio.
- **App** (`core/`): un módulo con sentido propio, que trae su `models.py`, `admin.py`, `views.py` y sus migraciones.

La idea de las apps es empaquetar dominios independientes: si hiciéramos una tienda, tendríamos una app `cuentas` y otra `catalogo`. La trampa es que separar apps tiene costo real: cada app suma archivos, migraciones propias, permisos y dependencias cruzadas.

### El ejemplo de nuestro proyecto

En este proyecto decidimos una sola app, `core`, con los 10 modelos adentro. Esa decisión está escrita y justificada en `tasks/plan.md` §2 (Alcance reducido): con dos personas principiantes y dos semanas, cinco apps (`catalog`, `production`, `inventory`, `sales`, `customers`) multiplican archivos y migraciones sin que el docente lo pida, y una sola app se explica en una frase.

La app se registra en dos lugares:

```python
# config/settings.py
INSTALLED_APPS = [..., "core"]

# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
```

`apps.py` es el "acta de nacimiento" de la app: dice cómo se llama y qué tipo de clave primaria usa por defecto. Django la genera con `startapp`.

### ¿Y el costo de una sola app?

Ninguno real para este tamaño: como todo está en `core/`, las migraciones se generan ordenadas según las dependencias (`Estilo` antes que `Cerveza`, porque `Cerveza` tiene una FK hacia `Estilo`), y no hay imports circulares que resolver.

> **Para la defensa:** "Elegimos una app única a propósito: con 10 modelos, dos integrantes y dos semanas, dividir en cinco apps agregaba complejidad operativa sin aportar, porque el docente pide modelos y endpoints, no una arquitectura modular. Es una decisión consciente, no una omisión."

### Ejercicio para comprobar que lo entendiste

1. El docente te dice: "vos podrías haber separado producción de ventas". Respondé en dos frases usando el argumento del alcance.
2. ¿Dónde se registra una app para que Django la cargue? Nombrá los dos archivos.

<details>
<summary>Respuesta</summary>

1. Podría haber sido, sí, pero cada app extra arrastra sus propias migraciones, sus serializers y sus imports. Con dos semanas y dos principiantes, el riesgo era no llegar; el requisito del docente es "≥10 modelos con relaciones", y eso lo cumple una sola app sin penalización.
2. En `INSTALLED_APPS` (en `config/settings.py`) y declarándola con `name = "core"` en `core/apps.py`.

</details>

---

## 4. Modelos: la base de datos

### La explicación en lenguaje llano

Un **modelo** es una clase de Python que Django convierte en una **tabla** de la base de datos. Cada atributo de la clase es una columna; cada objeto que creás es una fila.

Escribir modelos es el paso de traducir el negocio a datos: "una cerveza tiene nombre, precio, stock y un estilo". Django se encarga del SQL.

### Tipos de campo y cuándo usar cada uno

| Tipo de campo | Para qué sirve | Ejemplo nuestro |
|---|---|---|
| `CharField(max_length=N)` | Texto corto, con tope de largo | `Cerveza.nombre = CharField(max_length=150, unique=True)` |
| `TextField` | Texto largo, sin tope | `Cerveza.descripcion = TextField(blank=True)` |
| `IntegerField` | Enteros | `Cerveza.stock = IntegerField(default=0)` |
| `DecimalField(max_digits, decimal_places)` | Dinero y números con decimales exactos | `Pedido.total = DecimalField(max_digits=10, decimal_places=2)` |
| `DateField` | Fecha sin hora | `Lote.fecha_inicio = DateField()` |
| `DateTimeField` | Fecha y hora | `Pedido.fecha = DateTimeField(auto_now_add=True)` |
| `BooleanField` | Verdadero/falso | `Cerveza.activo = BooleanField(default=True)` |
| `EmailField` | Texto con validación de formato de email | `Cliente.email = EmailField(unique=True)` |
| `ForeignKey` | Relación "muchos hacia uno" | `Cerveza.estilo = FK(Estilo, PROTECT)` |

Dos detalles de oro:

- **Nunca `FloatField` para dinero.** Los flotantes tienen errores de redondeo (`0.1 + 0.2 != 0.3`). Para `precio` y `total` usamos `DecimalField`, que en Postgres es `numeric` y guarda exacto.
- `auto_now_add=True` pone la fecha de creación sola, y `auto_now=True` la actualiza en cada guardado. `Pedido.fecha` y `Cliente.fecha_alta` usan `auto_now_add`.

### Opciones de campo

| Opción | Qué hace | Ejemplo nuestro | Cuidado |
|---|---|---|---|
| `unique=True` | No puede repetirse en toda la tabla | `Cliente.dni`, `Lote.numero`, `Proveedor.cuit` | Es una restricción de la base, no solo del formulario. |
| `blank=True` | Puede venir vacío en formularios y serializers | `Cerveza.descripcion` | No toca la base. |
| `null=True` | La columna admite `NULL` en la base | `Lote.fecha_fin` | Para texto, preferí `blank=True` y nunca los dos. |
| `default=X` | Valor por defecto | `Cerveza.stock = 0`, `Cerveza.tipo = "ENVASE"` | Evita campos obligatorios molestos. |
| `choices` | Lista de valores válidos | `Cerveza.tipo`, `Lote.estado` | Valida en modelo y serializer, y documenta solo. |
| `related_name` | Nombre del acceso inverso | `related_name="cervezas"` | Ver sección 5. |
| `on_delete` | Qué hacer al borrar el padre | `PROTECT`, `CASCADE`, `SET_NULL` | Ver sección 5. |
| `db_index=True` | Índice para buscar más rápido | Para campos que se filtran mucho | Lo usamos poco: los filtros clave ya son FK o `unique`. |
| `validators` | Validaciones extra | `Opinion.puntaje` con `MinValueValidator(1)` y `MaxValueValidator(5)` | Se ejecutan en el serializer de DRF. |

**`null` vs `blank`, que es la pregunta clásica:** `blank` es validación (¿puede venir vacío en un formulario o en un POST?), `null` es la base de datos (¿se guarda `NULL`?). Por eso `descripcion = TextField(blank=True)` permite no escribir descripción, y `fecha_fin = DateField(null=True, blank=True)` además se guarda como `NULL` mientras el lote no terminó.

### `TextChoices`: los estados como constantes

Cuando un campo solo puede tener unos valores fijos, se define con `TextChoices`. Así evitamos "magia" (`"grifo"` vs `"GRIFO"` vs `"Grifo"`) y tenemos una lista que Django entiende.

```python
class Cerveza(models.Model):
    class Tipo(models.TextChoices):
        ENVASE = "ENVASE", "Envase"
        GRIFO = "GRIFO", "Grifo"

    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.ENVASE)
```

`Lote.estado` es igual pero con seis valores (`PLANIFICADO`, `EN_PRODUCCION`, `FERMENTACION`, `MADURACION`, `LISTO`, `CANCELADO`). Lo mismo en `EtapaFermentacion`, `Pedido.estado`, `Pedido.forma_pago` y `MateriaPrima`.

### `@property`: campos calculados que no existen en la base

Un `@property` es un método que se lee como si fuera un atributo. No es una columna: es lógica que se calcula al vuelo.

```python
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    # ...

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class LineaPedido(models.Model):
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # ...

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
```

DRF los puede exponer en la API como campos de solo lectura: es el caso de `subtotal` en `LineaPedidoSerializer`.

### El ejemplo completo de nuestro proyecto

Los dos modelos "cabeza" del dominio, con todo lo de arriba junto:

```python
from django.db import models


class Estilo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    ibu = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=20, blank=True)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Cerveza(models.Model):
    class Tipo(models.TextChoices):
        ENVASE = "ENVASE", "Envase"
        GRIFO = "GRIFO", "Grifo"

    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    volumen_ml = models.IntegerField(default=330)
    alcohol_pct = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    stock = models.IntegerField(default=0)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.ENVASE)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estilo = models.ForeignKey(
        Estilo, on_delete=models.PROTECT, related_name="cervezas"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
```

`__str__` no es campo: es cómo se muestra el objeto en Python, en el admin y en los logs. Sin él, verías `<Cerveza object (3)>` en el panel.

### Equivalencia Python → Django → PostgreSQL

| En Python lo pensamos como | Campo Django | Tipo en PostgreSQL |
|---|---|---|
| texto corto | `CharField(max_length=150)` | `varchar(150)` |
| texto largo | `TextField` | `text` |
| número entero | `IntegerField` | `integer` |
| dinero / decimal | `DecimalField(10, 2)` | `numeric(10, 2)` |
| booleano | `BooleanField` | `boolean` |
| fecha | `DateField` | `date` |
| fecha y hora | `DateTimeField` | `timestamp` |
| texto con formato de email | `EmailField` | `varchar(254)` (con validación en Django) |
| clave primaria | (automática) | `bigint` — por eso `DEFAULT_AUTO_FIELD = BigAutoField` |
| relación | `ForeignKey` | columna `estilo_id` con clave foránea |

> **Para la defensa:** "El modelo es la fuente de verdad: define campos, tipos, restricciones y relaciones, y de ahí Django genera las tablas con las migraciones. Para dinero usamos `DecimalField` porque los flotantes redondean mal, y los estados van con `TextChoices` para que validen solos."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué diferencia hay entre `blank=True` y `null=True`? Usá `Lote.fecha_fin` como ejemplo.
2. ¿Por qué `Cliente.dni` es `unique` y `direccion_entrega` de `Pedido` no?

<details>
<summary>Respuesta</summary>

1. `blank=True` dice "puede venir vacío en un formulario o en un JSON" (validación de Django/DRF). `null=True` dice "la columna de la base acepta `NULL`" (restricción de Postgres). `Lote.fecha_fin` tiene los dos: el lote recién planificado todavía no tiene fecha de fin, entonces no se pide y se guarda `NULL`.
2. El DNI identifica a una persona: si se repitiera, dos clientes serían indistinguibles; por eso `unique`. La dirección de entrega es un dato descriptivo del pedido que puede repetirse (dos clientes del mismo barrio) y no identifica nada.

</details>

---

## 5. Relaciones y `on_delete`

### La explicación en lenguaje llano

Las entidades del negocio no viven solas: una cerveza pertenece a un estilo, un pedido tiene líneas. Eso son **relaciones**:

| Tipo | Significado | Ejemplo | En nuestro proyecto |
|---|---|---|---|
| Uno a muchos (`ForeignKey`) | Un padre, muchos hijos | Un `Estilo` tiene muchas `Cerveza` | Las 10 FK de la tabla de abajo |
| Muchos a muchos | Ambos lados tienen muchos | Una cerveza tiene muchas opiniones, y un cliente escribe muchas | **No usamos ninguna.** Ver nota abajo. |
| Uno a uno | Como FK pero el hijo es único | Un usuario con un perfil | No usamos ninguna |

En todos los casos, la FK vive en el lado "muchos". `cerveza.estilo` te da el estilo de esa cerveza.

**Nota sobre muchos-a-muchos:** en este proyecto no hay ninguna relación M2M, y es una decisión. Por ejemplo, en vez de una tabla `Categoria` relacionada con `Cerveza`, usamos `Cerveza.tipo` con `choices` (`ENVASE`/`GRIFO`): clasifica igual, sin tabla ni endpoint extra. Lo que parece M2M (`Pedido` → muchas `LineaPedido` → una `Cerveza`) en realidad se resuelve con dos FK.

### `on_delete`: qué pasa si borro el padre

Es la opción más importante de una FK. Define el destino de las filas hijas cuando se borra el padre:

| Regla | Qué hace | Cuándo se usa |
|---|---|---|
| `CASCADE` | Borra también a los hijos | El hijo no existe sin el padre |
| `PROTECT` | **Bloquea** el borrado con un error si hay hijos | El histórico no se toca |
| `SET_NULL` | Desengancha: pone el FK en `NULL` | El dato es secundario |

Las 10 FK del proyecto, con su porqué:

| FK | Padre | `on_delete` | `related_name` | Por qué |
|---|---|---|---|---|
| `Cerveza.estilo` | `Estilo` | `PROTECT` | `cervezas` | No se borra un estilo que tiene cervezas catalogadas. |
| `Lote.cerveza` | `Cerveza` | `PROTECT` | `lotes` | El histórico de producción no se pierde. |
| `Lote.usuario` | `User` | `SET_NULL` | `lotes` | Si se va el usuario, el lote sigue existiendo; solo pierde responsable. |
| `EtapaFermentacion.lote` | `Lote` | `CASCADE` | `etapas` | Una etapa sin lote no tiene sentido. |
| `MateriaPrima.proveedor` | `Proveedor` | `SET_NULL` | `materias_primas` | La materia prima existe aunque el proveedor se dé de baja. |
| `Pedido.cliente` | `Cliente` | `PROTECT` | `pedidos` | Un pedido sin cliente pierde sentido comercial. |
| `LineaPedido.pedido` | `Pedido` | `CASCADE` | `lineas` | Las líneas son parte del pedido, no un ente aparte. |
| `LineaPedido.cerveza` | `Cerveza` | `PROTECT` | `lineas_pedido` | Qué cerveza se vendió no se puede perder. |
| `Opinion.cerveza` | `Cerveza` | `CASCADE` | `opiniones` | Una opinión no sobrevive a lo que comenta. |
| `Opinion.cliente` | `Cliente` | `CASCADE` | `opiniones` | Una opinión no sobrevive a quien la escribió. |

### Qué pasa si borrás mal

Tres escenarios que conviene poder contar:

```python
# 1. Borrado protegido -> error controlado
Cerveza.objects.get(pk=1).delete()
# Si tiene lotes o líneas: django.db.models.ProtectedError.
# Django lo frenó ANTES de tocar la base. Eso es lo que queremos.

# 2. Borrado en cascada -> borra de verdad
Lote.objects.get(numero="L-001").delete()
# Borra el lote y TODAS sus EtapaFermentacion.

# 3. Borrado que desengancha
lote = Lote.objects.get(numero="L-001")
lote.usuario.delete()        # se borra el usuario...
lote.refresh_from_db()
lote.usuario is None         # ...y el lote queda sin responsable, pero existe
```

### `related_name`: el acceso inverso y por qué lo ponemos siempre

`related_name` es el nombre con el que, desde el padre, llegás a los hijos: `estilo.cervezas.all()`, `pedido.lineas.all()`, `lote.etapas.all()`.

Se pone siempre por dos motivos:

1. **Legibilidad:** `pedido.lineas` se entiende; sin `related_name` te quedarías con `pedido.lineapedido_set`, que es el nombre por defecto de Django.
2. **Evita choques:** `Cliente` tiene dos FKs hacia sí (`Pedido.cliente` y `Opinion.cliente`). Sin nombres distintos (`pedidos` y `opiniones`), Django no sabría cómo exponer el acceso inverso.

```python
pedido = Pedido.objects.get(pk=1)
pedido.lineas.all()        # sus LineaPedido
pedido.lineas.count()      # cuántas tiene

cliente = Cliente.objects.get(pk=1)
cliente.pedidos.all()      # sus pedidos
cliente.opiniones.all()    # sus opiniones
```

> **Para la defensa:** "`on_delete` lo elegimos según el negocio, no por costumbre: `PROTECT` donde está el histórico (cervezas, clientes, ventas), `CASCADE` donde el hijo no existe sin el padre (etapas de un lote, líneas de un pedido) y `SET_NULL` donde el vínculo es secundario (el usuario responsable de un lote). Y siempre `related_name`, para poder recorrer la relación de vuelta con nombres claros."

### Ejercicio para comprobar que lo entendiste

1. Borro una `Cerveza` que tiene dos `Opinion` y un `Lote`. ¿Qué pasa y por qué?
2. Borro un `Cliente` que tiene tres `Pedido` y cinco `Opinion`. ¿Qué pasa?

<details>
<summary>Respuesta</summary>

1. Las opiniones se borran en cascada (`Opinion.cerveza` es `CASCADE`). El lote, en cambio, **bloquea** el borrado (`Lote.cerveza` es `PROTECT`): Django lanza `ProtectedError` y no borra nada, ni cerveza ni opiniones. Para eliminarla habría que borrar o desvincular el lote primero.
2. Se bloquea por los pedidos: `Pedido.cliente` es `PROTECT`, entonces Django no deja borrar al cliente. Las opiniones no son el problema (serían `CASCADE`), pero no llegan a ejecutarse porque el borrado se frena entero.

</details>

---

## 6. Migraciones

### La explicación en lenguaje llano

Cuando cambiás `models.py`, la base de datos no se entera sola: hay que decirle qué cambió. Una **migración** es un archivo que describe ese cambio de forma declarativa y versionable.

El flujo es siempre el mismo:

```
tocás models.py  →  makemigrations (genera el archivo)  →  migrate (lo aplica a la base)
```

`makemigrations` no toca la base: solo escribe el archivo. `migrate` es el que ejecuta el SQL. Por eso a veces ves "migraciones pendientes": el archivo existe pero nadie lo corrió.

### Comandos

| Comando | Qué hace |
|---|---|
| `uv run python manage.py makemigrations` | Genera migración desde los cambios de `models.py`. |
| `uv run python manage.py migrate` | Aplica las migraciones pendientes. |
| `uv run python manage.py showmigrations` | Lista las migraciones con `[x]` (aplicada) o `[ ]` (pendiente). |
| `uv run python manage.py makemigrations --check --dry-run` | No escribe nada: **falla** si hay cambios sin migrar. Es el guardia previo a commitear. |

### El ejemplo de nuestro proyecto

Nuestro orden de creación respeta las dependencias, y eso no es casual: Django no puede crear la tabla de `Cerveza` si todavía no existe la de `Estilo` a la que apunta.

```
Estilo → Cerveza → Lote → EtapaFermentacion
Proveedor → MateriaPrima
Cliente → Pedido → LineaPedido → Opinion
```

(`User` no necesita migración propia: la trae `django.contrib.auth`.)

Dentro de `core/migrations/` aparece un archivo por cambio, más el inicial:

```
backend/core/migrations/
├── 0001_initial.py      # crea las tablas
├── 0002_alter_cerveza_precio.py
└── ...
```

Y algo importante: en Docker, las migraciones se aplican solas en el arranque, porque el `command` del `compose.yaml` corre `python manage.py migrate` antes de levantar `gunicorn`. Así cualquier máquina que levante el stack queda con la base correcta.

### Por qué se versionan en el repo

Las migraciones van a git porque son parte del código. Si no se commitean:

- El entorno de Ema, el tuyo y el contenedor tendrían bases distintas.
- No se podría recrear la base desde cero en otra máquina.
- Nadie sabría qué cambios hubo y en qué orden.

Además se versionan **los modelos y las migraciones juntos**: un commit que toca `models.py` sin su migración está incompleto.

### Qué NO hacer y cómo se revierte

- **No editar a mano una migración ya aplicada.** Cambió el historial: tu base y la de otro ya no coinciden y nadie sabe qué pasó. Si te equivocaste, la forma es generar **otra** migración que corrija.
- **No borrar archivos de migración** para "ordenar". Es lo mismo de arriba.
- **No usar `runserver` como migrador** en producción: lo que despliega es el `migrate` del compose.

Para revertir hasta un punto conocido:

```bash
uv run python manage.py showmigrations core      # mirás los números
uv run python manage.py migrate core 0002        # volvés al estado del 0002
```

El segundo comando deshace las migraciones posteriores al `0002` (borra columnas o tablas que esas migraciones crearon). Por eso se usa con cuidado y solo sobre bases de las que te podés perder datos.

> **Para la defensa:** "Las migraciones son el historial de la base de datos: `makemigrations` genera el archivo desde los modelos, `migrate` lo aplica, y al versionarlas en el repo cualquiera puede recrear la base desde cero. Nunca editamos una migración aplicada: si hay un error, generamos otra que lo corrija."

### Ejercicio para comprobar que lo entendiste

1. Agregaste `Cerveza.destacada = BooleanField(default=False)` y al entrar al admin la columna no existe. ¿Qué dos comandos correr?
2. El docente pregunta: "¿y si se equivocan en una migración, cómo vuelven atrás?" Respondé con el comando exacto.

<details>
<summary>Respuesta</summary>

1. `uv run python manage.py makemigrations core` (genera el archivo) y después `uv run python manage.py migrate` (lo aplica).
2. Miran los números con `showmigrations core` y aplican `uv run python manage.py migrate core 0002`, que deja la base como estaba al final del `0002`. Y aclara que nunca se edita a mano la migración: se corrige con una nueva.

</details>

---

## 7. El ORM en la práctica

### La explicación en lenguaje llano

El **ORM** (mapeador objeto-relacional) es la capa que traduce Python a SQL. En vez de escribir `SELECT nombre, precio FROM core_cerveza WHERE tipo = 'GRIFO'`, escribís Python y Django arma el SQL.

El punto de partida es `objects`: el **manager** (administrador de consultas) que trae todo modelo. `Modelo.objects` devuelve un **QuerySet**, que es una consulta **perezosa**: no toca la base hasta que la iterás, la contás o la pedís.

### Los métodos que vas a usar

| Método | Qué hace | Ejemplo con nuestros modelos |
|---|---|---|
| `all()` | Todo | `Cerveza.objects.all()` |
| `filter(...)` | Filtra (se puede encadenar) | `Cerveza.objects.filter(tipo="GRIFO", activo=True)` |
| `exclude(...)` | Lo contrario del filtro | `Pedido.objects.exclude(estado="CANCELADO")` |
| `get(...)` | Trae **uno** o falla | `Lote.objects.get(numero="L-001")` |
| `first()` | El primero o `None` | `Pedido.objects.order_by("-fecha").first()` |
| `order_by(...)` | Ordena; el guion invierte | `Pedido.objects.order_by("-fecha")` |
| `values(...)` | Devuelve diccionarios, no objetos | `Cerveza.objects.values("nombre", "precio")` |
| `count()` | Cuántos | `LineaPedido.objects.filter(pedido=p).count()` |
| `aggregate(...)` | Resumen numérico | `Pedido.objects.aggregate(Sum("total"))` |
| `annotate(...)` | Resumen **por grupo** | `Pedido.objects.values("estado").annotate(cantidad=Count("id"))` |
| `create(...)` | Crea y guarda de una | `Cerveza.objects.create(nombre="...", precio=3500, estilo=e)` |
| `get_or_create(...)` | Trae o crea | `Estilo.objects.get_or_create(nombre="IPA", defaults={...})` |
| `select_related(...)` | JOIN para FK hacia adelante | `Pedido.objects.select_related("cliente")` |
| `prefetch_related(...)` | Precarga hijos por `related_name` | `Lote.objects.prefetch_related("etapas")` |

`filter` usa **dobles guiones bajos** para atravesar relaciones (`cliente__apellido`) y para comparar (`stock__gt=0`, `precio__gte=10000`). Es la convención de Django y es la que más se usa en el admin y en los filtros.

### Ejemplos reales: los pedidos

```python
from django.db.models import Avg, Count, Sum
from core.models import Pedido

# Pedidos pendientes del cliente "Pérez", más recientes primero
pedidos = (
    Pedido.objects
    .filter(cliente__apellido="Perez", estado="PENDIENTE")
    .order_by("-fecha")
)

# Totales: esto es exactamente lo que calcula GET /api/pedidos/estadisticas/
Pedido.objects.aggregate(
    total_pedidos=Count("id"),
    monto_total=Sum("total"),
    promedio_ticket=Avg("total"),
)

# Cuántos pedidos hay por estado
Pedido.objects.values("estado").annotate(cantidad=Count("id")).order_by("estado")
# [{'estado': 'PENDIENTE', 'cantidad': 4}, {'estado': 'ENTREGADO', 'cantidad': 9}, ...]
```

Fijate que `aggregate` devuelve **un** resumen y `values(...).annotate(...)` devuelve **uno por grupo**: es la diferencia entre "cuánto facturé en total" y "cuánto facturé por estado".

### Ejemplos reales: las cervezas

```python
from core.models import Cerveza

# Lo que sirve GET /api/cervezas/en_grifo/
Cerveza.objects.filter(tipo="GRIFO", activo=True, stock__gt=0)

# Cervezas activas y su precio, como diccionarios
Cerveza.objects.filter(activo=True).values("nombre", "precio")

# Crea una cerveza ya apuntando a un estilo existente
Cerveza.objects.create(nombre="Flachera IPA", precio=3500, estilo=estilo)

# Busca el estilo IPA o lo crea si no existe
estilo, creado = Estilo.objects.get_or_create(
    nombre="IPA",
    defaults={"descripcion": "India Pale Ale", "ibu": 60},
)
```

`get` versus `filter`: `get` devuelve **el objeto** y **lanza excepción** si no hay (`DoesNotExist`) o si hay más de uno (`MultipleObjectsReturned`). `filter` devuelve un QuerySet, que puede estar vacío y no truena. Regla práctica: `get` para buscar por clave única; `filter().first()` cuando puede no existir.

### El problema de las N+1, explicado con un caso nuestro

```python
# MAL: 1 consulta para traer los pedidos + 1 por cada cliente
pedidos = Pedido.objects.all()          # 1 query
for p in pedidos:
    print(p.cliente.nombre)             # 1 query por vuelta
# Con 50 pedidos: 51 queries.
```

Ese es el **problema N+1**: una consulta para la lista y otra por cada elemento para completar un dato que se podría haber traído de una.

```python
# BIEN: una sola query con JOIN
pedidos = Pedido.objects.select_related("cliente").all()
for p in pedidos:
    print(p.cliente.nombre)             # ya viene cargado: nada que consultar
```

La regla para elegir:

| Tipo de relación | Herramienta | Por qué | Ejemplo nuestro |
|---|---|---|---|
| FK hacia adelante (unir al padre) | `select_related("cliente")` | Hace un JOIN: todo en una query | `Pedido.objects.select_related("cliente")` |
| Acceso inverso por `related_name` (traer hijos) | `prefetch_related("etapas")` | Dos queries: los padres y después los hijos "WHERE lote_id IN (...)" | `Lote.objects.prefetch_related("etapas")` |

Y este problema no es teórico en nuestro proyecto: `GET /api/pedidos/` devuelve el cliente de cada pedido, y `GET /api/lotes/` anida las etapas. Sin `select_related`/`prefetch_related` en `get_queryset()`, cada página de 10 pedidos se pagarían 11 queries en vez de 2. Es un argumento muy bueno para la defensa.

> **Para la defensa:** "El ORM traduce consultas de Python a SQL. Usamos `filter`, `values` y `annotate` para las estadísticas sin escribir una línea de SQL, y `select_related`/`prefetch_related` para evitar el problema N+1: sin eso, un listado de 10 pedidos dispararía una consulta por pedido."

### Ejercicio para comprobar que lo entendiste

1. ¿Cuál es la diferencia entre `Pedido.objects.get(pk=1)` y `Pedido.objects.filter(pk=1).first()`?
2. Tenés el listado de `Lote` con sus `etapas` anidadas. ¿Qué línea agregás en `get_queryset()` para que no sea una query por lote?

<details>
<summary>Respuesta</summary>

1. `get` devuelve el objeto directamente, y si no existe lanza `Pedido.DoesNotExist` (la vista tendría que manejarlo para devolver un 404). `filter(...).first()` devuelve el objeto o `None`, sin excepción: es más cómodo cuando el registro puede no estar.
2. `Lote.objects.prefetch_related("etapas")`: hace una query de lotes y otra de etapas para todos juntos, en vez de una consulta por cada lote.

</details>

---

## 8. El panel de administración

### La explicación en lenguaje llano

Django trae un panel de administración **autogenerado**: si registrás un modelo con sus campos, obtenés un CRUD completo (alta, baja, listado, edición) sin escribir HTML ni vistas. Es la razón por la que Django se volvió famoso.

Registrar es declarar una clase `ModelAdmin` y pasarla con `admin.site.register(...)`. Esa clase tiene atributos que configuran cómo se ve la lista:

| Atributo | Qué controla | Ejemplo nuestro |
|---|---|---|
| `list_display` | Columnas de la tabla | `["nombre", "tipo", "precio", "stock", "activo"]` |
| `list_filter` | Filtros laterales | `["tipo", "activo"]` |
| `search_fields` | Buscador arriba | `["nombre", "descripcion"]` |
| `ordering` | Orden por defecto | `["nombre"]` |
| `autocomplete_fields` | Buscador con autocompletado para FK | `["cerveza", "usuario"]` en `LoteAdmin` |
| `readonly_fields` | Campos que no se pueden editar | Para `fecha_creacion`, que ya gestiona `auto_now_add` |
| `inlines` | Hijos editados en la misma pantalla | `EtapaFermentacionInline` en `Lote` |

### El ejemplo de nuestro proyecto

```python
# core/admin.py
from django.contrib import admin
from .models import Cerveza, EtapaFermentacion, Lote, Pedido, LineaPedido


@admin.register(Cerveza)
class CervezaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "tipo", "estilo", "precio", "stock", "activo"]
    list_filter = ["tipo", "activo", "estilo"]
    search_fields = ["nombre", "descripcion"]     # requisito del autocomplete, ver abajo
    ordering = ["nombre"]


class EtapaFermentacionInline(admin.TabularInline):
    model = EtapaFermentacion
    extra = 1                                      # filas vacías para agregar


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ["numero", "cerveza", "estado", "fecha_inicio", "volumen_litros"]
    list_filter = ["estado"]
    search_fields = ["numero", "cerveza__nombre"]  # doble guion bajo = busca en la FK
    ordering = ["-fecha_inicio"]
    autocomplete_fields = ["cerveza", "usuario"]
    inlines = [EtapaFermentacionInline]


class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "cliente", "estado", "forma_pago", "total", "fecha"]
    list_filter = ["estado", "forma_pago"]
    search_fields = ["cliente__nombre", "cliente__apellido"]
    ordering = ["-fecha"]
    inlines = [LineaPedidoInline]
```

Tres detalles que suelen caer en la defensa:

1. **`search_fields` con doble guion bajo.** `cerveza__nombre` significa "busca en el campo `nombre` del `cerveza` relacionado". Es el mismo doble guion del ORM.
2. **`autocomplete_fields` tiene un requisito.** Si en `LoteAdmin` pedís `autocomplete_fields = ["cerveza"]`, el `CervezaAdmin` **debe** tener `search_fields`; si no, Django directamente lanza un error al cargar el admin. (Con `User` no hace falta preocuparse: `django.contrib.auth` ya lo registra con `search_fields`.)
3. **`inlines` es el "nested" del admin.** Editar un `Lote` y ver sus etapas en la misma pantalla es el equivalente visual de `GET /api/lotes/` con `etapas` anidadas. Es una buena conexión para hacer en la defensa.

Sobre `actions`: el admin trae una acción por defecto ("Eliminar selección") que se puede usar en lote. Si quisiéramos una propia (por ejemplo, "dar de baja seleccionados"), se agrega un método en el `ModelAdmin`:

```python
@admin.action(description="Marcar como inactivo")
def marcar_inactivo(self, request, queryset):
    queryset.update(activo=False)

# y en la clase: actions = [marcar_inactivo]
```

En este proyecto no agregamos acciones propias porque ninguna consigna las pide; conviene igual poder mostrar que existe el mecanismo.

### ¿Por qué el docente lo evalúa?

Porque el admin es la demostración visible de que el modelo está bien pensado: filtros, búsqueda y relaciones se ven de un vistazo, y los `inlines` muestran la jerarquía de datos sin explicar nada. Es el requisito 11 del docente y, gratis, te sirve para cargar datos de prueba sin tocar la base a mano.

> **Para la defensa:** "El admin lo generamos registrando cada modelo con `list_display`, `list_filter`, `search_fields` y `ordering`; y agregamos dos `inlines` —etapas dentro de Lote y líneas dentro de Pedido—, que son el equivalente del panel a los serializers anidados de la API."

### Ejercicio para comprobar que lo entendiste

1. Entrás al admin de Pedido y no aparece el panel lateral de filtros de estado. ¿Qué atributo falta y con qué valor?
2. Al cargar `LoteAdmin` te tira un error de `autocomplete_fields`. ¿Qué revisás?

<details>
<summary>Respuesta</summary>

1. Falta `list_filter = ["estado", "forma_pago"]` en `PedidoAdmin`.
2. Que el modelo relacionado tenga `search_fields`: por ejemplo, que `CervezaAdmin` declare `search_fields = ["nombre"]`. Django exige eso porque el autocompletado es, en el fondo, una búsqueda.

</details>

---

## 9. Plantillas y vistas

### La explicación en lenguaje llano

Una **vista** es el código que responde a una URL. Una **plantilla** (template) es un archivo `.html` con marcas de Django adentro. La vista decide **qué** mostrar y la plantilla decide **cómo se ve**.

La forma más simple de devolver HTML es:

```python
return render(request, "bienvenida.html", contexto)
```

`render` hace tres cosas: arma la respuesta HTTP, busca la plantilla y la rellena con el **contexto** (un diccionario de Python disponible dentro del HTML como variables).

Hay dos estilos de vista:

| Estilo | Cuándo | Ejemplo |
|---|---|---|
| Función (`def vista(request): ...`) | Cuando hay lógica que escribir | Una vista que filtra datos |
| Clase (`TemplateView.as_view()`) | Cuando es solo mostrar una plantilla | Nuestra bienvenida |

### Los tags de plantilla que vas a ver

| Tag | Qué hace |
|---|---|
| `{% extends "base.html" %}` | Hereda de otra plantilla |
| `{% block contenido %}...{% endblock %}` | Marca un bloque que la hija puede reemplazar |
| `{% static "css/estilos.css" %}` | Ruta a un archivo estático (prefijo `STATIC_URL`) |
| `{{ variable }}` | Inserta una variable del contexto |

La herencia se usa así: `base.html` define la estructura con `{% block %}`, y cada página hija solo rellena esos bloques. En nuestro proyecto la bienvenida es una sola página, así que no usamos herencia de plantillas —es una decisión de alcance—, pero conviene saber el concepto porque el propio admin de Django funciona con plantillas heredadas (`admin/base_site.html`).

### El ejemplo de nuestro proyecto

La vista de bienvenida usa `TemplateView`, que en este caso ni siquiera necesita una función propia:

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("", TemplateView.as_view(template_name="bienvenida.html"), name="bienvenida"),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(), name="redoc"),
    path("api/auth-token/", obtain_auth_token, name="auth-token"),
]
```

Y el template `templates/bienvenida.html`, con la identidad de la marca (los colores salen del plan: ámbar `#F5A623`, lúpulo `#4A7C59`, malta `#8B4513`, espuma `#F7F7F7`, carbón `#2B2B2B`):

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Cervecería Los Flacheros</title>
  <link rel="stylesheet" href="{% static 'css/bienvenida.css' %}">
</head>
<body>
  <h1>Cervecería Los Flacheros</h1>
  <p class="lema">Arte en cada trago, tradición en cada lote</p>
</body>
</html>
```

Y si quisiéramos pasar datos desde Python, la función equivalente sería:

```python
from django.shortcuts import render

def bienvenida(request):
    contexto = {
        "titulo": "Cervecería Los Flacheros",
        "lema": "Arte en cada trago, tradición en cada lote",
    }
    return render(request, "bienvenida.html", contexto)
```

Con `{% load static %}` al principio: es el paso que carga las etiquetas de archivos estáticos; sin esa línea, `{% static %}` no existe.

> **Para la defensa:** "La vista de bienvenida es un `TemplateView` que renderiza `templates/bienvenida.html` con la identidad de la marca. Elegimos clase sobre función porque no tiene lógica: solo muestra una plantilla. Toda la data real la sirve la API, no las plantillas."

### Ejercicio para comprobar que lo entendiste

1. ¿Qué hace `{% static 'css/bienvenida.css' %}` y por qué no escribe la ruta a mano?
2. ¿Cuál es la diferencia entre lo que devuelve `/` y lo que devuelve `/api/cervezas/`?

<details>
<summary>Respuesta</summary>

1. Genera la URL del archivo estático concatenando `STATIC_URL` con la ruta relativa. No se escribe a mano porque, según el entorno, Django puede servirlos de `static/`, de `staticfiles/` (tras `collectstatic`) o de un CDN; escribir la ruta a mano rompería en cuanto cambie eso.
2. `/` devuelve HTML renderizado desde una plantilla (una página para humanos), y `/api/cervezas/` devuelve JSON desde DRF (datos para el frontend de Ema), paginado y con permisos.

</details>

---

## 10. Configuración y secretos

### La explicación en lenguaje llano

Hardcodear es pegar valores sensibles directamente en el código: la clave secreta, las contraseñas, la URL de la base. Es un error porque el código se sube a git y queda ahí para siempre, incluso si después lo borrás (git guarda el historial).

La solución es el patrón **12-factor**: la configuración vive en **variables de entorno**, no en el código. El archivo `.env` tiene los valores reales (no se commitea) y `.env.example` tiene la misma lista con placeholders (sí se commitea), para que otro sepa qué variables hace falta crear.

En Django, `django-environ` lee ese `.env` y lo convierte en variables tipadas:

```python
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("DJANGO_SECRET_KEY")          # string
DEBUG = env.bool("DEBUG", default=False)       # booleano de verdad
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])   # lista separada por comas
DATABASES = {"default": env.db("DATABASE_URL")}         # conexión parseada
```

Sin `django-environ`, tendrías que leer `os.environ[...]` y convertir a mano cada valor (¿`"True"` es True? ¿La lista, cómo?).

### `DEBUG`, `SECRET_KEY` y `ALLOWED_HOSTS`

| Variable | Qué es | Regla |
|---|---|---|
| `SECRET_KEY` | Clave que Django usa para firmar sesiones y tokens | Solo en `.env`. Rotarla invalida todas las sesiones. |
| `DEBUG` | Modo de desarrollo | `True` en local, **`False` en producción**. Con `DEBUG=True` Django muestra trazas completas con rutas y **settings enteros, incluida la `SECRET_KEY`**. |
| `ALLOWED_HOSTS` | Hosts permitidos | Si está vacío y `DEBUG=False`, Django rechaza todo con `DisallowedHost`. En Docker: `localhost`. |

### El ejemplo de nuestro proyecto

`backend/.env.example` (el que sí va a git; el `.env` real nunca):

```dotenv
DJANGO_SECRET_KEY=cambie-esto-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://flacheros:flacheros@localhost:5432/flacheros
POSTGRES_DB=flacheros
POSTGRES_USER=flacheros
POSTGRES_PASSWORD=flacheros
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Y `.gitignore` impide que el real se cuele:

```
.env
*.sqlite3
__pycache__/
.venv/
staticfiles/
```

En este proyecto no commiteamos secretos: `.env` está ignorado, `.env.example` tiene placeholders, y las credenciales del superusuario demo se documentan en el README como **credenciales de prueba explícitamente inseguras** (eso es distinto de exponer una clave real).

> **Para la defensa:** "Ningún valor sensible vive en el código: `django-environ` lee `.env`, que está en `.gitignore`, y en el repo solo va `.env.example` con placeholders. `DEBUG` queda en `False` fuera de desarrollo porque en `True` Django expone trazas y settings, incluida la `SECRET_KEY`."

### Ejercicio para comprobar que lo entendiste

1. ¿Por qué el `.env.example` se commitea y el `.env` no?
2. El docente te pregunta: "¿y si te roban el repo, tienen tu contraseña de la base?" ¿Cómo respondés?

<details>
<summary>Respuesta</summary>

1. Porque `.env.example` no tiene secretos: es la plantilla que le dice a otro desarrollador qué variables hay que crear. El `.env` sí tiene valores reales, y git guarda el historial para siempre.
2. "No, porque el repo no tiene secretos: solo tiene la plantilla `.env.example`. Los valores reales están en `.env`, que está en `.gitignore`, y además en Docker los inyecta `compose.yaml` con las variables del entorno."

</details>

---

## 11. Migrar de SQLite a PostgreSQL

### La explicación en lenguaje llano

Cuando creás un proyecto Django, `startproject` trae **SQLite** configurado: una base que vive en un solo archivo (`db.sqlite3`) y no necesita servidor. Es perfecta para arrancar, pero no es lo que se usa en un despliegue real: no escala bien con conexiones concurrentes y le faltan funciones de una base de verdad.

**PostgreSQL** es un servidor de base de datos: corre en otro proceso (en nuestro caso, en otro contenedor), soporta muchas conexiones simultáneas, y es el estándar de facto en Python. En este proyecto se usa `postgres:17`.

Lo lindo: para Django, cambiar de una a otra **es cambiar la URL de conexión**. No hay que tocar modelos ni migraciones, porque el ORM traduce el SQL a cada dialecto.

### El ejemplo de nuestro proyecto

El settings de Django traído de fábrica tiene esto:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Nosotros lo reemplazamos por una sola línea:

```python
DATABASES = {"default": env.db("DATABASE_URL")}
```

Eso significa que **quién decide la base es el entorno, no el código**. En cada uno el `DATABASE_URL` es otro:

| Entorno | `DATABASE_URL` | Quién la setea |
|---|---|---|
| Local en Windows | `postgres://flacheros:flacheros@localhost:5432/flacheros` | `backend/.env` (copia del `.env.example`) |
| Docker Compose | `postgres://flacheros:flacheros@db:5432/flacheros` | `compose.yaml`, en el bloque `environment` del servicio `web` |

Fijate en la diferencia: **`localhost` en local y `db` en Docker**. `db` no es un error de tipeo: es el nombre del servicio `db` del `compose.yaml`, y Docker resuelve ese hostname dentro de su red. Cambiar `localhost` por `db` (o al revés) es el error de conexión número uno de este proyecto.

Dos piezas más del rompecabezas:

- `psycopg[binary] 3.3.6` es el **driver**, el paquete que Django usa para hablar con Postgres. Sin él, `env.db()` apunta a Postgres pero nadie lo atiende.
- El `compose.yaml` espera a que la base esté sana antes de levantar el backend (`depends_on: condition: service_healthy` con un healthcheck `pg_isready`), y después corre `migrate` en el arranque.

Un detalle honesto para la defensa: al cambiar de base **no se migran los datos**; solo el esquema. Si tenías datos en SQLite y pasás a Postgres, hay que volver a correr el seed (`manage.py seed_datos`) contra la base nueva. Ese comando existe justamente para poder recrear datos de prueba en cualquier entorno.

> **Para la defensa:** "Local usamos la misma configuración que en Docker: `DATABASES` solo lee `DATABASE_URL` con `django-environ`, así que el cambio de SQLite a PostgreSQL es una variable, no un reescritorio de código. En el compose, esa URL apunta al servicio `db`, que es el hostname del contenedor de Postgres 17."

### Ejercicio para comprobar que lo entendiste

1. `docker compose up` y el backend tira un error de conexión a la base. ¿Qué dos hipótesis verificás primero?
2. ¿Por qué las migraciones se generan igual para SQLite y para Postgres si el SQL de cada una es distinto?

<details>
<summary>Respuesta</summary>

1. Primero: que el `DATABASE_URL` del entorno apunte a `db` (nombre del servicio) y no a `localhost`. Segundo: que el servicio `db` esté sano y hayan pasado las migraciones del arranque (revisar `docker compose logs db`).
2. Porque las migraciones describen los cambios en **términos de modelos** (agregar campo, crear tabla), no en SQL literal. El backend correspondiente (`django.db.backends.postgresql` o `...sqlite3`) traduce esa descripción al SQL de su base.

</details>

---

## 12. Comandos de `manage.py` que vas a usar

Todos se corren desde `backend/` y siempre con el prefijo `uv run`, para que usen el entorno del proyecto:

| Comando | Qué hace | Cuándo lo usás |
|---|---|---|
| `uv run python manage.py runserver` | Servidor de desarrollo en `http://localhost:8000/` | Probar en local (en Windows no corre gunicorn; eso es de Docker) |
| `uv run python manage.py migrate` | Aplica migraciones pendientes | Después de `makemigrations` y en el arranque del contenedor |
| `uv run python manage.py makemigrations` | Genera la migración desde `models.py` | Después de tocar modelos |
| `uv run python manage.py makemigrations --check --dry-run` | Falla si hay cambios de modelos sin migrar | Antes de cada commit; parte de la "triada de calidad" |
| `uv run python manage.py showmigrations` | Lista migraciones y su estado (`[x]` / `[ ]`) | Diagnosticar "¿se aplicó lo mío?" |
| `uv run python manage.py shell` | Consola Python con el proyecto cargado | Probar el ORM a mano (crear un Estilo, un Lote, etc.) |
| `uv run python manage.py createsuperuser` | Crea usuario staff para `/admin/` | Fase 3, y para el usuario demo |
| `uv run python manage.py check` | Revisa el proyecto sin tocar nada | Siempre que algo se ve raro; tira problemas de settings y apps |
| `uv run python manage.py collectstatic --noinput` | Junta los estáticos en `STATIC_ROOT` | Para que el admin tenga estilos en Docker (lo corre el compose) |
| `uv run python manage.py spectacular --file schema.yaml` | Genera el esquema OpenAPI | Para mirar o versionar el esquema |
| `uv run python manage.py spectacular --validate` | Valida el esquema sin escribirlo | Triada de calidad, antes de commitear |
| `uv run python manage.py test` | Corre tests (unittest) | Existe, pero nosotros usamos `uv run pytest` |

Dos comandos que **no** son de `manage.py` y también vas a usar todo el tiempo:

| Comando | Qué hace |
|---|---|
| `uv run pytest` | Corre los tests de `core/tests.py` con pytest-django |
| `uv run ruff check .` / `uv run ruff format .` | Lint y formateo (una sola herramienta) |

Y en la Fase 6 se suma `docker compose up --build`, que arranca la base y el backend juntos.

> **Para la defensa:** "El flujo de trabajo diario es `makemigrations` → `migrate` → `runserver`, y antes de cada commit corremos la triada: `pytest`, `ruff` y `makemigrations --check`. Todo con `uv run` para que no dependa del Python del sistema."

### Ejercicio para comprobar que lo entendiste

1. Vas a commitear y querés verificar que no faltan migraciones. ¿Qué correr? ¿Y si devuelve "exit 1"?
2. Querés crear una cerveza a mano para probar algo. ¿Qué comando te da un Python con los modelos cargados?

<details>
<summary>Respuesta</summary>

1. `uv run python manage.py makemigrations --check --dry-run`. Si sale con código distinto de cero es que cambiaste modelos sin generar la migración: corrés `makemigrations core` y commiteás migración y modelo juntos.
2. `uv run python manage.py shell`. Ahí podés hacer `from core.models import Cerveza, Estilo` y `Cerveza.objects.create(...)`. (Si querés crear datos de prueba completos y repetibles, mejor: `manage.py seed_datos`.)

</details>

---

## 13. Cómo leer un error de Django

### La explicación en lenguaje llano

Un error de Python se llama **traceback** (rastro) y tiene siempre la misma forma:

```
Traceback (most recent call last):      ← 1. La lista de "quién llamó a quién"
  File "...", line 12, in mi_vista       ← 2. Un frame: archivo + línea
    ...                                  ← 3. El código de esa línea
  File "...", line 30, in <module>
    ...
ValueError: invalid literal for int()     ← 4. EL TIPO de error + el mensaje
```

Cómo leerlo, en orden práctico:

1. **Empezá por el final.** La última línea dice *qué* falló (`IntegrityError`, `FieldError`, ...). Esa línea es la mitad del diagnóstico.
2. **Buscá el primer frame de TU código.** Los frames de Django o de librerías dicen "el fallo llegó hasta acá"; el primero tuyo dice *dónde* lo provocaste.
3. **Leé el mensaje entero.** Django es específico: te nombra la app, el modelo o la restricción.

Y una regla de oro para pedir ayuda: **un error pegado a medias no se puede resolver.** Siempre mandá estas tres cosas:

- el **comando exacto** que corriste (`uv run python manage.py migrate`),
- el **traceback completo**, de la primera línea a la última (sin recortar el medio),
- la salida de `uv run python manage.py check`.

### Los errores que más vas a ver en este proyecto

| Error | Qué significa | Causa típica acá | Qué hacer |
|---|---|---|---|
| `ModuleNotFoundError: No module named 'corsheaders'` | No encuentra un módulo | Falta `uv add django-cors-headers`, o corrés `python` en vez de `uv run python` | Instalar con `uv add` y siempre usar `uv run` |
| `OperationalError: no such table: core_cerveza` | La tabla no existe en la base | No corriste `migrate` después de crear los modelos | `uv run python manage.py migrate` |
| `OperationalError: could not connect to server` | No hay base escuchando | Postgres no levantado, o `DATABASE_URL` apunta a `localhost` cuando debería ser `db` (o al revés) | `docker compose up -d db` y revisar la URL (sección 11) |
| `ProgrammingError: column core_cerveza.alcohol_pct does not exist` | El SQL pide una columna que la base no tiene | Cambiaste un campo en `models.py` y no migraste | `makemigrations` + `migrate` |
| `ImproperlyConfigured: Requested setting DEBUG, but settings are not configured` | Django no sabe cuál es su settings | Falta `DJANGO_SETTINGS_MODULE = "config.settings"` en la config de pytest | Revisar `[tool.pytest.ini_options]` de `pyproject.toml` |
| `IntegrityError: duplicate key value violates unique constraint "core_cerveza_nombre_key"` | Violaste una restricción de la base | Intentaste crear dos cervezas con el mismo `nombre` (o dos clientes con el mismo `dni`) | Cambiar el dato; si era un `unique` de más, hay que generar una migración para quitarlo |
| `ProtectedError: Cannot delete ... because it is referenced through protected field` | `PROTECT` hizo su trabajo | Intentaste borrar una `Cerveza` con lotes, o un `Cliente` con pedidos | No borrar, o borrar primero lo dependiente. Es un freno, no un bug |
| `FieldError: Cannot resolve keyword 'estdo' into field` | Un campo que Django no conoce | Error de tipeo en un `filter()`, o un `related_name` equivocado | Revisar el nombre contra `models.py` |
| `AttributeError: 'NoneType' object has no attribute 'username'` | Un objeto es `None` y le pediste algo | `Lote.usuario` es `NULL` (es `SET_NULL`) y alguien accede a `lote.usuario.username` sin chequear | Chequear `if lote.usuario:` antes de usarlo |
| Blanco en el template donde esperabas un dato | En plantillas, Django no explota: rinde vacío | Un nombre mal escrito en `{{ ... }}` o un `None` (por ejemplo, el usuario del lote) | Revisar el contexto que pasa la vista; activar `DEBUG` para ver detalles |

Dos aclaraciones que te van a ahorrar malentendidos en la defensa:

- `ProtectedError` **no es un bug**: es la protección de la sección 5 funcionando. Django frenó el borrado antes de tocar la base.
- En templates, un dato que aparece **vacío** es tan sospechoso como un error en rojo: Django prefiere no romper la página, pero eso significa que el error está escondido.

> **Para la defensa:** "Ante un error leo el traceback de abajo para arriba: la última línea me dice qué falló y el primer frame del código nuestro me dice dónde. Después de diagnosticar, corro `manage.py check`. Y cuando pido ayuda, mando el comando, el traceback completo y ese check: un error pegado a medias no se puede resolver."

### Ejercicio para comprobar que lo entendiste

1. Mirá este mensaje y decí qué pasó y cómo lo resolvés: `IntegrityError: duplicate key value violates unique constraint "core_proveedor_cuit_key"`.
2. En `GET /api/lotes/` ves el campo `usuario` en `null` para un lote. ¿Es un error de Django? ¿Y si el serializer hace `lote.usuario.username`?

<details>
<summary>Respuesta</summary>

1. Intentaste crear (o editar) un `Proveedor` con un `cuit` que ya existe; `cuit` es `unique`. Se resuelve usando el CUIT correcto o cambiando el dato. No es un bug del código: es la restricción haciendo su trabajo.
2. No es un error: `Lote.usuario` es `SET_NULL`, está pensado para quedar `None` si se borra el usuario. El problema aparece recién cuando el serializer o la vista hacen `lote.usuario.username` sin chequear, porque ahí sí truena con `AttributeError`. Se evita chequeando `if lote.usuario` (o con `serializer_method_field`).

</details>

---

## 14. Resumen: qué memorizar para la defensa

Checklist final. Si podés marcar los 15 puntos sin mirar, esta guía está aprendida:

1. **Framework** = código genérico ya escrito; Django resuelve HTTP, sesiones, seguridad, ORM, admin y migraciones.
2. **Ciclo request/response:** cliente → middleware → `urls.py` → vista → base de datos → respuesta.
3. **Proyecto vs app:** `config/` es la configuración; `core/` es el módulo de negocio; una sola app es una decisión de alcance.
4. **`settings.py`:** `INSTALLED_APPS`, `MIDDLEWARE` (con `CorsMiddleware` primero), `DATABASES`, `TEMPLATES`, `STATIC_URL`.
5. **Modelo** = tabla; campo clave: `CharField`, `TextField`, `IntegerField`, `DecimalField`, `DateField`, `DateTimeField`, `BooleanField`, `EmailField`, `ForeignKey`.
6. **Dinero siempre con `DecimalField`**, nunca `FloatField`.
7. **`blank` es validación, `null` es la base de datos.**
8. **`TextChoices`** para estados y tipos; **`@property`** para `nombre_completo` y `subtotal` (no son columnas).
9. **`on_delete`:** `PROTECT` = histórico, `CASCADE` = hijo sin padre no existe, `SET_NULL` = vínculo secundario. Ejemplos: `Cerveza→Lote` PROTECT, `Lote→Etapa` CASCADE, `Lote→Usuario` SET_NULL.
10. **`related_name`** siempre: acceso inverso legible y sin choques.
11. **Migraciones:** `makemigrations` genera, `migrate` aplica, `--check` verifica antes de commitear; se versionan y no se editan a mano; se revierte con `migrate core 0002`.
12. **ORM:** `filter`/`exclude`/`get`/`order_by`/`values`/`annotate`; `select_related` para FK y `prefetch_related` para hijos = no N+1.
13. **Admin:** `list_display`, `list_filter`, `search_fields`, `ordering`, `inlines` (etapas en Lote, líneas en Pedido), y `autocomplete_fields` exige `search_fields` en el modelo relacionado.
14. **Secretos en `.env`** con `django-environ`; `.env.example` commiteado; `DEBUG=False` fuera de desarrollo.
15. **PostgreSQL por `DATABASE_URL`**; en Docker el host es `db`; los errores se leen de abajo para arriba y se piden con el traceback completo.

> **Para la defensa:** "Todo el backend se apoya en cinco ideas: modelos como fuente de verdad, migraciones para evolucionar la base sin romper datos, el ORM para no escribir SQL, relaciones con `on_delete` elegido según el negocio, y una configuración entera fuera del código en variables de entorno."

### Ejercicio para comprobar que lo entendiste

1. Grabate (o contale a tu compañero) explicando en 3 minutos por qué `EtapaFermentacion.lote` es `CASCADE` y `Lote.cerveza` es `PROTECT`. Marcá los ítems de la checklist que te salieron **sin mirar**.
2. Decí de memoria los tres comandos del flujo diario y qué hace cada uno.

<details>
<summary>Respuesta</summary>

1. Una etapa no existe sin su lote: si borrás el lote, sus etapas se borran con él (`CASCADE`). Pero un lote es histórico de producción de una cerveza: no se puede borrar la cerveza y arrastrar lotes hechos; Django lo frena con `PROTECT`. Si te salieron los dos `related_name` (`etapas` y `lotes`) y el `ProtectedError`, dominaste el ítem 9.
2. `makemigrations` genera el archivo de migración desde los modelos; `migrate` lo aplica a la base; `makemigrations --check --dry-run` verifica que no queden cambios sin migrar (sin escribir nada). Y se corren con `uv run python manage.py ...`.

</details>
