"""Fixtures compartidas por las pruebas de pytest de la semana 7."""
import json
from pathlib import Path

import pytest

from app.cobros.modelos import ROL_MECANICO, ROL_REGISTRADOR, ItemCobro, Trabajador

ARCHIVO_DATOS = Path(__file__).parent / "datos" / "datos_sinteticos.json"


@pytest.fixture(scope="session")
def datos_sinteticos():
    """Datos sintéticos del taller (ver registro_pruebas.md, sección 4)."""
    with ARCHIVO_DATOS.open(encoding="utf-8") as archivo:
        return json.load(archivo)


@pytest.fixture
def items_sinteticos(datos_sinteticos):
    """Ítems de una orden sintética con tildes, ñ, apóstrofo, texto vacío y precio 0."""
    return [ItemCobro(**item) for item in datos_sinteticos["items_orden"]]


@pytest.fixture
def motos_sinteticas(datos_sinteticos):
    """Motos sintéticas con placas válidas, en minúsculas, con espacios e inválidas."""
    return datos_sinteticos["motos"]


@pytest.fixture
def mecanico_1():
    """Mecánico con id 1, el asignado en la mayoría de las órdenes de prueba."""
    return Trabajador(id=1, rol=ROL_MECANICO)


@pytest.fixture
def registrador():
    """Registrador con id 3."""
    return Trabajador(id=3, rol=ROL_REGISTRADOR)
