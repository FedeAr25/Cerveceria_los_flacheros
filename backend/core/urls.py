"""URLs de la API: el `DefaultRouter` de DRF con los 10 ViewSets.

`config/urls.py` monta este router bajo `/api/`. Cada ViewSet se registra
con `basename` explícito: así los nombres de las rutas (los que usa el
format suffix y la reversa) no dependen del nombre de la clase
(`MateriaPrimaViewSet` → `materiaprima`, `LineaPedidoViewSet` →
`lineapedido`, etc.) y no se rompen si algún día se renombra una vista.
"""

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
router.register(r"estilos", EstiloViewSet, basename="estilo")
router.register(r"cervezas", CervezaViewSet, basename="cerveza")
router.register(r"lotes", LoteViewSet, basename="lote")
router.register(r"etapas", EtapaViewSet, basename="etapa")
router.register(r"proveedores", ProveedorViewSet, basename="proveedor")
router.register(r"materias-primas", MateriaPrimaViewSet, basename="materiaprima")
router.register(r"clientes", ClienteViewSet, basename="cliente")
router.register(r"pedidos", PedidoViewSet, basename="pedido")
router.register(r"lineas", LineaPedidoViewSet, basename="lineapedido")
router.register(r"opiniones", OpinionViewSet, basename="opinion")

urlpatterns = router.urls
