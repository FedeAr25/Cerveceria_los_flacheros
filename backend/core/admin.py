"""Panel de administración: control total sobre los 10 modelos.

Requisito del docente: cada modelo registrado con `list_display`,
`list_filter`, `search_fields` y `ordering`. Dos ideas clave para la defensa:

- PROTECT (en models.py): los FK con historial (Cerveza.estilo, Lote.cerveza,
  Pedido.cliente, LineaPedido.cerveza) impiden borrar registros con datos
  asociados: al intentar eliminar, el admin muestra "ProtectedError" en lugar
  de dejar un histórico huérfano.
- Autocomplete e inlines: ver los comentarios en cada ModelAdmin.
"""

from django.contrib import admin

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


class EtapaFermentacionInline(admin.TabularInline):
    """Las etapas se editan dentro de su lote.

    Relación 1-N con datos dependientes (etapa.lote es CASCADE): la etapa no
    existe sin el lote, así que mostrarla como inline evita pantallas sueltas
    donde se podría crear una etapa "colgada" de cualquier lote.
    """

    model = EtapaFermentacion
    extra = 1


class LineaPedidoInline(admin.TabularInline):
    """Los renglones se editan en la cabecera del pedido (pedido.lineas,
    CASCADE). Misma lógica que las etapas: un renglón sin pedido no existe."""

    model = LineaPedido
    extra = 1


@admin.register(Estilo)
class EstiloAdmin(admin.ModelAdmin):
    # search_fields acá también es requisito técnico del autocomplete de
    # Cerveza.estilo: Django exige que el admin destino defina search_fields.
    list_display = ["nombre", "ibu", "color", "orden"]
    list_filter = ["color"]
    search_fields = ["nombre", "descripcion", "color"]
    list_per_page = 25
    search_help_text = "Buscar por nombre, descripción o color."
    ordering = ["orden", "nombre"]


@admin.register(Cerveza)
class CervezaAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Catálogo", {"fields": ("nombre", "estilo", "tipo", "descripcion")}),
        ("Datos técnicos", {"fields": ("precio", "volumen_ml", "alcohol_pct")}),
        ("Stock y estado", {"fields": ("stock", "activo")}),
        ("Alta", {"fields": ("fecha_creacion",)}),
    )
    # El estilo se elige con autocomplete en vez de un desplegable gigante;
    # requiere que EstiloAdmin tenga search_fields (si no, Django tira 404).
    autocomplete_fields = ["estilo"]
    # "stock" y "activo" están en list_display y en list_editable a la vez:
    # Django lo exige así (E122 si falta en list_display; E124 solo si fuera
    # el PRIMER elemento). Editar stock/activo desde la lista es la demo de
    # "control total".
    list_display = ["nombre", "estilo", "tipo", "precio", "stock", "activo"]
    list_filter = ["tipo", "activo", "estilo"]
    date_hierarchy = "fecha_creacion"
    search_fields = ["nombre", "estilo__nombre", "descripcion"]
    list_select_related = ["estilo"]
    list_per_page = 25
    list_editable = ["stock", "activo"]
    search_help_text = "Buscar por nombre o estilo."
    readonly_fields = ["fecha_creacion"]
    ordering = ["nombre"]


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Producción", {"fields": ("numero", "cerveza", "estado", "usuario")}),
        (
            "Calendario y volumen",
            {"fields": ("fecha_inicio", "fecha_fin", "volumen_litros")},
        ),
        ("Notas", {"fields": ("notas",)}),
    )
    # Etapas como inline del lote (ver EtapaFermentacionInline).
    inlines = [EtapaFermentacionInline]
    autocomplete_fields = ["cerveza"]
    list_display = [
        "numero",
        "cerveza",
        "estado",
        "fecha_inicio",
        "volumen_litros",
        "usuario",
    ]
    list_filter = ["estado", "fecha_inicio"]
    date_hierarchy = "fecha_inicio"
    search_fields = ["numero", "cerveza__nombre", "notas"]
    list_select_related = ["cerveza", "usuario"]
    list_per_page = 25
    search_help_text = "Buscar por número de lote, cerveza o notas."
    ordering = ["-fecha_inicio"]


@admin.register(EtapaFermentacion)
class EtapaFermentacionAdmin(admin.ModelAdmin):
    # Autocomplete del lote: LoteAdmin define search_fields, así que puede
    # recibir búsquedas.
    autocomplete_fields = ["lote"]
    list_display = ["lote", "numero", "tipo", "estado", "fecha_inicio", "temperatura"]
    list_filter = ["tipo", "estado"]
    search_fields = ["lote__numero", "lote__cerveza__nombre"]
    list_select_related = ["lote"]
    list_per_page = 25
    search_help_text = "Buscar por número de lote o cerveza."
    ordering = ["lote", "numero"]


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    # search_fields acá sostiene el autocomplete de MateriaPrima.proveedor.
    list_display = ["razon_social", "cuit", "email", "telefono", "activo"]
    list_filter = ["activo"]
    search_fields = ["razon_social", "cuit", "email", "telefono"]
    list_per_page = 25
    search_help_text = "Buscar por razón social, CUIT o email."
    ordering = ["razon_social"]


@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    autocomplete_fields = ["proveedor"]
    list_display = [
        "nombre",
        "tipo",
        "unidad",
        "stock",
        "stock_minimo",
        "bajo_stock",
    ]
    list_filter = ["tipo", "unidad"]
    search_fields = ["nombre", "proveedor__razon_social"]
    list_select_related = ["proveedor"]
    list_per_page = 25
    search_help_text = "Buscar por nombre o proveedor."
    ordering = ["nombre"]

    @admin.display(boolean=True, description="bajo mínimo")
    def bajo_stock(self, obj):
        """Señal de reposición para el depósito: stock <= stock mínimo."""
        return obj.stock <= obj.stock_minimo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "apellido", "email", "dni", "activo", "fecha_alta"]
    list_filter = ["activo"]
    search_fields = ["nombre", "apellido", "email", "dni"]
    date_hierarchy = "fecha_alta"
    list_per_page = 25
    search_help_text = "Buscar por nombre, apellido, email o DNI."
    readonly_fields = ["fecha_alta"]
    ordering = ["apellido", "nombre"]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Las líneas se editan en la cabecera del pedido (ver LineaPedidoInline).
    inlines = [LineaPedidoInline]
    # El cliente se busca con autocomplete: ClienteAdmin tiene search_fields.
    autocomplete_fields = ["cliente"]
    list_display = ["pk", "cliente", "fecha", "estado", "forma_pago", "total"]
    list_filter = ["estado", "forma_pago", "fecha"]
    date_hierarchy = "fecha"
    search_fields = [
        "cliente__nombre",
        "cliente__apellido",
        "direccion_entrega",
        "observaciones",
    ]
    list_select_related = ["cliente"]
    list_per_page = 25
    search_help_text = "Buscar por cliente, dirección de entrega u observaciones."
    readonly_fields = ["fecha"]
    ordering = ["-fecha"]


@admin.register(LineaPedido)
class LineaPedidoAdmin(admin.ModelAdmin):
    # Los dos FK van con autocomplete: PedidoAdmin y CervezaAdmin tienen
    # search_fields.
    autocomplete_fields = ["pedido", "cerveza"]
    list_display = ["pedido", "cerveza", "cantidad", "precio_unitario", "subtotal"]
    list_filter = ["cerveza"]
    search_fields = [
        "cerveza__nombre",
        "pedido__cliente__nombre",
        "pedido__cliente__apellido",
    ]
    list_select_related = ["pedido", "cerveza"]
    list_per_page = 25
    search_help_text = "Buscar por cerveza o por el cliente del pedido."
    ordering = ["pedido", "id"]

    @admin.display(description="subtotal")
    def subtotal(self, obj):
        """Muestra la property del modelo (cantidad × precio unitario)."""
        return obj.subtotal


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    # Autocomplete de cerveza y cliente; ambos admins destino tienen
    # search_fields.
    autocomplete_fields = ["cerveza", "cliente"]
    list_display = ["cerveza", "cliente", "puntaje", "fecha"]
    list_filter = ["puntaje", "fecha"]
    date_hierarchy = "fecha"
    search_fields = [
        "comentario",
        "cerveza__nombre",
        "cliente__nombre",
        "cliente__apellido",
    ]
    list_select_related = ["cerveza", "cliente"]
    list_per_page = 25
    search_help_text = "Buscar por comentario, cerveza o cliente."
    readonly_fields = ["fecha"]
    ordering = ["-fecha"]
