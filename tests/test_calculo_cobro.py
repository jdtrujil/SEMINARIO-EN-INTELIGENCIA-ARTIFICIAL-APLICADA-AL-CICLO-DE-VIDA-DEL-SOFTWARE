"""Pruebas de la HU-07: cálculo del cobro de una orden, sin IVA.

Se escribieron antes de la implementación. Usan unittest, así que corren
con `python -m unittest discover -v` y también con `python -m pytest -v`.
"""
import unittest

from app.cobros.calculo import ItemCobro, ResumenCobro, calcular_cobro

# Datos del escenario 1 de la HU-07 (orden 48271936)
FILTRO = ItemCobro("repuesto", "Filtro de aceite", 1, 18000)
ACEITE = ItemCobro("repuesto", "Aceite, un litro", 1, 32000)
MANO_DE_OBRA = ItemCobro("mano de obra", "Cambio de aceite y revisión del motor", 1, 35000)


class CasosNormales(unittest.TestCase):

    def test_orden_con_repuestos_y_mano_de_obra_da_85000_sin_iva(self):
        resumen = calcular_cobro([FILTRO, ACEITE, MANO_DE_OBRA])

        self.assertEqual(resumen, ResumenCobro(total_repuestos=50000, total_mano_obra=35000, total=85000))

    def test_cantidad_mayor_a_uno_multiplica_el_precio_unitario(self):
        dos_litros = ItemCobro("repuesto", "Aceite, un litro", 2, 32000)

        resumen = calcular_cobro([dos_litros, MANO_DE_OBRA])

        self.assertEqual(resumen, ResumenCobro(total_repuestos=64000, total_mano_obra=35000, total=99000))


class CasosLimite(unittest.TestCase):

    def test_orden_sin_items_da_cero_en_todos_los_totales(self):
        self.assertEqual(calcular_cobro([]), ResumenCobro(total_repuestos=0, total_mano_obra=0, total=0))

    def test_orden_solo_con_mano_de_obra_deja_repuestos_en_cero(self):
        resumen = calcular_cobro([MANO_DE_OBRA])

        self.assertEqual(resumen, ResumenCobro(total_repuestos=0, total_mano_obra=35000, total=35000))

    def test_precio_cero_se_acepta_y_no_suma(self):
        repuesto_del_cliente = ItemCobro("repuesto", "Llanta que trajo el cliente", 1, 0)

        resumen = calcular_cobro([repuesto_del_cliente, MANO_DE_OBRA])

        self.assertEqual(resumen, ResumenCobro(total_repuestos=0, total_mano_obra=35000, total=35000))


class CasosDeError(unittest.TestCase):

    def test_repuesto_sin_precio_muestra_el_mensaje_de_la_historia(self):
        pastillas = ItemCobro("repuesto", "Pastillas de freno", 1, None)

        with self.assertRaises(ValueError) as error:
            calcular_cobro([FILTRO, pastillas])

        self.assertEqual(str(error.exception), "Escriba el precio del repuesto")

    def test_mano_de_obra_sin_valor_lanza_error(self):
        sin_valor = ItemCobro("mano de obra", "Ajuste de frenos", 1, None)

        with self.assertRaises(ValueError) as error:
            calcular_cobro([sin_valor])

        self.assertEqual(str(error.exception), "Escriba el valor de la mano de obra")

    def test_precio_negativo_lanza_error(self):
        negativo = ItemCobro("repuesto", "Filtro de aire", 1, -5000)

        with self.assertRaises(ValueError) as error:
            calcular_cobro([negativo])

        self.assertEqual(str(error.exception), "El precio no puede ser negativo")

    def test_cantidad_cero_lanza_error(self):
        sin_unidades = ItemCobro("repuesto", "Bujía", 0, 12000)

        with self.assertRaises(ValueError) as error:
            calcular_cobro([sin_unidades])

        self.assertEqual(str(error.exception), "La cantidad debe ser al menos 1")

    def test_tipo_desconocido_lanza_error(self):
        lavado = ItemCobro("servicio", "Lavado", 1, 10000)

        with self.assertRaises(ValueError) as error:
            calcular_cobro([lavado])

        self.assertEqual(str(error.exception), "Tipo de ítem no válido: servicio. Use repuesto o mano de obra")


if __name__ == "__main__":
    unittest.main()
