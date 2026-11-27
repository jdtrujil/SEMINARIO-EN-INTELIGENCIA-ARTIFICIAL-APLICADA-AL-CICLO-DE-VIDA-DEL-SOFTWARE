"""Prueba que falla a propósito para comprobar que el pipeline sale en rojo.

Solo vive en la rama temporal prueba-pipeline-rojo (semana 9); no se integra.
"""
from app.cobros.calculo import ItemCobro, calcular_cobro


def test_total_con_iva_falla_a_proposito():
    resumen = calcular_cobro([ItemCobro("repuesto", "Filtro de aceite", 1, 18000)])
    assert resumen.total == 21420  # 18.000 con IVA; el taller no cobra IVA
