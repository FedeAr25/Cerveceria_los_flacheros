"""URLs de la API: router de DRF montado en `/api/`.

El router está vacío hasta la Fase 4, cuando se registren los 10 ViewSets.
Igual expone `/api/` con la API navegable de DRF.
"""

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = router.urls
