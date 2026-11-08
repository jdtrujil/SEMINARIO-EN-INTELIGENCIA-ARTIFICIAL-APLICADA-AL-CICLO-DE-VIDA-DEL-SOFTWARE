'use strict';

const MENSAJE_SIN_TARIFA = 'No hay tarifa para esta zona';

/** No existe una tarifa registrada para el par de zonas (HU-02, escenario 2). */
class TarifaNoDisponibleError extends Error {
  constructor() {
    super(MENSAJE_SIN_TARIFA);
    this.name = 'TarifaNoDisponibleError';
    this.codigo = 'TARIFA_NO_DISPONIBLE';
  }
}

/** Un dato recibido no cumple el contrato (zona vacía, lista que no es lista, valor no válido). */
class DatosInvalidosError extends Error {
  constructor(mensaje) {
    super(mensaje);
    this.name = 'DatosInvalidosError';
    this.codigo = 'DATOS_INVALIDOS';
  }
}

module.exports = { TarifaNoDisponibleError, DatosInvalidosError };
