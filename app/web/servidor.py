"""Servidor web local del Taller Dos Ruedas, solo con la biblioteca estándar.

Uso: python -m app.web y abrir http://127.0.0.1:8000 en el navegador.
Variables opcionales: TALLER_HOST (por defecto 127.0.0.1, solo este equipo)
y TALLER_PUERTO (por defecto 8000).

Rutas:
    GET  /        formulario de la placa y del cobro
    GET  /salud   responde "ok" si el servidor está arriba (para operación)
    POST /placa   valida la placa (HU-01)
    POST /cobro   calcula el cobro sin IVA (HU-07)
"""

from __future__ import annotations

import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Dict, Mapping, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from app.web.paginas import (
    Formulario,
    Respuesta,
    pagina_error,
    pagina_inicio,
    pagina_no_encontrada,
    procesar_cobro,
    procesar_placa,
)

HOST_POR_DEFECTO = "127.0.0.1"
PUERTO_POR_DEFECTO = 8000
# Un formulario de cobro lleno ocupa menos de 2 KB; más de esto se rechaza.
TAMANO_MAXIMO = 10_000
MAXIMO_CAMPOS = 50
CABECERAS_SEGURIDAD = {
    "Content-Security-Policy": (
        "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
        "frame-ancestors 'none'; base-uri 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}
RUTAS_POST: Dict[str, Callable[[Formulario], Respuesta]] = {
    "/placa": procesar_placa,
    "/cobro": procesar_cobro,
}

registro = logging.getLogger("taller.web")


class ManejadorTaller(BaseHTTPRequestHandler):
    """Atiende cada petición; no guarda nada entre peticiones."""

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
        if ruta == "/":
            self._responder(200, pagina_inicio())
        elif ruta == "/salud":
            self._responder(200, "ok", tipo="text/plain; charset=utf-8")
        else:
            self._responder(404, pagina_no_encontrada())

    def do_POST(self) -> None:
        procesar = RUTAS_POST.get(urlsplit(self.path).path)
        if procesar is None:
            self._responder(404, pagina_no_encontrada())
            return
        formulario = self._leer_formulario()
        if formulario is not None:
            codigo, cuerpo = procesar(formulario)
            self._responder(codigo, cuerpo)

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

    def _responder(
        self, codigo: int, cuerpo: str, tipo: str = "text/html; charset=utf-8"
    ) -> None:
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        for nombre, valor in CABECERAS_SEGURIDAD.items():
            self.send_header(nombre, valor)
        self.end_headers()
        self.wfile.write(datos)

    def log_request(self, code: object = "-", size: object = "-") -> None:
        # Solo método, ruta y código: nunca el contenido del formulario.
        registro.info("%s %s %s", self.command, urlsplit(self.path).path, code)

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


def crear_servidor(host: str, puerto: int) -> ThreadingHTTPServer:
    """Crea el servidor sin arrancarlo. Con puerto 0 el sistema elige uno libre."""
    return ThreadingHTTPServer((host, puerto), ManejadorTaller)


def main(entorno: Optional[Mapping[str, str]] = None) -> int:
    """Arranca el servidor hasta Ctrl+C. Devuelve el código de salida."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    try:
        host, puerto = leer_configuracion(os.environ if entorno is None else entorno)
        servidor = crear_servidor(host, puerto)
    except (ValueError, OSError) as error:
        print(f"No se pudo iniciar el servidor: {error}", file=sys.stderr)
        print(
            "Si el puerto está ocupado, use otro: TALLER_PUERTO=8001", file=sys.stderr
        )
        return 1
    print(f"Taller Dos Ruedas en http://{host}:{puerto}  (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
    finally:
        servidor.server_close()
    return 0
