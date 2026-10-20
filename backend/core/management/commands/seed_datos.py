"""Comando `seed_datos`: carga datos de ejemplo realistas de la cervecería.

Para qué sirve: alimenta la base con un catálogo, producción, insumos,
ventas y reseñas creíbles para las capturas de pantalla del informe, la
demo de la API y el ensayo de defensa.

Dos garantías importantes:

1. **Idempotencia**: se puede correr N veces sin duplicar nada, porque
   cada registro se ata a su clave natural con `get_or_create` (nombre de
   estilo/cerveza/proveedor/materia prima, número de lote, email de
   cliente, (lote, número) de etapa, etc.). `Pedido` y `Opinion` no tienen
   una columna "número de pedido" única, así que se tratan aparte (ver
   comentarios en cada bloque).
2. **No toca autenticación**: jamás borra ni crea usuarios ni tokens;
   `--flush` vacía solo los 10 modelos del dominio.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
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


class Command(BaseCommand):
    """Carga (o recarga) datos de ejemplo de la cervecería."""

    help = (
        "Carga datos de ejemplo realistas (estilos, cervezas, proveedores, "
        "materias primas, clientes, lotes, pedidos y opiniones). Es "
        "idempotente: se puede repetir sin duplicar registros. Con --flush "
        "borra primero todos los datos del dominio (DESTRUCTIVO, no borra "
        "usuarios ni tokens) y vuelve a cargar desde cero."
    )

    def add_arguments(self, parser):
        # El texto del help de cada opción aparece en `manage.py seed_datos --help`.
        parser.add_argument(
            "--flush",
            action="store_true",
            help=(
                "DESTRUCTIVO: borra todos los registros de los 10 modelos del "
                "dominio (líneas, opiniones, pedidos, etapas, lotes, cervezas, "
                "materias primas, estilos, proveedores y clientes) y luego "
                "vuelve a cargar los datos de ejemplo. No toca usuarios ni "
                "tokens de autenticación."
            ),
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        # Contadores de "creados en esta corrida": con `get_or_create`, si el
        # registro ya existía, `created` viene en False y no lo contamos. Así
        # el resumen final distingue "cuánto cargó ahora" de "cuánto había".
        creados = {
            "estilos": 0,
            "cervezas": 0,
            "proveedores": 0,
            "materias primas": 0,
            "clientes": 0,
            "lotes": 0,
            "etapas de fermentación": 0,
            "pedidos": 0,
            "líneas de pedido": 0,
            "opiniones": 0,
        }

        self._cargar_estilos(creados)
        self._cargar_cervezas(creados)
        self._cargar_proveedores(creados)
        self._cargar_materias_primas(creados)
        self._cargar_clientes(creados)
        self._cargar_lotes_y_etapas(creados)
        self._cargar_pedidos(creados)
        self._cargar_opiniones(creados)

        # Resumen final: cuántos registros creó ESTA corrida de cada tipo.
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== Resumen de seed_datos ==="))
        for tipo, cantidad in creados.items():
            self.stdout.write(f"  {tipo}: {cantidad} creados")
        self.stdout.write(
            self.style.SUCCESS("Listo. Datos de ejemplo cargados correctamente.")
        )

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @staticmethod
    def _fecha(dias_atras: int):
        """Fecha (DateField) hace N días desde hoy.

        Se usa para que los lotes y las etapas muestren fechas pasadas o
        próximas coherentes en el admin, sin importar cuándo se corra el
        seed.
        """
        return timezone.now().date() - timedelta(days=dias_atras)

    @staticmethod
    def _datetime(dias_atras: int):
        """Marca de tiempo (DateTimeField) hace N días desde hoy.

        Pedidos y opiniones se reparten así en las últimas ~4 semanas para
        que el filtro por fecha del admin y el orden por fecha se vean
        creíbles en las capturas (no todos "recién cargados").
        """
        return timezone.now() - timedelta(days=dias_atras)

    def _flush(self):
        """Borra todos los datos del dominio en orden inverso de dependencias.

        El orden importa: primero lo "hijo" y después lo "padre", para no
        chocar con las protecciones del modelo (por ejemplo, `LineaPedido`
        tiene PROTECT sobre `Cerveza` y `Pedido` sobre `Cliente`: si
        intentáramos borrar un cliente con pedidos, Django lanzaría
        ProtectedError). Etapas y líneas usan CASCADE, pero se borran igual
        primero para mostrar el orden explícito y poder contar cuántas filas
        borró cada modelo.

        Ojo: NO se borra `auth_user` ni tokens; los usuarios de la aplicación
        (admin, demo) quedan intactos.
        """
        self.stdout.write(
            self.style.WARNING(
                "⚠️  --flush es DESTRUCTIVO: borra TODOS los datos de los 10 "
                "modelos del dominio (usuarios y tokens NO se tocan)."
            )
        )
        # Orden inverso de dependencias: hijos primero.
        modelos = [
            ("líneas de pedido", LineaPedido),
            ("opiniones", Opinion),
            ("pedidos", Pedido),
            ("etapas de fermentación", EtapaFermentacion),
            ("lotes", Lote),
            ("cervezas", Cerveza),
            ("materias primas", MateriaPrima),
            ("estilos", Estilo),
            ("proveedores", Proveedor),
            ("clientes", Cliente),
        ]
        for nombre, modelo in modelos:
            # `delete()` devuelve (total, {etiqueta: cantidad}); total es lo
            # que nos interesa para el mensaje, porque con CASCADE el detalle
            # puede incluir filas hijas borradas en cascada.
            total, _ = modelo.objects.all().delete()
            self.stdout.write(f"  Borrados {total} registros de {nombre}")
        self.stdout.write(self.style.WARNING("Base vacía. Procedo a recargar."))

    # ------------------------------------------------------------------
    # Bloques de carga (cada uno con `get_or_create` sobre clave natural)
    # ------------------------------------------------------------------

    def _cargar_estilos(self, creados):
        """5 estilos de la carta, con lo mínimo para describirlos en el admin.

        `nombre` es único en el modelo: es la clave natural del estilo.
        """
        datos = [
            {
                "nombre": "IPA",
                "descripcion": (
                    "India Pale Ale: lupulada, amarga y aromática. La receta "
                    "estrella de la casa."
                ),
                "ibu": 60,
                "color": "Ámbar dorado",
                "orden": 1,
            },
            {
                "nombre": "Stout",
                "descripcion": (
                    "Cerveza oscura de malta tostada, con notas de café y chocolate."
                ),
                "ibu": 35,
                "color": "Negro opaco",
                "orden": 2,
            },
            {
                "nombre": "Pilsener",
                "descripcion": (
                    "Lager clara y refrescante, de amargor suave y final limpio."
                ),
                "ibu": 22,
                "color": "Dorado claro",
                "orden": 3,
            },
            {
                "nombre": "Wheat (Trigo)",
                "descripcion": (
                    "Estilo de trigo (weizen): turbia, con aromas frutales "
                    "de la levadura."
                ),
                "ibu": 15,
                "color": "Amarillo pálido",
                "orden": 4,
            },
            {
                "nombre": "Amber Ale",
                "descripcion": (
                    "Ale rojiza de malta caramelizada, equilibrada entre "
                    "dulzor y amargor."
                ),
                "ibu": 30,
                "color": "Ámbar rojizo",
                "orden": 5,
            },
        ]
        for datos_estilo in datos:
            _, created = Estilo.objects.get_or_create(
                nombre=datos_estilo["nombre"], defaults=datos_estilo
            )
            if created:
                creados["estilos"] += 1

    def _cargar_cervezas(self, creados):
        """8 cervezas repartidas entre los estilos.

        Decisiones pensadas para las capturas y para las APIs:

        - 4 son GRIFO con stock > 0: la acción `en_grifo` del viewset
          filtra `tipo=GRIFO, stock>0 y activo=True`, así que necesita
          varias filas que pasen ese filtro para que la demo no muestre
          una lista vacía.
        - 1 está inactiva (`activo=False`): muestra que el catálogo admite
          dar de baja productos sin borrarlos (el histórico de pedidos la
          protege con PROTECT). Además ejemplifica el filtro por `activo`.
        - 1 con stock 0: sirve para mostrar el caso "sin stock" en la
          pantalla de catálogo.
        - `nombre` es único: es la clave natural de la cerveza.
        """
        datos = [
            {
                "nombre": "IPA del Flachero",
                "descripcion": "Nuestra IPA insignia: Cascade y Citra, amargor firme.",
                "estilo_nombre": "IPA",
                "precio": Decimal("4200.00"),
                "volumen_ml": 500,
                "alcohol_pct": Decimal("6.2"),
                "stock": 60,
                "tipo": Cerveza.Tipo.GRIFO,
                "activo": True,
            },
            {
                "nombre": "IPA Doble del Flachero",
                "descripcion": "DIPA de doble lupulado, intensa y resinosa.",
                "estilo_nombre": "IPA",
                "precio": Decimal("3800.00"),
                "volumen_ml": 330,
                "alcohol_pct": Decimal("6.5"),
                "stock": 45,
                "tipo": Cerveza.Tipo.ENVASE,
                "activo": True,
            },
            {
                "nombre": "Stout de la Casa",
                "descripcion": "Stout cremosa con malta chocolate y café tostado.",
                "estilo_nombre": "Stout",
                "precio": Decimal("4500.00"),
                "volumen_ml": 500,
                "alcohol_pct": Decimal("5.4"),
                "stock": 30,
                "tipo": Cerveza.Tipo.GRIFO,
                "activo": True,
            },
            {
                "nombre": "Stout Tostado de la Casa",
                "descripcion": "Edición intensa, con granos tostados y final seco.",
                "estilo_nombre": "Stout",
                "precio": Decimal("3600.00"),
                "volumen_ml": 330,
                "alcohol_pct": Decimal("6.0"),
                # Sin stock: permite mostrar el estado "agotada" en el
                # catálogo y en la API.
                "stock": 0,
                "tipo": Cerveza.Tipo.ENVASE,
                "activo": True,
            },
            {
                "nombre": "Pilsener del Flachero",
                "descripcion": "Lager de la casa: clara, seca y muy refrescante.",
                "estilo_nombre": "Pilsener",
                "precio": Decimal("3200.00"),
                "volumen_ml": 500,
                "alcohol_pct": Decimal("4.5"),
                "stock": 120,
                "tipo": Cerveza.Tipo.GRIFO,
                "activo": True,
            },
            {
                "nombre": "Trigo del Flachero",
                "descripcion": "Weizen de trigo, turbia, con notas de banana y clavo.",
                "estilo_nombre": "Wheat (Trigo)",
                "precio": Decimal("3400.00"),
                "volumen_ml": 500,
                "alcohol_pct": Decimal("4.8"),
                "stock": 90,
                "tipo": Cerveza.Tipo.GRIFO,
                "activo": True,
            },
            {
                "nombre": "Amber Ale de la Casa",
                "descripcion": "Ale rojiza equilibrada, maltas caramelizadas.",
                "estilo_nombre": "Amber Ale",
                "precio": Decimal("3100.00"),
                "volumen_ml": 330,
                "alcohol_pct": Decimal("5.2"),
                "stock": 75,
                "tipo": Cerveza.Tipo.ENVASE,
                "activo": True,
            },
            {
                "nombre": "Red Ale del Flachero",
                "descripcion": (
                    "Receta descontinuada de la primera temporada; se conserva "
                    "por el histórico de ventas."
                ),
                "estilo_nombre": "Amber Ale",
                "precio": Decimal("2800.00"),
                "volumen_ml": 330,
                "alcohol_pct": Decimal("4.2"),
                "stock": 15,
                "tipo": Cerveza.Tipo.ENVASE,
                # Inactiva: el catálogo permite dar de baja un producto sin
                # borrarlo, porque el histórico de pedidos la protege (PROTECT)
                # y las reseñas de los clientes siguen siendo válidas.
                "activo": False,
            },
        ]
        for datos_cerveza in datos:
            estilo = Estilo.objects.get(nombre=datos_cerveza.pop("estilo_nombre"))
            _, created = Cerveza.objects.get_or_create(
                nombre=datos_cerveza["nombre"],
                defaults={**datos_cerveza, "estilo": estilo},
            )
            if created:
                creados["cervezas"] += 1

    def _cargar_proveedores(self, creados):
        """2 proveedores ficticios.

        El CUIT es único en el modelo: es la clave natural. Los usamos con
        formato de 11 dígitos pero claramente ficticios, para no
        confundirlos con CUITs reales en la defensa.
        """
        datos = [
            {
                "razon_social": "Maltería Andina S.A.",
                "cuit": "20123456789",
                "email": "compras@malteriaandina.example.com",
                "telefono": "+54 351 555-0101",
                "activo": True,
            },
            {
                "razon_social": "Lúpatos del Sur S.R.L.",
                "cuit": "30987654321",
                "email": "ventas@lupatosdelsur.example.com",
                "telefono": "+54 221 555-0102",
                "activo": True,
            },
        ]
        for datos_proveedor in datos:
            _, created = Proveedor.objects.get_or_create(
                cuit=datos_proveedor["cuit"], defaults=datos_proveedor
            )
            if created:
                creados["proveedores"] += 1

    def _cargar_materias_primas(self, creados):
        """6 insumos cubriendo los 4 tipos (MALTA, LUPULO, LEVADURA, OTROS).

        Dos de ellos quedan con `stock <= stock_minimo` a propósito: el
        admin los muestra en la lista y la dashboard de reposición las marca
        como "stock bajo". Sin ese caso de prueba, la captura del depósito no
        ilustra para qué sirve el campo `stock_minimo`.

        `MateriaPrima.nombre` no es único en el modelo, pero en el seed
        funciona como clave natural: `get_or_create` devuelve la primera que
        encuentre con ese nombre y no duplica.
        """
        proveedor_malta = Proveedor.objects.get(cuit="20123456789")
        proveedor_lupulo = Proveedor.objects.get(cuit="30987654321")
        datos = [
            {
                "nombre": "Malta Pale Ale",
                "tipo": MateriaPrima.Tipo.MALTA,
                "unidad": MateriaPrima.Unidad.KG,
                "stock": Decimal("250.00"),
                "stock_minimo": Decimal("80.00"),
                "costo_unitario": Decimal("1800.00"),
                "proveedor": proveedor_malta,
            },
            {
                "nombre": "Malta Chocolate",
                "tipo": MateriaPrima.Tipo.MALTA,
                "unidad": MateriaPrima.Unidad.KG,
                # Stock por debajo del mínimo: caso "reposición urgente".
                "stock": Decimal("45.00"),
                "stock_minimo": Decimal("50.00"),
                "costo_unitario": Decimal("2300.00"),
                "proveedor": proveedor_malta,
            },
            {
                "nombre": "Lúpulo Cascade",
                "tipo": MateriaPrima.Tipo.LUPULO,
                "unidad": MateriaPrima.Unidad.G,
                "stock": Decimal("2500.00"),
                "stock_minimo": Decimal("500.00"),
                "costo_unitario": Decimal("12.00"),
                "proveedor": proveedor_lupulo,
            },
            {
                "nombre": "Lúpulo Citra",
                "tipo": MateriaPrima.Tipo.LUPULO,
                "unidad": MateriaPrima.Unidad.G,
                # Segundo caso de stock bajo (el seed garantiza ≥2).
                "stock": Decimal("400.00"),
                "stock_minimo": Decimal("500.00"),
                "costo_unitario": Decimal("15.00"),
                "proveedor": proveedor_lupulo,
            },
            {
                "nombre": "Levadura Safale US-05",
                "tipo": MateriaPrima.Tipo.LEVADURA,
                "unidad": MateriaPrima.Unidad.UNIDAD,
                "stock": Decimal("40.00"),
                "stock_minimo": Decimal("15.00"),
                "costo_unitario": Decimal("3800.00"),
                "proveedor": None,
            },
            {
                "nombre": "Corchos 23 mm",
                "tipo": MateriaPrima.Tipo.OTROS,
                "unidad": MateriaPrima.Unidad.UNIDAD,
                "stock": Decimal("500.00"),
                "stock_minimo": Decimal("200.00"),
                "costo_unitario": Decimal("55.00"),
                "proveedor": None,
            },
        ]
        for datos_mp in datos:
            _, created = MateriaPrima.objects.get_or_create(
                nombre=datos_mp["nombre"], defaults=datos_mp
            )
            if created:
                creados["materias primas"] += 1

    def _cargar_clientes(self, creados):
        """10 clientes de prueba.

        El `email` es único en el modelo: es la clave natural. Solo 2 tienen
        DNI cargado para mostrar que el campo es opcional (nullable) y
        aparece vacío en el resto de las fichas.
        """
        datos = [
            ("Camila", "Ferreyra", "+54 351 555-1001", "32123456"),
            ("Martín", "Quiroga", "+54 351 555-1002", None),
            ("Lucía", "Baldi", "+54 221 555-1003", None),
            ("Federico", "Sosa", "+54 11 555-1004", None),
            ("Valentina", "Ibarra", "+54 351 555-1005", "35987654"),
            ("Rodrigo", "Peña", "+54 341 555-1006", None),
            ("Sofía", "Camargo", "+54 11 555-1007", None),
            ("Nicolás", "Vera", "+54 351 555-1008", None),
            ("Jazmín", "Ledesma", "+54 221 555-1009", None),
            ("Bruno", "Acosta", "+54 341 555-1010", None),
        ]
        for i, (nombre, apellido, telefono, dni) in enumerate(datos, start=1):
            _, created = Cliente.objects.get_or_create(
                email=f"cliente{i}@example.com",
                defaults={
                    "nombre": nombre,
                    "apellido": apellido,
                    "telefono": telefono,
                    "dni": dni,
                },
            )
            if created:
                creados["clientes"] += 1

    def _cargar_lotes_y_etapas(self, creados):
        """4 lotes, uno por estado del camino feliz, y sus etapas.

        El `fecha_inicio` de cada lote es SIEMPRE anterior a hoy (así lo
        requiere el modelo de negocio: un lote ya comenzado tiene fecha de
        inicio pasada); la duración restante se refleja en `fecha_fin`.
        Las etapas siguen ese calendario con temperaturas coherentes por
        estilo: ales ~20 °C en fermentación y lagers más frías, con un
        madurado cercano a 4 °C.

        Las etapas no tienen columna única, pero (lote, número) funciona
        como clave natural: cada lote tiene una etapa 1, 2 y 3.
        """
        cerveza_ipa = Cerveza.objects.get(nombre="IPA del Flachero")
        cerveza_stout = Cerveza.objects.get(nombre="Stout de la Casa")
        cerveza_pilsener = Cerveza.objects.get(nombre="Pilsener del Flachero")
        cerveza_amber = Cerveza.objects.get(nombre="Amber Ale de la Casa")
        datos = [
            {
                "numero": "L-0041",
                "cerveza": cerveza_ipa,
                "estado": Lote.Estado.PLANIFICADO,
                "fecha_inicio": self._fecha(5),
                "fecha_fin": self._fecha(-9),  # fecha futura
                "volumen_litros": Decimal("500.00"),
                "notas": "Programado para la próxima semana de elaboración.",
                "etapas": [
                    # (número, tipo, inicio, fin, temp, estado)
                    (
                        1,
                        EtapaFermentacion.Tipo.PRIMARIA,
                        2,
                        -5,
                        Decimal("20.0"),
                        EtapaFermentacion.Estado.PENDIENTE,
                    ),
                    (
                        2,
                        EtapaFermentacion.Tipo.SECUNDARIA,
                        -5,
                        -12,
                        Decimal("18.0"),
                        EtapaFermentacion.Estado.PENDIENTE,
                    ),
                ],
            },
            {
                "numero": "L-0042",
                "cerveza": cerveza_stout,
                "estado": Lote.Estado.EN_PRODUCCION,
                "fecha_inicio": self._fecha(3),
                "fecha_fin": self._fecha(-11),
                "volumen_litros": Decimal("300.00"),
                "notas": "Cocción en curso; falta enfriar y sembrar levadura.",
                "etapas": [
                    (
                        1,
                        EtapaFermentacion.Tipo.PRIMARIA,
                        1,
                        -6,
                        Decimal("20.0"),
                        EtapaFermentacion.Estado.PENDIENTE,
                    ),
                    (
                        2,
                        EtapaFermentacion.Tipo.SECUNDARIA,
                        -6,
                        -13,
                        Decimal("18.0"),
                        EtapaFermentacion.Estado.PENDIENTE,
                    ),
                    (
                        3,
                        EtapaFermentacion.Tipo.MADURADO,
                        -13,
                        -20,
                        Decimal("4.0"),
                        EtapaFermentacion.Estado.PENDIENTE,
                    ),
                ],
            },
            {
                "numero": "L-0043",
                "cerveza": cerveza_pilsener,
                "estado": Lote.Estado.FERMENTACION,
                "fecha_inicio": self._fecha(12),
                "fecha_fin": self._fecha(-2),
                "volumen_litros": Decimal("800.00"),
                "notas": "Lager: fermentación primaria completa, en secundaria.",
                "etapas": [
                    (
                        1,
                        EtapaFermentacion.Tipo.PRIMARIA,
                        0,
                        5,
                        Decimal("12.0"),
                        EtapaFermentacion.Estado.COMPLETADA,
                    ),
                    # Etapa activa: `fecha_fin` queda vacía porque aún no terminó.
                    (
                        2,
                        EtapaFermentacion.Tipo.SECUNDARIA,
                        5,
                        None,
                        Decimal("10.0"),
                        EtapaFermentacion.Estado.ACTIVA,
                    ),
                    (
                        3,
                        EtapaFermentacion.Tipo.MADURADO,
                        12,
                        None,
                        Decimal("4.0"),
                        EtapaFermentacion.Estado.PENDIENTE,
                    ),
                ],
            },
            {
                "numero": "L-0044",
                "cerveza": cerveza_amber,
                "estado": Lote.Estado.LISTO,
                "fecha_inicio": self._fecha(35),
                "fecha_fin": self._fecha(10),
                "volumen_litros": Decimal("600.00"),
                "notas": "Lote cerrado y envasado; listo para despachar.",
                "etapas": [
                    (
                        1,
                        EtapaFermentacion.Tipo.PRIMARIA,
                        0,
                        7,
                        Decimal("21.0"),
                        EtapaFermentacion.Estado.COMPLETADA,
                    ),
                    (
                        2,
                        EtapaFermentacion.Tipo.SECUNDARIA,
                        7,
                        14,
                        Decimal("18.0"),
                        EtapaFermentacion.Estado.COMPLETADA,
                    ),
                    (
                        3,
                        EtapaFermentacion.Tipo.MADURADO,
                        14,
                        25,
                        Decimal("4.0"),
                        EtapaFermentacion.Estado.COMPLETADA,
                    ),
                ],
            },
        ]
        for datos_lote in datos:
            etapas = datos_lote.pop("etapas")
            lote, created_lote = Lote.objects.get_or_create(
                numero=datos_lote["numero"], defaults=datos_lote
            )
            if created_lote:
                creados["lotes"] += 1
            for numero, tipo, dias_ini, dias_fin, temp, estado in etapas:
                _, created_etapa = EtapaFermentacion.objects.get_or_create(
                    lote=lote,
                    numero=numero,
                    defaults={
                        "tipo": tipo,
                        "fecha_inicio": self._fecha(dias_ini),
                        "fecha_fin": self._fecha(dias_fin)
                        if dias_fin is not None
                        else None,
                        "temperatura": temp,
                        "estado": estado,
                    },
                )
                if created_etapa:
                    creados["etapas de fermentación"] += 1

    def _cargar_pedidos(self, creados):
        """15 pedidos con 1 a 3 líneas cada uno, repartidos en las últimas 4 semanas.

        `Pedido` no tiene ninguna columna única (no existe `numero_pedido`),
        así que no hay clave natural fiable para `get_or_create`. La política
        elegida es la más simple y segura: si ya existe al menos un pedido,
        no creamos ninguno más y avisamos por consola. Para regenerar los
        pedidos se usa `--flush` (que vacía el dominio y recarga todo).

        Las fechas se distribuyen en los últimos 27 días con un truco
        deliberado: los pedidos más viejos están ENTREGADO y los más
        recientes PENDIENTE/EN_PREPARACION. Así el listado del admin (que
        ordena por fecha) refleja un flujo de ventas verosímil en la
        captura, y el filtro por rango de fechas tiene datos en todo el
        rango.

        Detalle de `auto_now_add`: `Pedido.fecha` es `auto_now_add=True`, lo
        que significa que Django PISA el valor cada vez que hacemos
        `create()` (pisa incluso un `fecha=` explícito). Por eso creamos el
        pedido y después corregimos la fecha con un `update()` directo, que
        no pasa por el `save()` y por lo tanto no es tocado por
        `auto_now_add`.

        `Pedido.total` es un campo GUARDADO (no calculado): lo armamos en
        Python como la suma de `cantidad × precio_unitario` de cada línea, y
        congelamos ese precio de la cerveza al momento de la venta (mismo
        criterio que la capa de API). Así el total del histórico no se mueve
        si después cambian los precios del catálogo.
        """
        pedidos_existentes = Pedido.objects.count()
        if pedidos_existentes:
            self.stdout.write(
                self.style.WARNING(
                    f"Ya hay {pedidos_existentes} pedidos en la base: no se "
                    "crean más (Pedido no tiene clave natural única, repetirlos "
                    "duplicaría ventas). Usá --flush para regenerarlos."
                )
            )
            return

        clientes = list(Cliente.objects.order_by("email"))
        cervezas = list(Cerveza.objects.order_by("nombre"))
        # Formas de pago rotando para que los tres valores aparezcan en el listado.
        formas_pago = [
            Pedido.FormaPago.EFECTIVO,
            Pedido.FormaPago.TARJETA,
            Pedido.FormaPago.TRANSFERENCIA,
        ]
        # (días atrás, estado, cliente_idx, pago_idx, líneas[(cerveza, cantidad)])
        # Los más viejos = entregados; los más nuevos = pendientes.
        datos = [
            (26, Pedido.Estado.ENTREGADO, 0, 0, [(4, 2)]),
            (24, Pedido.Estado.ENTREGADO, 1, 1, [(0, 1), (5, 2)]),
            (22, Pedido.Estado.ENTREGADO, 2, 2, [(6, 3)]),
            (20, Pedido.Estado.LISTO_RETIRO, 3, 0, [(2, 1), (3, 1)]),
            (18, Pedido.Estado.LISTO_RETIRO, 4, 1, [(1, 2)]),
            (16, Pedido.Estado.LISTO_RETIRO, 5, 2, [(5, 1), (7, 2), (4, 1)]),
            (14, Pedido.Estado.EN_PREPARACION, 6, 0, [(0, 3)]),
            (12, Pedido.Estado.EN_PREPARACION, 7, 1, [(6, 2), (2, 2)]),
            (10, Pedido.Estado.EN_PREPARACION, 8, 2, [(4, 1)]),
            (8, Pedido.Estado.CONFIRMADO, 9, 0, [(5, 2), (1, 1)]),
            (6, Pedido.Estado.CONFIRMADO, 0, 1, [(2, 3)]),
            (4, Pedido.Estado.CONFIRMADO, 1, 2, [(3, 2), (6, 1)]),
            (3, Pedido.Estado.PENDIENTE, 2, 0, [(0, 1)]),
            (2, Pedido.Estado.PENDIENTE, 3, 1, [(7, 2), (4, 2)]),
            (0, Pedido.Estado.PENDIENTE, 4, 2, [(5, 1), (2, 1), (6, 2)]),
        ]
        for dias, estado, idx_cliente, idx_pago, lineas in datos:
            # Primero calculamos el total en Python para poder crear el
            # pedido con el total ya correcto desde el origen.
            subtotal_total = sum(
                cervezas[idx_cerveza].precio * cantidad
                for idx_cerveza, cantidad in lineas
            )
            pedido = Pedido.objects.create(
                cliente=clientes[idx_cliente],
                estado=estado,
                forma_pago=formas_pago[idx_pago],
                total=subtotal_total,
                direccion_entrega=f"Rivadavia {1000 + idx_cliente * 10}, Córdoba",
                observaciones="",
            )
            # Como `fecha` tiene `auto_now_add=True`, el `create()` de arriba
            # guardó "ahora" pese a no pasarle `fecha`; este `update()` (que
            # no ejecuta `save()`) es el que deja la fecha histórica
            # repartida en las últimas 4 semanas.
            Pedido.objects.filter(pk=pedido.pk).update(fecha=self._datetime(dias))
            creados["pedidos"] += 1
            for idx_cerveza, cantidad in lineas:
                LineaPedido.objects.create(
                    pedido=pedido,
                    cerveza=cervezas[idx_cerveza],
                    cantidad=cantidad,
                    # Congelamos el precio de catálogo al momento de la venta.
                    precio_unitario=cervezas[idx_cerveza].precio,
                )
                creados["líneas de pedido"] += 1

    def _cargar_opiniones(self, creados):
        """12 reseñas con puntaje 3-5 y comentarios cortos.

        `Opinion` tampoco tiene una columna única, pero la tupla
        (cliente, cerveza, puntaje, comentario) es suficientemente única
        para las 12 filas del seed: funciona como clave natural y mantiene
        el comando idempotente.

        El puntaje arranca en 3 (nunca en 1-2) a propósito: el ensayo y las
        capturas comunican un producto que gusta; igual el rango completo
        1-5 está soportado por los validators del modelo.

        Las fechas también se corren con `update()` porque `Opinion.fecha`
        tiene `auto_now_add=True` (mismo detalle que en `Pedido.fecha`): así
        las reseñas aparecen distribuidas y el orden por fecha del admin se
        ve creíble.
        """
        clientes = list(Cliente.objects.order_by("email"))
        cervezas = list(Cerveza.objects.order_by("nombre"))
        # (cliente_idx, cerveza_idx, puntaje, comentario, días atrás)
        datos = [
            (0, 0, 5, "La mejor IPA de la zona, lupulada y fresca.", 25),
            (1, 2, 4, "Stout con mucho cuerpo, ideal para la noche.", 23),
            (2, 4, 5, "Pilsener perfecta para el calor de Córdoba.", 21),
            (3, 1, 4, "Doble IPA intensa; para iniciados del estilo.", 18),
            (4, 5, 4, "Trigo refrescante, aroma frutal muy agradable.", 16),
            (5, 6, 5, "Amber equilibrada, se nota la malta caramelizada.", 14),
            (6, 3, 3, "Buena pero muy tostada para mi gusto.", 11),
            (7, 7, 4, "Buena cerveza aunque me extraña que falte stock.", 9),
            (8, 0, 5, "Clásica de la casa, siempre la pido.", 7),
            (9, 2, 5, "Stout de la casa con postre: combo perfecto.", 5),
            (1, 4, 4, "Muy buen precio por el litro en grifo.", 3),
            (3, 6, 3, "Correcta, esperaba un poco más de amargor.", 1),
        ]
        for idx_cliente, idx_cerveza, puntaje, comentario, dias in datos:
            opinion, created = Opinion.objects.get_or_create(
                cliente=clientes[idx_cliente],
                cerveza=cervezas[idx_cerveza],
                puntaje=puntaje,
                comentario=comentario,
            )
            if created:
                creados["opiniones"] += 1
                # `auto_now_add` dejó "ahora" en el `create()`; corregimos la
                # fecha para repartir las reseñas en las últimas 4 semanas.
                Opinion.objects.filter(pk=opinion.pk).update(fecha=self._datetime(dias))
