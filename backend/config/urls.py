"""URLs de configuración del proyecto Cervecería Los Flacheros.

Alcance inicial (Task 4): solo el admin. La vista de bienvenida, la API, el
schema y el endpoint de token se agregan en la Task 6.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
