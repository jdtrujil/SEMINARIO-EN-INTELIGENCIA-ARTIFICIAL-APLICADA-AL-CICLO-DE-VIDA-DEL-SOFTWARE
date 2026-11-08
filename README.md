# RutaYa

Aplicación de transporte bajo demanda en moto para una cooperativa de mototaxis de 60 conductores
(proyecto final del seminario *Inteligencia Artificial Aplicada al Ciclo de Vida del Software*; cliente y
cifras ficticios). El diseño completo está en el documento de diseño de la semana 4: monolito modular en
Node.js con API REST, PostgreSQL y Google Maps como único sistema externo (ADR-001).

## Estructura

| Carpeta | Contenido |
|---|---|
| `servidor/src/` | Código del servidor (monolito modular, un módulo por carpeta). |
| `servidor/src/tarifas/` | Módulo de tarifas por zona (HU-02). |
| `servidor/test/` | Pruebas automatizadas. |
| `bitacora_ia.md` | Bitácora de uso del asistente de IA. |

## Funcionalidad de la semana 5

### Historia de usuario

**HU-02** (prioridad Must, necesidad N-02). *Como pasajero, quiero ver la tarifa estimada antes de confirmar
el viaje para saber cuánto voy a pagar.*

Criterios de aceptación:

- **Escenario 1: tarifa por zona.** Dado que la tarifa de la zona Centro a la zona Norte es $9.500, cuando
  «Laura Gil» pide un viaje de Centro a Norte, entonces la pantalla muestra «Tarifa: $9.500» antes del botón
  «Confirmar».
- **Escenario 2 (error): zona sin tarifa.** Dado que la zona Oriente no tiene tarifa registrada, cuando
  «Laura Gil» pide un viaje que sale de Oriente, entonces el sistema muestra «No hay tarifa para esta zona» y
  no permite confirmar el viaje.

### Contrato

Módulo: `servidor/src/tarifas/tarifa.js` (JavaScript, Node.js 20 o superior, sin dependencias).

```js
/** Fila de la entidad Tarifa del modelo de datos: una por cada par ordenado de zonas. */
// typedef Tarifa = { zonaOrigen: string, zonaDestino: string, valor: number }

obtenerTarifa(zonaOrigen: string, zonaDestino: string, tarifas: Tarifa[]): number
formatearTarifa(valor: number): string
```

**`obtenerTarifa`**

- **Recibe:** el nombre de la zona de origen, el nombre de la zona de destino y la lista de tarifas vigentes
  (las filas de la tabla `Tarifa`).
- **Devuelve:** el `valor` en pesos colombianos (entero positivo) de la tarifa de ese par de zonas.
- **Errores:**
  - `TarifaNoDisponibleError` (mensaje «No hay tarifa para esta zona», `codigo: 'TARIFA_NO_DISPONIBLE'`) si no
    hay una fila para ese par de zonas. Es el escenario 2 de HU-02; en la API corresponde a `404` en
    `GET /tarifas`.
  - `DatosInvalidosError` (`codigo: 'DATOS_INVALIDOS'`) si una zona no es un texto con contenido o si
    `tarifas` no es una lista.

**`formatearTarifa`**

- **Recibe:** un valor en pesos.
- **Devuelve:** el texto que se muestra en pantalla, con punto como separador de miles: `Tarifa: $9.500`.
- **Errores:** `DatosInvalidosError` si el valor no es un número entero mayor que cero.

**Supuestos**

1. La tarifa depende del sentido: Centro→Norte y Norte→Centro son filas distintas y pueden tener valores
   distintos. La tabla completa de tarifas sigue pendiente con el cliente (P-01).
2. Los nombres de zona vienen de la tabla `Zona`, así que se comparan tal cual (distingue mayúsculas, sin
   recortar espacios).
3. La función no consulta la base de datos ni modifica la lista que recibe; quien la llama le pasa las tarifas.
4. La base de datos garantiza una sola fila por par de zonas; si hubiera repetidas, se usa la primera.
5. Origen y destino pueden ser la misma zona si existe esa tarifa.

**Casos límite**

- Lista de tarifas vacía.
- La tarifa buscada es la primera o la última de la lista.
- Origen igual al destino.
- Valores de `formatearTarifa` en el borde del separador de miles (999 y 1.000) y en cero.

**Ejemplos**

| Llamada | Resultado |
|---|---|
| `obtenerTarifa('Centro', 'Norte', tarifas)` con Centro→Norte = 9500 | `9500` |
| `obtenerTarifa('Norte', 'Centro', tarifas)` con Norte→Centro = 9000 | `9000` |
| `obtenerTarifa('Oriente', 'Centro', tarifas)` sin filas de Oriente | lanza `TarifaNoDisponibleError`: «No hay tarifa para esta zona» |
| `obtenerTarifa('', 'Norte', tarifas)` | lanza `DatosInvalidosError` |
| `formatearTarifa(9500)` | `'Tarifa: $9.500'` |
| `formatearTarifa(1250000)` | `'Tarifa: $1.250.000'` |
| `formatearTarifa(0)` | lanza `DatosInvalidosError` |

### Cómo ejecutar las pruebas

Requiere Node.js 20 o superior. No hay que instalar nada: usa el ejecutor de pruebas incluido en Node.

```bash
npm test
```
