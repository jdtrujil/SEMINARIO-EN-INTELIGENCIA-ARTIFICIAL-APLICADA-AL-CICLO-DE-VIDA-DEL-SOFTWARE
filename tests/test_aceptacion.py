"""Pruebas de aceptación: una por cada escenario construido de las historias.

Los datos y los resultados esperados se copian de los criterios Gherkin del
documento de requisitos de la semana 3 (docs/02_requisitos). La evaluación de
los 20 escenarios, incluidos los que no se han construido, está en la
sección 5 del informe final.
"""
import re

import pytest

from app.cobros.calculo import ItemCobro, ResumenCobro
from app.cobros.modelos import ROL_MECANICO, Orden, Trabajador
from app.cobros.servicio import registrar_item
from app.web.paginas import procesar_cobro


@pytest.fixture
def orden_48271936():
    """La orden del ejemplo de las historias, asignada al mecánico 1."""
    return Orden(numero="48271936", mecanico_id=1)


@pytest.fixture
def mecanico_asignado():
    return Trabajador(id=1, rol=ROL_MECANICO)


def test_hu07_escenario_1_total_sin_iva(orden_48271936, mecanico_asignado):
    # Dado que en la orden 48271936 registro un filtro de aceite de 18.000 pesos,
    # un litro de aceite de 32.000 pesos y una mano de obra de 35.000 pesos,
    # cuando guardo, entonces la orden muestra repuestos por 50.000, mano de obra
    # por 35.000 y un total a cobrar de 85.000 pesos, sin IVA.
    items = [
        ItemCobro("repuesto", "Filtro de aceite", 1, 18000),
        ItemCobro("repuesto", "Aceite, un litro", 1, 32000),
        ItemCobro("mano de obra", "Mano de obra", 1, 35000),
    ]
    for item in items:
        resumen = registrar_item(orden_48271936, item, mecanico_asignado)
    assert resumen == ResumenCobro(50000, 35000, 85000)
    assert orden_48271936.items == items


def test_hu07_escenario_2_repuesto_sin_precio(orden_48271936, mecanico_asignado):
    # Dado que agrego el repuesto "pastillas de freno" sin escribir el precio,
    # cuando intento guardarlo, entonces el sistema no lo agrega y muestra
    # "Escriba el precio del repuesto".
    pastillas = ItemCobro("repuesto", "Pastillas de freno", 1, None)
    with pytest.raises(ValueError, match="^Escriba el precio del repuesto$"):
        registrar_item(orden_48271936, pastillas, mecanico_asignado)
    assert orden_48271936.items == []


def test_hu08_escenario_1_detalle_del_cobro_en_parte():
    # Dado que la orden tiene repuestos por 50.000 y mano de obra por 35.000,
    # cuando se genera el detalle, entonces muestra el filtro por 18.000, el aceite
    # por 32.000, la mano de obra por 35.000 y el total de 85.000.
    # En parte: la página genera el detalle, pero aún no existen los estados de la
    # orden, así que no se comprueba que esté "Lista para entregar".
    formulario = {
        "tipo_1": ["repuesto"],
        "descripcion_1": ["Filtro de aceite"],
        "cantidad_1": ["1"],
        "precio_1": ["18000"],
        "tipo_2": ["repuesto"],
        "descripcion_2": ["Aceite, un litro"],
        "cantidad_2": ["1"],
        "precio_2": ["32000"],
        "tipo_3": ["mano de obra"],
        "descripcion_3": ["Mano de obra"],
        "cantidad_3": ["1"],
        "precio_3": ["35000"],
    }
    codigo, pagina = procesar_cobro(formulario)
    assert codigo == 200
    for descripcion, valor in [
        ("Filtro de aceite", "18.000"),
        ("Aceite, un litro", "32.000"),
        ("Mano de obra", "35.000"),
    ]:
        fila = re.search(rf"<tr><td>{re.escape(descripcion)}</td>.*?</tr>", pagina)
        assert fila is not None, descripcion
        assert f'<td class="num">$ {valor}</td>' in fila.group(0)
    assert '<th colspan="4">Total sin IVA</th><td class="num">$ 85.000</td>' in pagina
