# Bitácora de uso de IA

Proyecto: RutaYa, aplicación de transporte bajo demanda en moto para una cooperativa de mototaxis
Estudiante: Juan Diego Trujillo
Funcionalidad: HU-02 Ver la tarifa estimada antes de confirmar el viaje
Asistente usado: Claude (Anthropic), chat con ejecución de código

> **REVISAR antes de entregar:** este borrador se armó con lo que ocurrió en la sesión de trabajo con el
> asistente. Confirma que cada entrada corresponde a decisiones que tú tomaste (o cámbialas si decidiste otra
> cosa), reescribe la reflexión final con tus palabras y borra esta nota.

## Entradas

### Entrada 1

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «Con el contrato de HU-02 y sus dos escenarios, propón pruebas normales, de límite y de error para `obtenerTarifa` y `formatearTarifa`.» El asistente propuso las pruebas del archivo y, al plantearlas, contempló además dos de normalización de mayúsculas y espacios.
- **Decisión:** Aceptada con cambios
- **Por qué:** Esas dos pruebas comprobarían que `'centro'` y `' Centro '` encuentren la tarifa de Centro. Las descarté antes de escribirlas porque el supuesto 2 del contrato dice que los nombres de zona vienen de la tabla `Zona` y se comparan tal cual; probarlo habría pedido una función que el contrato no promete. Dejé 16 pruebas y mantuve la de «no modifica la lista de tarifas».
- **Verificación:** Cada prueba quedó ligada a un escenario de HU-02, a un caso límite o al contrato; con el esqueleto, `npm test` mostró 16 pruebas fallando por sus aserciones.
- **Commit relacionado:** `2bdebd4` Pruebas de tarifa por zona, HU-02 (en rojo)

### Entrada 2

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso dejar un esqueleto de `tarifa.js` con las dos clases de error ya definidas y las dos funciones lanzando «No implementado», antes de escribir las pruebas.
- **Decisión:** Aceptada
- **Por qué:** Si el archivo no existiera, el commit en rojo fallaría por «módulo no encontrado» y no por lo que las pruebas esperan. Con el esqueleto cada prueba falla por su propia aserción.
- **Verificación:** `npm test` con el esqueleto dio 16 fallos, ninguno por `MODULE_NOT_FOUND`.
- **Commit relacionado:** `f22e3ec` Contrato de HU-02 en el README y esqueleto del módulo

### Entrada 3

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Al plantear el contrato, el asistente consideró guardar las tarifas como un objeto con clave concatenada (`{ 'Centro->Norte': 9500 }`) para buscar sin recorrer la lista.
- **Decisión:** Rechazada
- **Por qué:** No coincide con la entidad `Tarifa` del modelo de datos del diseño (una fila por par de zonas, con `zona_origen_id`, `zona_destino_id` y `valor`), y una zona con «->» en el nombre rompería la clave. Con unas pocas zonas, `Array.find` es suficiente y más simple.
- **Verificación:** Comparé el contrato con la sección 5 del documento de diseño; las pruebas usan filas `{ zonaOrigen, zonaDestino, valor }` como las que devolvería la tabla.
- **Commit relacionado:** `f22e3ec` Contrato de HU-02 en el README y esqueleto del módulo

### Entrada 4

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «Implementa `obtenerTarifa` y `formatearTarifa` para que pasen estas pruebas, sin modificarlas.» El primer borrador usaba `tarifas.find(...)` y `valor.toLocaleString('es-CO')`, sin validar datos.
- **Decisión:** Aceptada con cambios
- **Por qué:** La búsqueda con `find` y el lanzamiento de `TarifaNoDisponibleError` eran correctos, pero el borrador pasaba 12 de 16 pruebas. Agregué la validación de zonas, de la lista y del valor que pide el contrato.
- **Verificación:** `npm test` mostró 12 aprobadas y 4 fallidas; después de los cambios, 16 de 16. `git diff 2bdebd4 -- servidor/test` salió vacío: no toqué ninguna prueba.
- **Commit relacionado:** `80d976a` Implementación de obtenerTarifa y formatearTarifa, HU-02 (pruebas en verde)

### Entrada 5

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «Refactoriza con las pruebas en verde: nombres, valores mágicos y duplicación.» El asistente propuso mover los errores a `errores.js`, extraer `validarZona()` y pasar los textos y números sueltos a constantes.
- **Decisión:** Aceptada
- **Por qué:** La validación de origen y de destino estaba escrita dos veces, y el prefijo «Tarifa: $», el punto y el 3 aparecían sueltos. El contrato no cambia, porque `tarifa.js` reexporta los errores.
- **Verificación:** 16 de 16 pruebas en verde con el archivo de pruebas idéntico al del commit en rojo; revisé a mano que 999, 1000, 100000 y 12345678 se formatearan bien.
- **Commit relacionado:** `8418e0d` Refactor del módulo de tarifas

### Entrada 6

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Mantener `toLocaleString('es-CO')` para poner el punto de los miles, como en el primer borrador.
- **Decisión:** Rechazada
- **Por qué:** Funciona en este Node, pero el resultado depende de los datos regionales de la máquina donde corra el servidor; en una instalación con datos reducidos mostraría «9,500» o «9500». Para una pantalla que el pasajero lee antes de pagar, preferí un formato que no cambie con el entorno.
- **Verificación:** Reemplacé la llamada por `agregarSeparadorMiles()` y las tres pruebas de formato siguieron pasando.
- **Commit relacionado:** `8418e0d` Refactor del módulo de tarifas

### Entrada 7

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso un `.gitignore` que excluya `.env` y `.env.*` (con la excepción `.env.example`) y `node_modules/` desde el primer commit.
- **Decisión:** Aceptada
- **Por qué:** La regla del curso prohíbe subir claves o archivos `.env`. Esta funcionalidad no usa secretos, pero el servidor los usará (base de datos, Google Maps), así que conviene dejar la regla desde el inicio.
- **Verificación:** `git ls-files | grep -i env` no devuelve nada; el repositorio no contiene claves.
- **Commit relacionado:** `f22e3ec` Contrato de HU-02 en el README y esqueleto del módulo

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 3 |
| Aceptadas con cambios | 2 |
| Rechazadas | 2 |

## Errores que atraparon las pruebas

El primer borrador de la implementación pasaba 12 de las 16 pruebas. Las cuatro que fallaron mostraron errores reales:

- **«una zona vacía lanza DatosInvalidosError»** y **«una zona que no es texto…»**: `obtenerTarifa('', 'Norte', ...)` respondía «No hay tarifa para esta zona». Confundía un dato mal escrito con una zona que de verdad no tiene tarifa. Se corrigió con `validarZona()`.
- **«si tarifas no es una lista…»**: con `null` el código fallaba con un `TypeError` de JavaScript («Cannot read properties of null»). Se corrigió comprobando `Array.isArray`.
- **«cero, negativos, decimales y no numéricos…»**: `formatearTarifa(0)` devolvía «Tarifa: $0», `formatearTarifa(9500.5)` devolvía «Tarifa: $9.500,5» y `formatearTarifa('9500')` devolvía «Tarifa: $9500» sin punto, sin avisar de nada. Se corrigió aceptando solo enteros mayores que cero.

## Reflexión final (5 a 8 líneas)

El asistente me ayudó más a ver los casos antes de programar: a partir de los dos escenarios de HU-02 salieron límites que yo no había escrito, como la lista vacía, la primera y la última tarifa, el 999 contra el 1.000 y los valores inválidos. Las pruebas atraparon que el primer borrador trataba una zona vacía como «sin tarifa» y que `formatearTarifa` aceptaba 0, decimales y texto; sin ellas el pasajero habría visto «Tarifa: $0» sin ningún aviso. Si solo hubiera leído el código, el borrador me habría parecido correcto. La próxima vez escribiré el contrato de los datos inválidos antes del primer prompt, para no descubrirlos cuando ya hay código, y revisaré también las dependencias del entorno, como pasó con el formato regional del número.
