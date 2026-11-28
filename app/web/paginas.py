"""Páginas de la versión web local del Taller Dos Ruedas.

Cada función recibe el formulario ya leído y devuelve el código HTTP y la
página. Nada se guarda: la versión local valida la placa (HU-01) y calcula el
cobro (HU-07) con las mismas reglas que prueban las pruebas del proyecto.
Todo texto que escribe el usuario se escapa antes de ponerlo en la página.
"""

from __future__ import annotations

import html
import re
from typing import Dict, List, Optional, Tuple

from app.cobros.calculo import ItemCobro, ResumenCobro, calcular_cobro
from app.cobros.formato import pesos
from app.cobros.modelos import MANO_DE_OBRA, REPUESTO
from app.ingresos.placas import validar_placa

# Lo que devuelve urllib.parse.parse_qs: cada campo con su lista de valores.
Formulario = Dict[str, List[str]]
# Código HTTP y página HTML.
Respuesta = Tuple[int, str]

FILAS_COBRO = 5
CAMPOS_FILA = ("tipo", "descripcion", "cantidad", "precio")
# Un entero con punto de miles, como lo escribe el registrador: 18.000 o 1.250.000.
_CON_PUNTO_DE_MILES = re.compile(r"-?[0-9]{1,3}(\.[0-9]{3})+")
_ENTERO = re.compile(r"-?[0-9]+")

_ESTILOS = """
body{font-family:system-ui,"Segoe UI",Arial,sans-serif;margin:0;
background:#f4f5f7;color:#1d2430}
header{background:#1f3a5f;color:#fff;padding:18px 24px}
header h1{margin:0;font-size:1.5rem}header p{margin:4px 0 0;opacity:.85}
main{max-width:920px;margin:24px auto;padding:0 16px}
section{background:#fff;border-radius:10px;padding:20px 24px;margin-bottom:20px;
box-shadow:0 1px 3px rgba(0,0,0,.08)}
h2{margin-top:0;font-size:1.2rem;color:#1f3a5f}
label{font-weight:600;display:block;margin-bottom:6px}
input,select{font:inherit;padding:7px 9px;border:1px solid #b8c0cc;border-radius:6px;
box-sizing:border-box;width:100%}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid #e3e6ea}
td.num,th.num{text-align:right}
tr.total th,tr.total td{font-size:1.1rem;border-top:2px solid #1f3a5f}
button{font:inherit;background:#1f3a5f;color:#fff;border:0;border-radius:6px;
padding:9px 18px;margin-top:12px;cursor:pointer}
.error{background:#fdecea;border-left:5px solid #c62828;padding:10px 14px;
border-radius:6px}
.ok{background:#e8f5e9;border-left:5px solid #2e7d32;padding:10px 14px;
border-radius:6px}
.fila-placa{display:flex;gap:10px;align-items:flex-end}.fila-placa div{flex:1}
footer{color:#5b6573;font-size:.85rem;text-align:center;margin:8px 0 28px}
a{color:#1f3a5f}
"""


PIE_DEMO = (
    "Versión local de demostración. No guarda datos y no pide datos "
    "personales del cliente."
)


def pagina(titulo: str, contenido: str, pie: str = PIE_DEMO) -> str:
    """Arma una página completa con el encabezado y el pie del taller.

    Parámetros:
        titulo: título de la pestaña; se escapa aquí.
        contenido: HTML del cuerpo, ya escapado por quien lo arma.
        pie: texto del pie de página; se escapa aquí.

    Devuelve:
        El documento HTML completo.
    """
    return (
        "<!DOCTYPE html>\n"
        '<html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(titulo)} | Taller Dos Ruedas</title>"
        f"<style>{_ESTILOS}</style></head><body>"
        "<header><h1>Taller Dos Ruedas</h1>"
        "<p>Ingreso de motos y cobro de repuestos y mano de obra, sin IVA</p></header>"
        f"<main>{contenido}</main>"
        f"<footer>{html.escape(pie)}</footer>"
        "</body></html>"
    )


def pagina_inicio() -> str:
    """Página principal con el formulario de la placa y el del cobro."""
    return pagina("Inicio", _formulario_placa("") + _formulario_cobro(None))


def pagina_no_encontrada() -> str:
    """Página para una dirección que no existe."""
    return pagina(
        "No encontrada",
        '<section><p class="error">Esta página no existe.</p>'
        '<p><a href="/">Volver al inicio</a></p></section>',
    )


def pagina_error(mensaje: str) -> str:
    """Página para un formulario que no se pudo leer.

    Parámetros:
        mensaje: explicación para el usuario; se escapa aquí.
    """
    return pagina(
        "Error",
        f'<section><p class="error">{html.escape(mensaje)}</p>'
        '<p><a href="/">Volver al inicio</a></p></section>',
    )


def procesar_placa(formulario: Formulario) -> Respuesta:
    """Valida la placa que escribió el registrador (HU-01).

    Parámetros:
        formulario: los campos enviados; se usa el campo "placa".

    Devuelve:
        200 con la placa normalizada, o 422 con el mensaje de la regla y el
        formulario lleno para corregirla.
    """
    placa = _valor(formulario, "placa")
    try:
        normalizada = validar_placa(placa)
    except ValueError as error:
        contenido = _formulario_placa(placa or "", _aviso("error", str(error)))
        return 422, pagina("Placa no válida", contenido + _volver())
    aviso = _aviso("ok", "Placa válida: ", normalizada)
    return 200, pagina(
        "Placa válida", _formulario_placa(normalizada, aviso) + _volver()
    )


def procesar_cobro(formulario: Formulario) -> Respuesta:
    """Calcula el cobro de las filas llenas del formulario (HU-07).

    Una fila sin descripción ni precio se ignora. Cada fila se valida con
    calcular_cobro, así que los mensajes son los de la regla, con el número
    de la fila adelante.

    Parámetros:
        formulario: los campos tipo_N, descripcion_N, cantidad_N y precio_N,
            con N de 1 a FILAS_COBRO.

    Devuelve:
        200 con el detalle y los totales sin IVA, o 422 con el mensaje de la
        primera fila que no cumple la regla y el formulario lleno.
    """
    filas = _leer_filas(formulario)
    items: List[ItemCobro] = []
    for numero, fila in enumerate(filas, start=1):
        if not fila["descripcion"].strip() and not fila["precio"].strip():
            continue
        item = ItemCobro(
            tipo=fila["tipo"],
            descripcion=fila["descripcion"].strip(),
            cantidad=_a_entero(fila["cantidad"]),
            precio_unitario=_a_entero(fila["precio"]),
        )
        try:
            calcular_cobro([item])
        except ValueError as error:
            aviso = _aviso("error", f"Fila {numero}: {error}")
            return 422, pagina("Revise el cobro", _formulario_cobro(filas, aviso))
        items.append(item)
    resumen = calcular_cobro(items)
    contenido = _tabla_cobro(items, resumen) + _formulario_cobro(filas)
    return 200, pagina("Cobro calculado", contenido)


def _valor(formulario: Formulario, campo: str) -> Optional[str]:
    """Devuelve el primer valor de un campo, o None si no se envió."""
    valores = formulario.get(campo)
    return valores[0] if valores else None


def _a_entero(texto: str) -> object:
    """Convierte lo que escribió el usuario en un entero si se puede.

    Acepta el punto de miles (18.000). Un campo vacío es None, como un precio
    que falta. Cualquier otra cosa se devuelve igual, para que calcular_cobro
    la rechace con el mensaje de la regla.
    """
    limpio = texto.strip()
    if not limpio:
        return None
    if _CON_PUNTO_DE_MILES.fullmatch(limpio):
        limpio = limpio.replace(".", "")
    if _ENTERO.fullmatch(limpio):
        try:
            return int(limpio)
        except ValueError:  # más dígitos de los que Python convierte
            return limpio
    return limpio


def _leer_filas(formulario: Formulario) -> List[Dict[str, str]]:
    """Lee las filas del formulario del cobro como texto, sin convertir."""
    filas = []
    for numero in range(1, FILAS_COBRO + 1):
        fila = {
            campo: _valor(formulario, f"{campo}_{numero}") or ""
            for campo in CAMPOS_FILA
        }
        filas.append(fila)
    return filas


def _aviso(clase: str, mensaje: str, destacado: str = "") -> str:
    """Párrafo de aviso con el mensaje y, si hay, un texto en negrilla."""
    negrilla = f"<strong>{html.escape(destacado)}</strong>" if destacado else ""
    return f'<p class="{clase}">{html.escape(mensaje)}{negrilla}</p>'


def _volver() -> str:
    return '<p><a href="/">Volver al inicio</a></p>'


def _formulario_placa(valor: str, aviso: str = "") -> str:
    """Formulario de ingreso de la moto con el campo de la placa."""
    return (
        "<section><h2>Ingreso de la moto</h2>"
        f"{aviso}"
        '<form method="post" action="/placa"><div class="fila-placa"><div>'
        '<label for="placa">Placa</label>'
        f'<input id="placa" name="placa" value="{html.escape(valor)}" '
        'placeholder="ABC12D o, si es antigua, ABC12" autocomplete="off"></div>'
        '<div style="flex:0"><button type="submit">Validar placa</button></div>'
        "</div></form></section>"
    )


def _formulario_cobro(filas: Optional[List[Dict[str, str]]], aviso: str = "") -> str:
    """Formulario del cobro con FILAS_COBRO filas, llenas si se envió antes."""
    if filas is None:
        filas = [
            {"tipo": REPUESTO, "descripcion": "", "cantidad": "1", "precio": ""}
            for _ in range(FILAS_COBRO)
        ]
    cuerpo = []
    for numero, fila in enumerate(filas, start=1):
        opciones = "".join(
            f'<option value="{html.escape(tipo)}"'
            f"{' selected' if fila['tipo'] == tipo else ''}>"
            f"{html.escape(tipo)}</option>"
            for tipo in (REPUESTO, MANO_DE_OBRA)
        )
        numerico = 'inputmode="numeric"'
        cuerpo.append(
            f"<tr><td>{numero}</td>"
            f'<td><select name="tipo_{numero}" aria-label="Tipo, fila {numero}">'
            f"{opciones}</select></td>"
            + _celda_campo("descripcion", "Descripción", numero, fila)
            + _celda_campo("cantidad", "Cantidad", numero, fila, numerico)
            + _celda_campo(
                "precio",
                "Precio unitario",
                numero,
                fila,
                numerico + ' placeholder="18.000"',
            )
            + "</tr>"
        )
    return (
        "<section><h2>Cobro de la orden</h2>"
        f"{aviso}"
        '<form method="post" action="/cobro"><table>'
        '<colgroup><col style="width:28px"><col style="width:150px"><col>'
        '<col style="width:90px"><col style="width:140px"></colgroup>'
        "<tr><th>#</th><th>Tipo</th><th>Descripción</th><th>Cantidad</th>"
        "<th>Precio unitario</th></tr>"
        f"{''.join(cuerpo)}</table>"
        '<button type="submit">Calcular cobro</button></form></section>'
    )


def _tabla_cobro(items: List[ItemCobro], resumen: ResumenCobro) -> str:
    """Detalle de los ítems y totales del cobro, sin IVA."""
    filas = "".join(
        f"<tr><td>{html.escape(item.descripcion)}</td>"
        f"<td>{html.escape(item.tipo)}</td>"
        f'<td class="num">{item.cantidad}</td>'
        f'<td class="num">$ {pesos(item.precio_unitario)}</td>'
        f'<td class="num">$ {pesos(item.cantidad * item.precio_unitario)}</td></tr>'
        for item in items
    )
    return (
        "<section><h2>Cobro calculado</h2><table>"
        '<tr><th>Descripción</th><th>Tipo</th><th class="num">Cantidad</th>'
        '<th class="num">Precio unitario</th><th class="num">Subtotal</th></tr>'
        f"{filas}"
        + _fila_total("Repuestos", resumen.total_repuestos)
        + _fila_total("Mano de obra", resumen.total_mano_obra)
        + _fila_total("Total sin IVA", resumen.total, ' class="total"')
        + "</table></section>"
    )


def _celda_campo(
    campo: str, etiqueta: str, numero: int, fila: Dict[str, str], extra: str = ""
) -> str:
    """Celda con el campo de texto de una fila del cobro, con su valor escapado."""
    return (
        f'<td><input name="{campo}_{numero}" aria-label="{etiqueta}, fila {numero}" '
        f'value="{html.escape(fila[campo])}" {extra}></td>'
    )


def _fila_total(etiqueta: str, valor: int, clase: str = "") -> str:
    """Fila de la tabla de totales, por ejemplo Total sin IVA y $ 85.000."""
    return (
        f'<tr{clase}><th colspan="4">{etiqueta}</th>'
        f'<td class="num">$ {pesos(valor)}</td></tr>'
    )
