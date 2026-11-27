"""Cálculo del cobro de una orden del taller (HU-07).

Al cliente se le cobra lo que se usó en repuestos más la mano de obra.
El taller no cobra IVA (necesidad N-06).
"""
from __future__ import annotations

from typing import List

from app.cobros.modelos import (
    MANO_DE_OBRA,
    REPUESTO,
    TIPOS_VALIDOS,
    ItemCobro,
    ResumenCobro,
)

# Se reexportan para que el código existente pueda seguir importándolos desde aquí
__all__ = ["CANTIDAD_MINIMA", "ItemCobro", "ResumenCobro", "calcular_cobro"]

CANTIDAD_MINIMA = 1
MENSAJE_SIN_PRECIO = {
    REPUESTO: "Escriba el precio del repuesto",
    MANO_DE_OBRA: "Escriba el valor de la mano de obra",
}


def calcular_cobro(items: List[ItemCobro]) -> ResumenCobro:
    """Suma los repuestos y la mano de obra de una orden, sin IVA.

    Primero valida todos los ítems y después calcula, así una orden con un
    ítem inválido nunca produce un total a medias. No modifica la lista.

    Parámetros:
        items: ítems de la orden. Puede estar vacía.

    Devuelve:
        ResumenCobro con total_repuestos, total_mano_obra y total, en pesos
        enteros. El total nunca incluye IVA (N-06). Con la lista vacía, los
        tres totales son 0.

    Lanza:
        ValueError: si un ítem tiene un tipo distinto de repuesto o mano de
            obra, no tiene precio, su precio no es un entero o es negativo, o
            su cantidad no es un entero o es menor que CANTIDAD_MINIMA.
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
    """Comprueba un ítem en el orden del contrato y falla en la primera regla rota.

    Parámetros:
        item: ítem que se va a validar.

    Lanza:
        ValueError: con el mensaje que ve el usuario, por ejemplo
            "Escriba el precio del repuesto".
    """
    if item.tipo not in TIPOS_VALIDOS:
        raise ValueError(
            f"Tipo de ítem no válido: {item.tipo}. Use repuesto o mano de obra"
        )
    if item.precio_unitario is None:
        raise ValueError(MENSAJE_SIN_PRECIO[item.tipo])
    if not _es_entero(item.precio_unitario):
        raise ValueError("El precio debe ser un número entero de pesos")
    if item.precio_unitario < 0:
        raise ValueError("El precio no puede ser negativo")
    if not _es_entero(item.cantidad):
        raise ValueError("La cantidad debe ser un número entero")
    if item.cantidad < CANTIDAD_MINIMA:
        raise ValueError(f"La cantidad debe ser al menos {CANTIDAD_MINIMA}")


def _es_entero(valor: object) -> bool:
    """Indica si el valor es un int de verdad.

    True y False son int en Python, pero aquí no cuentan como cantidades ni
    precios (hallazgo H-03).

    Parámetros:
        valor: cualquier valor recibido en un ítem.

    Devuelve:
        True si es un int y no es un bool.
    """
    return isinstance(valor, int) and not isinstance(valor, bool)


def _subtotal_por_tipo(items: List[ItemCobro], tipo: str) -> int:
    """Suma cantidad por precio unitario de los ítems de un tipo.

    Parámetros:
        items: ítems ya validados con _validar_item.
        tipo: REPUESTO o MANO_DE_OBRA.

    Devuelve:
        La suma en pesos enteros, o 0 si no hay ítems de ese tipo.
    """
    return sum(
        item.cantidad * item.precio_unitario for item in items if item.tipo == tipo
    )
