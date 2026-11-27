"""Pruebas nuevas de la semana 6 (hallazgo H-05): control de acceso.

La HU-07 dice "Como mecánico, quiero registrar los repuestos...", y el
documento de diseño responde 403 si el mecánico no tiene asignada la orden.
Solo el mecánico asignado puede registrar cobros. Las pruebas de abuso
comprueban que nadie más puede hacerlo y que la orden no cambia.
"""
import unittest

from app.cobros.errores import AccesoDenegado
from app.cobros.modelos import (
    ROL_MECANICO,
    ROL_REGISTRADOR,
    ItemCobro,
    Orden,
    ResumenCobro,
    Trabajador,
)
from app.cobros.servicio import registrar_item

MECANICO_1 = Trabajador(id=1, rol=ROL_MECANICO)
MECANICO_2 = Trabajador(id=2, rol=ROL_MECANICO)
REGISTRADOR = Trabajador(id=3, rol=ROL_REGISTRADOR)
FILTRO = ItemCobro("repuesto", "Filtro de aceite", 1, 18000)


class MecanicoAsignado(unittest.TestCase):

    def test_registra_el_item_y_devuelve_el_total(self):
        orden = Orden(numero="48271936", mecanico_id=MECANICO_1.id)

        resumen = registrar_item(orden, FILTRO, MECANICO_1)

        self.assertEqual(resumen, ResumenCobro(18000, 0, 18000))
        self.assertEqual(orden.items, [FILTRO])

    def test_item_invalido_no_se_agrega_a_la_orden(self):
        orden = Orden(numero="48271936", mecanico_id=MECANICO_1.id)
        sin_precio = ItemCobro("repuesto", "Pastillas de freno", 1, None)

        with self.assertRaises(ValueError):
            registrar_item(orden, sin_precio, MECANICO_1)
        self.assertEqual(orden.items, [])


class PruebasDeAbuso(unittest.TestCase):

    def test_registrador_no_puede_registrar_cobros(self):
        orden = Orden(numero="48271936", mecanico_id=MECANICO_1.id)

        with self.assertRaises(AccesoDenegado) as error:
            registrar_item(orden, FILTRO, REGISTRADOR)

        mensaje = "Solo un mecánico puede registrar cobros"
        self.assertEqual(str(error.exception), mensaje)
        self.assertEqual(orden.items, [])

    def test_mecanico_no_asignado_no_puede_registrar_en_orden_ajena(self):
        orden = Orden(numero="48271936", mecanico_id=MECANICO_1.id)

        with self.assertRaises(AccesoDenegado) as error:
            registrar_item(orden, FILTRO, MECANICO_2)

        self.assertEqual(str(error.exception), "Esta orden no está asignada a usted")
        self.assertEqual(orden.items, [])

    def test_nadie_registra_cobros_en_una_orden_sin_mecanico(self):
        orden = Orden(numero="48271936", mecanico_id=None)

        with self.assertRaises(AccesoDenegado):
            registrar_item(orden, FILTRO, MECANICO_1)
        self.assertEqual(orden.items, [])

    def test_acceso_denegado_es_un_error_de_permisos(self):
        self.assertTrue(issubclass(AccesoDenegado, PermissionError))


if __name__ == "__main__":
    unittest.main()
