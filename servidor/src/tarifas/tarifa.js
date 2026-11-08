'use strict';

class TarifaNoDisponibleError extends Error {
  constructor() {
    super('No hay tarifa para esta zona');
    this.name = 'TarifaNoDisponibleError';
    this.codigo = 'TARIFA_NO_DISPONIBLE';
  }
}

class DatosInvalidosError extends Error {
  constructor(mensaje) {
    super(mensaje);
    this.name = 'DatosInvalidosError';
    this.codigo = 'DATOS_INVALIDOS';
  }
}

function obtenerTarifa(zonaOrigen, zonaDestino, tarifas) {
  throw new Error('No implementado');
}

function formatearTarifa(valor) {
  throw new Error('No implementado');
}

module.exports = { obtenerTarifa, formatearTarifa, TarifaNoDisponibleError, DatosInvalidosError };
