# Bitácora de uso de IA

Proyecto: Taller Dos Ruedas, sistema de control de ingreso de motos
Estudiante: Juan Diego Trujillo Rodriguez
Funcionalidad: HU-07 Calcular el cobro de repuestos y mano de obra, sin IVA (semana 5) y su revisión de código y seguridad (semana 6)
Asistente usado: Claude, en modo chat y agente con acceso a la terminal

## Recorrido del uso de IA en el proyecto, semanas 2 a 6

Antes de escribir código, el proyecto ya usaba IA en cada entrega. El detalle de cada prompt está en esos documentos; aquí queda el resumen para tener todo el recorrido en un solo lugar.

| Semana | Entregable | Cómo se usó la IA | Qué se corrigió o se decidió |
|---|---|---|---|
| 2 | Trujillo_Juan_S2_Banco: banco de 10 prompts evaluados | Diez prompts con Claude para la función de cobro, el código heredado, la documentación, los requisitos, la base de datos, las pruebas, el formulario, las observaciones, el control de acceso y la auditoría | Dos prompts subieron de 3 a 5 al agregar formato y restricciones. Se quitó el IVA del cálculo y se agregó la consulta del cliente con el número de orden |
| 3 | Trujillo_Juan_S3_Requisitos y Trujillo_Juan_S3_Bitacora | Seis prompts: guion de entrevista, entrevista simulada (declarada como simulada), necesidades, historias con criterios Gherkin, revisión de defectos y modelo de dominio | Se detectaron 5 requisitos inventados, 5 ambigüedades, 2 contradicciones y 5 omisiones. Lo que no tenía cita pasó a preguntas pendientes |
| 4 | Trujillo_Juan_S4_Diseno: documento de diseño | Cinco prompts: alternativas de arquitectura, diagrama de contexto, diagrama de contenedores, modelo de datos y API | Se descartaron microservicios, Kubernetes y Redis por sobreingeniería. Se eligió el monolito modular (ADR-001) y la consulta con número aleatorio y límite de intentos (ADR-002) |
| 5 | Este repositorio: HU-07 | Entradas 1 a 6 de esta bitácora | Pruebas primero, implementación, refactor y un error del precio cero que atrapó una prueba de límite |
| 6 | Este repositorio: revisión de código y seguridad | Entradas 7 a 22 de esta bitácora | Ocho hallazgos corregidos, uno por commit, en la rama del agente |

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
- **Prompt o sugerencia:** "Actúa como revisor de código senior y de seguridad. Revisa app/cobros/calculo.py y sus pruebas con estos criterios: corrección frente al contrato del README (HU-07), casos límite, validación de entradas, control de acceso según la historia, manejo de errores, legibilidad y valores mágicos. Entrega una tabla con archivo y línea, problema, categoría, severidad y corrección propuesta. Separa los problemas seguros de las sospechas. No reescribas el código." Revisión hecha sobre el commit e76b374.
- **Decisión:** Aceptada con cambios
- **Por qué:** De siete hallazgos, cuatro eran reales (H-03, H-04 y H-05) y tres eran falsos positivos: un KeyError que no puede ocurrir porque el tipo se valida antes, un posible XSS en un mensaje que se devuelve como texto plano y el rechazo de "Repuesto" con mayúscula, que es lo que dice el contrato. Al informe y al código solo llevé los reales.
- **Verificación:** Antes de clasificar cada hallazgo ejecuté el caso: precio 18000.5, cantidad `True`, precio "18000" y tipo "servicio" sin precio. Los resultados están en la sección 3 de `revision_seguridad.md`.
- **Commit relacionado:** 44d5bd0 Informe de revisión de código y seguridad de la semana 6

### Entrada 8

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso configurar ruff en `pyproject.toml` con las reglas E, F, B y S y crear `requirements-dev.txt` con ruff 0.16.9 y pip-audit 2.7.3 fijados.
- **Decisión:** Aceptada
- **Por qué:** Es lo que pide el paso 1 de la tarea. Fijar las versiones evita que el linter cambie de reglas entre un equipo y otro. El sistema no tiene dependencias en tiempo de ejecución, así que solo se fijan las herramientas de revisión.
- **Verificación:** La primera ejecución de `ruff check --select E,F,B,S .` mostró 10 avisos E501: 2 en `calculo.py` y 8 en las pruebas de la semana 5.
- **Commit relacionado:** ea32a15 Configura ruff con reglas E, F, B y S y fija las herramientas de desarrollo

### Entrada 9

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Para dejar ruff sin avisos, el agente propuso dividir las líneas largas de `tests/test_calculo_cobro.py`.
- **Decisión:** Rechazada
- **Por qué:** La regla del curso prohíbe modificar pruebas. Excluí la regla E501 solo para ese archivo en `pyproject.toml` y lo justifiqué en el informe.
- **Verificación:** El archivo no cambió desde la semana 5 (`git diff e76b374 -- tests/test_calculo_cobro.py` vacío) y ruff responde "All checks passed!".
- **Commit relacionado:** ea32a15 Configura ruff con reglas E, F, B y S y fija las herramientas de desarrollo

### Entrada 10

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso dividir las dos líneas largas de `calculo.py` (líneas 61 y 72) sin cambiar su contenido (hallazgo H-01).
- **Decisión:** Aceptada
- **Por qué:** Era solo formato: el mensaje de error y la suma quedaron iguales.
- **Verificación:** Ruff sin avisos en `calculo.py` y las 10 pruebas siguen pasando.
- **Commit relacionado:** 8df8f4b Corrige E501: divide las dos líneas largas de calculo.py

### Entrada 11

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso crear `.env.example` con `DATABASE_URL` y `JWT_SECRET`, las variables que usará la API según el diseño de la semana 4 (hallazgo H-02).
- **Decisión:** Aceptada con cambios
- **Por qué:** Al crearlo, `git check-ignore` mostró que el patrón `.env.*` de `.gitignore` también ignoraba `.env.example`, así que se habría quedado fuera del repositorio. Agregué la excepción `!.env.example`. Los valores son de ejemplo, no claves reales.
- **Verificación:** `git ls-files` muestra `.env.example` en el repositorio y un `.env` de prueba siguió ignorado.
- **Commit relacionado:** a9a2ada Agrega .env.example y evita que .gitignore lo excluya

### Entrada 12

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso validar que cantidad y precio sean enteros con una función `_es_entero` que excluye `True` y `False`, y escribir primero cuatro pruebas nuevas en `tests/test_tipos_de_datos.py` (hallazgo H-03).
- **Decisión:** Aceptada
- **Por qué:** El contrato dice que los valores son pesos enteros, y la revisión mostró que un precio de 18000.5 daba un total con decimales. Las pruebas van en un archivo nuevo para no tocar las de la semana 5.
- **Verificación:** Las cuatro pruebas nuevas fallaron con el código anterior (3 fallos y 1 error) y pasaron después de la corrección, junto con las otras 10.
- **Commit relacionado:** 4d79e2f Corrige H-03: cantidad y precio deben ser enteros

### Entrada 13

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** La IA sugirió convertir el tipo a minúsculas para aceptar "Repuesto" o "REPUESTO".
- **Decisión:** Rechazada
- **Por qué:** El contrato define los valores exactos y la API los enviará desde una lista fija. Aceptar cualquier variante escondería errores de quien llama a la función.
- **Verificación:** `test_tipo_desconocido_lanza_error` sigue pasando sin cambios.
- **Commit relacionado:** No aplica, el código no cambió

### Entrada 14

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso que el mensaje "La cantidad debe ser al menos 1" use la constante `CANTIDAD_MINIMA` en lugar del 1 escrito a mano (hallazgo H-04).
- **Decisión:** Aceptada
- **Por qué:** Si la cantidad mínima cambia algún día, el mensaje cambia con ella. El texto que ve el usuario sigue igual.
- **Verificación:** `test_cantidad_cero_lanza_error`, que compara el mensaje exacto, sigue pasando.
- **Commit relacionado:** 7cc174a Corrige H-04: el mensaje de cantidad mínima usa la constante CANTIDAD_MINIMA

### Entrada 15

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso sacar `ItemCobro`, `ResumenCobro` y los tipos de ítem a `app/cobros/modelos.py`, y reexportarlos desde `calculo.py` para no romper las importaciones existentes (hallazgo H-07).
- **Decisión:** Aceptada
- **Por qué:** El control de acceso necesitaba los modelos sin depender del cálculo. Con la reexportación, las pruebas de la semana 5 siguen importando desde `calculo.py` sin cambios.
- **Verificación:** Las 14 pruebas que había en ese momento pasaron sin modificarlas y ruff quedó sin avisos.
- **Commit relacionado:** ec2a9cc Refactor: separa los modelos del cálculo en app/cobros/modelos.py

### Entrada 16

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Implementa en app/cobros/servicio.py una función registrar_item(orden, item, trabajador) que solo deje registrar cobros al mecánico asignado a la orden. Si no tiene permiso, lanza AccesoDenegado, que debe heredar de PermissionError, y no cambies la orden. Escribe primero pruebas de abuso para el registrador, un mecánico no asignado y una orden sin mecánico." (hallazgo H-05)
- **Decisión:** Aceptada con cambios
- **Por qué:** La lógica cumplía el diseño de la semana 4, que responde 403 si la orden no es del mecánico. Ruff marcó dos líneas largas en el código nuevo y las dividí antes del commit. Mantuve el orden propuesto, primero el permiso y después el ítem, para no darle información sobre el ítem a quien no tiene acceso.
- **Verificación:** Las pruebas nuevas fallaron antes de implementar y después pasaron las 20. Ruff quedó sin avisos.
- **Commit relacionado:** ebddbcc Corrige H-05: solo el mecánico asignado puede registrar cobros

### Entrada 17

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso docstrings para `calcular_cobro`, `_validar_item`, `_es_entero`, `_subtotal_por_tipo` y `registrar_item` con qué hacen, qué reciben, qué devuelven y qué lanzan (hallazgo H-08).
- **Decisión:** Aceptada
- **Por qué:** La tarea pide docstrings en las funciones principales. Comparé cada uno con el código: el orden de las validaciones, el caso de lista vacía, que la lista no se modifica y que `True` y `False` no cuentan como enteros.
- **Verificación:** Revisé cada afirmación del docstring contra una prueba que la cubre; las 20 pruebas siguen pasando.
- **Commit relacionado:** 963b1b5 Docstrings con qué hace, qué recibe, qué devuelve y qué lanza cada función del cálculo

### Entrada 18

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso un ejemplo ejecutable, `python -m app.cobros`, que registra los ítems del escenario 1 de la HU-07 y muestra el acceso denegado a otro mecánico.
- **Decisión:** Aceptada con cambios
- **Por qué:** El README necesita un comando de ejecución que funcione. Ruff marcó una línea de 90 caracteres en `__main__.py` y la dividí.
- **Verificación:** La salida muestra repuestos 50.000, mano de obra 35.000, total sin IVA 85.000 y el acceso denegado del mecánico 2.
- **Commit relacionado:** db614e5 Agrega un ejemplo ejecutable: python -m app.cobros

### Entrada 19

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso un flujo de GitHub Actions que corra ruff, pip-audit, las pruebas y el ejemplo en cada envío, con permisos de solo lectura (hallazgo H-06).
- **Decisión:** Aceptada
- **Por qué:** pip-audit necesita internet para consultar la base de vulnerabilidades, y GitHub Actions lo corre en un equipo limpio en cada envío.
- **Verificación:** La ejecución 46039574878 terminó en verde: ruff "All checks passed!", pip-audit "No known vulnerabilities found" y "Ran 20 tests ... OK".
- **Commit relacionado:** 5848e88 Integración continua: ruff, pip-audit, pruebas y ejemplo en cada envío

### Entrada 20

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso reescribir el README con las ocho secciones de la semana y agregar la licencia MIT.
- **Decisión:** Aceptada
- **Por qué:** La tarea pide qué es, requisitos, instalación, ejecución, pruebas, estructura, uso de IA, y autor y licencia. El contrato de la HU-07 se actualizó con los dos errores de tipo nuevos para que coincida con el código.
- **Verificación:** Cloné el repositorio en una carpeta limpia y corrí `python -m app.cobros`, `python -m unittest discover -v` y `ruff check --select E,F,B,S .`; los tres funcionaron. La instalación de `requirements-dev.txt` la prueba GitHub Actions en cada envío.
- **Commit relacionado:** 89a98e6 README con las ocho secciones y licencia MIT

### Entrada 21

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso llenar `revision_seguridad.md` con la plantilla de la tarea: herramientas, los cinco puntos de seguridad, ocho hallazgos con línea y commit, la revisión con IA y los pendientes.
- **Decisión:** Aceptada
- **Por qué:** Cada fila sale de un commit real de la rama, y lo que la IA no encontró (el problema de `.env.example` y la revisión del historial) quedó separado.
- **Verificación:** Comprobé las líneas citadas contra el commit revisado e76b374 y que cada commit de la tabla existe en la rama.
- **Commit relacionado:** 44d5bd0 Informe de revisión de código y seguridad de la semana 6

### Entrada 22

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Instrucción al agente de código: "Trabaja en la rama semana-6-revision-seguridad. Corrige los hallazgos del informe, un commit por hallazgo con un mensaje que diga qué se corrigió. No modifiques ninguna prueba existente; si una corrección cambia el comportamiento, agrega pruebas nuevas en otro archivo. No integres nada a main."
- **Decisión:** Aceptada
- **Por qué:** El agente, Claude con acceso a la terminal, hizo cada corrección en su propia rama y abrió la solicitud de cambios #1 en GitHub. Revisé el diff completo antes de integrarlo: no tocó `tests/test_calculo_cobro.py`, no subió claves ni archivos `.env` y cada commit corresponde a un hallazgo o a un paso de la tarea.
- **Verificación:** `git diff e76b374 -- tests/test_calculo_cobro.py` no muestra cambios, y GitHub Actions quedó en verde en cada envío de la rama.
- **Commit relacionado:** Rama semana-6-revision-seguridad, integrada a main con la solicitud de cambios #1

## Resumen

| Decisión | Semana 5 | Semana 6 | Total |
|---|---|---|---|
| Aceptadas | 2 | 10 | 12 |
| Aceptadas con cambios | 2 | 4 | 6 |
| Rechazadas | 2 | 2 | 4 |

## Errores que atraparon las pruebas

La prueba de límite `test_precio_cero_se_acepta_y_no_suma` falló con la primera versión del código generado. El asistente escribió `if not item.precio_unitario` para detectar un repuesto sin precio, pero en Python `not 0` es verdadero, así que una llanta que trae el cliente, con precio 0, se rechazaba con el mensaje "Escriba el precio del repuesto". Lo corregí comparando con `None`, que es como el contrato define un precio faltante. Sin esa prueba de límite, el error habría llegado hasta el taller.

En la semana 6, las 4 pruebas nuevas de `tests/test_tipos_de_datos.py` fallaron con el código anterior: 3 fallos y 1 error, porque un precio escrito como texto lanzaba TypeError en lugar de ValueError. Eso confirmó el hallazgo H-03 antes de corregirlo, y después de la corrección pasaron sin cambiar ninguna prueba.

## Reflexión final de la semana 5

El asistente me ayudó más a convertir el contrato en pruebas concretas: en pocos minutos tuve diez casos con los datos reales de la orden 48271936, incluido el mensaje exacto de la historia. También hizo un refactor limpio que pude verificar solo con volver a correr las pruebas. El error que atraparon mis pruebas fue el del precio cero, un detalle de Python que se ve correcto al leerlo y que no habría notado sin un caso de límite. Aprendí que el asistente arrastra decisiones viejas, como el IVA del prompt de la semana 2, si no reviso el contrato contra los requisitos. En la próxima funcionalidad escribiría primero los casos de límite y le pediría al asistente que explique cada condición antes de aceptarla.

## Reflexión final de la semana 6

La revisión con IA me ahorró tiempo para encontrar los casos de entrada que no había probado, como el precio con decimales o la cantidad `True`, pero tres de sus siete hallazgos eran falsos positivos y solo lo supe al ejecutar cada caso. Lo más importante, el control de acceso, salió de leer la historia de usuario y no solo el código: la función calculaba bien, pero cualquiera podía registrar cobros. La IA tampoco revisó el historial ni la configuración del repositorio, y ahí estaba el problema de `.env.example`. Trabajar al agente en una rama propia me dejó revisar todo el diff antes de integrarlo. En la próxima funcionalidad pondría la integración continua desde el primer commit.
