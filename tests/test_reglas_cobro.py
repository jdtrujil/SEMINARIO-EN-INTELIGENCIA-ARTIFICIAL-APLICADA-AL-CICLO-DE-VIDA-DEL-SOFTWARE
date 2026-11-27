"""Pruebas de calcular_cobro por particiones y valores límite (HU-07).

Cada fila dice de qué partición (P) o límite (L) de registro_pruebas.md sale.
Los esperados se calcularon a mano a partir de la regla, no ejecutando el código.
"""
import re

import pytest

from app.cobros.calculo import ItemCobro, ResumenCobro, calcular_cobro


def item(tipo="repuesto", cantidad=1, precio=18000, descripcion="Filtro de aceite"):
    """Crea un ítem de cobro con valores válidos que cada caso cambia."""
    return ItemCobro(tipo, descripcion, cantidad, precio)


@pytest.mark.parametrize(
    "items, esperado",
    [
        ([], ResumenCobro(0, 0, 0)),  # P1 lista vacía: no se cobra nada
        ([item()], ResumenCobro(18000, 0, 18000)),  # P2 y L3: un repuesto, cantidad 1
        (
            [item("mano de obra", precio=35000, descripcion="Cambio de aceite")],
            ResumenCobro(0, 35000, 35000),
        ),  # P3 solo mano de obra
        (
            [
                item(),
                item(precio=32000, descripcion="Aceite, un litro"),
                item("mano de obra", precio=35000, descripcion="Cambio de aceite"),
            ],
            ResumenCobro(50000, 35000, 85000),
        ),  # P4 escenario 1 de la HU-07: 18.000 + 32.000 y 35.000, sin IVA
        (
            [item(cantidad=2, precio=32000, descripcion="Aceite, un litro")],
            ResumenCobro(64000, 0, 64000),
        ),  # P15 dos litros a 32.000
        ([item(precio=0)], ResumenCobro(0, 0, 0)),  # P10 y L1: precio cero, no suma
        ([item(precio=1)], ResumenCobro(1, 0, 1)),  # L2 primer precio positivo
    ],
)
def test_calcula_los_totales_sin_iva(items, esperado):
    assert calcular_cobro(items) == esperado


@pytest.mark.parametrize(
    "item_invalido, mensaje",
    [
        (
            item("servicio"),
            "Tipo de ítem no válido: servicio. Use repuesto o mano de obra",
        ),  # P5 tipo distinto
        (
            item("Repuesto"),
            "Tipo de ítem no válido: Repuesto. Use repuesto o mano de obra",
        ),  # P6 tipo con mayúscula
        (item(precio=None), "Escriba el precio del repuesto"),  # P7
        (
            item("mano de obra", precio=None),
            "Escriba el valor de la mano de obra",
        ),  # P8
        (item(precio=-1), "El precio no puede ser negativo"),  # P9 y L1: -1
        (
            item(precio=18000.5),
            "El precio debe ser un número entero de pesos",
        ),  # P12 precio con decimales
        (
            item(precio="18000"),
            "El precio debe ser un número entero de pesos",
        ),  # P13 precio en texto
        (
            item(precio=18000.0),
            "El precio debe ser un número entero de pesos",
        ),  # P18 decimal con parte decimal cero (caso agregado por la mutación M5)
        (item(cantidad=0), "La cantidad debe ser al menos 1"),  # P14 y L3: cero
        (item(cantidad=1.5), "La cantidad debe ser un número entero"),  # P16
        (item(cantidad=True), "La cantidad debe ser un número entero"),  # P17
        (
            item(cantidad=2.0),
            "La cantidad debe ser un número entero",
        ),  # P19 cantidad 2.0 (caso agregado por la mutación M5)
    ],
)
def test_item_invalido_lanza_value_error_con_su_mensaje(item_invalido, mensaje):
    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        calcular_cobro([item_invalido])


def test_orden_con_datos_sinteticos_suma_a_mano(items_sinteticos):
    # Repuestos: 38.000 + 15.000 + 142.000 + 0 = 195.000
    # Mano de obra: 45.000 + 20.000 = 65.000. Total sin IVA: 260.000
    # Las descripciones tienen tildes, ñ, apóstrofo y una vacía (ambigüedad A5).
    assert calcular_cobro(items_sinteticos) == ResumenCobro(195000, 65000, 260000)
