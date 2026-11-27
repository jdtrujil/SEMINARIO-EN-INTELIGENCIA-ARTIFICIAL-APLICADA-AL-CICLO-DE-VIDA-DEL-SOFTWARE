"""Cálculo del cobro de una orden del taller (HU-07).

Al cliente se le cobra lo que se usó en repuestos más la mano de obra.
El taller no cobra IVA (necesidad N-06).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

REPUESTO = "repuesto"
MANO_DE_OBRA = "mano de obra"
TIPOS_VALIDOS = (REPUESTO, MANO_DE_OBRA)
CANTIDAD_MINIMA = 1
MENSAJE_SIN_PRECIO = {
    REPUESTO: "Escriba el precio del repuesto",
    MANO_DE_OBRA: "Escriba el valor de la mano de obra",
}


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

    Primero valida todos los ítems y después calcula, así una orden con un
    ítem inválido nunca produce un total a medias.
    """
    for item in items:
        _validar_item(item)

    total_repuestos = _subtotal_por_tipo(items, REPUESTO)
    total_mano_obra = _subtotal_por_tipo(items, MANO_DE_OBRA)
    return ResumenCobro(
        total_repuestos=total_repuestos,
        total_mano_obra=total_mano_obra,
        total=total_repuestos + total_mano_obra,
    )


def _validar_item(item: ItemCobro) -> None:
    """Lanza ValueError con el mensaje que ve el usuario si el ítem no es válido."""
    if item.tipo not in TIPOS_VALIDOS:
        raise ValueError(
            f"Tipo de ítem no válido: {item.tipo}. Use repuesto o mano de obra"
        )
    if item.precio_unitario is None:
        raise ValueError(MENSAJE_SIN_PRECIO[item.tipo])
    if item.precio_unitario < 0:
        raise ValueError("El precio no puede ser negativo")
    if item.cantidad < CANTIDAD_MINIMA:
        raise ValueError("La cantidad debe ser al menos 1")


def _subtotal_por_tipo(items: list[ItemCobro], tipo: str) -> int:
    """Suma cantidad por precio unitario de los ítems de un tipo."""
    return sum(
        item.cantidad * item.precio_unitario for item in items if item.tipo == tipo
    )
