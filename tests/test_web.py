"""Pruebas de la versión web local (entrega final).

Los esperados salen de las mismas reglas de registro_pruebas.md: la placa de
la HU-01 y el cobro sin IVA de la HU-07. La parte de seguridad comprueba lo
que exige revision_seguridad.md: escapar lo que escribe el usuario, limitar el
tamaño del formulario y no anunciar la versión de Python.
"""

import http.client
import threading

import pytest

from app.ingresos.placas import MENSAJE_FORMATO
from app.web.paginas import pagina_inicio, procesar_cobro, procesar_placa
from app.web.servidor import TAMANO_MAXIMO, crear_servidor, leer_configuracion


def fila(numero, tipo="repuesto", descripcion="", cantidad="1", precio=""):
    """Campos de una fila del formulario del cobro, como los envía el navegador."""
    return {
        f"tipo_{numero}": [tipo],
        f"descripcion_{numero}": [descripcion],
        f"cantidad_{numero}": [cantidad],
        f"precio_{numero}": [precio],
    }


def formulario_cobro(*filas):
    formulario = {}
    for campos in filas:
        formulario.update(campos)
    return formulario


ESCENARIO_1 = formulario_cobro(
    fila(1, descripcion="Filtro de aceite", precio="18000"),
    fila(2, descripcion="Aceite, un litro", precio="32000"),
    fila(3, "mano de obra", "Cambio de aceite y revisión del motor", "1", "35000"),
)


def total_en(pagina, etiqueta):
    """Valor de la fila de totales con esa etiqueta, por ejemplo "$ 85.000"."""
    marca = f'<th colspan="4">{etiqueta}</th><td class="num">'
    inicio = pagina.index(marca) + len(marca)
    return pagina[inicio : pagina.index("</td>", inicio)]


# --- Páginas, sin servidor ---


def test_inicio_tiene_los_dos_formularios_y_avisa_que_no_guarda_datos():
    pagina = pagina_inicio()
    assert '<form method="post" action="/placa">' in pagina
    assert '<form method="post" action="/cobro">' in pagina
    assert "No guarda datos y no pide datos personales del cliente." in pagina


@pytest.mark.parametrize(
    ("escrita", "esperada"),
    [
        ("ABC12D", "ABC12D"),  # V1 formato actual
        (" abc12d ", "ABC12D"),  # V3 y V4 minúsculas y espacios a los lados
        ("MOT09", "MOT09"),  # V2 placa antigua
    ],
)
def test_placa_valida_responde_200_con_la_placa_normalizada(escrita, esperada):
    codigo, pagina = procesar_placa({"placa": [escrita]})
    assert codigo == 200
    assert f"Placa válida: <strong>{esperada}</strong>" in pagina


@pytest.mark.parametrize(
    "escrita",
    [
        "ABC-12D",  # I4 guion en medio
        "ABC123",  # I1 formato de carro
        "",  # I5 vacía
    ],
)
def test_placa_invalida_responde_422_con_el_mensaje_de_la_regla(escrita):
    codigo, pagina = procesar_placa({"placa": [escrita]})
    assert codigo == 422
    assert MENSAJE_FORMATO in pagina


def test_placa_con_codigo_html_se_muestra_escapada():
    codigo, pagina = procesar_placa({"placa": ['"><script>alert(1)</script>']})
    assert codigo == 422
    assert "<script>" not in pagina
    assert "&lt;script&gt;" in pagina


def test_cobro_del_escenario_1_de_la_hu_07():
    codigo, pagina = procesar_cobro(ESCENARIO_1)
    assert codigo == 200
    assert total_en(pagina, "Repuestos") == "$ 50.000"
    assert total_en(pagina, "Mano de obra") == "$ 35.000"
    assert total_en(pagina, "Total sin IVA") == "$ 85.000"


def test_cobro_acepta_el_punto_de_miles_como_lo_escribe_el_registrador():
    formulario = formulario_cobro(
        fila(1, descripcion="Kit de arrastre", precio="142.000"),
        fila(2, "mano de obra", "Cambio del kit", "1", "1.250.000"),
    )
    codigo, pagina = procesar_cobro(formulario)
    assert codigo == 200
    assert total_en(pagina, "Total sin IVA") == "$ 1.392.000"


def test_cobro_ignora_las_filas_vacias_y_multiplica_la_cantidad():
    formulario = formulario_cobro(
        fila(1),
        fila(2, descripcion="Bombillo direccional", cantidad="2", precio="6000"),
    )
    codigo, pagina = procesar_cobro(formulario)
    assert codigo == 200
    assert total_en(pagina, "Repuestos") == "$ 12.000"
    assert total_en(pagina, "Total sin IVA") == "$ 12.000"


@pytest.mark.parametrize(
    ("campos", "mensaje"),
    [
        # Precio que falta: mensaje de la HU-07, escenario 2
        (
            fila(1, descripcion="Filtro de aceite"),
            "Fila 1: Escriba el precio del repuesto",
        ),
        # P9 precio negativo, en la segunda fila
        (
            formulario_cobro(fila(1, precio="1000"), fila(2, precio="-1")),
            "Fila 2: El precio no puede ser negativo",
        ),
        # P12 precio con decimales
        (
            fila(1, precio="18000,5"),
            "Fila 1: El precio debe ser un número entero de pesos",
        ),
        # P14 cantidad cero
        (
            fila(1, cantidad="0", precio="1000"),
            "Fila 1: La cantidad debe ser al menos 1",
        ),
        # P16 cantidad con decimales
        (
            fila(1, cantidad="1.5", precio="1000"),
            "Fila 1: La cantidad debe ser un número entero",
        ),
        # P5 tipo que no está en la lista, enviado a mano sin el navegador
        (
            fila(1, tipo="servicio", precio="1000"),
            "Fila 1: Tipo de ítem no válido: servicio. Use repuesto o mano de obra",
        ),
    ],
)
def test_cobro_con_una_fila_invalida_responde_422_con_el_mensaje_de_la_regla(
    campos, mensaje
):
    codigo, pagina = procesar_cobro(campos)
    assert codigo == 422
    assert f'<p class="error">{mensaje}</p>' in pagina


def test_descripcion_con_codigo_html_se_muestra_escapada():
    codigo, pagina = procesar_cobro(fila(1, descripcion="<b>Guaya</b>", precio="15000"))
    assert codigo == 200
    assert "<b>Guaya</b>" not in pagina
    assert "&lt;b&gt;Guaya&lt;/b&gt;" in pagina


@pytest.mark.parametrize(
    ("entorno", "esperado"),
    [
        ({}, ("127.0.0.1", 8000)),  # por defecto solo este equipo
        ({"TALLER_PUERTO": "8001"}, ("127.0.0.1", 8001)),
    ],
)
def test_configuracion_por_variables_de_entorno(entorno, esperado):
    assert leer_configuracion(entorno) == esperado


@pytest.mark.parametrize("puerto", ["0", "65536", "ocho mil", ""])
def test_puerto_fuera_de_rango_lanza_value_error(puerto):
    with pytest.raises(
        ValueError, match="^TALLER_PUERTO debe ser un número entre 1 y 65535$"
    ):
        leer_configuracion({"TALLER_PUERTO": puerto})


# --- Servidor real en un puerto libre de este equipo ---


@pytest.fixture
def servidor():
    servidor = crear_servidor("127.0.0.1", 0)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield servidor.server_address[1]
    servidor.shutdown()
    servidor.server_close()


def pedir(puerto, metodo, ruta, cuerpo=None):
    conexion = http.client.HTTPConnection("127.0.0.1", puerto, timeout=5)
    cabeceras = {"Content-Type": "application/x-www-form-urlencoded"} if cuerpo else {}
    conexion.request(metodo, ruta, body=cuerpo, headers=cabeceras)
    respuesta = conexion.getresponse()
    texto = respuesta.read().decode("utf-8")
    conexion.close()
    return respuesta, texto


def test_salud_responde_ok(servidor):
    respuesta, texto = pedir(servidor, "GET", "/salud")
    assert respuesta.status == 200
    assert texto == "ok"


def test_inicio_lleva_las_cabeceras_de_seguridad_y_no_muestra_la_version_de_python(
    servidor,
):
    respuesta, _ = pedir(servidor, "GET", "/")
    assert respuesta.status == 200
    assert respuesta.getheader("X-Content-Type-Options") == "nosniff"
    assert "default-src 'none'" in respuesta.getheader("Content-Security-Policy")
    assert respuesta.getheader("Server") == "TallerDosRuedas"


def test_post_del_cobro_por_http(servidor):
    cuerpo = (
        "tipo_1=repuesto&descripcion_1=Pi%C3%B1%C3%B3n&cantidad_1=1&precio_1=38.000"
    )
    respuesta, texto = pedir(servidor, "POST", "/cobro", cuerpo)
    assert respuesta.status == 200
    assert "Piñón" in texto
    assert total_en(texto, "Total sin IVA") == "$ 38.000"


def test_formulario_demasiado_grande_responde_413(servidor):
    respuesta, _ = pedir(servidor, "POST", "/placa", "placa=" + "A" * TAMANO_MAXIMO)
    assert respuesta.status == 413


@pytest.mark.parametrize(("metodo", "ruta"), [("GET", "/admin"), ("POST", "/borrar")])
def test_ruta_que_no_existe_responde_404(servidor, metodo, ruta):
    respuesta, _ = pedir(servidor, metodo, ruta, "x=1" if metodo == "POST" else None)
    assert respuesta.status == 404
