"""Pruebas nuevas de la semana 6 (hallazgo H-03).

La revisión encontró que calcular_cobro aceptaba precios con decimales,
cantidades como True y precios como texto. El contrato dice que los valores
son pesos enteros, así que ahora esos casos lanzan ValueError.
"""
import unittest

from app.cobros.calculo import ItemCobro, calcular_cobro


class TiposDeDatosInvalidos(unittest.TestCase):

    def assert_rechaza(self, item, mensaje):
        with self.assertRaises(ValueError) as error:
            calcular_cobro([item])
        self.assertEqual(str(error.exception), mensaje)

    def test_precio_con_decimales_se_rechaza(self):
        item = ItemCobro("repuesto", "Filtro de aceite", 1, 18000.5)
        self.assert_rechaza(item, "El precio debe ser un número entero de pesos")

    def test_precio_escrito_como_texto_se_rechaza_con_value_error(self):
        item = ItemCobro("repuesto", "Filtro de aceite", 1, "18000")
        self.assert_rechaza(item, "El precio debe ser un número entero de pesos")

    def test_cantidad_true_no_cuenta_como_una_unidad(self):
        item = ItemCobro("repuesto", "Filtro de aceite", True, 18000)
        self.assert_rechaza(item, "La cantidad debe ser un número entero")

    def test_cantidad_con_decimales_se_rechaza(self):
        item = ItemCobro("repuesto", "Aceite, un litro", 1.5, 32000)
        self.assert_rechaza(item, "La cantidad debe ser un número entero")


if __name__ == "__main__":
    unittest.main()
