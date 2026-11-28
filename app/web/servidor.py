"""Servidor web del Taller Dos Ruedas, con la biblioteca estándar de Python.

Uso: python -m app.web y abrir http://127.0.0.1:8000 en el navegador.

Configuración, por variables de entorno o en un archivo .env local que nunca
se sube al repositorio:
    TALLER_HOST        por defecto 127.0.0.1 (solo este equipo)
    TALLER_PUERTO      por defecto 8000
    DATABASE_URL       postgresql://usuario:clave@localhost:5432/taller
                       (ADR-001); sin ella se usa un archivo SQLite
    TALLER_BD_ARCHIVO  archivo SQLite, por defecto taller.db
    TALLER_MECANICOS   nombres separados por punto y coma; por defecto
                       "Mecánico 1;Mecánico 2"
    TALLER_NOMBRE      nombre del taller en el encabezado
    TALLER_LOGO        imagen del logo (PNG, JPG, WEBP o SVG); por defecto
                       marca/logo.png, y si no existe, el emblema genérico

Rutas:
    GET  /                      ingreso de motos y lista del taller
    POST /ordenes               registra el ingreso (HU-01, HU-02, HU-03, HU-05)
    GET  /ordenes/<número>      orden, cobro, factura e historial
    POST /ordenes/<número>/etapa    pasa a la etapa siguiente (HU-06)
    POST /ordenes/<número>/items    registra repuesto o mano de obra (HU-07)
    GET  /consulta, POST /consulta  consulta del cliente (HU-04, HU-08)
    GET  /calculadora           calculadora de cobro sin guardar datos
    POST /placa, POST /cobro    validan la placa y calculan el cobro
    GET  /salud                 "ok" si el servidor y la base responden
    GET  /logo, /estaticos/...  logo, estilos y JavaScript de la interfaz
"""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Deque, Dict, Mapping, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from app.ordenes.modelos import Mecanico, ahora
from app.ordenes.repositorio import Repositorio, abrir, es_postgres
from app.web import taller
from app.web.paginas import (
    NOMBRE_POR_DEFECTO,
    Formulario,
    Respuesta,
    pagina_error,
    pagina_inicio,
    pagina_no_encontrada,
    procesar_cobro,
    procesar_placa,
    configurar_marca,
)

HOST_POR_DEFECTO = "127.0.0.1"
PUERTO_POR_DEFECTO = 8000
ARCHIVO_BD_POR_DEFECTO = "taller.db"
MECANICOS_POR_DEFECTO = "Mecánico 1;Mecánico 2"
LOGO_POR_DEFECTO = "marca/logo.png"
CARPETA_ESTATICOS = Path(__file__).parent / "estaticos"
# Solo se sirven estos archivos: nada que venga de la ruta llega al disco.
ESTATICOS = {
    "estilos.css": "text/css; charset=utf-8",
    "app.js": "text/javascript; charset=utf-8",
    "emblema.svg": "image/svg+xml",
}
TIPOS_LOGO = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}
# Un formulario de cobro lleno ocupa menos de 2 KB; más de esto se rechaza.
TAMANO_MAXIMO = 10_000
MAXIMO_CAMPOS = 50
# ADR-002: 5 consultas del cliente cada 15 minutos por equipo.
INTENTOS_CONSULTA = 5
VENTANA_CONSULTA = 15 * 60
MENSAJE_DEMASIADOS_INTENTOS = (
    "Demasiados intentos. Espere 15 minutos y vuelva a consultar"
)
MENSAJE_SIN_BD = "No se pudo usar la base de datos. Revise que esté encendida"
CABECERAS_SEGURIDAD = {
    "Content-Security-Policy": (
        "default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}
RUTAS_POST: Dict[str, Callable[[Formulario], Respuesta]] = {
    "/placa": procesar_placa,
    "/cobro": procesar_cobro,
}
_RUTA_ORDEN = re.compile(r"/ordenes/([0-9]{8})(/etapa|/items)?")
_NUMERO_EN_RUTA = re.compile(r"[0-9]{8}")

registro = logging.getLogger("taller.web")


@dataclass(frozen=True)
class ConfiguracionBD:
    """Dónde se guardan los datos y qué mecánicos tiene el taller."""

    destino: str
    mecanicos: Tuple[Mecanico, ...]
    nombre: str = NOMBRE_POR_DEFECTO
    logo: str = LOGO_POR_DEFECTO


class LimiteDeIntentos:
    """Cuenta intentos por equipo en una ventana de tiempo (ADR-002)."""

    def __init__(
        self,
        maximo: int = INTENTOS_CONSULTA,
        ventana: float = VENTANA_CONSULTA,
        reloj: Callable[[], float] = time.monotonic,
    ) -> None:
        self._maximo = maximo
        self._ventana = ventana
        self._reloj = reloj
        self._intentos: Dict[str, Deque[float]] = {}
        self._candado = threading.Lock()

    def permitir(self, clave: str) -> bool:
        """Registra un intento y dice si todavía está dentro del límite."""
        ahora_s = self._reloj()
        with self._candado:
            intentos = self._intentos.setdefault(clave, deque())
            while intentos and ahora_s - intentos[0] >= self._ventana:
                intentos.popleft()
            if len(intentos) >= self._maximo:
                return False
            intentos.append(ahora_s)
            return True


class ServidorTaller(ThreadingHTTPServer):
    """Servidor con la configuración de la base y el límite de consultas."""

    def __init__(self, direccion: Tuple[str, int], configuracion: ConfiguracionBD):
        self.configuracion = configuracion
        self.limite = LimiteDeIntentos()
        super().__init__(direccion, ManejadorTaller)


class ManejadorTaller(BaseHTTPRequestHandler):
    """Atiende cada petición. Abre la base solo en las rutas que la usan."""

    server: ServidorTaller
    # No anunciar la versión de Python en la cabecera Server.
    server_version = "TallerDosRuedas"
    sys_version = ""
    # Una conexión que no envía nada en 15 segundos se cierra.
    timeout = 15

    def version_string(self) -> str:
        """Cabecera Server sin la versión de Python ni espacios de sobra."""
        return self.server_version

    # do_GET y do_POST son los nombres que exige http.server.
    def do_GET(self) -> None:
        ruta = urlsplit(self.path).path
        orden = _RUTA_ORDEN.fullmatch(ruta)
        if ruta == "/salud":
            self._salud()
        elif ruta.startswith("/estaticos/"):
            self._estatico(ruta[len("/estaticos/") :])
        elif ruta == "/logo":
            self._logo()
        elif ruta == "/calculadora":
            self._responder(200, pagina_inicio())
        elif ruta == "/consulta":
            self._web(taller.consulta())
        elif ruta == "/":
            self._con_bd(taller.panel)
        elif orden and orden.group(2) is None:
            numero = orden.group(1)
            self._con_bd(lambda repo: taller.ver_orden(repo, numero))
        else:
            self._responder(404, pagina_no_encontrada())

    def do_POST(self) -> None:
        ruta = urlsplit(self.path).path
        procesar = RUTAS_POST.get(ruta)
        orden = _RUTA_ORDEN.fullmatch(ruta)
        accion_orden = orden.group(2) if orden else None
        if (
            procesar is None
            and ruta not in ("/ordenes", "/consulta")
            and not accion_orden
        ):
            self._responder(404, pagina_no_encontrada())
            return
        formulario = self._leer_formulario()
        if formulario is None:
            return
        if procesar is not None:
            codigo, cuerpo = procesar(formulario)
            self._responder(codigo, cuerpo)
        elif ruta == "/ordenes":
            self._con_bd(lambda repo: taller.registrar(repo, formulario, ahora()))
        elif ruta == "/consulta":
            if not self.server.limite.permitir(self.client_address[0]):
                aviso = f'<p class="error">{MENSAJE_DEMASIADOS_INTENTOS}</p>'
                self._web(taller.consulta(aviso, codigo=429))
                return
            self._con_bd(lambda repo: taller.consultar(repo, formulario))
        elif orden is not None and accion_orden == "/etapa":
            numero = orden.group(1)
            self._con_bd(lambda repo: taller.avanzar(repo, numero, formulario, ahora()))
        elif orden is not None:
            numero = orden.group(1)
            self._con_bd(lambda repo: taller.agregar_item(repo, numero, formulario))

    def _con_bd(self, accion: Callable[[Repositorio], taller.RespuestaWeb]) -> None:
        """Abre la base, ejecuta la acción y responde; si la base falla, da 503."""
        try:
            with abrir(self.server.configuracion.destino) as repo:
                respuesta = accion(repo)
        except Exception as error:  # la base no responde o falló la consulta
            registro.error("Error de base de datos: %s", type(error).__name__)
            self._responder(503, pagina_error(MENSAJE_SIN_BD))
            return
        self._web(respuesta)

    def _salud(self) -> None:
        try:
            with abrir(self.server.configuracion.destino) as repo:
                repo.comprobar()
        except Exception as error:  # la base no responde
            registro.error("Salud sin base de datos: %s", type(error).__name__)
            self._responder(503, "sin base de datos", tipo="text/plain; charset=utf-8")
            return
        self._responder(200, "ok", tipo="text/plain; charset=utf-8")

    def _estatico(self, nombre: str) -> None:
        tipo = ESTATICOS.get(nombre)
        if tipo is None:
            self._responder(404, pagina_no_encontrada())
            return
        self._enviar(200, (CARPETA_ESTATICOS / nombre).read_bytes(), tipo)

    def _logo(self) -> None:
        """El logo del taller configurado en el equipo, o el emblema genérico."""
        archivo = Path(self.server.configuracion.logo)
        tipo = TIPOS_LOGO.get(archivo.suffix.lower())
        if tipo is not None and archivo.is_file():
            self._enviar(200, archivo.read_bytes(), tipo)
        else:
            self._estatico("emblema.svg")

    def _leer_formulario(self) -> Optional[Formulario]:
        """Lee el formulario enviado o responde el error y devuelve None."""
        try:
            largo = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._responder(411, pagina_error("Falta el tamaño del formulario."))
            return None
        if largo < 0 or largo > TAMANO_MAXIMO:
            # Se lee lo justo para responder sin dejar al navegador esperando.
            self.rfile.read(min(max(largo, 0), TAMANO_MAXIMO + 1))
            self._responder(413, pagina_error("El formulario es demasiado grande."))
            return None
        cuerpo = self.rfile.read(largo).decode("utf-8", errors="replace")
        try:
            return parse_qs(
                cuerpo, keep_blank_values=True, max_num_fields=MAXIMO_CAMPOS
            )
        except ValueError:
            self._responder(413, pagina_error("El formulario tiene demasiados campos."))
            return None

    def _web(self, respuesta: taller.RespuestaWeb) -> None:
        if respuesta.ubicacion is not None:
            self._responder(respuesta.codigo, "", ubicacion=respuesta.ubicacion)
        else:
            self._responder(respuesta.codigo, respuesta.cuerpo)

    def _responder(
        self,
        codigo: int,
        cuerpo: str,
        tipo: str = "text/html; charset=utf-8",
        ubicacion: Optional[str] = None,
    ) -> None:
        self._enviar(codigo, cuerpo.encode("utf-8"), tipo, ubicacion)

    def _enviar(
        self, codigo: int, datos: bytes, tipo: str, ubicacion: Optional[str] = None
    ) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        if ubicacion is not None:
            self.send_header("Location", ubicacion)
        for nombre, valor in CABECERAS_SEGURIDAD.items():
            self.send_header(nombre, valor)
        self.end_headers()
        self.wfile.write(datos)

    def log_request(self, code: object = "-", size: object = "-") -> None:
        # Solo método, ruta y código: nunca el contenido del formulario. Los
        # números de orden se ocultan porque son la llave de la consulta.
        ruta = _NUMERO_EN_RUTA.sub("********", urlsplit(self.path).path)
        registro.info("%s %s %s", self.command, ruta, code)

    def log_message(self, format: str, *args: object) -> None:
        registro.warning(format, *args)


def leer_configuracion(entorno: Mapping[str, str]) -> Tuple[str, int]:
    """Lee el host y el puerto de las variables de entorno.

    Lanza:
        ValueError: si TALLER_PUERTO no es un número entre 1 y 65535.
    """
    host = entorno.get("TALLER_HOST", HOST_POR_DEFECTO)
    texto = entorno.get("TALLER_PUERTO", str(PUERTO_POR_DEFECTO))
    if not texto.isdigit() or not 1 <= int(texto) <= 65535:
        raise ValueError("TALLER_PUERTO debe ser un número entre 1 y 65535")
    return host, int(texto)


def leer_configuracion_bd(entorno: Mapping[str, str]) -> ConfiguracionBD:
    """Lee dónde guardar los datos y los nombres de los mecánicos.

    Lanza:
        ValueError: si DATABASE_URL no es de PostgreSQL o no hay mecánicos.
    """
    url = entorno.get("DATABASE_URL", "").strip()
    if url and not es_postgres(url):
        raise ValueError("DATABASE_URL debe empezar por postgresql://")
    destino = url or entorno.get("TALLER_BD_ARCHIVO", ARCHIVO_BD_POR_DEFECTO)
    nombres = [
        nombre.strip()
        for nombre in entorno.get("TALLER_MECANICOS", MECANICOS_POR_DEFECTO).split(";")
        if nombre.strip()
    ]
    if not nombres:
        raise ValueError("TALLER_MECANICOS debe tener al menos un nombre")
    mecanicos = tuple(Mecanico(i, nombre) for i, nombre in enumerate(nombres, start=1))
    nombre_taller = entorno.get("TALLER_NOMBRE", "").strip() or NOMBRE_POR_DEFECTO
    logo = entorno.get("TALLER_LOGO", "").strip() or LOGO_POR_DEFECTO
    return ConfiguracionBD(destino, mecanicos, nombre_taller, logo)


def describir_destino(destino: str) -> str:
    """Describe la base sin mostrar el usuario ni la contraseña."""
    if es_postgres(destino):
        partes = urlsplit(destino)
        return f"PostgreSQL en {partes.hostname}:{partes.port or 5432}{partes.path}"
    return f"archivo SQLite {destino}"


def cargar_archivo_env(ruta: Path) -> Dict[str, str]:
    """Lee un archivo .env con líneas NOMBRE=valor; ignora comentarios y vacías."""
    valores: Dict[str, str] = {}
    if not ruta.is_file():
        return valores
    # utf-8-sig: el Bloc de notas puede guardar el archivo con BOM al comienzo.
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre, valor = linea.split("=", 1)
        valores[nombre.strip()] = valor.strip().strip('"').strip("'")
    return valores


def preparar_bd(configuracion: ConfiguracionBD) -> None:
    """Crea las tablas si faltan y guarda los nombres de los mecánicos."""
    with abrir(configuracion.destino) as repo:
        repo.crear_tablas()
        repo.guardar_mecanicos(configuracion.mecanicos)


def crear_servidor(
    host: str, puerto: int, entorno: Optional[Mapping[str, str]] = None
) -> ServidorTaller:
    """Prepara la base y crea el servidor sin arrancarlo.

    Con puerto 0 el sistema elige uno libre. Sin entorno usa os.environ.
    """
    configuracion = leer_configuracion_bd(os.environ if entorno is None else entorno)
    preparar_bd(configuracion)
    configurar_marca(configuracion.nombre)
    return ServidorTaller((host, puerto), configuracion)


def main(entorno: Optional[Mapping[str, str]] = None) -> int:
    """Arranca el servidor hasta Ctrl+C. Devuelve el código de salida."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    if entorno is None:
        # Las variables del sistema tienen prioridad sobre el archivo .env.
        entorno = {**cargar_archivo_env(Path(".env")), **os.environ}
    try:
        host, puerto = leer_configuracion(entorno)
        servidor = crear_servidor(host, puerto, entorno)
    except ImportError:
        print(
            "No se pudo iniciar el servidor: falta psycopg para PostgreSQL. "
            "Instálelo con: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1
    except Exception as error:  # puerto, configuración o base de datos
        print(f"No se pudo iniciar el servidor: {error}", file=sys.stderr)
        print(
            "Si el puerto está ocupado, use otro: TALLER_PUERTO=8001", file=sys.stderr
        )
        return 1
    print(f"Base de datos: {describir_destino(servidor.configuracion.destino)}")
    print(f"Taller Dos Ruedas en http://{host}:{puerto}  (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
    finally:
        servidor.server_close()
    return 0
