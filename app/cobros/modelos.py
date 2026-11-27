"""Datos del módulo de cobros: ítems, totales, trabajadores y órdenes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Tipos de ítem que se le pueden cobrar al cliente (HU-07)
REPUESTO = "repuesto"
MANO_DE_OBRA = "mano de obra"
TIPOS_VALIDOS = (REPUESTO, MANO_DE_OBRA)

# Roles de los trabajadores que usan el sistema (actores de la semana 3)
ROL_REGISTRADOR = "registrador"
ROL_MECANICO = "mecanico"


@dataclass(frozen=True)
class ItemCobro:
    """Un repuesto o un trabajo de mano de obra registrado en una orden.

    Atributos:
        tipo: "repuesto" o "mano de obra".
        descripcion: nombre del repuesto o del trabajo.
        cantidad: unidades, mínimo 1.
        precio_unitario: pesos enteros, o None si todavía no se escribió.
    """

    tipo: str
    descripcion: str
    cantidad: int
    precio_unitario: Optional[int]


@dataclass(frozen=True)
class ResumenCobro:
    """Totales de una orden, en pesos enteros y sin IVA."""

    total_repuestos: int
    total_mano_obra: int
    total: int


@dataclass(frozen=True)
class Trabajador:
    """Persona del taller que usa el sistema.

    Atributos:
        id: identificador del trabajador.
        rol: ROL_REGISTRADOR o ROL_MECANICO.
    """

    id: int
    rol: str


@dataclass
class Orden:
    """Orden de servicio con el mecánico asignado y los ítems ya registrados.

    Atributos:
        numero: número de orden de ocho dígitos que recibe el cliente.
        mecanico_id: id del mecánico asignado, o None si aún no tiene.
        items: ítems de cobro registrados hasta ahora.
    """

    numero: str
    mecanico_id: Optional[int]
    items: List[ItemCobro] = field(default_factory=list)
