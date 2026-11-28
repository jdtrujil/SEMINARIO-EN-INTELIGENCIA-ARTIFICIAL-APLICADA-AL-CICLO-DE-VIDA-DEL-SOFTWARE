# Bitácora de uso de IA

Proyecto: Taller Dos Ruedas, sistema de control de ingreso de motos
Estudiante: Juan Diego Trujillo Rodriguez
Funcionalidad: HU-07 Calcular el cobro de repuestos y mano de obra, sin IVA (semana 5), su revisión de código y seguridad (semana 6), la suite de pruebas con IA para el cobro, la placa de la HU-01 y el control de acceso (semana 7), la cobertura (semana 8), el pipeline y el contenedor (semana 9) y la versión web desplegable con el informe final (semana 10)
Asistente usado: Claude, en modo chat y agente con acceso a la terminal

## Recorrido del uso de IA en el proyecto, semanas 2 a 10

Antes de escribir código, el proyecto ya usaba IA en cada entrega. El detalle de cada prompt está en esos documentos; aquí queda el resumen para tener todo el recorrido en un solo lugar.

| Semana | Entregable | Cómo se usó la IA | Qué se corrigió o se decidió |
|---|---|---|---|
| 2 | Trujillo_Juan_S2_Banco: banco de 10 prompts evaluados | Diez prompts con Claude para la función de cobro, el código heredado, la documentación, los requisitos, la base de datos, las pruebas, el formulario, las observaciones, el control de acceso y la auditoría | Dos prompts subieron de 3 a 5 al agregar formato y restricciones. Se quitó el IVA del cálculo y se agregó la consulta del cliente con el número de orden |
| 3 | Trujillo_Juan_S3_Requisitos y Trujillo_Juan_S3_Bitacora | Seis prompts: guion de entrevista, entrevista simulada (declarada como simulada), necesidades, historias con criterios Gherkin, revisión de defectos y modelo de dominio | Se detectaron 5 requisitos inventados, 5 ambigüedades, 2 contradicciones y 5 omisiones. Lo que no tenía cita pasó a preguntas pendientes |
| 4 | Trujillo_Juan_S4_Diseno: documento de diseño | Cinco prompts: alternativas de arquitectura, diagrama de contexto, diagrama de contenedores, modelo de datos y API | Se descartaron microservicios, Kubernetes y Redis por sobreingeniería. Se eligió el monolito modular (ADR-001) y la consulta con número aleatorio y límite de intentos (ADR-002) |
| 5 | Este repositorio: HU-07 | Entradas 1 a 6 de esta bitácora | Pruebas primero, implementación, refactor y un error del precio cero que atrapó una prueba de límite |
| 6 | Este repositorio: revisión de código y seguridad | Entradas 7 a 22 de esta bitácora | Ocho hallazgos corregidos, uno por commit, en la rama del agente |
| 7 | Este repositorio: suite de pruebas y `registro_pruebas.md` | Entradas 23 a 31 de esta bitácora | Cuatro reglas inventadas descartadas, 17 decisiones sobre las pruebas de la IA y un error introducido que ninguna prueba atrapó hasta agregar dos casos |
| 8 | Este repositorio: cobertura y mutación | Entradas 33 y 34 | La columna Missing mostró 4 ramas de seguridad sin probar; 100 % de cobertura no evitó que sobreviviera un mutante |
| 9 | Este repositorio: pipeline y Dockerfile | Entradas 35 a 38 | Cuatro hallazgos en el pipeline de la semana 6, actionlint frenó una corrección del agente y la práctica de clase se rechazó con 12 problemas |
| 10 | Versión web, docs/, informe, sustentación y base de datos | Entradas 32 y 39 a 44 | La prueba de la cabecera Server encontró un error del código generado; cada dato del informe se comprobó contra su fuente |

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

## Entradas de la semana 7

### Entrada 23

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Con estas tres reglas, propón casos de prueba usando particiones de equivalencia (incluidas las inválidas), valores límite (último valor de una partición y primero de la siguiente) y una tabla de decisión para registrar_item. Para cada caso da la entrada y el resultado esperado." Le pasé la regla del cobro de la HU-07, la de la placa de la HU-01 y la de permisos del hallazgo H-05.
- **Decisión:** Aceptada con cambios
- **Por qué:** La propuesta tenía la estructura correcta, pero le faltaban particiones inválidas (mano de obra sin valor, precio en texto, cantidad booleana, placa con Ñ o que no es texto), bordes de la placa y la orden sin mecánico. Además esperaba un error para "abc12d", lo que contradice la decisión de pasar la placa a mayúsculas. Agregué lo que faltaba, cambié ese caso a V3 (devuelve ABC12D) y armé la tabla de decisión completa de 8 columnas.
- **Verificación:** Revisé la propuesta con las cinco preguntas de la semana y comparé cada esperado con la regla escrita, no con el código. El resultado está en las secciones 1.1 a 1.5 de `registro_pruebas.md`.
- **Commit relacionado:** 94ba12d Registro de pruebas: reglas, particiones, límites y tabla de decisión

### Entrada 24

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** En la misma propuesta, la IA agregó casos para cuatro reglas que nadie pidió: descripción obligatoria, precio máximo de 10.000.000, cantidad máxima de 100 y quitar el guion de la placa (ABC-12D devuelve ABC12D).
- **Decisión:** Rechazada
- **Por qué:** Ninguna de las cuatro está en las historias de usuario ni en la entrevista de la semana 3. Probarlas habría obligado a escribir código para reglas inventadas. Las dos primeras sí son dudas razonables, así que quedaron como ambigüedades A5 y A6 con las preguntas nuevas P-11 y P-12 para el cliente. El guion se rechaza por la decisión A2.
- **Verificación:** Busqué cada regla en los documentos de requisitos de la semana 3 y no aparece. Las pruebas con datos sintéticos documentan el comportamiento actual: una descripción vacía se acepta.
- **Commit relacionado:** 94ba12d Registro de pruebas: reglas, particiones, límites y tabla de decisión

### Entrada 25

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Implementa validar_placa en app/ingresos/placas.py con la regla de la sección 1.2 del registro: tres letras, dos números y una letra opcional; quita los espacios a los lados y pasa a mayúsculas; cualquier otra cosa lanza ValueError con un mensaje claro. Con docstring y sin dependencias nuevas."
- **Decisión:** Aceptada
- **Por qué:** El asistente usó `fullmatch` en lugar de `match`, así que "ABC12DE" no pasa por tener un prefijo válido, y `[A-Z]` en lugar de `\w` para no aceptar Ñ ni tildes. Revisa primero que la placa sea texto, para que `None` dé ValueError y no AttributeError, la misma lección del hallazgo H-03 de la semana 6.
- **Verificación:** Los casos de la sección 1.2 se diseñaron antes de ver el código. Después pasaron las 19 pruebas de `tests/test_placas.py`, y `ruff check` no reportó nada.
- **Commit relacionado:** 15af1d6 HU-01: validar_placa acepta ABC12D y placas antiguas ABC12

### Entrada 26

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Con las reglas y la tabla de casos revisada de registro_pruebas.md, escribe las pruebas en pytest. Usa @pytest.mark.parametrize con un comentario por fila que diga qué partición o límite cubre, asserts con el valor exacto y pytest.raises con el tipo exacto de error. Los datos de prueba deben venir de una fixture."
- **Decisión:** Aceptada con cambios
- **Por qué:** El borrador tenía 50 pruebas nuevas y todas pasaban, pero eso no prueba que sirvan. Con las tres preguntas descarté 7 filas o pruebas repetidas o que calculaban el esperado con el mismo código, corregí 8 que usaban `pytest.raises(Exception)`, `assert total > 0` o un if dentro de la prueba, y agregué la orden sin mecánico. El detalle de cada decisión está en la sección 2 del registro.
- **Verificación:** Guardé el borrador sin revisar en su propio commit para que el diff muestre la revisión. Después de revisar, las pruebas siguen en verde y la mutación M6 confirmó que la prueba corregida de la tabla de decisión ahora sí falla.
- **Commit relacionado:** 47b4e8a borrador de la IA y 3051ed9 Revisión de las pruebas de la IA con las tres preguntas

### Entrada 27

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Genera datos sintéticos para las pruebas de un taller de motos en Colombia: seis ítems de cobro (repuestos y mano de obra) y seis motos con placa, marca, cliente y teléfono. Sin personas reales y con teléfonos ficticios con 555. Incluye tildes, ñ, apóstrofo, texto vacío, un precio en cero y placas en minúsculas, con espacios, con guion y con Ñ. Para cada placa indica la placa esperada según la regla, o null si es inválida."
- **Decisión:** Aceptada
- **Por qué:** Los datos traen repuestos que sí se usan en el taller (piñón, guaya, kit de arrastre), las marcas que atiende y nombres que no corresponden a personas reales; la marca del kit es ficticia. Cada caso difícil que pedí aparece al menos una vez.
- **Verificación:** Revisé cada placa esperada contra la regla de la sección 1.2 y sumé a mano los ítems: 195.000 de repuestos, 65.000 de mano de obra y 260.000 en total. Esos valores son los esperados de las pruebas, no lo que devuelve el código.
- **Commit relacionado:** 47b4e8a `tests/datos/datos_sinteticos.json` y las fixtures de `tests/conftest.py`

### Entrada 28

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Dentro del borrador, la IA propuso `test_total_es_la_suma_de_los_subtotales`, que compara el total con la suma de los dos subtotales que devuelve la misma función.
- **Decisión:** Rechazada
- **Por qué:** El esperado sale del código y no de la regla. Si el cálculo sumara el IVA a los dos subtotales y al total, la prueba seguiría pasando. Una prueba así solo confirma que el código hace lo que ya hace.
- **Verificación:** Apliqué un IVA de 19 % a los dos subtotales en `calcular_cobro` y corrí la prueba del borrador: pasó. Con el mismo error, la suite actual tuvo 12 fallos, porque exige los totales exactos de la regla (50.000, 35.000 y 85.000). Deshice el cambio con `git restore` y volvieron a pasar las 70.
- **Commit relacionado:** 3051ed9 Revisión de las pruebas de la IA con las tres preguntas

### Entrada 29

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Propón errores pequeños y realistas para introducir en el código, uno a la vez, que una persona podría cometer en estas reglas: cambiar un < por <=, sumar IVA, saltarse un permiso, aflojar el formato de la placa. Para cada uno dime el archivo y la línea."
- **Decisión:** Aceptada
- **Por qué:** Introduje los siete errores, uno por uno, y corrí todas las pruebas con cada uno. Seis fallaron como se esperaba. El M5, que deja pasar un precio 18000.0, no hizo fallar ninguna prueba: era un hueco real, porque el precio con decimales solo se probaba con 18000.5. Agregué los casos P18 (precio 18000.0) y P19 (cantidad 2.0) sin cambiar ninguna prueba existente.
- **Verificación:** Con el M5 puesto, las dos pruebas nuevas fallan; sin él, pasan. Después de cada error corrí `git restore` y comprobé con `git diff app/` que el código quedó igual. El commit solo cambia `tests/test_reglas_cobro.py`. La tabla está en la sección 3 del registro.
- **Commit relacionado:** a138743 Agrega los casos que faltaban: precio 18000.0 y cantidad 2.0

### Entrada 30

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso fijar pytest 9.1.1 en `requirements-dev.txt`, correr las pruebas con pytest en GitHub Actions y en la tarea de VS Code, y permitir `assert` solo en la carpeta de pruebas en ruff.
- **Decisión:** Aceptada
- **Por qué:** Esta semana pide pytest, así que cambia la decisión de la entrada 2. Las pruebas de unittest de las semanas 5 y 6 siguen igual, porque pytest también las ejecuta. La excepción S101 de ruff aplica solo a `tests/`, donde `assert` es la forma normal de comprobar en pytest.
- **Verificación:** `python -m pytest -v` ejecuta las 70 pruebas en verde, y `git diff` muestra que no cambió ninguna prueba de las semanas 5 y 6.
- **Commit relacionado:** 672ac64 pytest como herramienta fijada: CI, tareas de VS Code y README

### Entrada 31

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso llenar las secciones 2, 3 y 4 de `registro_pruebas.md` con la revisión de cada prueba, la tabla de errores introducidos y el origen de los datos sintéticos, y agregar estas entradas a la bitácora.
- **Decisión:** Aceptada
- **Por qué:** Cada fila sale de un commit real de la rama. Corregí una cifra que estaba mal: el borrador tenía 50 pruebas nuevas, no 70, porque 20 eran de las semanas 5 y 6.
- **Verificación:** Comprobé las líneas de la sección 3 contra el código de la rama, conté las pruebas de cada archivo con `pytest --collect-only` en el commit del borrador y en el actual, y verifiqué que cada commit citado existe.
- **Commit relacionado:** b0a6ada Registro de pruebas: revisión de las pruebas de la IA, errores introducidos y datos sintéticos, y el commit de esta bitácora

## Entradas de la entrega final (semanas 8 a 10)

### Entrada 32

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Construye una versión web local del Taller Dos Ruedas solo con la biblioteca estándar de Python: un formulario para validar la placa y otro para calcular el cobro, reutilizando validar_placa y calcular_cobro. Que escuche solo en 127.0.0.1, escape todo lo que escribe el usuario, limite el tamaño del formulario, no guarde datos y tenga una ruta /salud. Escribe las pruebas con pytest."
- **Decisión:** Aceptada con cambios
- **Por qué:** Las reglas no se duplican: los mensajes de error de la página son los mismos de `calcular_cobro` y `validar_placa`, con el número de la fila adelante. Hubo dos cambios. La prueba de la cabecera `Server` falló: el código generado dejaba un espacio al final, y se corrigió el código sin tocar la prueba. En la primera captura, la columna del tipo cortaba "mano de obra", y se fijó el ancho de las columnas. Una decisión de la interfaz: el registrador escribe los precios como 18.000, así que la página acepta el punto de miles, pero solo en grupos exactos de tres dígitos. Por eso 1.5 sigue rechazado.
- **Verificación:** 30 pruebas nuevas en `tests/test_web.py` y 100 en verde, `ruff check` sin avisos y capturas de la página real, servida por el servidor ([docs/evidencias](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/tree/main/docs/evidencias)).
- **Commit relacionado:** [c71c436](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/c71c436) Versión web local: validar la placa y calcular el cobro en el navegador

### Entrada 33

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Propón errores pequeños y realistas para la versión web, uno a la vez, para comprobar que las pruebas nuevas los detectan: escapar, convertir los precios, limitar el tamaño y la dirección en que escucha."
- **Decisión:** Aceptada
- **Por qué:** Introduje cuatro errores, uno por uno. W1, la descripción sin escapar, hizo fallar 1 prueba. W2, sin quitar el punto de miles, hizo fallar 2. W3, sin límite de tamaño, 1. W4, escuchar en 0.0.0.0 por defecto, hizo fallar 2 pruebas y ruff lo marcó con S104. Los cuatro murieron.
- **Verificación:** Después de cada error restauré el archivo y volví a correr las 100 pruebas en verde. El resultado está en la sección 5.3 de [registro_pruebas.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/registro_pruebas.md).
- **Commit relacionado:** Ninguno, porque el código se restauró después de cada error

### Entrada 34

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Con lo de la semana 8, mide la cobertura de líneas y de ramas con pytest-cov en el pipeline (--cov=app --cov-branch --cov-report=term-missing) y usa la columna Missing para decidir qué falta probar."
- **Decisión:** Aceptada
- **Por qué:** La primera medición dio 83 %. La columna Missing mostró sin probar las ramas de seguridad del servidor: el formulario sin tamaño (411), el que tiene demasiados campos (413), un precio con miles de dígitos y el arranque con un puerto inválido. Se agregaron 4 pruebas sin cambiar el código y el total subió a 87 %. Los dos `__main__.py` quedaron en 0 % a propósito: son demos que el pipeline ejecuta aparte, y probarlos no comprobaría ninguna regla.
- **Verificación:** Ejecuciones [46064096065](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064096065) (antes) y [46064631239](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064631239) (después). Las reglas del negocio tienen 100 % de líneas y de ramas, y aun así la mutación M5 había sobrevivido en la semana 7: la cobertura dice qué se ejecutó, no qué se comprobó.
- **Commit relacionado:** [ebbc9bd](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/ebbc9bd) Cobertura con pytest-cov y prueba de humo, y [380ead2](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/380ead2) Pruebas guiadas por la columna Missing de la cobertura

### Entrada 35

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Escribe un Dockerfile para la versión web del Taller Dos Ruedas (python -m app.web, solo biblioteca estándar, puerto 8000) y su .dockerignore, siguiendo la lista de revisión de la semana 9: imagen base, secretos, usuario, .dockerignore, versiones y modo desarrollo."
- **Decisión:** Aceptada
- **Por qué:** Pasó las seis preguntas de la lista: `python:3.13-slim` sin `latest`, ningún secreto, usuario sin privilegios (uid 10001), un `.dockerignore` que deja fuera `.git`, `.env`, las pruebas y los documentos, sin `pip install` y sin `--reload`. Además trae un `HEALTHCHECK` a `/salud`. Queda un pendiente: fijar la imagen por digest. La línea `TALLER_HOST=0.0.0.0` parece un problema y no lo es: dentro del contenedor hace falta, y quién entra lo decide `-p 127.0.0.1:8000:8000`.
- **Verificación:** hadolint no dio avisos. El pipeline construye la imagen, la ejecuta y comprueba que `/salud` responde `ok` y que el usuario es el 10001.
- **Commit relacionado:** [89c7ca0](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/89c7ca0) Contenedor y pipeline revisados con la lista de la semana 9

### Entrada 36

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Revisa calidad.yml, el pipeline que generaste en la semana 6, con la lista de la semana 9: eventos, permisos, secretos, versiones, dependencias y si un fallo de las pruebas hace fallar el pipeline. Corrige lo que encuentres y agrega un trabajo que construya y pruebe el contenedor con hadolint y actionlint."
- **Decisión:** Aceptada con cambios
- **Por qué:** La revisión encontró que las acciones estaban fijadas por etiqueta y no por commit, que no había tiempo máximo, que solo se probaba Python 3.12 aunque el PC tiene 3.13 y que ningún paso probaba el contenedor. Los permisos, los secretos, las dependencias y el fallo de las pruebas estaban bien. La corrección del agente falló en su propio pipeline: actionlint marcó SC2034 en los dos ciclos de espera que el agente acababa de escribir, porque la variable `intento` no se usaba. En la misma ejecución, GitHub avisó que checkout v4 y setup-python v5 usan Node.js 20, que está obsoleto.
- **Verificación:** La [ejecución 46064439336](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064439336) salió en rojo por actionlint. Después de la corrección, la [46064631239](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064631239) salió en verde con 3.12, 3.13 y el contenedor. El detalle está en [revision_configuracion.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/revision_configuracion.md).
- **Commit relacionado:** [89c7ca0](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/89c7ca0) y [58762b4](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/58762b4) Corrige los avisos de actionlint y de GitHub en el pipeline

### Entrada 37

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El agente propuso comprobar que el pipeline de verdad falla: una rama temporal con una prueba que exige el total con IVA (21.420) para un repuesto de 18.000.
- **Decisión:** Aceptada
- **Por qué:** La lista de la semana 9 pide comprobar que un fallo de las pruebas hace fallar el pipeline. Un pipeline que siempre sale en verde, como el de la práctica con `continue-on-error`, no protege nada.
- **Verificación:** La [ejecución 46064652666](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064652666) salió en rojo con las dos versiones de Python, y el contenedor no se construyó. La rama `prueba-pipeline-rojo` no se integra.
- **Commit relacionado:** b8c77cc, solo en la rama `prueba-pipeline-rojo`

### Entrada 38

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** El código de práctica de la semana 9 trae un `ci.yml` y un `Dockerfile` generados por un asistente de IA con prompts simples ("Escribe un workflow de GitHub Actions para mi proyecto de Python con pytest" y "Escribe un Dockerfile para mi API de FastAPI").
- **Decisión:** Rechazada
- **Por qué:** Revisé los dos archivos sin ejecutarlos, como pide el LEEME. El `ci.yml` tiene seis problemas: la rama `master` cuando la rama es `main`, `write-all`, la clave escrita en el archivo, `3.10` sin comillas (YAML la lee como 3.1), dependencias sin versión y `continue-on-error`. El `Dockerfile` tiene otros seis: `latest`, la clave en `ENV`, `COPY . .` sin `.dockerignore`, root, `--reload` y la caché de pip. La línea `--host 0.0.0.0` no es un problema. Esta práctica es la que llevó a pedir el Dockerfile del proyecto con la lista desde el primer prompt (entrada 35).
- **Verificación:** Cada hallazgo se comparó con la lista de la semana. El código de práctica no se subió al repositorio, y su clave es ficticia.
- **Commit relacionado:** [d2c1d9d](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/d2c1d9d), sección 5 de [revision_configuracion.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/revision_configuracion.md)

### Entrada 39

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Pon el repositorio en su estado final: ordena docs/ por módulo con los entregables de las semanas 2 a 4, pasa los ADR de la semana 4 a archivos .md, escribe el ADR de la versión web, la guía de despliegue y el plan de operación, y actualiza el README."
- **Decisión:** Aceptada
- **Por qué:** El PDF del proyecto final pide los documentos de cada módulo en el repositorio. Los ADR-001 y ADR-002 se copiaron del documento de diseño sin cambiar la decisión. El ADR-003 explica por qué se despliega una versión con la biblioteca estándar antes de FastAPI. La guía y el plan describen lo que existe: una versión que no guarda datos, con `/salud` y el registro sin contenido de formularios.
- **Verificación:** Revisé que cada enlace de `docs/README.md` apunte a un archivo que existe y que los ADR coincidan con el PDF de la semana 4. También busqué datos personales reales en los documentos: los nombres, las placas y los teléfonos son ficticios.
- **Commit relacionado:** [d2c1d9d](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/d2c1d9d) Carpeta docs por módulo, ADR, guía de despliegue, plan de operación y revisión de configuración

### Entrada 40

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Con la plantilla informe_final_integrador.md y todo lo que hay en el repositorio, redacta el informe final: cada afirmación con el enlace a su evidencia, al menos tres casos de verificación de fases distintas con su commit, y la sección 6 sobre las decisiones de este proyecto, no sobre la ética de la IA en general."
- **Decisión:** Aceptada con cambios
- **Por qué:** El borrador seguía las ocho secciones y traía cinco casos, uno por fase. Antes de aceptarlo revisé cada dato contra su fuente. Hubo dos cambios: los conteos de la bitácora (entradas y rechazos) se ajustaron a lo que de verdad tiene este archivo, y el despliegue se describe solo como se hizo.
- **Verificación:** Busqué en los PDF de las semanas 3 y 4 cada error que el informe le atribuye a la IA: las citas de WhatsApp y del reporte diario, Kubernetes con "miles de usuarios concurrentes", la cédula, el correo, la tarjeta y los totales 86, 75 y 75. También busqué en la transcripción cada cita de la entrevista y comprobé con `git log` que existen los 12 commits citados.
- **Commit relacionado:** Rama `entrega-final`, solicitud de cambios #3

### Entrada 41

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Organiza la sustentación en PowerPoint, máximo 8 diapositivas, con la estructura sugerida del PDF: problema y usuario, solución y arquitectura, la IA en cada fase, el mejor caso de verificación, una decisión ética y aprendizajes. Muestra evidencias reales del repositorio y pon en las notas lo que digo y cuánto dura."
- **Decisión:** Aceptada con cambios
- **Por qué:** La estructura y los tiempos siguen el PDF y suman 10 minutos. Tres cambios después de ver cada diapositiva renderizada: acorté los títulos que ocupaban dos líneas, rehice las capturas de la terminal con menos texto para que se puedan leer y recorté las capturas de la página. No se pudo tomar una captura de la página de GitHub desde el entorno del agente, así que la evidencia del pipeline es la salida real de `gh run view`.
- **Verificación:** El archivo pasó la validación de PowerPoint y revisé las 8 diapositivas como imágenes. Los números de las capturas (104 pruebas, 87 %, los tres trabajos en verde) son los de la ejecución [46065039912](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46065039912).
- **Commit relacionado:** Rama `entrega-final`, solicitud de cambios #3 (`docs/entrega_final/`)

### Entrada 42

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Simula las preguntas que me pueden hacer en los 4 minutos de la sustentación, con los ejemplos del PDF, y dame para cada una la respuesta y el archivo y la línea que debo abrir."
- **Decisión:** Aceptada
- **Por qué:** Son 13 preguntas sobre el código, la verificación, los datos personales y el mantenimiento. Cada respuesta apunta a una evidencia que se puede abrir en vivo.
- **Verificación:** Abrí cada archivo en la línea citada (por ejemplo, `calculo.py:73` y `servicio.py:37-39`) y comprobé contra el ADR-002 y la sección 5 del registro de pruebas lo que dice cada respuesta.
- **Commit relacionado:** [docs/entrega_final/preguntas_sustentacion.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/entrega_final/preguntas_sustentacion.md)

### Entrada 43

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** "Haz la presentación con el mismo esquema de esta referencia, teniendo en cuenta mi proyecto, con una plantilla azul y gris, y edita el informe y la sustentación." La referencia tiene 8 diapositivas: portada, problema y solución, ciclo de vida, lo que la IA hizo mal, cómo verifiqué, operación, evaluación de las historias de usuario, y ética y aprendizajes.
- **Decisión:** Aceptada con cambios
- **Por qué:** El esquema pedía dos datos que el proyecto no había medido, y se midieron antes de ponerlos en una diapositiva. El primero es la evaluación de los 20 escenarios de las historias. Se escribió una prueba de aceptación por cada escenario construido, con sus datos exactos: se cumplen 2, 1 en parte y 17 están sin construir. El segundo es cuántos errores se le habrían escapado al borrador de pruebas de la IA. Los 7 errores de las reglas se corrieron contra el borrador del commit 47b4e8a: atrapó 5 y dejó pasar el M5 y el M6. El cambio vino después de ver las diapositivas renderizadas: se acortaron tres títulos que ocupaban dos líneas.
- **Verificación:** 107 pruebas en verde. Cada escenario se comparó con el documento de requisitos de la semana 3. La medición del borrador se hizo en una copia aparte del código, sin tocar el repositorio. La presentación pasó la validación de PowerPoint y se revisaron las 8 diapositivas como imágenes. El informe, el registro de pruebas y el README quedaron con las mismas cifras.
- **Commit relacionado:** Rama `sustentacion-esquema`, solicitud de cambios #4 ([tests/test_aceptacion.py](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/tests/test_aceptacion.py))

### Entrada 44

- **Fecha:** 2026-11-27
- **Prompt o sugerencia:** Pedido del cliente después del despliegue: "Valida la placa pero no guarda la factura con repuestos y saldos. No guarda datos: implemente PostgreSQL. Al registrar una motocicleta no me deja elegir qué mecánico la va a tomar; no guarda el historial ni menciona en qué etapa se encuentra: Recibida, En reparación, Terminada. Cuando muestre Terminada, que me deje guardar la operación y que el cliente pueda revisar el costo total con el código que se genere." Datos a guardar: fecha y hora de ingreso, placa, observaciones de ingreso y datos de la factura.
- **Decisión:** Aceptada con cambios
- **Por qué:** El agente construyó el módulo `ordenes` con PostgreSQL 16 y SQLite como respaldo (ADR-004), las páginas del taller y la consulta del cliente. Reutilizó `validar_placa`, `calcular_cobro` y `registrar_item`, así que el permiso del hallazgo H-05 también rige aquí. Los mensajes son los de los criterios de la semana 3. Hubo dos cambios. Los nombres reales de los mecánicos no entraron al repositorio: con el cliente se decidió dejarlos en el `.env` local, porque la regla del proyecto final prohíbe datos personales reales. Además, `ruff format` reformateó archivos que no eran parte del cambio, y se devolvieron a como estaban.
- **Verificación:** Se escribieron 69 pruebas nuevas, entre ellas 13 de aceptación con los datos de los escenarios, y las 107 anteriores pasan sin cambios. En la [ejecución 46084960626](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46084960626), las pruebas de las órdenes corrieron también contra PostgreSQL 16: 221 pruebas en verde y 93 % de cobertura. Se recorrió el flujo completo en el navegador con datos ficticios: el registro oculta los números de orden y una sexta consulta seguida recibe 429.
- **Commit relacionado:** [ebe82b9](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/ebe82b9) Registro de motos con mecánico, etapas, historial, factura y consulta del cliente, con PostgreSQL

## Resumen

| Decisión | Semana 5 | Semana 6 | Semana 7 | Entrega final (8 a 10) | Total |
|---|---|---|---|---|---|
| Aceptadas | 2 | 10 | 5 | 6 | 23 |
| Aceptadas con cambios | 2 | 4 | 2 | 6 | 14 |
| Rechazadas | 2 | 2 | 2 | 1 | 7 |
| **Entradas** | 6 | 16 | 9 | 13 | **44** |

## Errores que atraparon las pruebas

La prueba de límite `test_precio_cero_se_acepta_y_no_suma` falló con la primera versión del código generado. El asistente escribió `if not item.precio_unitario` para detectar un repuesto sin precio, pero en Python `not 0` es verdadero, así que una llanta que trae el cliente, con precio 0, se rechazaba con el mensaje "Escriba el precio del repuesto". Lo corregí comparando con `None`, que es como el contrato define un precio faltante. Sin esa prueba de límite, el error habría llegado hasta el taller.

En la semana 6, las 4 pruebas nuevas de `tests/test_tipos_de_datos.py` fallaron con el código anterior: 3 fallos y 1 error, porque un precio escrito como texto lanzaba TypeError en lugar de ValueError. Eso confirmó el hallazgo H-03 antes de corregirlo, y después de la corrección pasaron sin cambiar ninguna prueba.

En la semana 7 ninguna prueba falló contra el código real, así que no apareció un defecto nuevo. Al romper el código a propósito, las pruebas atraparon seis de siete errores: el precio cero rechazado, el IVA, el permiso saltado, la placa con un solo número, el ítem agregado antes de validarlo y la placa sin mayúsculas. El séptimo, aceptar un precio 18000.0, pasó sin que nada fallara. Agregué dos casos y ahora ese error también se atrapa.

En la entrega final, la prueba `test_inicio_lleva_las_cabeceras_de_seguridad_y_no_muestra_la_version_de_python` falló con el código que generó la IA: la cabecera `Server` quedaba con un espacio al final. Se corrigió el código, no la prueba. En el pipeline, actionlint frenó la ejecución 46064439336 por dos variables sin usar que el agente acababa de escribir.

## Reflexión final de la semana 5

El asistente me ayudó más a convertir el contrato en pruebas concretas: en pocos minutos tuve diez casos con los datos reales de la orden 48271936, incluido el mensaje exacto de la historia. También hizo un refactor limpio que pude verificar solo con volver a correr las pruebas. El error que atraparon mis pruebas fue el del precio cero, un detalle de Python que se ve correcto al leerlo y que no habría notado sin un caso de límite. Aprendí que el asistente arrastra decisiones viejas, como el IVA del prompt de la semana 2, si no reviso el contrato contra los requisitos. En la próxima funcionalidad escribiría primero los casos de límite y le pediría al asistente que explique cada condición antes de aceptarla.

## Reflexión final de la semana 6

La revisión con IA me ahorró tiempo para encontrar los casos de entrada que no había probado, como el precio con decimales o la cantidad `True`, pero tres de sus siete hallazgos eran falsos positivos y solo lo supe al ejecutar cada caso. Lo más importante, el control de acceso, salió de leer la historia de usuario y no solo el código: la función calculaba bien, pero cualquiera podía registrar cobros. La IA tampoco revisó el historial ni la configuración del repositorio, y ahí estaba el problema de `.env.example`. Trabajar al agente en una rama propia me dejó revisar todo el diff antes de integrarlo. En la próxima funcionalidad pondría la integración continua desde el primer commit.

## Reflexión final de la semana 7

La IA me ayudó a llegar rápido a una tabla de casos completa y a un borrador de pruebas que ya pasaba, pero que pasaran no quería decir que sirvieran: varias calculaban el esperado con el mismo código o aceptaban cualquier error. Lo que más me sirvió fue romper el código a propósito, porque mostró un hueco que ninguna revisión a ojo habría visto: un precio 18000.0 pasaba sin que fallara nada. También vi que la IA inventa reglas con mucha seguridad, como un precio máximo o la descripción obligatoria; si las hubiera aceptado, estaría probando un sistema que el taller no pidió. Ahora esas dudas son preguntas para el cliente. En la próxima funcionalidad escribiría primero la regla y los esperados, y solo después le pediría a la IA que escriba las pruebas.

## Reflexión final del proyecto

Al empezar pensaba que la IA serviría sobre todo para escribir código. Al final, donde más aportó fue en proponer: alternativas de arquitectura, casos de prueba, revisiones de seguridad y listas de lo que podía fallar. Pero en cada fase propuso algo que no estaba bien y que se veía bien: citas que el cliente nunca dijo, microservicios para 25 motos al día, una cédula que nadie pidió, un `not` que rechazaba el precio cero, pruebas que pasaban sin comprobar nada y un pipeline sin límite de tiempo. Lo que los detectó no fue leer con más cuidado, sino tener algo contra qué comparar: la transcripción, la matriz recalculada, una prueba escrita antes, el código roto a propósito y una lista de revisión. Por eso cada sugerencia de esta bitácora tiene su verificación al lado. La IA propone, yo verifico y respondo por el resultado.
