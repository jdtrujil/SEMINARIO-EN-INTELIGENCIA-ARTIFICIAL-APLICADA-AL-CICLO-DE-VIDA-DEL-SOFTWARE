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
    """Suma los repuestos y la mano de obra de una orden, sin IVA.

    Lanza ValueError si un ítem no tiene precio, tiene precio negativo,
    cantidad menor que 1 o un tipo distinto de repuesto o mano de obra.
    """
    total_repuestos = 0
    total_mano_obra = 0
    for item in items:
        if item.tipo not in ("repuesto", "mano de obra"):
            raise ValueError(f"Tipo de ítem no válido: {item.tipo}. Use repuesto o mano de obra")
        if item.precio_unitario is None:
            if item.tipo == "repuesto":
                raise ValueError("Escriba el precio del repuesto")
            raise ValueError("Escriba el valor de la mano de obra")
        if item.precio_unitario < 0:
            raise ValueError("El precio no puede ser negativo")
        if item.cantidad < 1:
            raise ValueError("La cantidad debe ser al menos 1")
        if item.tipo == "repuesto":
            total_repuestos += item.cantidad * item.precio_unitario
        else:
            total_mano_obra += item.cantidad * item.precio_unitario
    return ResumenCobro(total_repuestos, total_mano_obra, total_repuestos + total_mano_obra)
