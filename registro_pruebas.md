# Registro de pruebas

Proyecto: Taller Dos Ruedas, sistema de control de ingreso de motos
Estudiante: Juan Diego Trujillo Rodriguez
Fecha: 2026-11-27
Funciones probadas: `calcular_cobro` (cálculo), `validar_placa` (validación) y `registrar_item` (permisos, varias condiciones)

## 1. Reglas y tablas de casos

Cada regla sale de la historia de usuario, de la entrevista de la semana 3 o del diseño de la semana 4. Es el oráculo: los resultados esperados salen de la regla, nunca de ejecutar el código. Todos los valores son pesos enteros, por eso ninguna prueba necesita `pytest.approx`.

### 1.1 calcular_cobro (HU-07)

**Regla.** Al cliente se le cobra la suma de cantidad por precio unitario de cada repuesto más la de cada trabajo de mano de obra, sin IVA (N-06: "no cobramos IVA"). Cada ítem es "repuesto" o "mano de obra". El precio no puede faltar y es un entero de pesos mayor o igual a 0. La cantidad es un entero mayor o igual a 1. Si un ítem rompe una regla no hay total y se informa el error con su mensaje.

**Particiones de equivalencia**

| Id | Dato | Partición | ¿Válida? | Ejemplo | Esperado |
|---|---|---|---|---|---|
| P1 | Lista | Vacía | Sí | sin ítems | 0, 0 y 0 |
| P2 | Lista | Solo repuestos | Sí | filtro 1 x 18.000 | repuestos 18.000, mano de obra 0, total 18.000 |
| P3 | Lista | Solo mano de obra | Sí | mano de obra 1 x 35.000 | 0, 35.000 y 35.000 |
| P4 | Lista | Repuestos y mano de obra | Sí | filtro 18.000, aceite 32.000 y mano de obra 35.000 | 50.000, 35.000 y 85.000 (escenario 1 de la HU-07) |
| P5 | Tipo | Texto distinto | No | "servicio" | ValueError: Tipo de ítem no válido: servicio. Use repuesto o mano de obra |
| P6 | Tipo | Con mayúscula | No | "Repuesto" | ValueError del tipo (el contrato fija los valores exactos) |
| P7 | Precio | Falta, en repuesto | No | sin precio | ValueError: Escriba el precio del repuesto |
| P8 | Precio | Falta, en mano de obra | No | sin precio | ValueError: Escriba el valor de la mano de obra |
| P9 | Precio | Negativo | No | -5.000 | ValueError: El precio no puede ser negativo |
| P10 | Precio | Cero | Sí | 0 | suma 0 |
| P11 | Precio | Positivo | Sí | 18.000 | se suma |
| P12 | Precio | Con decimales | No | 18000.5 | ValueError: El precio debe ser un número entero de pesos |
| P13 | Precio | Texto | No | "18000" | el mismo ValueError |
| P14 | Cantidad | Cero o menos | No | 0 y -1 | ValueError: La cantidad debe ser al menos 1 |
| P15 | Cantidad | Uno o más | Sí | 2 litros a 32.000 | repuestos 64.000 |
| P16 | Cantidad | Con decimales | No | 1.5 | ValueError: La cantidad debe ser un número entero |
| P17 | Cantidad | Verdadero o falso | No | True | el mismo ValueError |
| P18 | Precio | Decimal con parte decimal cero | No | 18000.0 | ValueError: El precio debe ser un número entero de pesos (agregada por la mutación M5) |
| P19 | Cantidad | Decimal con parte decimal cero | No | 2.0 | ValueError: La cantidad debe ser un número entero (agregada por la mutación M5) |

**Valores límite**

| Id | Borde | Último valor de una partición | Primero de la siguiente |
|---|---|---|---|
| L1 | Precio negativo y no negativo | -1: ValueError | 0: válido, suma 0 |
| L2 | Precio cero y positivo | 0: suma 0 | 1: suma 1 |
| L3 | Cantidad inválida y válida | 0: ValueError | 1: válido |

### 1.2 validar_placa (HU-01)

**Regla.** La placa de una moto en Colombia tiene tres letras, dos números y una letra, como ABC12D (HU-01 y banco de prompts de la semana 2). Las motos antiguas tienen la placa sin la letra final, como ABC12, y también se reciben (registrador en la entrevista: "hay motos viejas que tienen la placa sin la letra al final. Esas también las recibimos"). La función devuelve la placa en mayúsculas y sin espacios a los lados; cualquier otro formato se rechaza con ValueError.

**Particiones de equivalencia**

| Id | Partición | ¿Válida? | Ejemplo | Esperado |
|---|---|---|---|---|
| V1 | Formato actual | Sí | ABC12D | ABC12D |
| V2 | Formato antiguo | Sí | MOT09 | MOT09 |
| V3 | En minúsculas | Sí (A1) | abc12d | ABC12D |
| V4 | Con espacios a los lados | Sí (A2) | " QWE45R " | QWE45R |
| I1 | Vacía | No | "" | ValueError |
| I2 | Solo espacios | No | "   " | ValueError |
| I3 | Formato de carro: tres letras y tres números | No | ABC123 | ValueError |
| I4 | Letras y números en otro orden | No | 12ABCD | ValueError |
| I5 | Con guion o espacio en medio | No (A2) | ABC-12D y "ABC 12D" | ValueError |
| I6 | Con Ñ o tilde | No (A3) | ÑAB12C | ValueError |
| I7 | No es texto | No | None y 12345 | ValueError: La placa debe ser texto |

**Valores límite**

| Id | Borde | Último valor de una partición | Primero de la siguiente |
|---|---|---|---|
| L4 | Longitud 4 y 5 | ABC1: ValueError | ABC12: válida |
| L5 | Longitud 6 y 7 | ABC12D: válida | ABC12DE: ValueError |
| L6 | Cantidad de números | ABC1D, un número: ValueError | ABC12D, dos números: válida |
| L7 | Cantidad de números | ABC12D, dos números: válida | ABC123, tres números: ValueError |
| L8 | Letras iniciales | AB12C, dos letras: ValueError | ABC12, tres letras: válida |

### 1.3 registrar_item (HU-07, diseño de la semana 4 y hallazgo H-05)

**Regla.** Solo un mecánico puede registrar cobros, y solo en una orden asignada a él (el diseño responde 403 en otro caso). Primero se verifica el rol, después la asignación y por último el ítem. Si algo falla, la orden no cambia. Si todo está bien, el ítem se agrega a la orden y se devuelven los totales.

**Tabla de decisión completa**

| Condición o acción | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C1. El trabajador es mecánico | Sí | Sí | Sí | Sí | No | No | No | No |
| C2. La orden está asignada a ese trabajador | Sí | Sí | No | No | Sí | Sí | No | No |
| C3. El ítem es válido | Sí | No | Sí | No | Sí | No | Sí | No |
| Registra y devuelve totales | X | | | | | | | |
| ValueError del ítem | | X | | | | | | |
| AccesoDenegado: Esta orden no está asignada a usted | | | X | X | | | | |
| AccesoDenegado: Solo un mecánico puede registrar cobros | | | | | X | X | X | X |
| La orden queda igual | | X | X | X | X | X | X | X |

**Tabla simplificada** (el guion significa que la condición no importa)

| Regla | C1 | C2 | C3 | Resultado |
|---|---|---|---|---|
| R1 | No | - | - | AccesoDenegado por rol; la orden no cambia |
| R2 | Sí | No | - | AccesoDenegado por asignación; la orden no cambia |
| R3 | Sí | Sí | No | ValueError del ítem; la orden no cambia |
| R4 | Sí | Sí | Sí | Agrega el ítem y devuelve los totales |

C2 es "No" en dos situaciones distintas que se prueban por separado: la orden tiene otro mecánico y la orden no tiene mecánico. Las columnas 5 y 6 (no es mecánico, pero su id coincide con el de la orden) no pasan en el taller, porque cada trabajador tiene un id único; se prueban para comprobar que el rol se verifica antes que la asignación.

### 1.4 Ambigüedades de las reglas

| Id | Ambigüedad | Decisión provisional | Con quién se valida |
|---|---|---|---|
| A1 | ¿Una placa escrita en minúsculas se rechaza o se corrige? | Se convierte a mayúsculas, como pedía el prompt del formulario de la semana 2 | Cliente, pregunta P-08 |
| A2 | ¿Se aceptan placas con guion o con espacio en medio? | Solo se quitan los espacios a los lados; guion y espacio en medio se rechazan | Cliente, pregunta P-08 |
| A3 | ¿Una placa puede tener Ñ o letras con tilde? | No: se usa el alfabeto de la A a la Z | Cliente, pregunta P-08 |
| A4 | ¿Cuál es el formato exacto de las placas antiguas? | Tres letras y dos números, como dijo el registrador | Cliente, pregunta P-08 |
| A5 | ¿Un ítem de cobro puede tener la descripción vacía? | La regla no dice nada, así que hoy se acepta; una prueba con datos sintéticos lo documenta | Cliente, pregunta nueva P-11 |
| A6 | ¿Hay un precio máximo para evitar errores de digitación, como 320.000 en vez de 32.000? | No hay límite superior porque nadie lo pidió | Cliente, pregunta nueva P-12 |

### 1.5 Revisión de la propuesta de casos de la IA

Le pedí a la IA casos para las tres reglas, nombrando las técnicas (bitácora, entrada 23). Revisé su propuesta con las cinco preguntas de la semana:

| Pregunta | Qué encontré | Qué hice |
|---|---|---|
| ¿Están todas las particiones, incluidas las inválidas? | Faltaban mano de obra sin valor, tipo con mayúscula, precio en texto, cantidad con decimales y booleana; en placas faltaban espacios, solo espacios, Ñ y datos que no son texto; en permisos faltaba la orden sin mecánico | Agregué P6, P8, P13, P16, P17, V4, I2, I6, I7 y las columnas 5 a 8 de la tabla de decisión |
| ¿Cada borde tiene sus dos valores? | Los bordes del precio y la cantidad estaban bien; en placas faltaban los bordes de cuántos números y cuántas letras | Agregué L6, L7 y L8 |
| ¿El esperado sale de la regla? | Proponía que "abc12d" fuera un error, lo que contradice la decisión de convertir a mayúsculas | Lo cambié a V3: devuelve ABC12D |
| ¿Señaló ambigüedades? | Ninguna | Las anoté yo: A1 a A6 |
| ¿Inventó reglas? | Cuatro: descripción obligatoria, precio máximo de 10.000.000, cantidad máxima de 100 y quitar el guion de la placa | Las descarté como casos; las dos primeras quedaron como ambigüedades A5 y A6 para preguntar al cliente |

## 2. Pruebas de la IA corregidas, descartadas o agregadas

La IA escribió un borrador de pruebas con pytest a partir de las reglas y de la tabla revisada (commit 47b4e8a, bitácora entrada 26). Las 70 pasaban, pero apliqué a cada una las tres preguntas: (1) ¿el esperado sale de la regla?, (2) ¿fallaría si rompo el código?, (3) ¿cubre algo que otra prueba no cubre? La versión revisada está en el commit 3051ed9.

| # | Prueba del borrador | Pregunta que no pasó | Decisión | Razón | Qué hice en su lugar |
|---|---|---|---|---|---|
| 1 | `test_calcula_totales_sin_iva`, fila "L1 primer valor no negativo" | 3 | Descartada | Misma entrada y mismo esperado que la fila P10 (precio 0) | La fila P10 ahora dice "P10 y L1" |
| 2 | `test_calcula_totales_sin_iva`, fila "L3 cantidad mínima" | 3 | Descartada | Idéntica a la fila P2, que ya usa cantidad 1 | La fila P2 ahora dice "P2 y L3" |
| 3 | `test_total_es_la_suma_de_los_subtotales` | 1 y 2 | Descartada | El esperado salía del mismo código: si el cálculo sumara IVA a todo, la prueba seguiría pasando | Los totales exactos de P4 (50.000, 35.000 y 85.000) salen de la regla |
| 4 | `test_items_invalidos_lanzan_error` | 2 | Corregida | `pytest.raises(Exception)` acepta cualquier error, incluso el TypeError del hallazgo H-03 de la semana 6, y no revisa el mensaje | `pytest.raises(ValueError, match=...)` con el mensaje exacto de la regla en cada fila |
| 5 | Fila P9 con precio -5.000 | 3 | Descartada | Misma partición que -1, y -1 además prueba el borde | Fila "P9 y L1: -1" |
| 6 | Fila P14 con cantidad -1 | 3 | Descartada | Misma partición que 0, y 0 es el borde | Fila "P14 y L3: cero" |
| 7 | `test_orden_con_datos_sinteticos` | 1 y 2 | Corregida | Comparaba el total con la suma de los subtotales que da el mismo código | Esperado calculado a mano: 195.000, 65.000 y 260.000 |
| 8 | `test_placas_validas`, fila "L5 longitud 6" (ABC12D) | 3 | Descartada | Idéntica a la fila V1 | V1 cubre L5, L6 y L7 |
| 9 | `test_placas_validas`, fila "L4 longitud 5" (ABC12) | 3 | Descartada | Misma partición que V2: placa antigua de 5 caracteres | V2 (MOT09) cubre L4 y L8 |
| 10 | `test_placas_invalidas` | 2 | Corregida | No tenía comentario por fila, como exige la tarea, y solo revisaba el tipo de error | Comentario con la partición o el límite de cada fila y `match` con el mensaje de formato |
| 11 | `test_placa_none` | 2 | Corregida | No revisaba el mensaje y faltaba el número 12345 de la partición I7 | Parametrizada con None y 12345 y el mensaje "La placa debe ser texto" |
| 12 | `test_placas_sinteticas` | 2 | Corregida | `assert validar_placa(...)` solo comprueba que devuelva algo, y saltaba las placas inválidas | Dos pruebas: las válidas se comparan con la placa exacta y las inválidas exigen el ValueError |
| 13 | `test_tabla_de_decision`, columna 1 | 2 | Corregida | `assert resumen.total > 0` pasaría con IVA o con cualquier total | Prueba propia que exige `ResumenCobro(18000, 0, 18000)` y que la orden tenga el ítem |
| 14 | `test_tabla_de_decision`, columnas 2 a 8 | 2 | Corregida | No revisaba qué AccesoDenegado salía ni que la orden quedara igual; agregar el ítem antes de validarlo habría pasado | `match` con el mensaje de rol o de asignación y `orden.items == []`. La mutación M6 confirmó que ahora falla |
| 15 | `test_tabla_de_decision` | Diseño | Corregida | Tenía un if dentro de la prueba que decidía qué comprobar | Una prueba para el éxito y otra parametrizada para los rechazos |
| 16 | Faltaba | 1 | Agregada | La tabla separa la orden sin mecánico y el borrador no la probaba | Fila "C2 sin mecánico" |
| 17 | Faltaba | 2 | Agregada | La mutación M5 sobrevivió: nada probaba un decimal con parte decimal cero | Filas P18 (18000.0) y P19 (2.0), commit a138743 |

**Resumen:** de 70 pruebas del borrador se descartaron 7 filas o pruebas, se corrigieron 8 y se agregaron 3 filas. La suite final de la semana 7 tiene 50 pruebas, y con las 20 de las semanas 5 y 6 son 70.

**Ningún esperado se ajustó al código.** Ninguna prueba falló contra el código, así que no hubo que decidir entre corregir el código o la prueba, y no apareció ningún defecto nuevo. Donde una prueba no fallaba al romper el código, se agregó el caso.

## 3. Romper el código a propósito

Cada error se introdujo solo, se corrieron todas las pruebas con `pytest` y se deshizo con `git restore`. Las líneas son las de la rama `semana-7-pruebas`.

| # | Error introducido | Archivo y línea | Pruebas que fallaron | Resultado |
|---|---|---|---|---|
| M1 | `precio_unitario < 0` cambia a `<= 0`, así que el precio 0 se rechaza | app/cobros/calculo.py:77 | 4: la de precio cero de la semana 5, la fila P10 y L1 y las dos de datos sintéticos | Atrapado |
| M2 | El total se multiplica por 1,19, como si se cobrara IVA | app/cobros/calculo.py:55 | 12 de las semanas 5, 6 y 7 | Atrapado |
| M3 | La verificación de permisos siempre deja pasar (`return` al inicio) | app/cobros/servicio.py:40 | 11: tres pruebas de abuso de la semana 6 y ocho de la tabla de decisión | Atrapado |
| M4 | La placa acepta uno o dos números (`[0-9]{1,2}`) | app/ingresos/placas.py:8 | 2: ABC1 (L4) y ABC1D (L6) | Atrapado |
| M5 | `_es_entero` acepta decimales con parte decimal cero, como 18000.0 | app/cobros/calculo.py:97 | Ninguna | No atrapado: se agregaron P18 y P19; con ellas fallan 2 pruebas |
| M6 | El ítem se agrega a la orden antes de validarlo | app/cobros/servicio.py:38 | 2: la de la semana 6 y la columna 2 de la tabla de decisión | Atrapado |
| M7 | La placa no se pasa a mayúsculas | app/ingresos/placas.py:32 | 2: la fila V3 (abc12d) y la de placas sintéticas válidas | Atrapado |

## 4. Datos de prueba sintéticos

**Origen.** Los generó Claude el 2026-11-27 con este prompt: "Genera datos sintéticos para las pruebas de un taller de motos en Colombia: seis ítems de cobro (repuestos y mano de obra) y seis motos con placa, marca, cliente y teléfono. Sin personas reales y con teléfonos ficticios con 555. Incluye tildes, ñ, apóstrofo, texto vacío, un precio en cero y placas en minúsculas, con espacios, con guion y con Ñ. Para cada placa indica la placa esperada según la regla, o null si es inválida." Revisé cada placa esperada contra la regla de la sección 1.2 y cada total a mano. Ningún nombre corresponde a una persona real ni a mí ni a mi familia.

**Contexto local.** Repuestos comunes en motos de Colombia (piñón, guaya del clutch, kit de arrastre), las marcas que atiende el taller (Bajaj, AKT, Honda, Yamaha, Kymco y Suzuki), placas con el formato colombiano y teléfonos celulares de 10 dígitos.

| Caso difícil | Dónde aparece |
|---|---|
| Tildes | "Sincronización y revisión eléctrica", María, Ángel, Sofía |
| Ñ | "Piñón de arrastre", Begoña Ñáñez, Muñoz, Peñaloza y la placa ÑKY12C |
| Apóstrofo | "Kit de arrastre D'Luca (marca ficticia)" y José D'Alessandro |
| Texto vacío | Descripción de una mano de obra (ambigüedad A5), un cliente y una placa vacíos |
| Valores en cero | "Llanta trasera que trajo el cliente" con precio 0 |
| Placas difíciles | akt45m en minúsculas, " HND08 " antigua con espacios y YMH-34K con guion |

**Fixture.** `tests/datos/datos_sinteticos.json` se carga en `tests/conftest.py` con las fixtures `datos_sinteticos`, `items_sinteticos` y `motos_sinteticas`. Las usan cuatro pruebas: la orden sintética que suma 260.000, las placas sintéticas válidas e inválidas, el registrador que no puede registrar cobros y el mecánico que registra toda la orden.

## 5. Cómo ejecutar

```
pip install -r requirements-dev.txt
python -m pytest -v
```

Resultado: 70 pruebas en verde. GitHub Actions las corre en cada envío junto con ruff y pip-audit.
