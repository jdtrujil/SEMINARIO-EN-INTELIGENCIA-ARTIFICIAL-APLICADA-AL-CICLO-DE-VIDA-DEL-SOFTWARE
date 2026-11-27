"""Cálculo del cobro de una orden del taller (HU-07).

Al cliente se le cobra lo que se usó en repuestos más la mano de obra.
El taller no cobra IVA (necesidad N-06).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ItemCobro:
    """Un repuesto o un trabajo de mano de obra registrado en una orden."""

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


def calcular_cobro(items: list[ItemCobro]) -> ResumenCobro:
    """Pendiente: se implementa en el paso 3, después de las pruebas."""
    raise NotImplementedError("calcular_cobro todavía no está implementada")
