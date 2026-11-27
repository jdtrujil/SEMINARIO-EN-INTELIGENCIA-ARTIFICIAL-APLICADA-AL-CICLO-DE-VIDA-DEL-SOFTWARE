"""Validación de la placa de una moto al registrar su ingreso (HU-01)."""
from __future__ import annotations

import re

# Tres letras, dos números y una letra opcional: ABC12D (actual) o ABC12 (antigua).
# Se usa [A-Z] y [0-9] para no aceptar Ñ, tildes ni dígitos de otros alfabetos.
FORMATO_PLACA = re.compile(r"[A-Z]{3}[0-9]{2}[A-Z]?")
MENSAJE_FORMATO = "Placa no válida: use el formato ABC12D o, si es antigua, ABC12"


def validar_placa(placa: object) -> str:
    """Valida la placa de una moto y la devuelve normalizada.

    Acepta el formato actual (tres letras, dos números y una letra, como
    ABC12D) y el de las motos antiguas, sin la letra final (ABC12). Antes de
    validar quita los espacios a los lados y pasa las letras a mayúsculas.

    Parámetros:
        placa: el texto que escribió el registrador.

    Devuelve:
        La placa en mayúsculas y sin espacios a los lados, por ejemplo "ABC12D".

    Lanza:
        ValueError: si la placa no es texto, o si después de normalizarla no
            tiene ninguno de los dos formatos (por ejemplo ABC123, ABC-12D o
            una placa con Ñ).
    """
    if not isinstance(placa, str):
        raise ValueError("La placa debe ser texto")
    normalizada = placa.strip().upper()
    if not FORMATO_PLACA.fullmatch(normalizada):
        raise ValueError(MENSAJE_FORMATO)
    return normalizada
