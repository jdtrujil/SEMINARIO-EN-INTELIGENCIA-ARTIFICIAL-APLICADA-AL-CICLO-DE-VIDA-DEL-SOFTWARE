"""Datos del módulo de cobros: ítems y totales."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Tipos de ítem que se le pueden cobrar al cliente (HU-07)
REPUESTO = "repuesto"
MANO_DE_OBRA = "mano de obra"
TIPOS_VALIDOS = (REPUESTO, MANO_DE_OBRA)


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

