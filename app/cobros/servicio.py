"""Operaciones del módulo de cobros que verifican permisos (HU-07, H-05)."""
from __future__ import annotations

from app.cobros.calculo import calcular_cobro
from app.cobros.errores import AccesoDenegado
from app.cobros.modelos import (
    ROL_MECANICO,
    ItemCobro,
    Orden,
    ResumenCobro,
    Trabajador,
)


def registrar_item(
    orden: Orden, item: ItemCobro, trabajador: Trabajador
) -> ResumenCobro:
    """Registra un repuesto o mano de obra en la orden y devuelve los nuevos totales.

    Solo el mecánico asignado a la orden puede registrar cobros. Primero se
    verifica el permiso y después el ítem, y la orden solo cambia si las dos
    verificaciones pasan.

    Parámetros:
        orden: orden de servicio a la que se agrega el ítem.
        item: repuesto o mano de obra que se quiere registrar.
        trabajador: quien hace la operación.

    Devuelve:
        ResumenCobro con los totales de la orden incluido el ítem nuevo, sin IVA.

    Lanza:
        AccesoDenegado: si el trabajador no es mecánico o la orden no está
            asignada a él.
        ValueError: si el ítem no es válido (ver calcular_cobro).
    """
    _verificar_permiso_de_cobro(orden, trabajador)
    resumen = calcular_cobro([*orden.items, item])
    orden.items.append(item)
    return resumen


def _verificar_permiso_de_cobro(orden: Orden, trabajador: Trabajador) -> None:
    """Lanza AccesoDenegado si el trabajador no puede registrar cobros en la orden."""
    if trabajador.rol != ROL_MECANICO:
        raise AccesoDenegado("Solo un mecánico puede registrar cobros")
    if orden.mecanico_id != trabajador.id:
        raise AccesoDenegado("Esta orden no está asignada a usted")
