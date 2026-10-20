"""Suite de tests de la API de Cervecería Los Flacheros (Fase 7, Tasks 23-24).

Son la evidencia de los requisitos de la consigna (plan §12): propiedades de
los modelos, permisos (401 sin identificar, 403 sin permiso), paginación,
"datos anidados SOLO en list", filtros y búsqueda, y las tres `@action`
(`en_grifo`, `estadisticas`, `avanzar`) más la excepción del mostrador.

Se corren con pytest + pytest-django (configurado en `pyproject.toml`,
`testpaths = ["core"]`), desde `backend/`. Para usar una base de pruebas
propia y no tocar la base del proyecto:

    $env:DATABASE_URL="sqlite:///db_tests.sqlite3"
    uv run pytest -v

Cada test crea sus propios datos y pytest-django revierte la transacción al
terminar: los tests no dependen del orden ni dejan datos sucios.
"""

import json
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import (
    Cerveza,
    Cliente,
    Estilo,
    EtapaFermentacion,
    LineaPedido,
    Lote,
    Pedido,
)

# --- Helpers -----------------------------------------------------------------
# Pequeñas factories para no repetir setup en cada test; se leen de arriba
# hacia abajo y usan valores por defecto únicos por test.


def crear_usuario(username="mostrador", staff=False):
    """Usuario de prueba; `staff=True` cuando el test necesita IsAdminUser."""
    return User.objects.create_user(username=username, is_staff=staff)


def token_de(usuario):
    """Clave del Token del usuario, para el header `Authorization: Token <clave>`."""
    return Token.objects.create(user=usuario).key


def autenticar(cliente, usuario):
    """Deja al cliente de pruebas mandando el header de token de `usuario`."""
    cliente.credentials(HTTP_AUTHORIZATION=f"Token {token_de(usuario)}")


def crear_estilo(nombre="IPA"):
    """Estilo compartido; get_or_create para poder crear varias cervezas."""
    return Estilo.objects.get_or_create(nombre=nombre)[0]


def crear_cerveza(
    nombre,
    estilo=None,
    tipo=Cerveza.Tipo.ENVASE,
    stock=10,
    activo=True,
    precio="4500.00",
):
    return Cerveza.objects.create(
        nombre=nombre,
        precio=Decimal(precio),
        stock=stock,
        tipo=tipo,
        activo=activo,
        estilo=estilo or crear_estilo(),
    )


def crear_cliente(email="ana@ejemplo.com", nombre="Ana", apellido="Pérez"):
    """Cliente; get_or_create por email para poder pedir dos veces al mismo."""
    cliente, _ = Cliente.objects.get_or_create(
        email=email,
        defaults={"nombre": nombre, "apellido": apellido},
    )
    return cliente


def crear_pedido(cliente=None, total=Decimal("0")):
    return Pedido.objects.create(cliente=cliente or crear_cliente(), total=total)


def crear_linea(pedido, cerveza, cantidad=1, precio_unitario="4500.00"):
    return LineaPedido.objects.create(
        pedido=pedido,
        cerveza=cerveza,
        cantidad=cantidad,
        precio_unitario=Decimal(precio_unitario),
    )


def crear_lote(numero="L-0001", estado=Lote.Estado.PLANIFICADO, cerveza=None):
    """Lote PLANIFICADO por defecto; el número es único por llamada."""
    return Lote.objects.create(
        numero=numero,
        fecha_inicio=date(2026, 10, 1),
        volumen_litros=Decimal("200.00"),
        estado=estado,
        cerveza=cerveza or crear_cerveza(f"Cerveza del {numero}"),
    )


def crear_etapa(lote, numero=1, tipo=EtapaFermentacion.Tipo.PRIMARIA):
    return EtapaFermentacion.objects.create(
        lote=lote,
        numero=numero,
        tipo=tipo,
        fecha_inicio=date(2026, 10, 1),
    )


def json_de(respuesta):
    """Cuerpo de la respuesta parseado como JSON (dict o lista)."""
    return json.loads(respuesta.content)


@pytest.fixture
def client():
    """El `client` de los tests: el APIClient de DRF, no el Client crudo.

    Sombrea el `client` de pytest-django: así cada test habla con la API
    igual que el frontend (header de token con `credentials()`, sin CSRF) y
    puede usar `force_login` para el login por sesión.
    """
    return APIClient()


# --- Modelos (plan §12: tests 1-3) -------------------------------------------


@pytest.mark.django_db
def test_cliente_nombre_completo():
    """Requisito: Cliente.nombre_completo devuelve "nombre apellido"."""
    cliente = Cliente.objects.create(
        nombre="Ana", apellido="Pérez", email="ana@ejemplo.com"
    )
    assert cliente.nombre_completo == "Ana Pérez"
    # Sin apellido no queda un espacio colgado al final.
    sin_apellido = Cliente.objects.create(
        nombre="Solo", apellido="", email="solo@ejemplo.com"
    )
    assert sin_apellido.nombre_completo == "Solo"


@pytest.mark.django_db
def test_linea_pedido_subtotal():
    """Requisito: LineaPedido.subtotal es cantidad × precio_unitario."""
    pedido = crear_pedido()
    cerveza = crear_cerveza("Dorada de la Casa")
    linea = crear_linea(pedido, cerveza, cantidad=3, precio_unitario="4500.00")
    # Si el subtotal devolviera solo el precio o multiplicara mal, falla acá.
    assert linea.subtotal == Decimal("13500.00")


@pytest.mark.django_db
def test_lote_estado_choices():
    """Requisito: Lote.estado solo acepta los valores de su TextChoices."""
    lote = crear_lote("L-0001")
    # Un estado inventado no pasa la validación de choices...
    lote.estado = "EN_PRUEBAS"
    with pytest.raises(ValidationError) as exc:
        lote.full_clean()
    assert "estado" in exc.value.message_dict
    # ...pero uno del catálogo sí: el rechazo es por el valor, no por otra cosa.
    lote.estado = Lote.Estado.FERMENTACION
    lote.full_clean()


# --- Autenticación y permisos de lectura (plan §12: tests 4, 5, 13) ----------


@pytest.mark.django_db
def test_listado_sin_token_devuelve_401(client):
    """Requisito: GET /api/cervezas/ sin token responde 401 (sin lectura anónima)."""
    respuesta = client.get("/api/cervezas/")
    assert respuesta.status_code == 401
    # TokenAuthentication va primero en settings: por eso DRF puede mandar el
    # desafío y responder 401 (y no 403, que sería "no tenés permiso").
    assert respuesta["WWW-Authenticate"] == "Token"


@pytest.mark.django_db
def test_listado_con_token_devuelve_200(client):
    """Requisito: GET /api/cervezas/ con token válido responde 200."""
    autenticar(client, crear_usuario())
    assert client.get("/api/cervezas/").status_code == 200
    # Con un token inventado no entra: la autenticación valida la clave.
    client.credentials(HTTP_AUTHORIZATION="Token clave-inventada")
    assert client.get("/api/cervezas/").status_code == 401


@pytest.mark.django_db
def test_sesion_ya_autenticado_devuelve_200(client):
    """Requisito: el login por sesión entra (200) y el mismo GET anónimo da 401."""
    assert client.get("/api/cervezas/").status_code == 401
    client.force_login(crear_usuario())
    assert client.get("/api/cervezas/").status_code == 200


# --- Contrato del listado (plan §12: tests 6-9, 11-12) -----------------------


@pytest.mark.django_db
def test_paginacion_estructura(client):
    """Requisito: el listado trae count/next/previous/results y pagina de a 10."""
    autenticar(client, crear_usuario())
    estilo = crear_estilo()
    for numero in range(12):
        crear_cerveza(f"Cerveza {numero:02d}", estilo=estilo)

    pagina_1 = json_de(client.get("/api/cervezas/"))
    assert isinstance(pagina_1, dict)
    assert set(pagina_1) == {"count", "next", "previous", "results"}
    assert pagina_1["count"] == 12
    # DefaultPagination: page_size = 10 → 10 en la primera página y 2 en la 2.
    assert len(pagina_1["results"]) == 10
    assert pagina_1["previous"] is None
    assert pagina_1["next"] is not None

    pagina_2 = json_de(client.get("/api/cervezas/?page=2"))
    assert len(pagina_2["results"]) == 2
    assert pagina_2["previous"] is not None
    assert pagina_2["next"] is None


@pytest.mark.django_db
def test_lotes_nested_solo_en_list(client):
    """Requisito: `etapas` existe en GET /api/lotes/ y no en GET /api/lotes/{id}/."""
    autenticar(client, crear_usuario())
    lote = crear_lote("L-0042")
    etapa = crear_etapa(lote)

    listado = json_de(client.get("/api/lotes/"))
    assert listado["count"] == 1
    primero = listado["results"][0]
    assert primero["id"] == lote.id
    assert [etapa_anidada["id"] for etapa_anidada in primero["etapas"]] == [etapa.id]

    detalle = json_de(client.get(f"/api/lotes/{lote.id}/"))
    assert detalle["id"] == lote.id  # es el lote, no un error
    assert "numero" in detalle  # el detalle va con el serializer plano
    assert "etapas" not in detalle


@pytest.mark.django_db
def test_pedidos_nested_solo_en_list(client):
    """Requisito: `lineas` existe en GET /api/pedidos/ pero no en el detalle."""
    autenticar(client, crear_usuario())
    pedido = crear_pedido()
    cerveza = crear_cerveza("Roja del Patio")
    linea = crear_linea(pedido, cerveza, cantidad=2)

    listado = json_de(client.get("/api/pedidos/"))
    assert listado["count"] == 1
    primero = listado["results"][0]
    assert primero["id"] == pedido.id
    assert [linea_anidada["id"] for linea_anidada in primero["lineas"]] == [linea.id]

    detalle = json_de(client.get(f"/api/pedidos/{pedido.id}/"))
    assert detalle["id"] == pedido.id  # es el pedido, no un error
    assert "total" in detalle  # el detalle va con el serializer plano
    assert "lineas" not in detalle


@pytest.mark.django_db
def test_en_grifo(client):
    """Requisito: en_grifo devuelve solo cervezas GRIFO, activas y con stock > 0."""
    autenticar(client, crear_usuario())
    estilo = crear_estilo()
    grifo = crear_cerveza(
        "De Grifo Buena", estilo=estilo, tipo=Cerveza.Tipo.GRIFO, stock=5
    )
    crear_cerveza("De Grifo Sin Stock", estilo=estilo, tipo=Cerveza.Tipo.GRIFO, stock=0)
    crear_cerveza(
        "De Grifo De Baja",
        estilo=estilo,
        tipo=Cerveza.Tipo.GRIFO,
        activo=False,
        stock=5,
    )
    crear_cerveza("Envasada", estilo=estilo, tipo=Cerveza.Tipo.ENVASE, stock=5)
    assert Cerveza.objects.count() == 4  # sanity: se crearon las 4

    respuesta = client.get("/api/cervezas/en_grifo/")
    assert respuesta.status_code == 200
    datos = json_de(respuesta)
    assert datos["count"] == 1
    assert {c["id"] for c in datos["results"]} == {grifo.id}


@pytest.mark.django_db
def test_filtro_cervezas_tipo(client):
    """Requisito: ?tipo=GRIFO de /api/cervezas/ devuelve solo las de grifo."""
    autenticar(client, crear_usuario())
    estilo = crear_estilo()
    grifo = crear_cerveza("Grifo Fuera", estilo=estilo, tipo=Cerveza.Tipo.GRIFO)
    envase = crear_cerveza("Envase Cartón", estilo=estilo, tipo=Cerveza.Tipo.ENVASE)
    assert Cerveza.objects.count() == 2  # sanity: hay una de cada tipo

    datos = json_de(client.get("/api/cervezas/?tipo=GRIFO"))
    assert datos["count"] == 1
    assert {c["id"] for c in datos["results"]} == {grifo.id}
    assert envase.id not in {c["id"] for c in datos["results"]}


@pytest.mark.django_db
def test_busqueda_cervezas(client):
    """Requisito: ?search=ipa encuentra la cerveza esperada (SearchFilter)."""
    autenticar(client, crear_usuario())
    estilo = crear_estilo()
    ipa = crear_cerveza("Apolo IPA", estilo=estilo)
    crear_cerveza("Luna Stout", estilo=estilo, precio="5000.00")

    # minúsculas: la búsqueda tiene que ser case-insensitive para encontrarla.
    datos = json_de(client.get("/api/cervezas/?search=ipa"))
    assert datos["count"] == 1
    assert datos["results"][0]["id"] == ipa.id
    assert datos["results"][0]["nombre"] == "Apolo IPA"


# --- Acción estadisticas (plan §12: test 10) ---------------------------------


@pytest.mark.django_db
def test_estadisticas_permisos(client):
    """Requisito: estadisticas da 403 sin staff y 200 con staff (IsAdminUser)."""
    # Un pedido cargado para comprobar que los agregados son reales.
    pedido = crear_pedido(total=Decimal("1500.00"))

    autenticar(client, crear_usuario("barra"))
    sin_staff = client.get("/api/pedidos/estadisticas/")
    assert sin_staff.status_code == 403

    autenticar(client, crear_usuario("gerencia", staff=True))
    con_staff = client.get("/api/pedidos/estadisticas/")
    assert con_staff.status_code == 200
    datos = json_de(con_staff)
    assert datos["total_pedidos"] == 1
    assert datos["monto_total"] == 1500.0
    assert datos["promedio_ticket"] == 1500.0
    assert datos["pedidos_por_estado"] == {pedido.estado: 1}


# --- Escritura: catálogo staff vs. mostrador (plan §12: tests 14-16) --------


@pytest.mark.django_db
def test_escritura_requiere_staff(client):
    """Requisito: POST /api/cervezas/ da 403 sin staff y 201 con staff."""
    estilo = crear_estilo()
    payload = {
        "nombre": "Cerveza Nuevo Lote",
        "precio": "4500.00",
        "tipo": "ENVASE",
        "stock": 12,
        "estilo": estilo.id,
    }

    autenticar(client, crear_usuario("barra"))
    sin_staff = client.post("/api/cervezas/", payload, format="json")
    assert sin_staff.status_code == 403
    assert not Cerveza.objects.filter(nombre=payload["nombre"]).exists()

    autenticar(client, crear_usuario("jefatura", staff=True))
    con_staff = client.post("/api/cervezas/", payload, format="json")
    assert con_staff.status_code == 201
    assert Cerveza.objects.filter(nombre=payload["nombre"]).exists()


@pytest.mark.django_db
def test_mostrador_crea_pedido(client):
    """Requisito: el mostrador (no staff) crea pedidos con POST /api/pedidos/ (201)."""
    cliente = crear_cliente()
    barman = crear_usuario("barman")
    assert not barman.is_staff  # la excepción es para cualquier autenticado

    autenticar(client, barman)
    respuesta = client.post(
        "/api/pedidos/",
        {"cliente": cliente.id, "direccion_entrega": "Av. Siempreviva 742"},
        format="json",
    )
    assert respuesta.status_code == 201
    pedido = Pedido.objects.get(cliente=cliente)
    assert pedido.estado == Pedido.Estado.PENDIENTE  # estado por defecto


@pytest.mark.django_db
def test_linea_recalcula_total_del_pedido(client):
    """Requisito: crear líneas deja Pedido.total = suma de subtotales."""
    pedido = crear_pedido()  # total 0 hasta que entren las líneas
    cerveza = crear_cerveza("Negra del Sur")
    autenticar(client, crear_usuario())

    primera = client.post(
        "/api/lineas/",
        {
            "pedido": pedido.id,
            "cerveza": cerveza.id,
            "cantidad": 2,
            "precio_unitario": "4500.00",
        },
        format="json",
    )
    assert primera.status_code == 201
    pedido.refresh_from_db()
    assert pedido.total == Decimal("9000.00")

    segunda = client.post(
        "/api/lineas/",
        {
            "pedido": pedido.id,
            "cerveza": cerveza.id,
            "cantidad": 1,
            "precio_unitario": "1000.00",
        },
        format="json",
    )
    assert segunda.status_code == 201
    pedido.refresh_from_db()
    assert pedido.total == Decimal("10000.00")
    # Y no solo el valor esperado: coincide con la suma real de sus renglones.
    assert pedido.total == sum(
        (linea.subtotal for linea in pedido.lineas.all()), Decimal("0")
    )


# --- Acción avanzar (plan §12: test 17) --------------------------------------


@pytest.mark.django_db
def test_avanzar_lote_transicion_invalida(client):
    """Requisito: avanzar mueve un paso (200) y un salto inválido responde 400."""
    autenticar(client, crear_usuario("produccion", staff=True))

    # Camino válido: PLANIFICADO → EN_PRODUCCION, un paso por vez.
    lote = crear_lote("L-0100")
    avance = client.post(f"/api/lotes/{lote.id}/avanzar/", {}, format="json")
    assert avance.status_code == 200
    assert json_de(avance)["estado"] == "EN_PRODUCCION"
    lote.refresh_from_db()
    assert lote.estado == "EN_PRODUCCION"

    # Salto inválido: desde PLANIFICADO no se puede ir directo a LISTO.
    lote_salto = crear_lote("L-0200")
    salto = client.post(
        f"/api/lotes/{lote_salto.id}/avanzar/", {"estado": "LISTO"}, format="json"
    )
    assert salto.status_code == 400
    assert "detail" in json_de(salto)
    lote_salto.refresh_from_db()
    assert lote_salto.estado == "PLANIFICADO"  # el salto rechazado no mueve nada

    # Además: la acción es staff; un usuario normal queda en 403.
    autenticar(client, crear_usuario("barra"))
    denegado = client.post(f"/api/lotes/{lote_salto.id}/avanzar/", {}, format="json")
    assert denegado.status_code == 403
    lote_salto.refresh_from_db()
    assert lote_salto.estado == "PLANIFICADO"
