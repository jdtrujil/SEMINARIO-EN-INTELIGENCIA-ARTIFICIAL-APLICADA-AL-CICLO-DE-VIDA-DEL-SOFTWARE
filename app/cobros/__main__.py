"""Ejemplo ejecutable del módulo de cobros: python -m app.cobros

Registra los ítems del escenario 1 de la HU-07 en la orden 48271936 con el
mecánico asignado y muestra el cobro. Después muestra que otro mecánico no
puede registrar cobros en esa orden.
"""
from app.cobros.errores import AccesoDenegado
from app.cobros.formato import pesos
from app.cobros.modelos import ROL_MECANICO, ItemCobro, Orden, Trabajador
from app.cobros.servicio import registrar_item


def main() -> None:
    """Corre el ejemplo de la HU-07 e imprime el resultado."""
    mecanico_1 = Trabajador(id=1, rol=ROL_MECANICO)
    mecanico_2 = Trabajador(id=2, rol=ROL_MECANICO)
    orden = Orden(numero="48271936", mecanico_id=mecanico_1.id)

    items = [
        ItemCobro("repuesto", "Filtro de aceite", 1, 18000),
        ItemCobro("repuesto", "Aceite, un litro", 1, 32000),
        ItemCobro("mano de obra", "Cambio de aceite y revisión del motor", 1, 35000),
    ]
    for item in items:
        resumen = registrar_item(orden, item, mecanico_1)

    print(f"Orden {orden.numero}")
    for item in orden.items:
        precio = pesos(item.precio_unitario)
        print(f"  {item.descripcion:<40} {item.cantidad} x {precio}")
    print(f"Repuestos:      {pesos(resumen.total_repuestos):>8}")
    print(f"Mano de obra:   {pesos(resumen.total_mano_obra):>8}")
    print(f"Total sin IVA:  {pesos(resumen.total):>8}")

    try:
        registrar_item(orden, items[0], mecanico_2)
    except AccesoDenegado as error:
        print(f"Mecánico 2 en la misma orden: acceso denegado ({error})")


if __name__ == "__main__":
    main()
