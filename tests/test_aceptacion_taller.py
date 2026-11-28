"""Pruebas de aceptación de los escenarios que se construyeron con la base de datos.

Datos y resultados de los criterios Gherkin de la semana 3. El 2026-11-27 el
cliente cambió las etapas a Recibida, En reparación y Terminada; "Lista para
entregar" de las historias corresponde a Terminada. Los escenarios marcados
"en parte" cumplen lo que la prueba comprueba y dicen qué les falta.
"""

from datetime import datetime, timedelta

import pytest

from app.cobros.calculo import ItemCobro, ResumenCobro
from app.ordenes import servicio
from app.ordenes.modelos import EN_REPARACION, HORA_COLOMBIA, RECIBIDA, TERMINADA

INGRESO = datetime(2026, 11, 26, 8, 15, tzinfo=HORA_COLOMBIA)
FILTRO = ItemCobro("repuesto", "Filtro de aceite", 1, 18000)
ACEITE = ItemCobro("repuesto", "Aceite, un litro", 1, 32000)
MANO = ItemCobro("mano de obra", "Mano de obra", 1, 35000)


def orden_48271936(repo, observaciones="Sin daños visibles"):
    return servicio.registrar_ingreso(
        repo, "ABC12D", observaciones, 1, INGRESO, lambda: "48271936"
    )


def en_reparacion_con(repo, *items):
    numero = orden_48271936(repo)
    servicio.avanzar_etapa(repo, numero, EN_REPARACION, INGRESO + timedelta(hours=1))
    for item in items:
        servicio.registrar_cobro(repo, numero, item, 1)
    return numero


def test_hu01_escenario_1_ingreso_en_parte(repo):
    # Dado que llega la moto de placa ABC12D, cuando guardo el ingreso con el motivo
    # "cambio de aceite y ruido en el motor al acelerar", entonces queda guardado con
    # la fecha y la hora y aparece en la lista de motos en el taller.
    # En parte: por decisión del cliente no se guardan los datos del dueño ni el
    # kilometraje.
    numero = orden_48271936(repo, "Cambio de aceite y ruido en el motor al acelerar")
    orden = repo.orden(numero)
    assert orden.fecha_ingreso == INGRESO
    assert [o.numero for o in repo.ordenes_recientes()] == ["48271936"]


def test_hu02_escenario_1_observacion_guardada_en_parte(repo):
    # Dado que la moto ABC12D llega con un rayón en el lado izquierdo del tanque, un
    # cuarto de tanque de gasolina y sin el espejo derecho, cuando guardo esa
    # observación, entonces queda en la orden con la fecha y la hora.
    # En parte: sin usuarios todavía, no se guarda el nombre del registrador.
    texto = (
        "Rayón en el lado izquierdo del tanque, un cuarto de tanque de gasolina "
        "y sin el espejo derecho"
    )
    orden = repo.orden(orden_48271936(repo, texto))
    assert orden.observaciones == texto
    assert orden.historial[0].fecha_hora == INGRESO


def test_hu02_escenario_2_observacion_vacia(repo):
    # Dado que dejo vacío el estado de llegada, cuando intento guardar el ingreso,
    # entonces el sistema no lo guarda y muestra el mensaje.
    with pytest.raises(
        ValueError,
        match="^Describa cómo llega la moto. "
        "Si no tiene daños, escriba sin daños visibles$",
    ):
        orden_48271936(repo, "")
    assert repo.ordenes_recientes() == []


def test_hu03_escenario_1_numero_generado(repo):
    # Cuando el registro termina, el sistema muestra un número de ocho dígitos que no
    # está repetido en ninguna otra orden.
    primero = servicio.registrar_ingreso(
        repo, "ABC12D", "Sin daños visibles", 1, INGRESO
    )
    segundo = servicio.registrar_ingreso(
        repo, "XYZ98E", "Sin daños visibles", 2, INGRESO
    )
    assert len(primero) == 8 and primero.isdigit()
    assert len(segundo) == 8 and segundo.isdigit()
    assert primero != segundo


def test_hu03_escenario_2_moto_con_orden_abierta(repo):
    # Dado que ABC12D ya tiene abierta la orden 48271936, cuando intento registrar un
    # nuevo ingreso con esa placa, entonces se muestra el mensaje y no hay otro número.
    orden_48271936(repo)
    with pytest.raises(
        ValueError, match="^Esta moto ya tiene una orden abierta: 48271936$"
    ):
        servicio.registrar_ingreso(repo, "ABC12D", "Otra vez", 1, INGRESO)
    assert len(repo.ordenes_recientes()) == 1


def test_hu04_escenario_1_moto_lista(repo):
    # Dado que la orden 48271936 está Terminada desde el 26 de noviembre de 2026 a las
    # 3:40 de la tarde, cuando escribo ese número en la consulta, entonces veo la etapa
    # y la fecha y hora de la última actualización.
    numero = en_reparacion_con(repo, MANO)
    terminada = datetime(2026, 11, 26, 15, 40, tzinfo=HORA_COLOMBIA)
    servicio.avanzar_etapa(repo, numero, TERMINADA, terminada)
    consulta = servicio.consultar(repo, "48271936")
    assert consulta.etapa == TERMINADA
    assert consulta.actualizada == terminada


def test_hu04_escenario_2_numero_que_no_existe(repo):
    orden_48271936(repo)
    with pytest.raises(
        servicio.OrdenNoEncontrada,
        match="^No encontramos una orden con ese número. "
        "Revise el papel que le entregó el registrador$",
    ):
        servicio.consultar(repo, "12345678")


def test_hu05_escenario_1_asignacion_en_parte(repo):
    # Cuando asigno la orden al Mecánico 1, aparece como suya.
    # En parte: el mecánico se elige al registrar; no hay lista de motos sin asignar.
    orden = repo.orden(orden_48271936(repo))
    assert orden.mecanico_id == 1


def test_hu06_escenario_1_moto_terminada(repo):
    # Dado que la orden está En reparación, tiene mano de obra y está asignada a mí,
    # cuando la marco como Terminada, entonces la etapa queda guardada con la fecha y
    # la hora y es la que ve el cliente.
    numero = en_reparacion_con(repo, MANO)
    fin = INGRESO + timedelta(hours=6)
    servicio.avanzar_etapa(repo, numero, TERMINADA, fin)
    assert repo.orden(numero).historial[-1].fecha_hora == fin
    assert servicio.consultar(repo, numero).etapa == TERMINADA


def test_hu06_escenario_2_falta_la_mano_de_obra(repo):
    numero = en_reparacion_con(repo, FILTRO)
    with pytest.raises(
        ValueError,
        match="^Registre la mano de obra antes de marcar la moto como terminada$",
    ):
        servicio.avanzar_etapa(repo, numero, TERMINADA, INGRESO)
    assert repo.orden(numero).etapa == EN_REPARACION


def test_hu07_escenario_1_total_sin_iva_guardado(repo):
    # Registro filtro de 18.000, aceite de 32.000 y mano de obra de 35.000; al guardar,
    # la orden muestra 50.000, 35.000 y 85.000 sin IVA, y queda en la base de datos.
    numero = en_reparacion_con(repo, FILTRO, ACEITE, MANO)
    servicio.avanzar_etapa(repo, numero, TERMINADA, INGRESO)
    assert repo.orden(numero).factura == ResumenCobro(50000, 35000, 85000)


def test_hu08_escenario_1_detalle_completo(repo):
    # Dado que la orden está Terminada con repuestos por 50.000 y mano de obra por
    # 35.000, el detalle tiene el filtro por 18.000, el aceite por 32.000, la mano de
    # obra por 35.000 y el total de 85.000.
    numero = en_reparacion_con(repo, FILTRO, ACEITE, MANO)
    servicio.avanzar_etapa(repo, numero, TERMINADA, INGRESO)
    orden = servicio.detalle_del_cobro(repo, numero)
    assert orden.items == [FILTRO, ACEITE, MANO]
    assert orden.factura.total == 85000


def test_hu08_escenario_2_moto_que_no_esta_lista(repo):
    numero = en_reparacion_con(repo, FILTRO, MANO)
    with pytest.raises(
        ValueError, match="^La moto todavía no está lista para entregar$"
    ):
        servicio.detalle_del_cobro(repo, numero)
    assert repo.orden(numero).etapa == EN_REPARACION
    assert repo.orden(numero).etapa != RECIBIDA
