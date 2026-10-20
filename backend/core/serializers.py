"""Serializers de la app core: el traductor entre modelos y JSON.

Hay 10 serializers planos (uno por modelo) más dos anidados
(`LoteNestedSerializer` y `PedidoNestedSerializer`) que suman los hijos
(`etapas`, `lineas`), pero que solo se usan en `list` — el detalle y las
escrituras van planos (plan §8, "nested solo en list").

Convenciones, iguales a las de `docs/02-drf-esencial.md`:

- Las FK viajan como id (`PrimaryKeyRelatedField`): es lo más simple para
  el frontend. `Lote.usuario` y `MateriaPrima.proveedor` son nulables
  (`allow_null=True, required=False`).
- Los `@property` del modelo (`Cliente.nombre_completo`,
  `LineaPedido.subtotal`) se declaran a mano como campos de solo lectura:
  `ModelSerializer` solo infiere columnas de tabla, no cálculos de Python.
- Los campos `Decimal` llevan `coerce_to_string=False` porque el contrato
  con el frontend (tasks/api-contract.md) los congela como números JSON
  (`"precio": 4500.00`); sin eso, DRF por defecto los manda como strings
  (`"4500.00"`) y el frontend tendría que parsearlos a mano.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

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


class EstiloSerializer(serializers.ModelSerializer):
    """Estilo de cerveza (IPA, Stout, APA, Weizen)."""

    class Meta:
        model = Estilo
        fields = ["id", "nombre", "descripcion", "ibu", "color", "orden"]


class CervezaSerializer(serializers.ModelSerializer):
    """Cerveza vendible: precio, stock, tipo y su estilo (como id)."""

    class Meta:
        model = Cerveza
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "volumen_ml",
            "alcohol_pct",
            "stock",
            "tipo",
            "activo",
            "fecha_creacion",
            "estilo",
        ]
        extra_kwargs = {
            "precio": {"coerce_to_string": False},
            "alcohol_pct": {"coerce_to_string": False},
        }


class LoteSerializer(serializers.ModelSerializer):
    """Lote de producción plano: sin `etapas` (esas van en el nested de list)."""

    # FK nulable: el lote sobrevive aunque se borre el usuario responsable
    # (SET_NULL en el modelo), así que el campo acepta null y no es obligatorio.
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Lote
        fields = [
            "id",
            "numero",
            "fecha_inicio",
            "fecha_fin",
            "volumen_litros",
            "estado",
            "notas",
            "cerveza",
            "usuario",
        ]
        extra_kwargs = {"volumen_litros": {"coerce_to_string": False}}


class EtapaFermentacionSerializer(serializers.ModelSerializer):
    """Etapa dentro de un lote (primaria, secundaria, madurado)."""

    class Meta:
        model = EtapaFermentacion
        fields = [
            "id",
            "numero",
            "tipo",
            "fecha_inicio",
            "fecha_fin",
            "temperatura",
            "estado",
            "lote",
        ]
        extra_kwargs = {"temperatura": {"coerce_to_string": False}}


class ProveedorSerializer(serializers.ModelSerializer):
    """Proveedor de materia prima."""

    class Meta:
        model = Proveedor
        fields = ["id", "razon_social", "cuit", "email", "telefono", "activo"]


class MateriaPrimaSerializer(serializers.ModelSerializer):
    """Insumo del depósito, con su proveedor (id o null)."""

    # FK nulable: el insumo queda en el depósito aunque se dé de baja al
    # proveedor (SET_NULL en el modelo).
    proveedor = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = MateriaPrima
        fields = [
            "id",
            "nombre",
            "tipo",
            "unidad",
            "stock",
            "stock_minimo",
            "costo_unitario",
            "proveedor",
        ]
        extra_kwargs = {
            "stock": {"coerce_to_string": False},
            "stock_minimo": {"coerce_to_string": False},
            "costo_unitario": {"coerce_to_string": False},
        }


class ClienteSerializer(serializers.ModelSerializer):
    """Ficha del cliente; `nombre_completo` es un @property, no una columna."""

    # El modelo calcula nombre + apellido en el @property `nombre_completo`:
    # ModelSerializer no lo infiere, va declarado a mano y solo lectura.
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id",
            "nombre",
            "apellido",
            "email",
            "telefono",
            "dni",
            "activo",
            "fecha_alta",
            "nombre_completo",
        ]


class PedidoSerializer(serializers.ModelSerializer):
    """Cabecera del pedido plano: sin `lineas` (esas van en el nested de list).

    `total` es un campo guardado en la base: lo mantiene la capa de API
    (el recálculo vive en `LineaPedidoViewSet`), no se recalcula en cada
    respuesta.
    """

    class Meta:
        model = Pedido
        fields = [
            "id",
            "fecha",
            "estado",
            "forma_pago",
            "total",
            "direccion_entrega",
            "observaciones",
            "cliente",
        ]
        extra_kwargs = {"total": {"coerce_to_string": False}}


class LineaPedidoSerializer(serializers.ModelSerializer):
    """Renglón del pedido: `subtotal` es el @property cantidad × precio."""

    # El modelo lo calcula con un @property (no es columna de la tabla), así
    # que se declara a mano; al ser read_only, nadie manda un subtotal trucho.
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, coerce_to_string=False
    )

    class Meta:
        model = LineaPedido
        fields = [
            "id",
            "cantidad",
            "precio_unitario",
            "subtotal",
            "pedido",
            "cerveza",
        ]
        extra_kwargs = {"precio_unitario": {"coerce_to_string": False}}


class OpinionSerializer(serializers.ModelSerializer):
    """Reseña de un cliente sobre una cerveza (puntaje 1-5 + comentario)."""

    class Meta:
        model = Opinion
        fields = ["id", "puntaje", "comentario", "fecha", "cerveza", "cliente"]


class LoteNestedSerializer(LoteSerializer):
    """Lote con sus etapas y el nombre de la cerveza: SOLO para el listado.

    El detalle (`{id}/`) y las escrituras usan `LoteSerializer` (plano).
    """

    etapas = EtapaFermentacionSerializer(many=True, read_only=True)
    cerveza_nombre = serializers.CharField(source="cerveza.nombre", read_only=True)

    class Meta(LoteSerializer.Meta):
        fields = [
            "id",
            "numero",
            "fecha_inicio",
            "fecha_fin",
            "volumen_litros",
            "estado",
            "notas",
            "cerveza",
            "cerveza_nombre",
            "usuario",
            "etapas",
        ]


class PedidoNestedSerializer(PedidoSerializer):
    """Pedido con sus líneas y el nombre del cliente: SOLO para el listado.

    El detalle (`{id}/`) y las escrituras usan `PedidoSerializer` (plano).
    """

    lineas = LineaPedidoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(
        source="cliente.nombre_completo", read_only=True
    )

    class Meta(PedidoSerializer.Meta):
        fields = [
            "id",
            "fecha",
            "estado",
            "forma_pago",
            "total",
            "direccion_entrega",
            "observaciones",
            "cliente",
            "cliente_nombre",
            "lineas",
        ]


class EstadisticasPedidoSerializer(serializers.Serializer):
    """Métricas de pedidos: cuatro valores calculados, no filas de una tabla.

    `monto_total` y `promedio_ticket` son `allow_null=True` porque, sin
    pedidos cargados, los agregados del ORM (`Sum`, `Avg`) devuelven `None`
    y el contrato los congela como `null`.
    """

    total_pedidos = serializers.IntegerField()
    monto_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, coerce_to_string=False
    )
    pedidos_por_estado = serializers.DictField()
    promedio_ticket = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, coerce_to_string=False
    )
