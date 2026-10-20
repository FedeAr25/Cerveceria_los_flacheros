"""Vistas de la app core: la bienvenida en `/` y los 10 ViewSets de la API.

Regla única de permisos (plan §8): **lectura** = cualquier usuario
autenticado (`IsAuthenticated`, el global de settings); **escritura** = solo
staff (`IsAdminUser`), con una sola excepción: el mostrador
(`PedidoViewSet` y `LineaPedidoViewSet`), donde cualquier usuario
autenticado crea y edita — ahí atiende el bar, que no es staff.

La regla se ve explícita en el código vía `get_permissions()` en las bases
compartidas de este archivo (`APIViewSet`, `CatalogoViewSet`,
`MostradorViewSet`), no escondida en settings.
"""

from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Cerveza,
    Cliente,
    Estilo,
    EtapaFermentacion,
    LineaPedido,
    Lote,
    MateriaPrima,
    Opinion,
    Pedido,
    Proveedor,
)
from .serializers import (
    CervezaSerializer,
    ClienteSerializer,
    EstadisticasPedidoSerializer,
    EstiloSerializer,
    EtapaFermentacionSerializer,
    LineaPedidoSerializer,
    LoteNestedSerializer,
    LoteSerializer,
    MateriaPrimaSerializer,
    OpinionSerializer,
    PedidoNestedSerializer,
    PedidoSerializer,
    ProveedorSerializer,
)


class HomeView(TemplateView):
    """Vista de bienvenida de la cervecería (página pública en `/`)."""

    template_name = "bienvenida.html"


# --- Bases de permisos ------------------------------------------------------
# `self.action` guarda qué está haciendo la request ("list", "create",
# "avanzar", ...): con eso, `get_permissions()` decide quién puede pasar.


class APIViewSet(viewsets.ModelViewSet):
    """CRUD base de la API con permisos por acción.

    Lectura → `IsAuthenticated`; escritura → `IsAdminUser` para las acciones
    listadas en `acciones_staff` de cada subclase.
    """

    # Acciones que escriben sobre el recurso y por lo tanto piden staff.
    acciones_staff = ()

    def get_permissions(self):
        if self.action in self.acciones_staff:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class CatalogoViewSet(APIViewSet):
    """Catálogo (estilos, cervezas, lotes, ...): escribir es cosa del staff."""

    acciones_staff = ("create", "update", "partial_update", "destroy")


class MostradorViewSet(APIViewSet):
    """Mostrador (pedidos y líneas): cualquier autenticado crea y edita.

    A propósito no hereda el `acciones_staff` de `CatalogoViewSet`: acá se
    toma pedido en el bar, y el que atiende no es staff.
    """


# --- Catálogo: producción e insumos ------------------------------------------


class EstiloViewSet(CatalogoViewSet):
    """Estilos de cerveza (IPA, Stout, APA, Weizen)."""

    queryset = Estilo.objects.all()
    serializer_class = EstiloSerializer
    search_fields = ["nombre"]
    ordering_fields = ["orden", "nombre"]
    ordering = ["orden", "nombre"]


class CervezaViewSet(CatalogoViewSet):
    """Cervezas vendibles; filtro por estilo/tipo/activo y acción `en_grifo`."""

    queryset = Cerveza.objects.select_related("estilo").all()
    serializer_class = CervezaSerializer
    filterset_fields = ["estilo", "tipo", "activo"]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["precio", "nombre", "fecha_creacion"]
    ordering = ["-fecha_creacion"]

    @action(detail=False, methods=["GET"], url_path="en_grifo")
    def en_grifo(self, request):
        queryset = self.get_queryset().filter(tipo="GRIFO", activo=True, stock__gt=0)
        # paginate_queryset y get_paginated_response respetan la paginación
        # global: la respuesta tiene la misma forma que cualquier listado.
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class EtapaViewSet(CatalogoViewSet):
    """Etapas de fermentación dentro de un lote (primaria, secundaria, ...)."""

    queryset = EtapaFermentacion.objects.select_related("lote").all()
    serializer_class = EtapaFermentacionSerializer
    filterset_fields = ["lote"]
    ordering_fields = ["numero"]
    ordering = ["numero"]


class LoteViewSet(CatalogoViewSet):
    """Lotes de producción: `etapas` anidadas solo en list + acción `avanzar`."""

    queryset = (
        Lote.objects.select_related("cerveza", "usuario")
        .prefetch_related("etapas")
        .all()
    )
    serializer_class = LoteSerializer
    search_fields = ["numero", "cerveza__nombre"]
    ordering_fields = ["fecha_inicio"]
    ordering = ["-fecha_inicio"]
    # `avanzar` mueve el estado del lote: además de escribir el registro,
    # es una acción propia que pide staff.
    acciones_staff = CatalogoViewSet.acciones_staff + ("avanzar",)

    def get_serializer_class(self):
        # Datos anidados SOLO en `list` (requisito de la consigna): el
        # detalle y las escrituras van con el serializer plano, liviano.
        if self.action == "list":
            return LoteNestedSerializer
        return LoteSerializer

    @action(
        detail=True,
        methods=["POST"],
        url_path="avanzar",
        permission_classes=[IsAdminUser],
    )
    def avanzar(self, request, pk=None):
        lote = self.get_object()
        # Acepta opcionalmente {"estado": "..."} para pedir un salto concreto;
        # sin body avanza un paso a el siguiente de la máquina de estados.
        destino = request.data.get("estado") or Lote.TRANSICIONES.get(lote.estado)
        if destino is None:
            # LISTO y CANCELADO son terminales: no tienen estado siguiente.
            return Response(
                {
                    "detail": (
                        f"El lote {lote.numero} no se puede avanzar: "
                        f"está en {lote.estado}."
                    )
                },
                status=400,
            )
        if not lote.puede_avanzar_a(destino):
            # La máquina de estados solo permite avanzar un paso por vez.
            return Response(
                {
                    "detail": (
                        f"Salto inválido: el lote {lote.numero} está en "
                        f"{lote.estado} y no puede pasar directo a {destino}."
                    )
                },
                status=400,
            )
        lote.estado = destino
        lote.save(update_fields=["estado"])
        return Response(self.get_serializer(lote).data)


class ProveedorViewSet(CatalogoViewSet):
    """Proveedores de materia prima."""

    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    search_fields = ["razon_social", "cuit"]
    ordering_fields = ["razon_social"]
    ordering = ["razon_social"]


class MateriaPrimaViewSet(CatalogoViewSet):
    """Insumos del depósito, filtrables por tipo y proveedor."""

    queryset = MateriaPrima.objects.select_related("proveedor").all()
    serializer_class = MateriaPrimaSerializer
    filterset_fields = ["tipo", "proveedor"]
    search_fields = ["nombre"]
    ordering_fields = ["tipo", "nombre"]
    ordering = ["tipo", "nombre"]


# --- Ventas y feedback ------------------------------------------------------


class ClienteViewSet(CatalogoViewSet):
    """Fichas de clientes (el mostrador solo lee: escribir cliente es staff)."""

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    search_fields = ["nombre", "apellido", "email", "dni"]
    ordering_fields = ["fecha_alta"]
    ordering = ["-fecha_alta"]


class PedidoViewSet(MostradorViewSet):
    """Pedidos del mostrador: `lineas` anidadas solo en list + `estadisticas`."""

    queryset = Pedido.objects.select_related("cliente").prefetch_related("lineas").all()
    serializer_class = PedidoSerializer
    filterset_fields = ["estado", "forma_pago"]
    search_fields = ["cliente__nombre", "cliente__apellido"]
    ordering_fields = ["fecha"]
    ordering = ["-fecha"]
    # Es el mostrador: cualquiera autenticado crea y edita pedidos; la única
    # acción que pide staff son las métricas agregadas.
    acciones_staff = ("estadisticas",)

    def get_serializer_class(self):
        # Datos anidados SOLO en `list` (requisito de la consigna): el
        # detalle y las escrituras van con el serializer plano, liviano.
        if self.action == "list":
            return PedidoNestedSerializer
        return PedidoSerializer

    @action(
        detail=False,
        methods=["GET"],
        url_path="estadisticas",
        permission_classes=[IsAdminUser],
    )
    def estadisticas(self, request):
        queryset = self.get_queryset()
        totales = queryset.aggregate(monto=Sum("total"), promedio=Avg("total"))
        por_estado = {
            fila["estado"]: fila["n"]
            for fila in queryset.values("estado").annotate(n=Count("id"))
        }
        data = {
            "total_pedidos": queryset.count(),
            "monto_total": totales["monto"],
            "pedidos_por_estado": por_estado,
            "promedio_ticket": totales["promedio"],
        }
        serializer = EstadisticasPedidoSerializer(instance=data)
        return Response(serializer.data)


class LineaPedidoViewSet(MostradorViewSet):
    """Líneas de pedido del mostrador; mantienen vivo el `total` del pedido."""

    queryset = LineaPedido.objects.select_related("pedido", "cerveza").all()
    serializer_class = LineaPedidoSerializer
    ordering_fields = ["pedido__fecha"]
    ordering = ["-pedido__fecha"]

    def _recalcular_total(self, pedido):
        # `Pedido.total` es un campo GUARDADO (no se recalcula en cada
        # respuesta): lo re-sumo desde los subtotales de sus líneas para que
        # el total que ve el frontend sea siempre el real.
        pedido.total = sum(
            (linea.subtotal for linea in pedido.lineas.all()), Decimal("0")
        )
        pedido.save(update_fields=["total"])

    def perform_create(self, serializer):
        linea = serializer.save()
        self._recalcular_total(linea.pedido)

    def perform_update(self, serializer):
        pedido_anterior = serializer.instance.pedido
        linea = serializer.save()
        self._recalcular_total(pedido_anterior)
        if linea.pedido_id != pedido_anterior.pk:
            # Si la línea cambió de pedido, hay que recalcular los dos.
            self._recalcular_total(linea.pedido)

    def perform_destroy(self, instance):
        pedido = instance.pedido
        instance.delete()
        self._recalcular_total(pedido)


class OpinionViewSet(CatalogoViewSet):
    """Reseñas de clientes (puntaje 1-5 + comentario); escribir es staff."""

    queryset = Opinion.objects.select_related("cerveza", "cliente").all()
    serializer_class = OpinionSerializer
    ordering_fields = ["fecha"]
    ordering = ["-fecha"]
