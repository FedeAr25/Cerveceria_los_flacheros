"""Los 10 modelos del dominio de la Cervecería Los Flacheros.

Viven todos en una sola app (`core`), agrupados por el negocio:
catálogo (Estilo, Cerveza), producción (Lote, EtapaFermentacion),
insumos (Proveedor, MateriaPrima), ventas (Cliente, Pedido, LineaPedido)
y feedback (Opinion).
"""

from django.db import models


class Estilo(models.Model):
    """Categoría o receta base de cerveza: IPA, Stout, APA, Weizen."""

    nombre = models.CharField("nombre", max_length=100, unique=True)
    descripcion = models.TextField("descripción", blank=True)
    ibu = models.IntegerField("IBU", null=True, blank=True)
    color = models.CharField("color", max_length=20, blank=True)
    orden = models.IntegerField("orden", default=0)

    class Meta:
        verbose_name = "estilo"
        verbose_name_plural = "estilos"

    def __str__(self):
        return self.nombre


class Cerveza(models.Model):
    """Producto vendible: nombre propio, precio, stock y estilo."""

    class Tipo(models.TextChoices):
        ENVASE = "ENVASE", "Envase"
        GRIFO = "GRIFO", "Grifo"

    nombre = models.CharField("nombre", max_length=150, unique=True)
    descripcion = models.TextField("descripción", blank=True)
    precio = models.DecimalField("precio", max_digits=10, decimal_places=2)
    volumen_ml = models.IntegerField("volumen (ml)", default=330)
    alcohol_pct = models.DecimalField(
        "alcohol (%)", max_digits=4, decimal_places=1, null=True, blank=True
    )
    stock = models.IntegerField("stock", default=0)
    tipo = models.CharField(
        "tipo", max_length=10, choices=Tipo.choices, default=Tipo.ENVASE
    )
    activo = models.BooleanField("activo", default=True)
    fecha_creacion = models.DateTimeField("fecha de creación", auto_now_add=True)
    # PROTECT: no se puede borrar un estilo que ya tiene cervezas cargadas;
    # el catálogo es histórico y se protege.
    estilo = models.ForeignKey(
        Estilo,
        on_delete=models.PROTECT,
        related_name="cervezas",
        verbose_name="estilo",
    )

    class Meta:
        verbose_name = "cerveza"
        verbose_name_plural = "cervezas"

    def __str__(self):
        return self.nombre
