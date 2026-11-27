"""Pruebas de registrar_item con la tabla de decisión (HU-07, H-05)."""
import pytest

from app.cobros.errores import AccesoDenegado
from app.cobros.modelos import ROL_MECANICO, ROL_REGISTRADOR, ItemCobro, Orden, Trabajador
from app.cobros.servicio import registrar_item

MECANICO_1 = Trabajador(id=1, rol=ROL_MECANICO)
REGISTRADOR_ID_1 = Trabajador(id=1, rol=ROL_REGISTRADOR)
VALIDO = ItemCobro("repuesto", "Filtro de aceite", 1, 18000)
INVALIDO = ItemCobro("repuesto", "Pastillas de freno", 1, None)


@pytest.mark.parametrize(
    "trabajador, mecanico_de_la_orden, item, error",
    [
        (MECANICO_1, 1, VALIDO, None),  # columna 1
        (MECANICO_1, 1, INVALIDO, ValueError),  # columna 2
        (MECANICO_1, 2, VALIDO, AccesoDenegado),  # columna 3
        (MECANICO_1, 2, INVALIDO, AccesoDenegado),  # columna 4
        (REGISTRADOR_ID_1, 1, VALIDO, AccesoDenegado),  # columna 5
        (REGISTRADOR_ID_1, 1, INVALIDO, AccesoDenegado),  # columna 6
        (REGISTRADOR_ID_1, 2, VALIDO, AccesoDenegado),  # columna 7
        (REGISTRADOR_ID_1, 2, INVALIDO, AccesoDenegado),  # columna 8
    ],
)
def test_tabla_de_decision(trabajador, mecanico_de_la_orden, item, error):
    orden = Orden("48271936", mecanico_de_la_orden)
    if error is None:
        resumen = registrar_item(orden, item, trabajador)
        assert resumen.total > 0
    else:
        with pytest.raises(error):
            registrar_item(orden, item, trabajador)
