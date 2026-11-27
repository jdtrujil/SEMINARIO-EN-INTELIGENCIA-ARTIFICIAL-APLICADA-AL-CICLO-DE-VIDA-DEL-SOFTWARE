"""Etapas y datos de una orden del taller.

Las etapas las definió el cliente el 2026-11-27: Recibida, En reparación y
Terminada (antes "Lista para entregar" en las historias de la semana 3).
Se guardan la fecha y hora de ingreso, la placa, las observaciones, el
mecánico, el historial de etapas y la factura. No se guardan datos personales
del cliente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from app.cobros.calculo import ItemCobro, ResumenCobro

RECIBIDA = "Recibida"
EN_REPARACION = "En reparación"
TERMINADA = "Terminada"
ETAPAS = (RECIBIDA, EN_REPARACION, TERMINADA)
# Cada etapa solo puede pasar a la siguiente.
SIGUIENTE = {RECIBIDA: EN_REPARACION, EN_REPARACION: TERMINADA}

# Colombia no tiene horario de verano: UTC-5 todo el año. Se usa un desfase fijo
# porque en Windows zoneinfo necesita un paquete extra.
HORA_COLOMBIA = timezone(timedelta(hours=-5), "COT")


def ahora() -> datetime:
    """Fecha y hora actuales en Colombia, sin microsegundos."""
    return datetime.now(HORA_COLOMBIA).replace(microsecond=0)


@dataclass(frozen=True)
class Mecanico:
    """Mecánico del taller. Los nombres se configuran en cada equipo."""

    id: int
    nombre: str


@dataclass(frozen=True)
class CambioDeEtapa:
    """Una línea del historial: a qué etapa pasó la moto y cuándo."""

    etapa: str
    fecha_hora: datetime


@dataclass
class OrdenTaller:
    """Una moto en el taller, desde el ingreso hasta la factura."""

    numero: str
    placa: str
    observaciones: str
    mecanico_id: int
    etapa: str
    fecha_ingreso: datetime
    items: List[ItemCobro] = field(default_factory=list)
    historial: List[CambioDeEtapa] = field(default_factory=list)
    factura: Optional[ResumenCobro] = None


@dataclass(frozen=True)
class ConsultaCliente:
    """Lo que ve el cliente con su número: nunca la placa ni otros datos."""

    numero: str
    etapa: str
    actualizada: datetime
    items: Tuple[ItemCobro, ...] = ()
    factura: Optional[ResumenCobro] = None
