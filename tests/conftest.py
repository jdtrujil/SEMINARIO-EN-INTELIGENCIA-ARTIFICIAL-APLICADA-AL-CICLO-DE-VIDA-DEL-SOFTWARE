"""Fixtures compartidas por las pruebas de pytest (semana 7 y entrega final)."""
import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from app.cobros.modelos import ROL_MECANICO, ROL_REGISTRADOR, ItemCobro, Trabajador
from app.ordenes.modelos import HORA_COLOMBIA, Mecanico
from app.ordenes.repositorio import abrir

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


# --- Base de datos de las órdenes (entrega final) ---------------------------

MECANICOS_PRUEBA = (Mecanico(1, "Mecánico 1"), Mecanico(2, "Mecánico 2"))
# Con TALLER_PG_PRUEBAS (en el pipeline) las pruebas de órdenes corren también
# contra PostgreSQL 16; sin ella, solo contra SQLite.
DESTINOS = ["sqlite"] + (["postgres"] if os.environ.get("TALLER_PG_PRUEBAS") else [])


@pytest.fixture(autouse=True)
def base_temporal(monkeypatch, tmp_path):
    """Cada prueba usa su propio archivo SQLite y nunca la base real del taller."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("TALLER_MECANICOS", raising=False)
    monkeypatch.setenv("TALLER_BD_ARCHIVO", str(tmp_path / "servidor.db"))


@pytest.fixture(params=DESTINOS)
def destino_bd(request, tmp_path):
    """Base vacía con las tablas creadas y los dos mecánicos de prueba."""
    if request.param == "postgres":
        destino = os.environ["TALLER_PG_PRUEBAS"]
        with abrir(destino) as repo:
            repo.eliminar_tablas()
    else:
        destino = str(tmp_path / "taller.db")
    with abrir(destino) as repo:
        repo.crear_tablas()
        repo.guardar_mecanicos(MECANICOS_PRUEBA)
    return destino


@pytest.fixture
def repo(destino_bd):
    """Repositorio abierto sobre la base de prueba; confirma al terminar."""
    with abrir(destino_bd) as repositorio:
        yield repositorio


@pytest.fixture
def fecha_ingreso():
    """26 de noviembre de 2026 a las 8:15 de la mañana, hora de Colombia."""
    return datetime(2026, 11, 26, 8, 15, tzinfo=HORA_COLOMBIA)
