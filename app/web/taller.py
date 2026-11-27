"""Páginas del taller que guardan datos: ingreso, orden, factura y consulta.

Cada función recibe el repositorio abierto y el formulario leído, y devuelve
una RespuestaWeb. Después de guardar, redirige a la página de la orden
(303), para que recargar la página no repita el registro.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence

from app.cobros.calculo import ItemCobro, ResumenCobro, calcular_cobro
from app.cobros.errores import AccesoDenegado
from app.cobros.formato import pesos
from app.cobros.modelos import MANO_DE_OBRA, REPUESTO
from app.ordenes import servicio
from app.ordenes.modelos import (
    EN_REPARACION,
    RECIBIDA,
    TERMINADA,
    ConsultaCliente,
    Mecanico,
)
from app.ordenes.repositorio import Repositorio
from app.web.paginas import Formulario, _a_entero, _valor, pagina

PIE_TALLER = (
    "Se guardan la fecha y hora de ingreso, la placa, las observaciones, el mecánico, "
    "las etapas y la factura. No se guardan datos personales del cliente."
)
_ESTILOS_TALLER = (
    "<style>"
    "nav{margin:0 0 16px}nav a{margin-right:16px;font-weight:600}"
    "textarea{font:inherit;padding:7px 9px;border:1px solid #b8c0cc;border-radius:6px;"
    "width:100%;box-sizing:border-box;min-height:70px}"
    ".campo{margin-bottom:12px}"
    ".etapa{display:inline-block;padding:3px 10px;border-radius:12px;font-weight:600;"
    "background:#e3ecf7;color:#1f3a5f}"
    ".numero{font-size:1.6rem;font-weight:700;letter-spacing:2px;color:#1f3a5f}"
    ".fila-botones form{display:inline-block;margin-right:10px}"
    "</style>"
)


@dataclass(frozen=True)
class RespuestaWeb:
    """Código HTTP, cuerpo HTML y, si es una redirección, la dirección."""

    codigo: int
    cuerpo: str = ""
    ubicacion: Optional[str] = None


def _e(texto: object) -> str:
    return html.escape(str(texto))


def _fecha(fecha: datetime) -> str:
    return fecha.strftime("%Y-%m-%d %H:%M")


def _pagina(titulo: str, contenido: str) -> str:
    menu = (
        '<nav><a href="/">Taller</a><a href="/consulta">Consulta del cliente</a>'
        '<a href="/calculadora">Calculadora de cobro</a></nav>'
    )
    return pagina(titulo, _ESTILOS_TALLER + menu + contenido, pie=PIE_TALLER)


def _aviso(clase: str, mensaje: str) -> str:
    return f'<p class="{clase}">{_e(mensaje)}</p>'


def _opciones_mecanico(mecanicos: Sequence[Mecanico], elegido: str = "") -> str:
    opciones = ['<option value="">Elija el mecánico</option>']
    for mecanico in mecanicos:
        marcado = " selected" if str(mecanico.id) == elegido else ""
        opciones.append(
            f'<option value="{mecanico.id}"{marcado}>{_e(mecanico.nombre)}</option>'
        )
    return "".join(opciones)


def _nombre(mecanicos: Sequence[Mecanico], mecanico_id: int) -> str:
    for mecanico in mecanicos:
        if mecanico.id == mecanico_id:
            return mecanico.nombre
    return f"Mecánico {mecanico_id}"


def _entero_o_none(texto: Optional[str]) -> Optional[int]:
    valor = _a_entero(texto or "")
    return valor if isinstance(valor, int) else None


# --- Panel del taller -----------------------------------------------------


def panel(
    repo: Repositorio,
    aviso: str = "",
    valores: Optional[dict] = None,
    codigo: int = 200,
) -> RespuestaWeb:
    """Formulario de ingreso y lista de las motos del taller."""
    valores = valores or {}
    mecanicos = repo.mecanicos()
    formulario = (
        "<section><h2>Registrar el ingreso de una moto</h2>"
        f"{aviso}"
        '<form method="post" action="/ordenes">'
        '<div class="campo"><label for="placa">Placa</label>'
        f'<input id="placa" name="placa" value="{_e(valores.get("placa", ""))}" '
        'placeholder="ABC12D o, si es antigua, ABC12" autocomplete="off"></div>'
        '<div class="campo"><label for="observaciones">Observaciones de ingreso</label>'
        '<textarea id="observaciones" name="observaciones" '
        'placeholder="Rayones, nivel de gasolina, accesorios que faltan">'
        f"{_e(valores.get('observaciones', ''))}</textarea></div>"
        '<div class="campo"><label for="mecanico">Mecánico que toma la moto</label>'
        f'<select id="mecanico" name="mecanico">'
        f"{_opciones_mecanico(mecanicos, valores.get('mecanico', ''))}</select></div>"
        '<button type="submit">Registrar ingreso</button></form></section>'
    )
    filas = "".join(
        f'<tr><td><a href="/ordenes/{o.numero}">{o.numero}</a></td>'
        f"<td>{_e(o.placa)}</td>"
        f"<td>{_e(_nombre(mecanicos, o.mecanico_id))}</td>"
        f'<td><span class="etapa">{_e(o.etapa)}</span></td>'
        f"<td>{_fecha(o.fecha_ingreso)}</td></tr>"
        for o in repo.ordenes_recientes()
    )
    lista = (
        "<section><h2>Motos en el taller</h2>"
        + (
            "<table><tr><th>Orden</th><th>Placa</th><th>Mecánico</th><th>Etapa</th>"
            f"<th>Ingreso</th></tr>{filas}</table>"
            if filas
            else "<p>Todavía no hay motos registradas.</p>"
        )
        + "</section>"
    )
    return RespuestaWeb(codigo, _pagina("Taller", formulario + lista))


def registrar(
    repo: Repositorio, formulario: Formulario, fecha: datetime
) -> RespuestaWeb:
    """Guarda el ingreso y redirige a la orden, o vuelve al panel con el error."""
    valores = {
        campo: _valor(formulario, campo) or ""
        for campo in ("placa", "observaciones", "mecanico")
    }
    try:
        numero = servicio.registrar_ingreso(
            repo,
            valores["placa"],
            valores["observaciones"],
            _entero_o_none(valores["mecanico"]),
            fecha,
        )
    except ValueError as error:
        return panel(repo, _aviso("error", str(error)), valores, codigo=422)
    return RespuestaWeb(303, ubicacion=f"/ordenes/{numero}")


# --- Página de una orden --------------------------------------------------


def _tabla_items(items: List[ItemCobro], resumen: Optional[ResumenCobro]) -> str:
    if not items:
        return "<p>Todavía no hay repuestos ni mano de obra registrados.</p>"
    filas = "".join(
        f"<tr><td>{_e(i.descripcion)}</td><td>{_e(i.tipo)}</td>"
        f'<td class="num">{i.cantidad}</td>'
        f'<td class="num">$ {pesos(i.precio_unitario)}</td>'
        f'<td class="num">$ {pesos(i.cantidad * i.precio_unitario)}</td></tr>'
        for i in items
    )
    totales = ""
    if resumen is not None:
        totales = (
            f'<tr><th colspan="4">Repuestos</th>'
            f'<td class="num">$ {pesos(resumen.total_repuestos)}</td></tr>'
            f'<tr><th colspan="4">Mano de obra</th>'
            f'<td class="num">$ {pesos(resumen.total_mano_obra)}</td></tr>'
            f'<tr class="total"><th colspan="4">Total sin IVA</th>'
            f'<td class="num">$ {pesos(resumen.total)}</td></tr>'
        )
    return (
        '<table><tr><th>Descripción</th><th>Tipo</th><th class="num">Cantidad</th>'
        '<th class="num">Precio unitario</th><th class="num">Subtotal</th></tr>'
        f"{filas}{totales}</table>"
    )


def _boton_etapa(numero: str, etapa: str, texto: str) -> str:
    return (
        f'<form method="post" action="/ordenes/{numero}/etapa">'
        f'<input type="hidden" name="etapa" value="{_e(etapa)}">'
        f'<button type="submit">{_e(texto)}</button></form>'
    )


def ver_orden(
    repo: Repositorio, numero: str, aviso: str = "", codigo: int = 200
) -> RespuestaWeb:
    """Datos de la orden, historial de etapas, cobro y acciones según la etapa."""
    try:
        orden = servicio.buscar(repo, numero)
    except servicio.OrdenNoEncontrada as error:
        contenido = f"<section>{_aviso('error', str(error))}</section>"
        return RespuestaWeb(404, _pagina("Orden no encontrada", contenido))
    mecanicos = repo.mecanicos()
    nombre_mecanico = _nombre(mecanicos, orden.mecanico_id)
    datos = (
        f'<section><h2>Orden <span class="numero">{orden.numero}</span></h2>{aviso}'
        "<p>Este es el número que se le entrega al cliente para consultar su moto.</p>"
        "<table>"
        f"<tr><th>Placa</th><td>{_e(orden.placa)}</td></tr>"
        f"<tr><th>Ingreso</th><td>{_fecha(orden.fecha_ingreso)}</td></tr>"
        f"<tr><th>Mecánico</th><td>{_e(nombre_mecanico)}</td></tr>"
        f"<tr><th>Observaciones de ingreso</th><td>{_e(orden.observaciones)}</td></tr>"
        f'<tr><th>Etapa</th><td><span class="etapa">{_e(orden.etapa)}</span></td></tr>'
        "</table></section>"
    )
    historial = "".join(
        f"<tr><td>{_e(c.etapa)}</td><td>{_fecha(c.fecha_hora)}</td></tr>"
        for c in orden.historial
    )
    seccion_historial = (
        "<section><h2>Historial</h2><table><tr><th>Etapa</th><th>Fecha y hora</th></tr>"
        f"{historial}</table></section>"
    )
    acciones = ""
    if orden.etapa == RECIBIDA:
        acciones = (
            "<section><h2>Siguiente paso</h2>"
            f"{_boton_etapa(orden.numero, EN_REPARACION, 'Pasar a En reparación')}"
            "</section>"
        )
    elif orden.etapa == EN_REPARACION:
        acciones = (
            "<section><h2>Registrar repuesto o mano de obra</h2>"
            f'<form method="post" action="/ordenes/{orden.numero}/items"><table>'
            "<tr><th>Tipo</th><th>Descripción</th><th>Cantidad</th>"
            "<th>Precio unitario</th></tr><tr>"
            f'<td><select name="tipo" aria-label="Tipo">'
            f'<option value="{REPUESTO}">{REPUESTO}</option>'
            f'<option value="{MANO_DE_OBRA}">{MANO_DE_OBRA}</option></select></td>'
            '<td><input name="descripcion" aria-label="Descripción"></td>'
            '<td><input name="cantidad" value="1" aria-label="Cantidad" '
            'inputmode="numeric"></td>'
            '<td><input name="precio" aria-label="Precio unitario" inputmode="numeric" '
            'placeholder="18.000"></td></tr></table>'
            '<div class="campo"><label for="quien">Mecánico que registra</label>'
            '<select id="quien" name="mecanico">'
            f"{_opciones_mecanico(mecanicos)}</select>"
            "</div>"
            '<button type="submit">Agregar</button></form></section>'
            "<section><h2>Terminar</h2>"
            "<p>Al terminar se guarda la factura y ya no se pueden agregar ítems.</p>"
            f"{_boton_etapa(orden.numero, TERMINADA, 'Marcar como Terminada')}"
            "</section>"
        )
    titulo_cobro = "Factura" if orden.etapa == TERMINADA else "Cobro registrado"
    resumen = orden.factura
    if resumen is None and orden.items:
        resumen = calcular_cobro(orden.items)
    cobro = f"<section><h2>{titulo_cobro}</h2>{_tabla_items(orden.items, resumen)}"
    if orden.etapa == TERMINADA:
        cobro += (
            "<p>La factura quedó guardada. El cliente puede ver el total en "
            '<a href="/consulta">Consulta del cliente</a> con el número '
            f"{orden.numero}.</p>"
        )
    cobro += "</section>"
    contenido = datos + acciones + cobro + seccion_historial
    return RespuestaWeb(codigo, _pagina(f"Orden {orden.numero}", contenido))


def avanzar(
    repo: Repositorio, numero: str, formulario: Formulario, fecha: datetime
) -> RespuestaWeb:
    """Pasa la orden a la etapa que llega en el formulario."""
    etapa = _valor(formulario, "etapa") or ""
    try:
        servicio.avanzar_etapa(repo, numero, etapa, fecha)
    except servicio.OrdenNoEncontrada:
        return ver_orden(repo, numero)
    except ValueError as error:
        return ver_orden(repo, numero, _aviso("error", str(error)), codigo=422)
    return RespuestaWeb(303, ubicacion=f"/ordenes/{numero}")


def agregar_item(
    repo: Repositorio, numero: str, formulario: Formulario
) -> RespuestaWeb:
    """Registra un repuesto o una mano de obra con el mecánico que lo hace."""
    item = ItemCobro(
        tipo=_valor(formulario, "tipo") or "",
        descripcion=(_valor(formulario, "descripcion") or "").strip(),
        cantidad=_a_entero(_valor(formulario, "cantidad") or ""),
        precio_unitario=_a_entero(_valor(formulario, "precio") or ""),
    )
    try:
        servicio.registrar_cobro(
            repo, numero, item, _entero_o_none(_valor(formulario, "mecanico"))
        )
    except servicio.OrdenNoEncontrada:
        return ver_orden(repo, numero)
    except AccesoDenegado as error:
        return ver_orden(repo, numero, _aviso("error", str(error)), codigo=403)
    except ValueError as error:
        return ver_orden(repo, numero, _aviso("error", str(error)), codigo=422)
    return RespuestaWeb(303, ubicacion=f"/ordenes/{numero}")


# --- Consulta del cliente -------------------------------------------------


def _formulario_consulta(numero: str = "") -> str:
    return (
        '<form method="post" action="/consulta"><div class="campo">'
        '<label for="numero">Número de orden</label>'
        f'<input id="numero" name="numero" value="{_e(numero)}" inputmode="numeric" '
        'placeholder="8 dígitos" autocomplete="off"></div>'
        '<button type="submit">Consultar</button></form>'
    )


def consulta(aviso: str = "", numero: str = "", codigo: int = 200) -> RespuestaWeb:
    """Formulario de la consulta del cliente."""
    contenido = (
        "<section><h2>Consulte su moto</h2>"
        "<p>Escriba el número que le entregó el registrador.</p>"
        f"{aviso}{_formulario_consulta(numero)}</section>"
    )
    return RespuestaWeb(codigo, _pagina("Consulta del cliente", contenido))


def _resultado(c: ConsultaCliente) -> str:
    partes = [
        f"<section><h2>Orden {c.numero}</h2><table>"
        f'<tr><th>Etapa</th><td><span class="etapa">{_e(c.etapa)}</span></td></tr>'
        f"<tr><th>Última actualización</th><td>{_fecha(c.actualizada)}</td></tr>"
        "</table>"
    ]
    if c.factura is None:
        partes.append(_aviso("ok", servicio.MENSAJE_NO_LISTA))
    else:
        partes.append(
            f"<h2>Detalle del cobro</h2>{_tabla_items(list(c.items), c.factura)}"
        )
    partes.append("</section>")
    return "".join(partes)


def consultar(repo: Repositorio, formulario: Formulario) -> RespuestaWeb:
    """Muestra la etapa y, si está terminada, el detalle y el total (HU-04, HU-08)."""
    numero = (_valor(formulario, "numero") or "").strip()
    try:
        resultado = servicio.consultar(repo, numero)
    except servicio.OrdenNoEncontrada as error:
        return consulta(_aviso("error", str(error)), numero, codigo=404)
    return RespuestaWeb(
        200, _pagina(f"Orden {resultado.numero}", _resultado(resultado))
    )
