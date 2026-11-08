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
  if (typeof zonaOrigen !== 'string' || zonaOrigen.trim() === '') {
    throw new DatosInvalidosError('La zona de origen debe ser un texto con contenido');
  }
  if (typeof zonaDestino !== 'string' || zonaDestino.trim() === '') {
    throw new DatosInvalidosError('La zona de destino debe ser un texto con contenido');
  }
  if (!Array.isArray(tarifas)) {
    throw new DatosInvalidosError('Las tarifas deben ser una lista');
  }
  const fila = tarifas.find((t) => t.zonaOrigen === zonaOrigen && t.zonaDestino === zonaDestino);
  if (!fila) {
    throw new TarifaNoDisponibleError();
  }
  return fila.valor;
}

function formatearTarifa(valor) {
  if (!Number.isInteger(valor) || valor <= 0) {
    throw new DatosInvalidosError('La tarifa debe ser un número entero mayor que cero');
  }
  return `Tarifa: $${valor.toLocaleString('es-CO')}`;
}

module.exports = { obtenerTarifa, formatearTarifa, TarifaNoDisponibleError, DatosInvalidosError };
