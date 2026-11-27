"""Errores propios del módulo de cobros."""


class AccesoDenegado(PermissionError):
    """El trabajador no tiene permiso para la operación que intentó.

    Hereda de PermissionError para que la API la traduzca a HTTP 403
    (documento de diseño, sección 6).
    """
