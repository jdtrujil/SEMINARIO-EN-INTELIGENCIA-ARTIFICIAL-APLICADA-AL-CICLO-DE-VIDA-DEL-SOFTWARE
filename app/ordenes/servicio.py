"""Reglas de las órdenes: ingreso, etapas, cobro, factura y consulta del cliente.

Los mensajes de error son los de los criterios de aceptación de la semana 3
(docs/02_requisitos), con las etapas que definió el cliente el 2026-11-27.
"""

from __future__ import annotations

import re
import secrets
from datetime import datetime
from typing import Callable, Optional

from app.cobros.calculo import ItemCobro, ResumenCobro, calcular_cobro
from app.cobros.modelos import MANO_DE_OBRA, ROL_MECANICO, Orden, Trabajador
from app.cobros.servicio import registrar_item
from app.ingresos.placas import validar_placa
from app.ordenes.modelos import (
    EN_REPARACION,
    ETAPAS,
    SIGUIENTE,
    TERMINADA,
    ConsultaCliente,
    OrdenTaller,
)
from app.ordenes.repositorio import Repositorio

MENSAJE_OBSERVACIONES = (
    "Describa cómo llega la moto. Si no tiene daños, escriba sin daños visibles"
)
MENSAJE_SIN_MECANICO = "Elija el mecánico que va a tomar la moto"
MENSAJE_ORDEN_ABIERTA = "Esta moto ya tiene una orden abierta: {numero}"
MENSAJE_NO_EXISTE = (
    "No encontramos una orden con ese número. "
    "Revise el papel que le entregó el registrador"
)
MENSAJE_SIN_MANO_DE_OBRA = (
    "Registre la mano de obra antes de marcar la moto como terminada"
)
MENSAJE_NO_LISTA = "La moto todavía no está lista para entregar"
MENSAJE_SOLO_EN_REPARACION = (
    "Pase la moto a En reparación antes de registrar repuestos o mano de obra"
)
MENSAJE_QUIEN_REGISTRA = "Elija el mecánico que registra el cobro"
MENSAJE_ETAPA = "La moto está en {actual}; el paso siguiente es {siguiente}"
MENSAJE_TERMINADA = "La moto ya está terminada y su factura está guardada"
MENSAJE_SIN_NUMERO = "No se pudo generar un número de orden libre. Intente de nuevo"

FORMATO_NUMERO = re.compile(r"[0-9]{8}")
INTENTOS_NUMERO = 5


class OrdenNoEncontrada(LookupError):
    """El número no corresponde a ninguna orden."""


def numero_aleatorio() -> str:
    """Número de orden de ocho dígitos al azar, del 10000000 al 99999999 (ADR-002)."""
    return str(10_000_000 + secrets.randbelow(90_000_000))


def registrar_ingreso(
    repo: Repositorio,
    placa: object,
    observaciones: str,
    mecanico_id: Optional[int],
    fecha: datetime,
    generar_numero: Callable[[], str] = numero_aleatorio,
) -> str:
    """Registra la moto en la etapa Recibida y devuelve el número de orden.

    Lanza:
        ValueError: placa inválida (HU-01), observaciones vacías (HU-02),
            mecánico que no existe (HU-05) o placa con una orden abierta (HU-03).
    """
    placa_valida = validar_placa(placa)
    texto = observaciones.strip()
    if not texto:
        raise ValueError(MENSAJE_OBSERVACIONES)
    ids = {mecanico.id for mecanico in repo.mecanicos()}
    if mecanico_id not in ids:
        raise ValueError(MENSAJE_SIN_MECANICO)
    abierta = repo.orden_abierta_de_placa(placa_valida)
    if abierta is not None:
        raise ValueError(MENSAJE_ORDEN_ABIERTA.format(numero=abierta))
    for _ in range(INTENTOS_NUMERO):
        numero = generar_numero()
        if not repo.existe_numero(numero):
            repo.crear_orden(numero, placa_valida, texto, mecanico_id, fecha)
            return numero
    raise RuntimeError(MENSAJE_SIN_NUMERO)


def buscar(repo: Repositorio, numero: str) -> OrdenTaller:
    """La orden de ese número; lanza OrdenNoEncontrada si no existe."""
    orden = repo.orden(numero) if FORMATO_NUMERO.fullmatch(numero) else None
    if orden is None:
        raise OrdenNoEncontrada(MENSAJE_NO_EXISTE)
    return orden


def avanzar_etapa(
    repo: Repositorio, numero: str, etapa: str, fecha: datetime
) -> OrdenTaller:
    """Pasa la orden a la etapa siguiente y la guarda en el historial (HU-06).

    Al pasar a Terminada calcula y guarda la factura con calcular_cobro.

    Lanza:
        ValueError: si la etapa no es la siguiente, o si falta la mano de obra
            al terminar.
    """
    orden = buscar(repo, numero)
    if orden.etapa == TERMINADA:
        raise ValueError(MENSAJE_TERMINADA)
    siguiente = SIGUIENTE[orden.etapa]
    if etapa not in ETAPAS or etapa != siguiente:
        raise ValueError(MENSAJE_ETAPA.format(actual=orden.etapa, siguiente=siguiente))
    factura = None
    if etapa == TERMINADA:
        if not any(item.tipo == MANO_DE_OBRA for item in orden.items):
            raise ValueError(MENSAJE_SIN_MANO_DE_OBRA)
        factura = calcular_cobro(orden.items)
    repo.cambiar_etapa(numero, etapa, fecha, factura)
    return buscar(repo, numero)


def registrar_cobro(
    repo: Repositorio, numero: str, item: ItemCobro, mecanico_id: Optional[int]
) -> ResumenCobro:
    """Agrega un repuesto o una mano de obra a la orden (HU-07).

    Usa registrar_item, así que valida el ítem con las reglas del cobro y solo
    deja registrar al mecánico asignado.

    Lanza:
        ValueError: si la moto no está En reparación o el ítem no es válido.
        AccesoDenegado: si quien registra no es el mecánico asignado.
    """
    orden = buscar(repo, numero)
    if orden.etapa != EN_REPARACION:
        raise ValueError(MENSAJE_SOLO_EN_REPARACION)
    if mecanico_id is None:
        raise ValueError(MENSAJE_QUIEN_REGISTRA)
    orden_cobro = Orden(
        numero=numero, mecanico_id=orden.mecanico_id, items=list(orden.items)
    )
    trabajador = Trabajador(id=mecanico_id, rol=ROL_MECANICO)
    resumen = registrar_item(orden_cobro, item, trabajador)
    repo.agregar_item(numero, item)
    return resumen


def detalle_del_cobro(repo: Repositorio, numero: str) -> OrdenTaller:
    """La orden con su factura, solo si está terminada (HU-08)."""
    orden = buscar(repo, numero)
    if orden.etapa != TERMINADA:
        raise ValueError(MENSAJE_NO_LISTA)
    return orden


def consultar(repo: Repositorio, numero: str) -> ConsultaCliente:
    """Lo que ve el cliente con su número (HU-04).

    Muestra la etapa y la fecha de la última actualización. Si la moto está
    terminada, también el detalle y el total de la factura. Nunca la placa.
    """
    orden = buscar(repo, numero.strip())
    ultima = orden.historial[-1].fecha_hora if orden.historial else orden.fecha_ingreso
    if orden.etapa == TERMINADA:
        return ConsultaCliente(
            orden.numero, orden.etapa, ultima, tuple(orden.items), orden.factura
        )
    return ConsultaCliente(orden.numero, orden.etapa, ultima)
