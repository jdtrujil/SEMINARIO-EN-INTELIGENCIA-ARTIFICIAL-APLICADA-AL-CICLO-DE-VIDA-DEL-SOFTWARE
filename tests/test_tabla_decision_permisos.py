"""Pruebas de registrar_item con la tabla de decisión (HU-07, H-05).

C1: el trabajador es mecánico. C2: la orden está asignada a ese trabajador.
C3: el ítem es válido. Las columnas son las de registro_pruebas.md, sección 1.3.
"""
import re

import pytest

from app.cobros.errores import AccesoDenegado
from app.cobros.modelos import (
    ROL_MECANICO,
    ROL_REGISTRADOR,
    ItemCobro,
    Orden,
    ResumenCobro,
    Trabajador,
)
from app.cobros.servicio import registrar_item

MECANICO_1 = Trabajador(id=1, rol=ROL_MECANICO)
# No pasa en el taller porque los ids son únicos; sirve para comprobar que el
# rol se verifica antes que la asignación (columnas 5 y 6).
REGISTRADOR_CON_ID_1 = Trabajador(id=1, rol=ROL_REGISTRADOR)
VALIDO = ItemCobro("repuesto", "Filtro de aceite", 1, 18000)
INVALIDO = ItemCobro("repuesto", "Pastillas de freno", 1, None)

POR_ROL = "Solo un mecánico puede registrar cobros"
POR_ASIGNACION = "Esta orden no está asignada a usted"
SIN_PRECIO = "Escriba el precio del repuesto"


def test_columna_1_mecanico_asignado_con_item_valido_registra():
    orden = Orden("48271936", mecanico_id=1)

    resumen = registrar_item(orden, VALIDO, MECANICO_1)

    assert resumen == ResumenCobro(18000, 0, 18000)
    assert orden.items == [VALIDO]


@pytest.mark.parametrize(
    "trabajador, mecanico_de_la_orden, item, error, mensaje",
    [
        (MECANICO_1, 1, INVALIDO, ValueError, SIN_PRECIO),  # columna 2, regla R3
        (MECANICO_1, 2, VALIDO, AccesoDenegado, POR_ASIGNACION),  # columna 3, R2
        (MECANICO_1, 2, INVALIDO, AccesoDenegado, POR_ASIGNACION),  # columna 4, R2
        (MECANICO_1, None, VALIDO, AccesoDenegado, POR_ASIGNACION),  # C2 sin mecánico
        (REGISTRADOR_CON_ID_1, 1, VALIDO, AccesoDenegado, POR_ROL),  # columna 5, R1
        (REGISTRADOR_CON_ID_1, 1, INVALIDO, AccesoDenegado, POR_ROL),  # columna 6, R1
        (REGISTRADOR_CON_ID_1, 2, VALIDO, AccesoDenegado, POR_ROL),  # columna 7, R1
        (REGISTRADOR_CON_ID_1, 2, INVALIDO, AccesoDenegado, POR_ROL),  # columna 8, R1
    ],
)
def test_columnas_2_a_8_rechazan_sin_cambiar_la_orden(
    trabajador, mecanico_de_la_orden, item, error, mensaje
):
    orden = Orden("48271936", mecanico_id=mecanico_de_la_orden)

    with pytest.raises(error, match=f"^{re.escape(mensaje)}$"):
        registrar_item(orden, item, trabajador)

    assert orden.items == []


def test_registrador_de_los_datos_sinteticos_no_registra_cobros(
    registrador, items_sinteticos
):
    orden = Orden("48271936", mecanico_id=1)

    with pytest.raises(AccesoDenegado, match=f"^{re.escape(POR_ROL)}$"):
        registrar_item(orden, items_sinteticos[0], registrador)

    assert orden.items == []


def test_mecanico_asignado_registra_toda_la_orden_sintetica(
    mecanico_1, items_sinteticos
):
    orden = Orden("48271936", mecanico_id=1)

    for item in items_sinteticos:
        resumen = registrar_item(orden, item, mecanico_1)

    assert resumen == ResumenCobro(195000, 65000, 260000)  # calculado a mano
    assert orden.items == items_sinteticos
