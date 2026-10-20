"""
Settings globales del proyecto Cervecería Los Flacheros.

Archivo único (no paquete): todos los ajustes viven acá. Los valores
sensibles o por-entorno (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL,
CORS_ALLOWED_ORIGINS) se leen del archivo `.env` con django-environ.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# `.env.example` es la plantilla; `.env` NO se commitea (está en .gitignore).
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # API REST y ecosistema
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    # App única del dominio de la cervecería
    "core",
]

MIDDLEWARE = [
    # CorsMiddleware SIEMPRE primero: debe correr antes de cualquier respuesta.
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Base de datos: SQLite local por defecto. En Docker (Fase 6) el compose
# inyecta una URL de PostgreSQL vía DATABASE_URL.
DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3")}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Argentina (ITEC Río Cuarto, Córdoba)
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Cordoba"
USE_I18N = True
USE_TZ = True

# Las URLs de estáticos deben ser absolutas (con "/" inicial) para que
# whitenoise y el `{% static %}` funcionen en cualquier ruta, no solo en la raíz.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# whitenoise sirve los estáticos (admin y plantillas) dentro del contenedor,
# sin necesidad de nginx.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # El manifiesto exige re-correr `collectstatic` cuando se agrega un
        # archivo estático nuevo; si no, whitenoise tira "Missing staticfiles
        # manifest entry" y el sitio se cae.
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    # Sesión + token: requisito del docente (autenticación por ambos medios).
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Sin token no hay API: cada ViewSet afina el permiso que necesita.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "config.settings.DefaultPagination",
    # Sin PAGE_SIZE acá: el tamaño de página vive en la clase DefaultPagination
    # (page_size=10, page_size_query_param="page_size", max_page_size=50).
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
    # Sin esto, dos choice sets que comparten nombre de campo (p. ej. "estado"
    # en Lote y Pedido) colisionan y drf-spectacular les pone nombres
    # autogenerados tipo "EstadoD9aEnum" en Swagger UI. Cada entrada
    # {nombre_en_el_schema: ruta_python} fija un nombre legible. Las rutas de
    # enums anidados en un modelo son "app.Modelo.Clase".
    "ENUM_NAME_OVERRIDES": {
        "EstadoLote": "core.models.Lote.Estado",
        "EstadoPedido": "core.models.Pedido.Estado",
        "EstadoEtapa": "core.models.EtapaFermentacion.Estado",
        "TipoCerveza": "core.models.Cerveza.Tipo",
        "TipoEtapa": "core.models.EtapaFermentacion.Tipo",
        "TipoMateriaPrima": "core.models.MateriaPrima.Tipo",
        "UnidadMateriaPrima": "core.models.MateriaPrima.Unidad",
        "FormaPagoPedido": "core.models.Pedido.FormaPago",
    },
}

# Origen del frontend (Next.js, puerto 3000). Restringido a propósito:
# nunca CORS_ALLOW_ALL_ORIGINS junto a CORS_ALLOW_CREDENTIALS.
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)

# El import va DESPUÉS de REST_FRAMEWORK y no arriba del archivo: importar un
# módulo de DRF mientras este archivo se está ejecutando (aún sin terminar de
# cargar settings) hace que DRF cachee sus settings desde un módulo a medio
# cargar y pierda DEFAULT_SCHEMA_CLASS. Con REST_FRAMEWORK ya definido, DRF
# resuelve bien. noqa=E402 porque el orden es deliberado.
from rest_framework.pagination import PageNumberPagination  # noqa: E402


class DefaultPagination(PageNumberPagination):
    """Paginación global: 10 por página; el cliente puede pedir hasta 50."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
