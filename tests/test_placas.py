"""Pruebas de validar_placa por particiones y valores límite (HU-01).

Cada fila dice de qué partición (V válida, I inválida) o límite (L) de
registro_pruebas.md sale.
"""
import re

import pytest

from app.ingresos.placas import validar_placa

FORMATO = "Placa no válida: use el formato ABC12D o, si es antigua, ABC12"
NO_ES_TEXTO = "La placa debe ser texto"


@pytest.mark.parametrize(
    "placa, esperada",
    [
        ("ABC12D", "ABC12D"),  # V1, L5, L6 y L7: formato actual, 6 caracteres
        ("MOT09", "MOT09"),  # V2, L4 y L8: formato antiguo, 5 caracteres
        ("abc12d", "ABC12D"),  # V3: minúsculas se convierten (A1)
        (" QWE45R ", "QWE45R"),  # V4: se quitan los espacios a los lados (A2)
    ],
)
def test_placa_valida_se_devuelve_normalizada(placa, esperada):
    assert validar_placa(placa) == esperada


@pytest.mark.parametrize(
    "placa",
    [
        "",  # I1 vacía
        "   ",  # I2 solo espacios
        "ABC123",  # I3 y L7: formato de carro, tres números
        "12ABCD",  # I4 números antes de las letras
        "ABC-12D",  # I5 guion en medio (A2)
        "ABC 12D",  # I5 espacio en medio (A2)
        "ÑAB12C",  # I6 letra Ñ (A3)
        "ABC1",  # L4: 4 caracteres
        "ABC12DE",  # L5: 7 caracteres
        "ABC1D",  # L6: un solo número
        "AB12C",  # L8: dos letras iniciales
    ],
)
def test_placa_con_formato_invalido_lanza_value_error(placa):
    with pytest.raises(ValueError, match=f"^{re.escape(FORMATO)}$"):
        validar_placa(placa)


@pytest.mark.parametrize(
    "placa",
    [
        None,  # I7 sin placa
        12345,  # I7 número en lugar de texto
    ],
)
def test_placa_que_no_es_texto_lanza_value_error(placa):
    with pytest.raises(ValueError, match=f"^{re.escape(NO_ES_TEXTO)}$"):
        validar_placa(placa)


def test_placas_sinteticas_validas_se_normalizan(motos_sinteticas):
    validas = [moto for moto in motos_sinteticas if moto["placa_esperada"]]
    assert [validar_placa(moto["placa"]) for moto in validas] == [
        "BJX27F",  # V1
        "AKT45M",  # V3 minúsculas
        "HND08",  # V2 y V4 antigua con espacios
    ]


def test_placas_sinteticas_invalidas_se_rechazan(motos_sinteticas):
    invalidas = [
        moto["placa"] for moto in motos_sinteticas if not moto["placa_esperada"]
    ]
    assert invalidas == ["YMH-34K", "ÑKY12C", ""]  # I5, I6 e I1
    for placa in invalidas:
        with pytest.raises(ValueError, match=f"^{re.escape(FORMATO)}$"):
            validar_placa(placa)
