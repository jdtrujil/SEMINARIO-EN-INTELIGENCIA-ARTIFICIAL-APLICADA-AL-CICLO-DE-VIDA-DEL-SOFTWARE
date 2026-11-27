# Bitácora de uso de IA

Proyecto: Taller Dos Ruedas, sistema de control de ingreso de motos
Estudiante: Juan Diego Trujillo Rodriguez
Funcionalidad: HU-07 Calcular el cobro de repuestos y mano de obra, sin IVA
Asistente usado: Claude, en modo chat y agente con acceso a la terminal

## Entradas

### Entrada 1

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Con el contrato de calcular_cobro que está en el README, escribe al menos 5 pruebas en unittest: 2 normales, 2 de límite y 1 de error, con los datos del escenario 1 de la HU-07. No escribas la implementación todavía."
- **Decisión:** Aceptada
- **Por qué:** El asistente propuso 10 pruebas: 2 normales, 3 de límite (lista vacía, solo mano de obra y precio cero) y 5 de error, una de ellas con el mensaje exacto del escenario 2 de la HU-07. Todas salen del contrato y usan los datos de la orden 48271936.
- **Verificación:** Ejecuté `python -m unittest discover -v` contra la función vacía y las 10 fallaron, que es lo esperado antes de implementar.
- **Commit relacionado:** Pruebas del cálculo del cobro HU-07 (en rojo)

### Entrada 2

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Escribir las pruebas como funciones sueltas con `pytest.raises`, el estilo más común de pytest.
- **Decisión:** Rechazada
- **Por qué:** Obliga a instalar pytest en cada equipo antes de poder ejecutar las pruebas. Con unittest, que viene con Python, las pruebas corren sin instalar nada y pytest también las ejecuta si está instalado.
- **Verificación:** Las 10 pruebas pasan tanto con `python -m unittest discover -v` como con `python -m pytest -v`.
- **Commit relacionado:** Pruebas del cálculo del cobro HU-07 (en rojo)

### Entrada 3

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El prompt 1 de mi banco de la semana 2 le pedía al asistente una función que recibiera el porcentaje de IVA aplicable y redondeara el total a dos decimales.
- **Decisión:** Rechazada
- **Por qué:** El taller no cobra IVA (N-06, "no cobramos IVA") y el modelo de datos de la semana 4 guarda los valores en pesos enteros. Dejar un parámetro de IVA abre la puerta a cobrarlo por error, y los decimales no sirven para pesos colombianos.
- **Verificación:** La prueba `test_orden_con_repuestos_y_mano_de_obra_da_85000_sin_iva` exige un total exacto de 85.000 pesos; con IVA del 19 por ciento daría 101.150 y fallaría.
- **Commit relacionado:** Implementación de calcular_cobro: pruebas en verde

### Entrada 4

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Implementa calcular_cobro para que pasen estas pruebas sin modificarlas. Respeta el contrato del README: pesos enteros, sin IVA y ValueError con los mensajes exactos."
- **Decisión:** Aceptada con cambios
- **Por qué:** La primera versión validaba el precio con `if not item.precio_unitario`. En Python el 0 cuenta como falso, así que un repuesto con precio 0 se rechazaba como si no tuviera precio, lo que contradice el contrato. Cambié la condición a `if item.precio_unitario is None`.
- **Verificación:** Con la primera versión falló `test_precio_cero_se_acepta_y_no_suma` con el error "Escriba el precio del repuesto". Después del cambio pasaron las 10 pruebas.
- **Commit relacionado:** Implementación de calcular_cobro: pruebas en verde

### Entrada 5

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Con las pruebas en verde, refactoriza calcular_cobro sin cambiar su comportamiento: quita los textos repetidos y separa la validación del cálculo. No toques el archivo de pruebas."
- **Decisión:** Aceptada
- **Por qué:** Los textos "repuesto" y "mano de obra" aparecían varias veces dentro de la función y un error de escritura en uno de ellos habría pasado a las sumas sin aviso. El asistente los pasó a constantes, separó `_validar_item` y `_subtotal_por_tipo` y dejó `calcular_cobro` en pocas líneas que se leen como el contrato.
- **Verificación:** Las 10 pruebas siguen pasando y `git diff` muestra que el archivo de pruebas no cambió desde el commit en rojo.
- **Commit relacionado:** Refactor: constantes para los tipos de ítem y funciones de validación y subtotal

### Entrada 6

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El asistente propuso una tarea de VS Code que ejecutara `python -m unittest discover -v`.
- **Decisión:** Aceptada con cambios
- **Por qué:** Mi equipo usa Windows, donde Python puede estar instalado como `py` o como `python`. Ajusté la tarea para que use el que encuentre y muestre la versión antes de ejecutar las pruebas.
- **Verificación:** Ejecuté la tarea "Ejecutar pruebas" desde el menú Terminal de VS Code en mi computador y pasaron las 10 pruebas.
- **Commit relacionado:** Estructura inicial: README con el contrato de HU-07, .gitignore y tareas de VS Code

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 2 |
| Aceptadas con cambios | 2 |
| Rechazadas | 2 |

## Errores que atraparon las pruebas

La prueba de límite `test_precio_cero_se_acepta_y_no_suma` falló con la primera versión del código generado. El asistente escribió `if not item.precio_unitario` para detectar un repuesto sin precio, pero en Python `not 0` es verdadero, así que una llanta que trae el cliente, con precio 0, se rechazaba con el mensaje "Escriba el precio del repuesto". Lo corregí comparando con `None`, que es como el contrato define un precio faltante. Sin esa prueba de límite, el error habría llegado hasta el taller.

## Reflexión final

El asistente me ayudó más a convertir el contrato en pruebas concretas: en pocos minutos tuve diez casos con los datos reales de la orden 48271936, incluido el mensaje exacto de la historia. También hizo un refactor limpio que pude verificar solo con volver a correr las pruebas. El error que atraparon mis pruebas fue el del precio cero, un detalle de Python que se ve correcto al leerlo y que no habría notado sin un caso de límite. Aprendí que el asistente arrastra decisiones viejas, como el IVA del prompt de la semana 2, si no reviso el contrato contra los requisitos. En la próxima funcionalidad escribiría primero los casos de límite y le pediría al asistente que explique cada condición antes de aceptarla.
