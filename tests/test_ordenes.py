"""Reglas de las órdenes: ingreso, etapas, cobro, factura y consulta.

Corren contra SQLite y, en el pipeline, también contra PostgreSQL 16 (fixture
destino_bd en conftest.py). Los mensajes esperados son los de los criterios de
aceptación de la semana 3, con las etapas que definió el cliente.
"""

import re
from datetime import timedelta

import pytest

from app.cobros.calculo import ItemCobro, ResumenCobro
from app.cobros.errores import AccesoDenegado
from app.ingresos.placas import MENSAJE_FORMATO
from app.ordenes import servicio
from app.ordenes.modelos import EN_REPARACION, RECIBIDA, TERMINADA, CambioDeEtapa
from app.ordenes.repositorio import abrir

FILTRO = ItemCobro("repuesto", "Filtro de aceite", 1, 18000)
ACEITE = ItemCobro("repuesto", "Aceite, un litro", 1, 32000)
MANO_DE_OBRA = ItemCobro("mano de obra", "Cambio de aceite", 1, 35000)


def numeros(*lista):
    """Generador de números de orden predecible para las pruebas."""
    pendientes = list(lista)
    return lambda: pendientes.pop(0)


def ingresar(repo, fecha, placa="ABC12D", numero="48271936", mecanico=1):
    return servicio.registrar_ingreso(
        repo, placa, "Rayón en el tanque", mecanico, fecha, numeros(numero)
    )


def en_reparacion_con_cobro(repo, fecha, items=(FILTRO, ACEITE, MANO_DE_OBRA)):
    numero = ingresar(repo, fecha)
    servicio.avanzar_etapa(repo, numero, EN_REPARACION, fecha + timedelta(hours=1))
    for item in items:
        servicio.registrar_cobro(repo, numero, item, 1)
    return numero


# --- Ingreso ---------------------------------------------------------------


def test_ingreso_guarda_fecha_placa_observaciones_mecanico_y_etapa(repo, fecha_ingreso):
    numero = servicio.registrar_ingreso(
        repo,
        " abc12d ",
        "  Rayón en el tanque  ",
        2,
        fecha_ingreso,
        numeros("48271936"),
    )
    orden = repo.orden(numero)
    assert numero == "48271936"
    assert orden.placa == "ABC12D"  # la placa se guarda normalizada
    assert orden.observaciones == "Rayón en el tanque"
    assert orden.mecanico_id == 2
    assert orden.etapa == RECIBIDA
    assert orden.fecha_ingreso == fecha_ingreso
    assert orden.historial == [CambioDeEtapa(RECIBIDA, fecha_ingreso)]
    assert orden.items == []
    assert orden.factura is None


def test_los_datos_quedan_guardados_al_cerrar_y_abrir_la_base(
    destino_bd, fecha_ingreso
):
    with abrir(destino_bd) as repo:
        numero = ingresar(repo, fecha_ingreso)
    with abrir(destino_bd) as otra_conexion:
        orden = otra_conexion.orden(numero)
    assert orden.placa == "ABC12D"
    assert orden.fecha_ingreso == fecha_ingreso


@pytest.mark.parametrize(
    ("placa", "observaciones", "mecanico", "mensaje"),
    [
        ("ABC-12D", "Sin daños visibles", 1, MENSAJE_FORMATO),  # placa con guion
        ("ABC12D", "   ", 1, servicio.MENSAJE_OBSERVACIONES),  # HU-02 vacía
        ("ABC12D", "Sin daños visibles", None, servicio.MENSAJE_SIN_MECANICO),
        ("ABC12D", "Sin daños visibles", 3, servicio.MENSAJE_SIN_MECANICO),  # no existe
    ],
)
def test_ingreso_invalido_no_se_guarda(
    repo, fecha_ingreso, placa, observaciones, mecanico, mensaje
):
    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        servicio.registrar_ingreso(
            repo, placa, observaciones, mecanico, fecha_ingreso, numeros("48271936")
        )
    assert repo.ordenes_recientes() == []


def test_moto_con_orden_abierta_no_recibe_otro_numero(repo, fecha_ingreso):
    ingresar(repo, fecha_ingreso)
    with pytest.raises(
        ValueError, match="^Esta moto ya tiene una orden abierta: 48271936$"
    ):
        ingresar(repo, fecha_ingreso, placa="abc12d", numero="55555555")
    assert [o.numero for o in repo.ordenes_recientes()] == ["48271936"]


def test_moto_terminada_puede_volver_a_ingresar(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso + timedelta(hours=3))
    nuevo = ingresar(repo, fecha_ingreso + timedelta(days=5), numero="55555555")
    assert nuevo == "55555555"


def test_numero_repetido_se_cambia_por_otro(repo, fecha_ingreso):
    ingresar(repo, fecha_ingreso, numero="48271936")
    numero = servicio.registrar_ingreso(
        repo,
        "XYZ98E",
        "Sin daños visibles",
        1,
        fecha_ingreso,
        numeros("48271936", "55555555"),
    )
    assert numero == "55555555"


def test_sin_numero_libre_despues_de_cinco_intentos_lanza_error(repo, fecha_ingreso):
    ingresar(repo, fecha_ingreso, numero="48271936")
    with pytest.raises(RuntimeError, match=f"^{servicio.MENSAJE_SIN_NUMERO}$"):
        servicio.registrar_ingreso(
            repo,
            "XYZ98E",
            "Sin daños visibles",
            1,
            fecha_ingreso,
            numeros(*["48271936"] * 5),
        )


def test_numero_aleatorio_tiene_ocho_digitos_y_no_empieza_en_cero():
    for _ in range(200):
        numero = servicio.numero_aleatorio()
        assert re.fullmatch(r"[1-9][0-9]{7}", numero)


# --- Etapas ----------------------------------------------------------------


def test_etapas_en_orden_quedan_en_el_historial_con_fecha_y_hora(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    fin = fecha_ingreso + timedelta(hours=7, minutes=25)
    orden = servicio.avanzar_etapa(repo, numero, TERMINADA, fin)
    assert [c.etapa for c in orden.historial] == [RECIBIDA, EN_REPARACION, TERMINADA]
    assert orden.historial[-1].fecha_hora == fin


@pytest.mark.parametrize(
    ("etapa", "mensaje"),
    [
        (TERMINADA, "La moto está en Recibida; el paso siguiente es En reparación"),
        (RECIBIDA, "La moto está en Recibida; el paso siguiente es En reparación"),
        ("Lista", "La moto está en Recibida; el paso siguiente es En reparación"),
    ],
)
def test_no_se_salta_ni_se_inventa_una_etapa(repo, fecha_ingreso, etapa, mensaje):
    numero = ingresar(repo, fecha_ingreso)
    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        servicio.avanzar_etapa(repo, numero, etapa, fecha_ingreso)
    assert repo.orden(numero).etapa == RECIBIDA


def test_terminar_sin_mano_de_obra_no_cambia_la_etapa(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso, items=(FILTRO,))
    with pytest.raises(ValueError, match=f"^{servicio.MENSAJE_SIN_MANO_DE_OBRA}$"):
        servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso)
    orden = repo.orden(numero)
    assert orden.etapa == EN_REPARACION
    assert orden.factura is None


def test_al_terminar_se_guarda_la_factura_sin_iva(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso + timedelta(hours=3))
    assert repo.orden(numero).factura == ResumenCobro(50000, 35000, 85000)


def test_una_orden_terminada_no_cambia_de_etapa(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso)
    with pytest.raises(ValueError, match=f"^{servicio.MENSAJE_TERMINADA}$"):
        servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso)


# --- Cobro -----------------------------------------------------------------


def test_cobro_solo_en_reparacion(repo, fecha_ingreso):
    numero = ingresar(repo, fecha_ingreso)
    with pytest.raises(ValueError, match=f"^{servicio.MENSAJE_SOLO_EN_REPARACION}$"):
        servicio.registrar_cobro(repo, numero, FILTRO, 1)
    assert repo.orden(numero).items == []


def test_no_se_agregan_items_a_una_factura_cerrada(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso)
    with pytest.raises(ValueError, match=f"^{servicio.MENSAJE_SOLO_EN_REPARACION}$"):
        servicio.registrar_cobro(repo, numero, FILTRO, 1)
    assert len(repo.orden(numero).items) == 3


@pytest.mark.parametrize(
    ("item", "mecanico", "error", "mensaje"),
    [
        # Otro mecánico: el permiso del hallazgo H-05 se aplica también aquí
        (FILTRO, 2, AccesoDenegado, "Esta orden no está asignada a usted"),
        (FILTRO, None, ValueError, servicio.MENSAJE_QUIEN_REGISTRA),
        # Ítem inválido: las reglas del cobro de la semana 5
        (
            ItemCobro("repuesto", "Pastillas de freno", 1, None),
            1,
            ValueError,
            "Escriba el precio del repuesto",
        ),
        (
            ItemCobro("repuesto", "Guaya", 1, -1),
            1,
            ValueError,
            "El precio no puede ser negativo",
        ),
    ],
)
def test_cobro_rechazado_no_se_guarda(
    repo, fecha_ingreso, item, mecanico, error, mensaje
):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso, items=())
    with pytest.raises(error, match=f"^{re.escape(mensaje)}$"):
        servicio.registrar_cobro(repo, numero, item, mecanico)
    assert repo.orden(numero).items == []


def test_cobro_valido_queda_guardado_en_orden(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    assert repo.orden(numero).items == [FILTRO, ACEITE, MANO_DE_OBRA]


# --- Detalle y consulta del cliente ---------------------------------------


def test_detalle_del_cobro_solo_cuando_esta_terminada(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    with pytest.raises(ValueError, match=f"^{servicio.MENSAJE_NO_LISTA}$"):
        servicio.detalle_del_cobro(repo, numero)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso)
    orden = servicio.detalle_del_cobro(repo, numero)
    assert orden.factura == ResumenCobro(50000, 35000, 85000)


@pytest.mark.parametrize("numero", ["12345678", "1234", "abcdefgh", ""])
def test_consulta_de_un_numero_que_no_existe(repo, fecha_ingreso, numero):
    ingresar(repo, fecha_ingreso)
    with pytest.raises(servicio.OrdenNoEncontrada, match="^No encontramos una orden"):
        servicio.consultar(repo, numero)


def test_consulta_antes_de_terminar_no_muestra_el_cobro(repo, fecha_ingreso):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    consulta = servicio.consultar(repo, numero)
    assert consulta.etapa == EN_REPARACION
    assert consulta.actualizada == fecha_ingreso + timedelta(hours=1)
    assert consulta.items == ()
    assert consulta.factura is None


def test_consulta_terminada_muestra_detalle_y_total_pero_no_la_placa(
    repo, fecha_ingreso
):
    numero = en_reparacion_con_cobro(repo, fecha_ingreso)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fecha_ingreso + timedelta(hours=3))
    consulta = servicio.consultar(repo, f" {numero} ")
    assert consulta.etapa == TERMINADA
    assert consulta.items == (FILTRO, ACEITE, MANO_DE_OBRA)
    assert consulta.factura.total == 85000
    assert not hasattr(consulta, "placa")


def test_cambiar_los_nombres_de_los_mecanicos_actualiza_la_base(repo):
    from app.ordenes.modelos import Mecanico

    repo.guardar_mecanicos([Mecanico(1, "Ana Prueba"), Mecanico(2, "Beto Prueba")])
    assert [m.nombre for m in repo.mecanicos()] == ["Ana Prueba", "Beto Prueba"]
