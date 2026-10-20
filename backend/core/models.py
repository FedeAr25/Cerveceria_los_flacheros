"""Los 10 modelos del dominio de la Cervecería Los Flacheros.

Viven todos en una sola app (`core`), agrupados por el negocio:
catálogo (Estilo, Cerveza), producción (Lote, EtapaFermentacion),
insumos (Proveedor, MateriaPrima), ventas (Cliente, Pedido, LineaPedido)
y feedback (Opinion).
"""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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


class Proveedor(models.Model):
    """El que nos vende materia prima: malta, lúpulo, levadura."""

    razon_social = models.CharField("razón social", max_length=150)
    cuit = models.CharField("CUIT", max_length=20, unique=True)
    email = models.EmailField("email", blank=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.razon_social


class MateriaPrima(models.Model):
    """Insumo del depósito: malta, lúpulo, levadura u otro."""

    class Tipo(models.TextChoices):
        MALTA = "MALTA", "Malta"
        LUPULO = "LUPULO", "Lúpulo"
        LEVADURA = "LEVADURA", "Levadura"
        OTROS = "OTROS", "Otros"

    class Unidad(models.TextChoices):
        KG = "KG", "Kilogramo"
        G = "G", "Gramo"
        LT = "LT", "Litro"
        UNIDAD = "UNIDAD", "Unidad"

    nombre = models.CharField("nombre", max_length=150)
    tipo = models.CharField("tipo", max_length=10, choices=Tipo.choices)
    unidad = models.CharField(
        "unidad", max_length=10, choices=Unidad.choices, default=Unidad.KG
    )
    stock = models.DecimalField("stock", max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(
        "stock mínimo", max_digits=10, decimal_places=2, default=0
    )
    costo_unitario = models.DecimalField(
        "costo unitario", max_digits=10, decimal_places=2, default=0
    )
    # SET_NULL: la materia prima sigue existiendo aunque el proveedor se dé de
    # baja; solo desenganchamos el vínculo.
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="materias_primas",
        verbose_name="proveedor",
    )

    class Meta:
        verbose_name = "materia prima"
        verbose_name_plural = "materias primas"

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    """La persona que nos compra: ficha con DNI y mail únicos."""

    nombre = models.CharField("nombre", max_length=100)
    apellido = models.CharField("apellido", max_length=100)
    email = models.EmailField("email", unique=True)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    dni = models.CharField("DNI", max_length=20, unique=True, null=True, blank=True)
    activo = models.BooleanField("activo", default=True)
    fecha_alta = models.DateTimeField("fecha de alta", auto_now_add=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self):
        """No es columna de la base: es un atributo calculado que el
        serializer expone como si fuera un campo (solo lectura)."""
        return f"{self.nombre} {self.apellido}".strip()


class Pedido(models.Model):
    """La orden de venta a un cliente: cabecera con su estado y total."""

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        EN_PREPARACION = "EN_PREPARACION", "En preparación"
        LISTO_RETIRO = "LISTO_RETIRO", "Listo para retiro"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    class FormaPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    fecha = models.DateTimeField("fecha", auto_now_add=True)
    estado = models.CharField(
        "estado", max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    forma_pago = models.CharField(
        "forma de pago",
        max_length=15,
        choices=FormaPago.choices,
        default=FormaPago.EFECTIVO,
    )
    # `total` es un campo GUARDADO, no se recalcula en cada respuesta: lo
    # calcula la capa de API (serializers, Fase 4) al crear el pedido. Por eso
    # el contrato con el frontend lo congela al crear el pedido: si cambian los
    # precios después, el total del histórico no se mueve.
    total = models.DecimalField("total", max_digits=10, decimal_places=2, default=0)
    direccion_entrega = models.CharField(
        "dirección de entrega", max_length=255, blank=True
    )
    observaciones = models.TextField("observaciones", blank=True)
    # PROTECT: un pedido sin cliente pierde sentido comercial; no se puede
    # borrar un cliente que tiene pedidos.
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="cliente",
    )

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido {self.pk} — {self.cliente}"


class LineaPedido(models.Model):
    """Cada renglón del pedido: qué cerveza, con qué cantidad y precio."""

    cantidad = models.IntegerField("cantidad", default=1)
    precio_unitario = models.DecimalField(
        "precio unitario", max_digits=10, decimal_places=2
    )
    # CASCADE: las líneas son parte del pedido; si desaparece el pedido, sus
    # renglones quedan huérfanos, así que se borran con él.
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="lineas", verbose_name="pedido"
    )
    # PROTECT: una venta registrada no se reescribe borrando la cerveza; el
    # histórico se protege.
    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.PROTECT,
        related_name="lineas_pedido",
        verbose_name="cerveza",
    )

    class Meta:
        verbose_name = "línea de pedido"
        verbose_name_plural = "líneas de pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.cerveza}"

    @property
    def subtotal(self):
        """Cálculo (no columna): cantidad × precio unitario. El serializer lo
        expone como campo de solo lectura."""
        return self.cantidad * self.precio_unitario


class Opinion(models.Model):
    """Reseña de un cliente sobre una cerveza: puntaje 1-5 y comentario."""

    # Los validators rechazan un puntaje fuera de 1-5 en `full_clean()` y en
    # el serializer (que llama a `full_clean`): sin ellos, un 0 o un 9 entraría
    # silenciosamente a la base.
    puntaje = models.IntegerField(
        "puntaje",
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField("comentario", blank=True)
    fecha = models.DateTimeField("fecha", auto_now_add=True)
    # CASCADE: una opinión no sobrevive a la cerveza que comenta.
    cerveza = models.ForeignKey(
        Cerveza,
        on_delete=models.CASCADE,
        related_name="opiniones",
        verbose_name="cerveza",
    )
    # CASCADE: una opinión no sobrevive a quien la escribió.
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="opiniones",
        verbose_name="cliente",
    )

    class Meta:
        verbose_name = "opinión"
        verbose_name_plural = "opiniones"

    def __str__(self):
        return f"{self.get_puntaje_display()}★ — {self.cerveza}"
