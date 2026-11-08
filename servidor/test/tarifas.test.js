'use strict';

const { describe, test } = require('node:test');
const assert = require('node:assert/strict');
const {
  obtenerTarifa,
  formatearTarifa,
  TarifaNoDisponibleError,
  DatosInvalidosError,
} = require('../src/tarifas/tarifa');

// Datos de ejemplo de HU-02: Centro a Norte cuesta $9.500. Oriente no tiene tarifa.
const TARIFAS = [
  { zonaOrigen: 'Centro', zonaDestino: 'Norte', valor: 9500 },
  { zonaOrigen: 'Norte', zonaDestino: 'Centro', valor: 9000 },
  { zonaOrigen: 'Centro', zonaDestino: 'Sur', valor: 7000 },
  { zonaOrigen: 'Centro', zonaDestino: 'Centro', valor: 5000 },
  { zonaOrigen: 'Sur', zonaDestino: 'Norte', valor: 12000 },
];

function esTarifaNoDisponible(error) {
  return (
    error instanceof TarifaNoDisponibleError &&
    error.message === 'No hay tarifa para esta zona' &&
    error.codigo === 'TARIFA_NO_DISPONIBLE'
  );
}

describe('obtenerTarifa: casos normales (HU-02, escenario 1)', () => {
  test('devuelve 9500 para un viaje de Centro a Norte', () => {
    assert.equal(obtenerTarifa('Centro', 'Norte', TARIFAS), 9500);
  });

  test('la tarifa depende del sentido: de Norte a Centro vale 9000', () => {
    assert.equal(obtenerTarifa('Norte', 'Centro', TARIFAS), 9000);
  });
});

describe('obtenerTarifa: casos límite', () => {
  test('encuentra la tarifa cuando es la primera de la lista', () => {
    assert.equal(obtenerTarifa('Centro', 'Norte', TARIFAS), TARIFAS[0].valor);
  });

  test('encuentra la tarifa cuando es la última de la lista', () => {
    assert.equal(obtenerTarifa('Sur', 'Norte', TARIFAS), 12000);
  });

  test('acepta origen y destino iguales cuando existe esa tarifa', () => {
    assert.equal(obtenerTarifa('Centro', 'Centro', TARIFAS), 5000);
  });

  test('con la lista de tarifas vacía lanza TarifaNoDisponibleError', () => {
    assert.throws(() => obtenerTarifa('Centro', 'Norte', []), esTarifaNoDisponible);
  });

  test('no modifica la lista de tarifas que recibe', () => {
    const copia = JSON.parse(JSON.stringify(TARIFAS));
    obtenerTarifa('Centro', 'Norte', TARIFAS);
    assert.deepEqual(TARIFAS, copia);
  });
});

describe('obtenerTarifa: casos de error (HU-02, escenario 2)', () => {
  test('un viaje que sale de Oriente, sin tarifa, lanza «No hay tarifa para esta zona»', () => {
    assert.throws(() => obtenerTarifa('Oriente', 'Centro', TARIFAS), esTarifaNoDisponible);
  });

  test('si el origen tiene tarifas pero no hacia ese destino, también lanza TarifaNoDisponibleError', () => {
    assert.throws(() => obtenerTarifa('Centro', 'Oriente', TARIFAS), esTarifaNoDisponible);
  });

  test('una zona vacía lanza DatosInvalidosError', () => {
    assert.throws(() => obtenerTarifa('', 'Norte', TARIFAS), DatosInvalidosError);
  });

  test('una zona que no es texto lanza DatosInvalidosError', () => {
    assert.throws(() => obtenerTarifa('Centro', undefined, TARIFAS), DatosInvalidosError);
  });

  test('si tarifas no es una lista lanza DatosInvalidosError', () => {
    assert.throws(() => obtenerTarifa('Centro', 'Norte', null), DatosInvalidosError);
  });
});

describe('formatearTarifa', () => {
  test('muestra «Tarifa: $9.500» para 9500 (HU-02, escenario 1)', () => {
    assert.equal(formatearTarifa(9500), 'Tarifa: $9.500');
  });

  test('límite del separador de miles: 999 no lleva punto y 1000 sí', () => {
    assert.equal(formatearTarifa(999), 'Tarifa: $999');
    assert.equal(formatearTarifa(1000), 'Tarifa: $1.000');
  });

  test('separa los millones con punto', () => {
    assert.equal(formatearTarifa(1250000), 'Tarifa: $1.250.000');
  });

  test('cero, negativos, decimales y no numéricos lanzan DatosInvalidosError', () => {
    for (const invalido of [0, -9500, 9500.5, NaN, '9500', null]) {
      assert.throws(() => formatearTarifa(invalido), DatosInvalidosError, `valor: ${String(invalido)}`);
    }
  });
});
