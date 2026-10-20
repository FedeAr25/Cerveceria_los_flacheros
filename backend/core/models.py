"""Los 10 modelos del dominio de la Cervecería Los Flacheros.

Viven todos en una sola app (`core`), agrupados por el negocio:
catálogo (Estilo, Cerveza), producción (Lote, EtapaFermentacion),
insumos (Proveedor, MateriaPrima), ventas (Cliente, Pedido, LineaPedido)
y feedback (Opinion).
"""

from django.contrib.auth.models import User
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


class Lote(models.Model):
    """Producción concreta de una cerveza: "el lote L-0042, 200 litros"."""

    class Estado(models.TextChoices):
        PLANIFICADO = "PLANIFICADO", "Planificado"
        EN_PRODUCCION = "EN_PRODUCCION", "En producción"
        FERMENTACION = "FERMENTACION", "Fermentación"
        MADURACION = "MADURACION", "Maduración"
        LISTO = "LISTO", "Listo"
        CANCELADO = "CANCELADO", "Cancelado"

    # Máquina de estados: de PLANIFICADO a LISTO avanzando un paso por vez.
    # CANCELADO es terminal: no tiene transición a ningún estado.
    # La @action "avanzar" (Task 18, Fase 4) valida la transición con
    # `puede_avanzar_a` antes de mover el lote; un salto inválido responde 400.
    TRANSICIONES = {
        "PLANIFICADO": "EN_PRODUCCION",
        "EN_PRODUCCION": "FERMENTACION",
        "FERMENTACION": "MADURACION",
        "MADURACION": "LISTO",
    }

    numero = models.CharField("número", max_length=50, unique=True)
    fecha_inicio = models.DateField("fecha de inicio")
    fecha_fin = models.DateField("fecha de fin", null=True, blank=True)
    volumen_litros = models.DecimalField(
        "volumen (litros)", max_digits=8, decimal_places=2
    )
    estado = models.CharField(
        "estado", max_length=20, choices=Estado.choices, default=Estado.PLANIFICADO
    )
    notas = models.TextField("notas", blank=True)
    # PROTECT: el lote es historial de producción; no se puede borrar la
    # cerveza que ya se produjo.
    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.PROTECT,
        related_name="lotes",
        verbose_name="cerveza",
    )
    # SET_NULL: si se borra el usuario, el lote queda sin responsable pero
    # se conserva (el responsable es un dato secundario).
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lotes",
        verbose_name="usuario",
    )

    class Meta:
        verbose_name = "lote"
        verbose_name_plural = "lotes"

    def __str__(self):
        return f"{self.numero} — {self.cerveza}"

    def puede_avanzar_a(self, estado) -> bool:
        """¿Es válido el salto del estado actual al estado dado?

        Solo se permite avanzar un paso (CANCELADO es terminal). Lo usa la
        @action "avanzar" (Task 18) para rechazar con 400 los saltos inválidos.
        """
        return self.TRANSICIONES.get(self.estado) == estado


class EtapaFermentacion(models.Model):
    """Cada fase dentro de un lote: primaria, secundaria o madurado."""

    class Tipo(models.TextChoices):
        PRIMARIA = "PRIMARIA", "Primaria"
        SECUNDARIA = "SECUNDARIA", "Secundaria"
        MADURADO = "MADURADO", "Madurado"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACTIVA = "ACTIVA", "Activa"
        COMPLETADA = "COMPLETADA", "Completada"

    numero = models.IntegerField("número")
    tipo = models.CharField("tipo", max_length=10, choices=Tipo.choices)
    fecha_inicio = models.DateField("fecha de inicio")
    fecha_fin = models.DateField("fecha de fin", null=True, blank=True)
    temperatura = models.DecimalField(
        "temperatura (°C)", max_digits=4, decimal_places=1, null=True, blank=True
    )
    estado = models.CharField(
        "estado", max_length=15, choices=Estado.choices, default=Estado.PENDIENTE
    )
    # CASCADE: una etapa no existe sin su lote; al borrar el lote, sus etapas
    # se borran con él.
    lote = models.ForeignKey(
        Lote, on_delete=models.CASCADE, related_name="etapas", verbose_name="lote"
    )

    class Meta:
        verbose_name = "etapa de fermentación"
        verbose_name_plural = "etapas de fermentación"

    def __str__(self):
        return f"Etapa {self.numero} ({self.get_tipo_display()}) — {self.lote}"
