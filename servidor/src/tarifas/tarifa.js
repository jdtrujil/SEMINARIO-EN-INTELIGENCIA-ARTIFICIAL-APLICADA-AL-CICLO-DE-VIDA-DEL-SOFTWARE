'use strict';

const { TarifaNoDisponibleError, DatosInvalidosError } = require('./errores');

const PREFIJO_TARIFA = 'Tarifa: $';
const SEPARADOR_MILES = '.';
const DIGITOS_POR_GRUPO = 3;

function validarZona(zona, nombre) {
  if (typeof zona !== 'string' || zona.trim() === '') {
    throw new DatosInvalidosError(`La zona de ${nombre} debe ser un texto con contenido`);
  }
}

/**
 * Devuelve el valor en pesos de la tarifa del par ordenado (zonaOrigen, zonaDestino).
 * Lanza TarifaNoDisponibleError si no hay tarifa y DatosInvalidosError si los datos no cumplen el contrato.
 */
function obtenerTarifa(zonaOrigen, zonaDestino, tarifas) {
  validarZona(zonaOrigen, 'origen');
  validarZona(zonaDestino, 'destino');
  if (!Array.isArray(tarifas)) {
    throw new DatosInvalidosError('Las tarifas deben ser una lista');
  }

  const tarifa = tarifas.find((t) => t.zonaOrigen === zonaOrigen && t.zonaDestino === zonaDestino);
  if (!tarifa) {
    throw new TarifaNoDisponibleError();
  }
  return tarifa.valor;
}

// Se agrega el punto a mano para que el resultado no dependa del idioma configurado en el servidor.
function agregarSeparadorMiles(entero) {
  const grupos = new RegExp(`\\B(?=(\\d{${DIGITOS_POR_GRUPO}})+(?!\\d))`, 'g');
  return String(entero).replace(grupos, SEPARADOR_MILES);
}

/** Devuelve el texto de pantalla de la tarifa, por ejemplo «Tarifa: $9.500». */
function formatearTarifa(valor) {
  if (!Number.isInteger(valor) || valor <= 0) {
    throw new DatosInvalidosError('La tarifa debe ser un número entero mayor que cero');
  }
  return `${PREFIJO_TARIFA}${agregarSeparadorMiles(valor)}`;
}

// Se reexportan los errores para que quien use el módulo solo importe este archivo.
module.exports = { obtenerTarifa, formatearTarifa, TarifaNoDisponibleError, DatosInvalidosError };
