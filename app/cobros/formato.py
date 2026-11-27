"""Formato de valores en pesos colombianos para mostrar al cliente."""


def pesos(valor: int) -> str:
    """Formatea un valor en pesos con punto de miles, por ejemplo 85.000.

    Parámetros:
        valor: un número entero de pesos.

    Devuelve:
        El valor con punto como separador de miles, sin el signo $.
    """
    return f"{valor:,}".replace(",", ".")
