"""Pruebas de validar_placa por particiones y valores límite (HU-01)."""
import pytest

from app.ingresos.placas import validar_placa


@pytest.mark.parametrize(
    "placa, esperada",
    [
        ("ABC12D", "ABC12D"),  # V1 formato actual
        ("MOT09", "MOT09"),  # V2 formato antiguo
        ("abc12d", "ABC12D"),  # V3 minúsculas
        (" QWE45R ", "QWE45R"),  # V4 espacios a los lados
        ("ABC12", "ABC12"),  # L4 longitud 5
        ("ABC12D", "ABC12D"),  # L5 longitud 6
    ],
)
def test_placas_validas(placa, esperada):
    assert validar_placa(placa) == esperada


@pytest.mark.parametrize(
    "placa",
    ["", "   ", "ABC123", "12ABCD", "ABC-12D", "ABC 12D", "ÑAB12C",
     "ABC1", "ABC12DE", "ABC1D", "AB12C"],
)
def test_placas_invalidas(placa):
    with pytest.raises(ValueError):
        validar_placa(placa)


def test_placa_none():
    with pytest.raises(ValueError):
        validar_placa(None)


def test_placas_sinteticas(motos_sinteticas):
    for moto in motos_sinteticas:
        if moto["placa_esperada"] is not None:
            assert validar_placa(moto["placa"])
