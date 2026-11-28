"""Pruebas de la interfaz: estilos, JavaScript, logo, nombre del taller y seguridad."""

import http.client
import threading
import urllib.parse

import pytest

from app.web import paginas
from app.web.servidor import CARPETA_ESTATICOS, crear_servidor

PNG_MINIMO = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


@pytest.fixture
def levantar(tmp_path):
    servidores = []

    def _levantar(**extra):
        entorno = {
            "TALLER_BD_ARCHIVO": str(tmp_path / "taller.db"),
            "TALLER_MECANICOS": "Ana Prueba;Beto Prueba",
            **extra,
        }
        servidor = crear_servidor("127.0.0.1", 0, entorno)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        servidores.append(servidor)
        return servidor

    yield _levantar
    for servidor in servidores:
        servidor.shutdown()
        servidor.server_close()
    paginas.configurar_marca(paginas.NOMBRE_POR_DEFECTO)


def pedir(servidor, metodo, ruta, campos=None):
    conexion = http.client.HTTPConnection(
        "127.0.0.1", servidor.server_address[1], timeout=5
    )
    cuerpo = urllib.parse.urlencode(campos) if campos is not None else None
    cabeceras = {"Content-Type": "application/x-www-form-urlencoded"} if cuerpo else {}
    conexion.request(metodo, ruta, body=cuerpo, headers=cabeceras)
    respuesta = conexion.getresponse()
    datos = respuesta.read()
    conexion.close()
    return respuesta, datos


@pytest.mark.parametrize(
    ("archivo", "tipo"),
    [
        ("estilos.css", "text/css; charset=utf-8"),
        ("app.js", "text/javascript; charset=utf-8"),
        ("emblema.svg", "image/svg+xml"),
    ],
)
def test_archivos_estaticos_se_sirven_con_su_tipo(levantar, archivo, tipo):
    respuesta, datos = pedir(levantar(), "GET", f"/estaticos/{archivo}")
    assert respuesta.status == 200
    assert respuesta.getheader("Content-Type") == tipo
    assert datos == (CARPETA_ESTATICOS / archivo).read_bytes()


@pytest.mark.parametrize(
    "ruta",
    [
        "/estaticos/../servidor.py",  # intento de salir de la carpeta
        "/estaticos/%2e%2e/servidor.py",
        "/estaticos/otro.css",  # archivo que no está en la lista
        "/estaticos/",
    ],
)
def test_solo_se_sirven_los_archivos_de_la_lista(levantar, ruta):
    assert pedir(levantar(), "GET", ruta)[0].status == 404


def test_sin_logo_configurado_se_usa_el_emblema(levantar, tmp_path):
    servidor = levantar(TALLER_LOGO=str(tmp_path / "no_existe.png"))
    respuesta, datos = pedir(servidor, "GET", "/logo")
    assert respuesta.getheader("Content-Type") == "image/svg+xml"
    assert datos.startswith(b"<svg")


def test_logo_del_equipo_se_sirve_tal_cual(levantar, tmp_path):
    logo = tmp_path / "logo.png"
    logo.write_bytes(PNG_MINIMO)
    respuesta, datos = pedir(levantar(TALLER_LOGO=str(logo)), "GET", "/logo")
    assert respuesta.status == 200
    assert respuesta.getheader("Content-Type") == "image/png"
    assert datos == PNG_MINIMO


def test_logo_con_extension_no_permitida_usa_el_emblema(levantar, tmp_path):
    archivo = tmp_path / "logo.html"
    archivo.write_text("<h1>no</h1>", encoding="utf-8")
    respuesta, datos = pedir(levantar(TALLER_LOGO=str(archivo)), "GET", "/logo")
    assert respuesta.getheader("Content-Type") == "image/svg+xml"


def test_nombre_del_taller_en_el_encabezado_y_escapado(levantar):
    servidor = levantar(TALLER_NOMBRE='Taller <b>"Prueba"</b>')
    _, datos = pedir(servidor, "GET", "/")
    texto = datos.decode("utf-8")
    assert "<h1>Taller &lt;b&gt;&quot;Prueba&quot;&lt;/b&gt;</h1>" in texto
    assert "<b>" not in texto


def test_nombre_por_defecto(levantar):
    _, datos = pedir(levantar(), "GET", "/")
    assert "<h1>Taller Dos Ruedas</h1>" in datos.decode("utf-8")


def test_politica_de_seguridad_sin_estilos_ni_scripts_en_linea(levantar):
    respuesta, _ = pedir(levantar(), "GET", "/")
    politica = respuesta.getheader("Content-Security-Policy")
    assert "script-src 'self'" in politica
    assert "style-src 'self'" in politica
    assert "img-src 'self'" in politica
    assert "unsafe-inline" not in politica


def test_las_paginas_no_tienen_estilos_en_linea(levantar):
    servidor = levantar()
    respuesta, _ = pedir(
        servidor,
        "POST",
        "/ordenes",
        {"placa": "ABC12D", "observaciones": "Sin daños", "mecanico": "1"},
    )
    orden = respuesta.getheader("Location")
    for ruta in ("/", orden, "/consulta", "/calculadora"):
        texto = pedir(servidor, "GET", ruta)[1].decode("utf-8")
        assert ' style="' not in texto
        assert "<style>" not in texto
        assert '<link rel="stylesheet" href="/estaticos/estilos.css">' in texto
        assert '<script src="/estaticos/app.js" defer></script>' in texto


def test_menu_marca_la_pagina_actual(levantar):
    servidor = levantar()
    taller = pedir(servidor, "GET", "/")[1].decode("utf-8")
    consulta = pedir(servidor, "GET", "/consulta")[1].decode("utf-8")
    assert '<a href="/" class="activo">Taller</a>' in taller
    assert '<a href="/consulta" class="activo">Consulta del cliente</a>' in consulta


def test_tablero_cuenta_las_motos_por_etapa(levantar):
    servidor = levantar()
    for placa in ("ABC12D", "XYZ98E"):
        pedir(
            servidor,
            "POST",
            "/ordenes",
            {"placa": placa, "observaciones": "Sin daños", "mecanico": "1"},
        )
    texto = pedir(servidor, "GET", "/")[1].decode("utf-8")
    assert "<strong>2</strong><span>Todas</span>" in texto
    assert "<strong>2</strong><span>Recibida</span>" in texto
    assert "<strong>0</strong><span>Terminada</span>" in texto
    assert 'data-etapa="Recibida"' in texto


def test_orden_muestra_los_pasos_y_pide_confirmar_al_terminar(levantar):
    servidor = levantar()
    respuesta, _ = pedir(
        servidor,
        "POST",
        "/ordenes",
        {"placa": "ABC12D", "observaciones": "Sin daños", "mecanico": "1"},
    )
    orden = respuesta.getheader("Location")
    pedir(servidor, "POST", f"{orden}/etapa", {"etapa": "En reparación"})
    texto = pedir(servidor, "GET", orden)[1].decode("utf-8")
    assert '<li class="hecho">Recibida</li>' in texto
    assert '<li class="actual">En reparación</li>' in texto
    assert '<li class="">Terminada</li>' in texto
    assert "data-confirmar=" in texto
    assert "data-subtotal" in texto
    assert f'data-copiar="{orden.rsplit("/", 1)[1]}"' in texto
