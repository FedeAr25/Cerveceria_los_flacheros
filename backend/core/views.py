"""Vistas de la app core."""

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Vista de bienvenida de la cervecería (página pública en `/`)."""

    template_name = "bienvenida.html"
