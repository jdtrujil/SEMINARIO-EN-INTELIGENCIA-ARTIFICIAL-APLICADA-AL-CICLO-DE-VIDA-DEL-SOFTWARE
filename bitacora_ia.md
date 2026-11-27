# Bitácora de uso de IA

Proyecto: Taller Dos Ruedas, sistema de control de ingreso de motos
Estudiante: Juan Diego Trujillo Rodriguez
Funcionalidad: HU-07 Calcular el cobro de repuestos y mano de obra, sin IVA (semana 5) y su revisión de código y seguridad (semana 6)
Asistente usado: Claude, en modo chat y agente con acceso a la terminal

## Entradas de la semana 5

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

## Entradas de la semana 6

### Entrada 7

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Actúa como revisor de código senior y de seguridad. Revisa app/cobros/calculo.py y sus pruebas con estos criterios: corrección frente al contrato del README (HU-07), casos límite, validación de entradas, control de acceso según la historia, manejo de errores, legibilidad y valores mágicos. Entrega una tabla con archivo y línea, problema, categoría, severidad y corrección propuesta. Separa los problemas seguros de las sospechas. No reescribas el código."
- **Decisión:** Aceptada con cambios
- **Por qué:** De siete hallazgos, cuatro eran reales (H-03, H-04 y H-05) y tres eran falsos positivos: un KeyError que no puede ocurrir porque el tipo se valida antes, un posible XSS en un mensaje que se devuelve como texto plano y el rechazo de "Repuesto" con mayúscula, que es lo que dice el contrato. Al informe y al código solo llevé los reales.
- **Verificación:** Antes de clasificar cada hallazgo ejecuté el caso: precio 18000.5, cantidad `True`, precio "18000" y tipo "servicio" sin precio. Los resultados están en la sección 3 de `revision_seguridad.md`.
- **Commit relacionado:** Informe de revisión de código y seguridad de la semana 6

### Entrada 8

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Implementa en app/cobros/servicio.py una función registrar_item(orden, item, trabajador) que solo deje registrar cobros al mecánico asignado a la orden. Si no tiene permiso, lanza AccesoDenegado, que debe heredar de PermissionError, y no cambies la orden. Escribe primero pruebas de abuso para el registrador, un mecánico no asignado y una orden sin mecánico."
- **Decisión:** Aceptada con cambios
- **Por qué:** La lógica cumplía el diseño de la semana 4, que responde 403 si la orden no es del mecánico. Ruff marcó dos líneas largas en el código nuevo y las dividí antes del commit. Mantuve el orden propuesto, primero el permiso y después el ítem, para no darle información sobre el ítem a quien no tiene acceso.
- **Verificación:** Las pruebas nuevas fallaron antes de implementar y después pasaron las 20. Ruff quedó sin avisos.
- **Commit relacionado:** Corrige H-05: solo el mecánico asignado puede registrar cobros

### Entrada 9

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Instrucción al agente de código: "Trabaja en la rama semana-6-revision-seguridad. Corrige los hallazgos del informe, un commit por hallazgo con un mensaje que diga qué se corrigió. No modifiques ninguna prueba existente; si una corrección cambia el comportamiento, agrega pruebas nuevas en otro archivo. No integres nada a main."
- **Decisión:** Aceptada
- **Por qué:** El agente, Claude con acceso a la terminal, hizo 13 commits en su propia rama, uno por corrección, y abrió una solicitud de cambios en GitHub. Revisé el diff completo antes de integrarlo: no tocó `tests/test_calculo_cobro.py`, no subió claves ni archivos `.env` y cada commit corresponde a un hallazgo o a un paso de la tarea.
- **Verificación:** `git diff e76b374 -- tests/test_calculo_cobro.py` no muestra cambios, y GitHub Actions quedó en verde con ruff, pip-audit y las 20 pruebas.
- **Commit relacionado:** Rama semana-6-revision-seguridad, integrada a main con su solicitud de cambios

### Entrada 10

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** La IA sugirió convertir el tipo a minúsculas para aceptar "Repuesto" o "REPUESTO".
- **Decisión:** Rechazada
- **Por qué:** El contrato define los valores exactos y la API los enviará desde una lista fija. Aceptar cualquier variante escondería errores de quien llama a la función.
- **Verificación:** `test_tipo_desconocido_lanza_error` sigue pasando sin cambios.
- **Commit relacionado:** No aplica, el código no cambió

### Entrada 11

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Para dejar ruff sin avisos, el asistente propuso dividir las líneas largas de `tests/test_calculo_cobro.py`.
- **Decisión:** Rechazada
- **Por qué:** La regla del curso prohíbe modificar pruebas. Excluí la regla E501 solo para ese archivo en `pyproject.toml` y lo justifiqué en el informe.
- **Verificación:** El archivo no cambió desde la semana 5 y ruff responde "All checks passed!".
- **Commit relacionado:** Configura ruff con reglas E, F, B y S y fija las herramientas de desarrollo

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 3 |
| Aceptadas con cambios | 4 |
| Rechazadas | 4 |

## Errores que atraparon las pruebas

La prueba de límite `test_precio_cero_se_acepta_y_no_suma` falló con la primera versión del código generado. El asistente escribió `if not item.precio_unitario` para detectar un repuesto sin precio, pero en Python `not 0` es verdadero, así que una llanta que trae el cliente, con precio 0, se rechazaba con el mensaje "Escriba el precio del repuesto". Lo corregí comparando con `None`, que es como el contrato define un precio faltante. Sin esa prueba de límite, el error habría llegado hasta el taller.

En la semana 6, las 4 pruebas nuevas de `tests/test_tipos_de_datos.py` fallaron con el código anterior: 3 fallos y 1 error, porque un precio escrito como texto lanzaba TypeError en lugar de ValueError. Eso confirmó el hallazgo H-03 antes de corregirlo, y después de la corrección pasaron sin cambiar ninguna prueba.

## Reflexión final de la semana 5

El asistente me ayudó más a convertir el contrato en pruebas concretas: en pocos minutos tuve diez casos con los datos reales de la orden 48271936, incluido el mensaje exacto de la historia. También hizo un refactor limpio que pude verificar solo con volver a correr las pruebas. El error que atraparon mis pruebas fue el del precio cero, un detalle de Python que se ve correcto al leerlo y que no habría notado sin un caso de límite. Aprendí que el asistente arrastra decisiones viejas, como el IVA del prompt de la semana 2, si no reviso el contrato contra los requisitos. En la próxima funcionalidad escribiría primero los casos de límite y le pediría al asistente que explique cada condición antes de aceptarla.

## Reflexión final de la semana 6

La revisión con IA me ahorró tiempo para encontrar los casos de entrada que no había probado, como el precio con decimales o la cantidad `True`, pero tres de sus siete hallazgos eran falsos positivos y solo lo supe al ejecutar cada caso. Lo más importante, el control de acceso, salió de leer la historia de usuario y no solo el código: la función calculaba bien, pero cualquiera podía registrar cobros. La IA tampoco revisó el historial ni la configuración del repositorio, y ahí estaba el problema de `.env.example`. Trabajar al agente en una rama propia me dejó revisar todo el diff antes de integrarlo. En la próxima funcionalidad pondría la integración continua desde el primer commit.
