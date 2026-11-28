"""Pruebas por HTTP de las páginas que guardan datos (entrega final).

Cada prueba levanta el servidor real en un puerto libre con su propio archivo
SQLite y dos mecánicos ficticios.
"""

import http.client
import logging
import re
import threading
import urllib.parse

import pytest

from app.ordenes.modelos import Mecanico
from app.ordenes import servicio
from app.web.servidor import (
    MENSAJE_DEMASIADOS_INTENTOS,
    MENSAJE_SIN_BD,
    ConfiguracionBD,
    LimiteDeIntentos,
    cargar_archivo_env,
    crear_servidor,
    describir_destino,
    leer_configuracion_bd,
    main,
)


@pytest.fixture
def taller(tmp_path):
    entorno = {
        "TALLER_BD_ARCHIVO": str(tmp_path / "taller.db"),
        "TALLER_MECANICOS": "Ana Prueba;Beto Prueba",
    }
    servidor = crear_servidor("127.0.0.1", 0, entorno)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield servidor
    servidor.shutdown()
    servidor.server_close()


def pedir(servidor, metodo, ruta, campos=None):
    conexion = http.client.HTTPConnection(
        "127.0.0.1", servidor.server_address[1], timeout=5
    )
    cuerpo = urllib.parse.urlencode(campos) if campos is not None else None
    cabeceras = {"Content-Type": "application/x-www-form-urlencoded"} if cuerpo else {}
    conexion.request(metodo, ruta, body=cuerpo, headers=cabeceras)
    respuesta = conexion.getresponse()
    texto = respuesta.read().decode("utf-8")
    conexion.close()
    return respuesta, texto


def registrar(
    servidor, placa="ABC12D", observaciones="Rayón en el tanque", mecanico="1"
):
    respuesta, _ = pedir(
        servidor,
        "POST",
        "/ordenes",
        {"placa": placa, "observaciones": observaciones, "mecanico": mecanico},
    )
    assert respuesta.status == 303
    ubicacion = respuesta.getheader("Location")
    assert re.fullmatch(r"/ordenes/[0-9]{8}", ubicacion)
    return ubicacion.rsplit("/", 1)[1]


def agregar(servidor, numero, tipo, descripcion, precio, mecanico="1"):
    return pedir(
        servidor,
        "POST",
        f"/ordenes/{numero}/items",
        {
            "tipo": tipo,
            "descripcion": descripcion,
            "cantidad": "1",
            "precio": precio,
            "mecanico": mecanico,
        },
    )


def avanzar(servidor, numero, etapa):
    return pedir(servidor, "POST", f"/ordenes/{numero}/etapa", {"etapa": etapa})


def test_panel_muestra_los_mecanicos_configurados(taller):
    respuesta, texto = pedir(taller, "GET", "/")
    assert respuesta.status == 200
    assert '<option value="1">Ana Prueba</option>' in texto
    assert '<option value="2">Beto Prueba</option>' in texto
    assert "Todavía no hay motos registradas." in texto


def test_registrar_y_ver_la_orden(taller):
    numero = registrar(taller, placa="abc12d", mecanico="2")
    respuesta, texto = pedir(taller, "GET", f"/ordenes/{numero}")
    assert respuesta.status == 200
    assert f'<span class="numero">{numero}</span>' in texto
    assert "<tr><th>Placa</th><td>ABC12D</td></tr>" in texto
    assert "<tr><th>Mecánico</th><td>Beto Prueba</td></tr>" in texto
    assert (
        "<tr><th>Observaciones de ingreso</th><td>Rayón en el tanque</td></tr>" in texto
    )
    assert '<span class="etapa">Recibida</span>' in texto
    _, panel = pedir(taller, "GET", "/")
    assert f'<a href="/ordenes/{numero}">{numero}</a>' in panel


def test_ingreso_invalido_responde_422_y_conserva_lo_escrito_escapado(taller):
    respuesta, texto = pedir(
        taller,
        "POST",
        "/ordenes",
        {"placa": '"><b>x', "observaciones": "", "mecanico": "1"},
    )
    assert respuesta.status == 422
    assert "<b>x" not in texto
    assert "&quot;&gt;&lt;b&gt;x" in texto
    assert "Placa no válida" in texto


def test_recorrido_completo_hasta_la_factura_y_la_consulta(taller):
    numero = registrar(taller)
    assert avanzar(taller, numero, "En reparación")[0].status == 303
    assert (
        agregar(taller, numero, "repuesto", "Filtro de aceite", "18.000")[0].status
        == 303
    )
    assert (
        agregar(taller, numero, "repuesto", "Aceite, un litro", "32000")[0].status
        == 303
    )
    assert (
        agregar(taller, numero, "mano de obra", "Cambio de aceite", "35.000")[0].status
        == 303
    )
    assert avanzar(taller, numero, "Terminada")[0].status == 303
    _, texto = pedir(taller, "GET", f"/ordenes/{numero}")
    assert "<h2>Factura</h2>" in texto
    assert '<th colspan="4">Total sin IVA</th><td class="num">$ 85.000</td>' in texto
    assert texto.count("<tr><td>Terminada</td>") == 1  # historial
    respuesta, consulta = pedir(taller, "POST", "/consulta", {"numero": numero})
    assert respuesta.status == 200
    assert '<span class="etapa">Terminada</span>' in consulta
    assert '<th colspan="4">Total sin IVA</th><td class="num">$ 85.000</td>' in consulta
    assert "ABC12D" not in consulta  # el cliente nunca ve la placa


def test_consulta_antes_de_terminar_dice_que_no_esta_lista(taller):
    numero = registrar(taller)
    _, texto = pedir(taller, "POST", "/consulta", {"numero": numero})
    assert '<span class="etapa">Recibida</span>' in texto
    assert f'<p class="ok">{servicio.MENSAJE_NO_LISTA}</p>' in texto
    assert "Total sin IVA" not in texto


def test_cobro_de_otro_mecanico_responde_403_y_no_se_guarda(taller):
    numero = registrar(taller, mecanico="1")
    avanzar(taller, numero, "En reparación")
    respuesta, texto = agregar(
        taller, numero, "repuesto", "Guaya", "15000", mecanico="2"
    )
    assert respuesta.status == 403
    assert '<p class="error">Esta orden no está asignada a usted</p>' in texto
    assert "Guaya" not in texto


def test_terminar_sin_mano_de_obra_responde_422(taller):
    numero = registrar(taller)
    avanzar(taller, numero, "En reparación")
    respuesta, texto = avanzar(taller, numero, "Terminada")
    assert respuesta.status == 422
    assert servicio.MENSAJE_SIN_MANO_DE_OBRA in texto
    assert '<span class="etapa">En reparación</span>' in texto


@pytest.mark.parametrize(
    ("ruta", "texto_esperado"),
    [
        ("/ordenes/12345678", servicio.MENSAJE_NO_EXISTE),
        ("/ordenes/1234", "Esta página no existe."),
    ],
)
def test_orden_que_no_existe_responde_404(taller, ruta, texto_esperado):
    respuesta, texto = pedir(taller, "GET", ruta)
    assert respuesta.status == 404
    assert texto_esperado in texto


def test_consulta_de_numero_inexistente_responde_404_sin_otros_datos(taller):
    registrar(taller)
    respuesta, texto = pedir(taller, "POST", "/consulta", {"numero": "12345678"})
    assert respuesta.status == 404
    assert servicio.MENSAJE_NO_EXISTE in texto
    assert "ABC12D" not in texto


def test_sexta_consulta_seguida_responde_429(taller):
    for _ in range(5):
        assert (
            pedir(taller, "POST", "/consulta", {"numero": "12345678"})[0].status == 404
        )
    respuesta, texto = pedir(taller, "POST", "/consulta", {"numero": "12345678"})
    assert respuesta.status == 429
    assert MENSAJE_DEMASIADOS_INTENTOS in texto


def test_la_calculadora_sigue_disponible(taller):
    respuesta, texto = pedir(taller, "GET", "/calculadora")
    assert respuesta.status == 200
    assert '<form method="post" action="/cobro">' in texto


def test_observaciones_con_html_se_muestran_escapadas(taller):
    numero = registrar(taller, observaciones="<script>alert(1)</script>")
    _, texto = pedir(taller, "GET", f"/ordenes/{numero}")
    assert "<script>" not in texto
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in texto


def test_sin_base_de_datos_responde_503(taller, tmp_path):
    # Una carpeta en lugar de un archivo: SQLite no la puede abrir.
    taller.configuracion = ConfiguracionBD(
        str(tmp_path), taller.configuracion.mecanicos
    )
    assert pedir(taller, "GET", "/salud")[0].status == 503
    respuesta, texto = pedir(taller, "GET", "/")
    assert respuesta.status == 503
    assert MENSAJE_SIN_BD in texto


def test_el_registro_oculta_los_numeros_de_orden(taller, caplog):
    numero = registrar(taller)
    with caplog.at_level(logging.INFO, logger="taller.web"):
        pedir(taller, "GET", f"/ordenes/{numero}")
    mensajes = " ".join(registro.getMessage() for registro in caplog.records)
    assert "GET /ordenes/******** 200" in mensajes
    assert numero not in mensajes


# --- Configuración --------------------------------------------------------


def test_configuracion_por_defecto_usa_sqlite_y_mecanicos_ficticios():
    configuracion = leer_configuracion_bd({})
    assert configuracion.destino == "taller.db"
    assert configuracion.mecanicos == (
        Mecanico(1, "Mecánico 1"),
        Mecanico(2, "Mecánico 2"),
    )


def test_configuracion_con_postgresql_y_nombres_locales():
    configuracion = leer_configuracion_bd(
        {
            "DATABASE_URL": "postgresql://taller:clave@localhost:5432/taller",
            "TALLER_MECANICOS": " Ana Prueba ; Beto Prueba ;",
        }
    )
    assert configuracion.destino == "postgresql://taller:clave@localhost:5432/taller"
    assert [m.nombre for m in configuracion.mecanicos] == ["Ana Prueba", "Beto Prueba"]


@pytest.mark.parametrize(
    ("entorno", "mensaje"),
    [
        ({"DATABASE_URL": "mysql://x"}, "DATABASE_URL debe empezar por postgresql://"),
        ({"TALLER_MECANICOS": " ; "}, "TALLER_MECANICOS debe tener al menos un nombre"),
    ],
)
def test_configuracion_invalida_lanza_value_error(entorno, mensaje):
    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        leer_configuracion_bd(entorno)


def test_describir_destino_no_muestra_la_clave():
    texto = describir_destino("postgresql://taller:secreta@localhost:5432/taller")
    assert texto == "PostgreSQL en localhost:5432/taller"


def test_archivo_env_ignora_comentarios_y_quita_comillas(tmp_path):
    archivo = tmp_path / ".env"
    archivo.write_text(
        '# comentario\n\nTALLER_MECANICOS="Ana Prueba;Beto Prueba"\nSIN_IGUAL\n',
        encoding="utf-8",
    )
    assert cargar_archivo_env(archivo) == {"TALLER_MECANICOS": "Ana Prueba;Beto Prueba"}
    assert cargar_archivo_env(tmp_path / "no_existe.env") == {}


def test_limite_de_intentos_se_libera_al_pasar_la_ventana():
    reloj = [0.0]
    limite = LimiteDeIntentos(maximo=5, ventana=900, reloj=lambda: reloj[0])
    assert all(limite.permitir("equipo") for _ in range(5))
    assert limite.permitir("equipo") is False
    assert limite.permitir("otro equipo") is True
    reloj[0] = 900.0
    assert limite.permitir("equipo") is True


def test_main_con_base_invalida_termina_con_codigo_1(capsys):
    assert main({"TALLER_PUERTO": "8000", "DATABASE_URL": "mysql://x"}) == 1
    assert "DATABASE_URL debe empezar por postgresql://" in capsys.readouterr().err
