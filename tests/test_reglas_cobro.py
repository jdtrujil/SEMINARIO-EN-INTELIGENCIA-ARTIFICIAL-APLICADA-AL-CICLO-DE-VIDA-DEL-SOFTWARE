"""Pruebas de calcular_cobro por particiones y valores límite (HU-07)."""
import pytest

from app.cobros.calculo import ItemCobro, ResumenCobro, calcular_cobro


def item(tipo="repuesto", cantidad=1, precio=18000, descripcion="Filtro de aceite"):
    return ItemCobro(tipo, descripcion, cantidad, precio)


@pytest.mark.parametrize(
    "items, esperado",
    [
        ([], ResumenCobro(0, 0, 0)),  # P1 lista vacía
        ([item()], ResumenCobro(18000, 0, 18000)),  # P2 solo repuestos
        ([item("mano de obra", precio=35000)], ResumenCobro(0, 35000, 35000)),  # P3
        (
            [item(), item(precio=32000), item("mano de obra", precio=35000)],
            ResumenCobro(50000, 35000, 85000),
        ),  # P4 escenario 1 de la HU-07
        ([item(cantidad=2, precio=32000)], ResumenCobro(64000, 0, 64000)),  # P15
        ([item(precio=0)], ResumenCobro(0, 0, 0)),  # P10 precio cero
        ([item(precio=0)], ResumenCobro(0, 0, 0)),  # L1 primer valor no negativo
        ([item(precio=1)], ResumenCobro(1, 0, 1)),  # L2 primer precio positivo
        ([item(cantidad=1)], ResumenCobro(18000, 0, 18000)),  # L3 cantidad mínima
    ],
)
def test_calcula_totales_sin_iva(items, esperado):
    assert calcular_cobro(items) == esperado


def test_total_es_la_suma_de_los_subtotales():
    resumen = calcular_cobro([item(), item("mano de obra", precio=35000)])
    assert resumen.total == resumen.total_repuestos + resumen.total_mano_obra


@pytest.mark.parametrize(
    "item_invalido",
    [
        item("servicio"),  # P5 tipo distinto
        item("Repuesto"),  # P6 tipo con mayúscula
        item(precio=None),  # P7 repuesto sin precio
        item("mano de obra", precio=None),  # P8 mano de obra sin valor
        item(precio=-5000),  # P9 precio negativo
        item(precio=-1),  # L1 último precio negativo
        item(precio=18000.5),  # P12 precio con decimales
        item(precio="18000"),  # P13 precio en texto
        item(cantidad=0),  # P14 y L3 cantidad cero
        item(cantidad=-1),  # P14 cantidad negativa
        item(cantidad=1.5),  # P16 cantidad con decimales
        item(cantidad=True),  # P17 cantidad booleana
    ],
)
def test_items_invalidos_lanzan_error(item_invalido):
    with pytest.raises(Exception):
        calcular_cobro([item_invalido])


def test_orden_con_datos_sinteticos(items_sinteticos):
    resumen = calcular_cobro(items_sinteticos)
    assert resumen.total == resumen.total_repuestos + resumen.total_mano_obra
