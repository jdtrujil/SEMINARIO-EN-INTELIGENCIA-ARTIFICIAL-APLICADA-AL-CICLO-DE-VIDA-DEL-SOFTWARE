# Informe final del proyecto integrador

Proyecto: Taller Dos Ruedas, sistema de control de ingreso y cobro de un taller de motos
Estudiante: Juan Diego Trujillo Rodriguez
Repositorio: https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE
Fecha: 2026-11-27

## 1. Resumen

El Taller Dos Ruedas (nombre ficticio) registra el ingreso de las motos en un cuaderno, suma el cobro a mano y no tiene cómo avisarle al cliente si la moto ya está lista. El proyecto diseñó un sistema web para ese taller y construyó:

- La regla del cobro de repuestos y mano de obra sin IVA, con control de acceso por mecánico (HU-07), y la validación de la placa (HU-01).
- El registro de cada moto con la fecha y hora, la placa, las observaciones y el mecánico que la toma.
- Las etapas Recibida, En reparación y Terminada, con su historial.
- La factura, que se guarda al terminar, y la consulta del cliente con su número de orden.
- Una base de datos PostgreSQL 16, o un archivo SQLite si no hay PostgreSQL.

La interfaz usa los colores del logo del taller, y el logo y el nombre real se configuran en cada equipo. Se despliega con Python o en un contenedor, y el pipeline lo prueba en cada envío.

Usé Claude en las seis fases: prompts y propuesta, requisitos, diseño, código, pruebas y operación. Cada resultado quedó registrado en una bitácora de 45 entradas, y 7 de esas sugerencias se rechazaron. La verificación encontró errores de la IA en cada fase:

- **Requisitos:** citas inventadas.
- **Diseño:** microservicios para 25 motos al día y datos personales que nadie pidió.
- **Código:** un precio cero rechazado.
- **Pruebas:** pruebas que pasaban sin comprobar nada.
- **Operación:** un pipeline con acciones sin fijar y sin límite de tiempo.

El resultado final son 194 pruebas en verde (239 en el pipeline, que repite las de las órdenes contra PostgreSQL 16), con 100 % de cobertura de líneas y de ramas en las reglas del cobro y de las órdenes y 100 % de mutantes detectados en las reglas. De los 20 escenarios de las historias de usuario se cumplen 11, 3 se cumplen en parte y 6 no se han construido.

## 2. Problema y usuario

El taller tiene un registrador que recibe las motos de pie en la entrada, con una tablet, dos mecánicos y un ayudante. Atiende las marcas Kymco, Yamaha, Duke, Suzuki, Honda, Bajaj y AKT, y recibe entre 20 y 25 motos al día ([propuesta del módulo 1](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/01_fundamentos/propuesta.md)).

Hoy el registrador anota el ingreso en un cuaderno y le entrega al cliente un papelito con un número consecutivo. La entrevista del módulo 2 ([documento de requisitos](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/02_requisitos/Trujillo_Juan_S3_Requisitos.pdf), anexo con la transcripción) mostró tres necesidades:

- **Saber cómo llegó la moto.** El registrador: "El problema es cuando el cliente vuelve y dice que el rayón se lo hicimos nosotros".
- **Cobrar bien y sin IVA.** El registrador: "Aquí cobramos lo que lleve en repuestos más la mano de obra, no cobramos IVA".
- **Consultar el estado sin exponer datos.** La clienta: "Tampoco quiero que cualquiera meta un número y vea mi moto o mi teléfono".

La entrevista es simulada, porque no tuve acceso a un taller real, y así lo declara el documento. Los nombres, las placas y los teléfonos son ficticios. De ahí salieron 11 necesidades y 10 historias de usuario, 6 de ellas Must.

## 3. La IA en el ciclo de vida

La herramienta fue Claude (Anthropic) en dos modos: chat para los documentos y agente con acceso a la terminal para el código, las pruebas y la configuración. La [bitácora de IA](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/bitacora_ia.md) registra cada uso con su decisión y su verificación.

| Módulo y fase | Qué hice con IA | Herramienta | Evidencia | Cómo verifiqué |
|---|---|---|---|---|
| 1. Fundamentos | Definí el problema y escribí 10 prompts para tareas del proyecto (cobro, requisitos, base de datos, pruebas, formulario, control de acceso), calificados de 1 a 5 | Claude chat y Claude Code | [Banco de prompts](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/01_fundamentos/Trujillo_Juan_S2_Banco.pdf), [propuesta](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/01_fundamentos/propuesta.md) | Califiqué cada respuesta con las cinco piezas del prompt; dos prompts subieron de 3 a 5 al agregar formato y restricciones. Probé la función de cobro generada |
| 2. Requisitos | Guion de entrevista, entrevista simulada, necesidades con cita, 10 historias con criterios Gherkin, revisión de defectos y modelo de dominio | Claude chat | [Requisitos](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/02_requisitos/Trujillo_Juan_S3_Requisitos.pdf), [bitácora de la semana 3](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/02_requisitos/Trujillo_Juan_S3_Bitacora.pdf) | Busqué cada cita palabra por palabra en la transcripción. Revisé las historias con INVEST y recalculé el cobro a mano |
| 3. Diseño | Alternativas de arquitectura con matriz ponderada, diagramas C4, modelo de datos y API | Claude chat | [Documento de diseño](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/Trujillo_Juan_S4_Diseno.pdf), [ADR-001](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-001-monolito-modular.md), [ADR-002](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-002-numero-de-orden.md) | Recalculé la matriz con mis pesos y comparé cada entidad y campo con las historias |
| 4. Código | HU-07 con TDD (rojo, verde, refactor), segunda revisión de código y seguridad, correcciones en la rama del agente, docstrings y CI | Claude, agente con terminal | [app/](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/tree/main/app), commits [9a63256](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/9a63256), [ef5c923](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/ef5c923), [cb2296b](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/cb2296b), [revisión de seguridad](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/revision_seguridad.md), [solicitud de cambios #1](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/pull/1), bitácora, entradas 1 a 22 | Pruebas en rojo antes de implementar y en verde después. Ejecuté cada hallazgo de la revisión antes de aceptarlo (3 de 7 eran falsos positivos). ruff con reglas de seguridad |
| 5. Pruebas | Casos con particiones, límites y tabla de decisión; borrador de pruebas en pytest; datos sintéticos; mutación y cobertura | Claude, agente con terminal | [registro_pruebas.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/registro_pruebas.md), [tests/](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/tree/main/tests), commits [47b4e8a](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/47b4e8a) (borrador) y [3051ed9](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/3051ed9) (revisado), bitácora, entradas 23 a 31 | Tres preguntas a cada prueba, 11 errores introducidos a propósito y la columna Missing de pytest-cov |
| 6. Operación | Versión web local, Dockerfile, revisión del pipeline con la lista de la semana 9, despliegue y plan de operación | Claude, agente con terminal | [Guía de despliegue](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/guia_despliegue.md), [revisión de configuración](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/revision_configuracion.md), [despliegue realizado](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/despliegue_realizado.md), [pipeline en verde](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/workflows/calidad.yml?query=branch%3Amain) | Lista de seis preguntas, hadolint, actionlint, un pipeline en rojo a propósito y la verificación de `/salud` después de desplegar |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontré

### Caso 1: requisitos con citas inventadas

- **Fase:** requisitos (semana 3).
- **Qué propuso la IA:** al extraer las necesidades de la entrevista, incluyó "avisar al cliente por WhatsApp cuando la moto esté lista" y "generar un reporte diario para el dueño", cada una con una cita entre comillas.
- **Qué estaba mal:** esas citas no aparecen en la transcripción. La IA inventó el respaldo de dos requisitos.
- **Cómo lo detecté:** revisión contra la fuente. Busqué cada cita palabra por palabra con el buscador del editor ([bitácora de la semana 3](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/02_requisitos/Trujillo_Juan_S3_Bitacora.pdf), prompt 3).
- **Qué hice:** pasé las dos necesidades a preguntas pendientes para el cliente (P-01 y P-07) y quedaron 11 necesidades con cita textual. El documento corregido está en el repositorio desde el commit [d2c1d9d](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/d2c1d9d); la corrección se hizo en el documento de la semana 3, antes de que existiera el repositorio.

### Caso 2: microservicios para un taller de 25 motos al día

- **Fase:** diseño (semana 4).
- **Qué propuso la IA:** después de calificar cuatro alternativas, recomendó microservicios desplegados en Kubernetes "por escalabilidad", justificada con "miles de usuarios concurrentes". En el modelo de datos agregó la cédula y el correo del cliente, y el número de tarjeta en una entidad Pago.
- **Qué estaba mal:** sobreingeniería. Son 3 usuarios internos, 25 motos al día y un solo desarrollador, y nadie mencionó miles de usuarios. La escalabilidad pesaba 1 de 5 en mis atributos de calidad. El total ponderado de su propia matriz tampoco cuadraba. Los campos personales no salían de ninguna historia.
- **Cómo lo detecté:** recalculé la matriz con los pesos que salen de la semana 3 (86, 75 y 75 puntos) y revisé cada campo del modelo contra las historias.
- **Qué hice:** elegí el monolito modular ([ADR-001](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-001-monolito-modular.md)) y quité la cédula, el correo, la tarjeta y la entidad Pago (sección 6). Los ADR están en el repositorio desde el commit [d2c1d9d](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/d2c1d9d).

### Caso 3: el precio cero que el código rechazaba

- **Fase:** código (semana 5).
- **Qué propuso la IA:** para detectar un repuesto sin precio, la primera implementación de `calcular_cobro` usaba `if not item.precio_unitario`.
- **Qué estaba mal:** en Python `not 0` es verdadero. Una llanta que trae el cliente, con precio 0, se rechazaba con "Escriba el precio del repuesto". El código se veía bien al leerlo.
- **Cómo lo detecté:** la prueba de límite `test_precio_cero_se_acepta_y_no_suma`, escrita antes del código en el commit [9a63256](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/9a63256), falló con la primera versión (bitácora, entrada 4).
- **Qué hice:** cambié la condición a `is None`, como dice el contrato, sin tocar la prueba. Commit [ef5c923](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/ef5c923). En la misma fase, la revisión de la semana 6 encontró que cualquier trabajador podía registrar cobros en cualquier orden. Se corrigió con pruebas de abuso en el commit [ebddbcc](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/ebddbcc) (hallazgo H-05).

### Caso 4: pruebas que pasaban sin comprobar nada

- **Fase:** pruebas (semanas 7 y 8).
- **Qué propuso la IA:** un borrador de 50 pruebas en pytest, todas en verde (commit [47b4e8a](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/47b4e8a)). Entre ellas, `pytest.raises(Exception)` sin mensaje, `assert resumen.total > 0` y `test_total_es_la_suma_de_los_subtotales`, que calculaba el esperado con el mismo código que probaba.
- **Qué estaba mal:** varias pruebas no fallaban al romper el código. Con el IVA del 19 % aplicado a los subtotales, la prueba de la suma seguía pasando, y `pytest.raises(Exception)` aceptaba hasta el TypeError del hallazgo H-03.
- **Cómo lo detecté:** apliqué tres preguntas a cada prueba (¿el esperado sale de la regla?, ¿fallaría si rompo el código?, ¿repite otra prueba?) y rompí el código a propósito. Con la mutación del IVA en los subtotales, la prueba de la IA pasó y la suite revisada tuvo 12 fallos (bitácora, entrada 28). Además, la mutación M5, que acepta un precio 18000.0, sobrevivió aunque `calculo.py` tenía 100 % de cobertura de líneas y de ramas. Para medir el borrador sin revisar, corrí contra él los 7 errores de las reglas: atrapó 5 y dejó pasar 2, el M5 y el M6, que agrega el ítem a la orden antes de validarlo ([registro_pruebas.md, sección 5.3](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/registro_pruebas.md)).
- **Qué hice:**
  - Descarté 7 pruebas o filas y corregí 8 con el mensaje exacto de cada error y los totales calculados a mano (commit [3051ed9](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/3051ed9)).
  - Agregué los casos P18 y P19 para matar la mutación M5 (commit [a138743](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/a138743)).
  - El detalle está en las secciones 2, 3 y 5 de [registro_pruebas.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/registro_pruebas.md).

### Caso 5: un pipeline que funcionaba, pero con riesgos

- **Fase:** operación (semana 9 y entrega final).
- **Qué propuso la IA:** en la semana 6, el agente generó el pipeline de GitHub Actions (commit [5848e88](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/5848e88)). Usaba `actions/checkout@v4` y `actions/setup-python@v5` por etiqueta, no tenía tiempo máximo y solo probaba con Python 3.12. Al generar la versión web, el código enviaba la cabecera `Server` con un espacio de sobra.
- **Qué estaba mal:**
  - Una etiqueta se puede mover y cambiar el código que corre el pipeline, y esas versiones usan Node.js 20, que GitHub ya marca como obsoleto.
  - Un paso colgado puede correr 6 horas.
  - El PC del taller tiene Python 3.13, una versión que el pipeline no probaba.
- **Cómo lo detecté:**
  - La lista de seis preguntas de la semana 9.
  - actionlint, que además encontró dos avisos SC2034 que yo no había visto.
  - El aviso de Node.js 20 en la [ejecución 46064439336](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064439336).
  - La prueba de cabeceras de `tests/test_web.py`, que encontró el espacio de sobra.
- **Qué hice:**
  - Fijé las acciones por commit en sus versiones actuales, agregué `timeout-minutes` y una matriz con 3.12 y 3.13.
  - Agregué un trabajo que construye y prueba el contenedor (commits [89c7ca0](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/89c7ca0) y [58762b4](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/58762b4)).
  - Comprobé que una prueba dañada a propósito pone el pipeline en rojo ([ejecución 46064652666](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064652666)).
  - El detalle está en [revision_configuracion.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/revision_configuracion.md).

## 5. Estado final del sistema

- **Arquitectura:** monolito modular en Python, con un módulo por carpeta en `app/` ([ADR-001](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-001-monolito-modular.md)). La versión web usa `http.server` de la biblioteca estándar ([ADR-003](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-003-version-web-local.md)): escucha solo en el equipo, escapa todo lo que escribe el usuario y tiene `/salud` para la operación. Después del despliegue, el cliente pidió guardar los datos. Las órdenes se guardan en PostgreSQL 16, o en un archivo SQLite si no hay servidor, con las mismas consultas ([ADR-004](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-004-persistencia-y-etapas.md)). FastAPI y React siguen previstos para cuando haya usuarios con inicio de sesión.
- **Funcionalidades terminadas.** Cada escenario Gherkin de la semana 3 se evaluó con sus datos exactos. Cada escenario construido tiene su prueba de aceptación en [tests/test_aceptacion.py](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/tests/test_aceptacion.py) y [tests/test_aceptacion_taller.py](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/tests/test_aceptacion_taller.py). Se cumplen 11 de 20 escenarios, 3 en parte y 6 no se han construido. El cliente cambió "Lista para entregar" por Terminada:

  | Historia | Resultado |
  |---|---|
  | HU-03 Número de orden (Must) | Cumple 2 de 2: ocho dígitos sin repetir y una sola orden abierta por moto |
  | HU-04 Consulta del cliente (Must) | Cumple 2 de 2: etapa y fecha de la última actualización, y el mensaje del número que no existe. Máximo 5 consultas cada 15 minutos |
  | HU-06 Cambio de etapa (Must) | Cumple 2 de 2: Terminada con fecha y hora, y no se termina sin mano de obra |
  | HU-07 Repuestos y mano de obra (Must) | Cumple 2 de 2: total sin IVA de 85.000 guardado en la base, y repuesto sin precio que no se agrega |
  | HU-08 Detalle del cobro (Should) | Cumple 2 de 2: detalle con cada ítem y el total, solo cuando está Terminada |
  | HU-02 Estado de llegada (Must) | Cumple el escenario 2 (observación vacía). El 1 en parte: se guarda con fecha y hora, pero sin el nombre del registrador, porque no hay usuarios |
  | HU-01 Registrar el ingreso (Must) | Escenario 1 en parte: se guardan la placa, las observaciones, la fecha y la hora, pero no el kilometraje ni el dueño, por decisión del cliente. Escenario 2 (kilometraje vacío) sin construir |
  | HU-05 Asignar mecánico (Should) | Escenario 1 en parte: el mecánico se elige al registrar. Escenario 2 (cambiar de mecánico) sin construir |
  | HU-09 Historial por placa (Could) y HU-10 Entrega (Should) | Sin construir |

- **Pruebas:**
  - 194 pruebas: 20 de las semanas 5 y 6, 50 de la semana 7, 34 de la versión web, 3 de aceptación de la sustentación, 69 de la base de datos (reglas, páginas por HTTP y 13 de aceptación) y 18 de la interfaz.
  - En el pipeline, las pruebas de las órdenes se repiten contra un PostgreSQL 16 desechable: 239 en total.
  - Cobertura en el pipeline: 100 % de líneas y de ramas en `calculo.py`, `servicio.py` de cobros y de órdenes, `placas.py` y `paginas.py`, y 94 % del total. Lo que falta son los demos, el ciclo de arranque del servidor y algunas ramas de error de la base de datos.
  - Mutación a mano: 11 de 11 mutantes detectados en las reglas y en la versión web.
  - [Última ejecución del pipeline en `main`](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/workflows/calidad.yml?query=branch%3Amain), en verde con Python 3.12, 3.13, PostgreSQL y el contenedor. La [ejecución 46084960626](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46084960626) es la de la rama de la base de datos.
- **Pendientes y por qué:**
  - Faltan los usuarios con inicio de sesión: hoy quien registra un cobro elige su nombre en una lista. También faltan el kilometraje y los datos del dueño, el cambio de mecánico, la entrega con el número de orden y el historial por placa. Se priorizó que lo construido estuviera probado y guardado.
  - Seis preguntas al cliente siguen abiertas (P-01 a P-12 en los documentos), por ejemplo, si una descripción vacía es válida o si debe haber un precio máximo.

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | El sistema guarda la fecha y hora de ingreso, la placa, las observaciones, el mecánico, las etapas y la factura, y ningún dato personal del cliente. Quité la cédula, el correo y el número de tarjeta que propuso la IA, porque ninguna historia los necesita. La consulta pública responde la etapa, la fecha y, al terminar, el total, nunca la placa. El registro del servidor oculta los números de orden. Los nombres reales de los mecánicos solo están en el `.env` de cada equipo, que no se sube; en el repositorio son ficticios. Las pruebas usan datos sintéticos (teléfonos con 555, una marca ficticia) y la entrevista es simulada. Pendiente antes de guardar datos del dueño: la autorización previa, expresa e informada del titular, y una forma de conocer, actualizar y rectificar sus datos | [Diseño, sección 5](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/Trujillo_Juan_S4_Diseno.pdf), [ADR-002](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/adr/ADR-002-numero-de-orden.md), [datos sintéticos](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/tests/datos/datos_sinteticos.json), [servidor.py](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/app/web/servidor.py) |
| Sesgo | La IA trajo supuestos de otros contextos: IVA del 19 %, precios con decimales, cédula y pago con tarjeta. Cada regla se comparó con lo que dijo el taller. Los datos sintéticos incluyen tildes, ñ y apóstrofos (Begoña Ñáñez, José D'Alessandro) para que el sistema no falle con nombres comunes en Colombia. Riesgo abierto: la placa solo acepta los formatos ABC12D y ABC12, así que una moto con otro formato (por ejemplo, una placa extranjera) quedaría por fuera. Por eso es la pregunta P-08 para el cliente, no una regla cerrada | [registro_pruebas.md, secciones 1.4 y 4](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/registro_pruebas.md), bitácora, entrada 3 |
| Transparencia | La página dice que es una versión de demostración que no guarda datos. Los errores explican la regla que no se cumple ("Fila 2: El precio no puede ser negativo"). El README, la bitácora y este informe declaran el uso de IA, y la entrevista se presenta como simulada | [Captura de la página](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/evidencias/web_cobro_error.png), [README, Uso de IA](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/README.md) |
| Responsabilidad | Respondo yo por los errores del software, no la IA. Ninguna sugerencia entró sin verificación y la bitácora registra quién decidió qué. El plan de operación define qué hacer si un cobro no cuadra: reproducir el caso con una prueba, corregir y, mientras tanto, cobrar a mano. Los términos de Anthropic advierten que no se debe confiar en las respuestas sin confirmarlas por cuenta propia, y así se trabajó | [Plan de operación, secciones 4 y 6](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/plan_operacion.md), [bitácora](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/bitacora_ia.md) |
| Propiedad intelectual y política de uso | El código es del proyecto, con licencia MIT. No copié código de terceros. Las herramientas de desarrollo (ruff, pytest, pytest-cov y pip-audit) son de código abierto y solo se usan para revisar, no se distribuyen con el sistema. El código de práctica de la semana 9 no se subió al repositorio. Los documentos citan sus fuentes en APA, por ejemplo Nygard (2011) para el formato de los ADR | [LICENSE](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/LICENSE), [requirements-dev.txt](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/requirements-dev.txt) |

**El dilema más importante.** En el diseño, la IA propuso guardar la cédula del cliente, y la idea tenía un argumento a favor: al entregar la moto, la cédula serviría para comprobar que quien la recoge es el dueño. Pero la Ley 1581 pide que cada dato tenga una finalidad y que el titular autorice su tratamiento, y guardar cédulas convierte una libreta de taller en una base de datos que hay que proteger. Además, la historia HU-10 ya resuelve la entrega con el número de orden que lleva el cliente. Decidí no guardar la cédula y dejar en pregunta para el dueño del taller si quiere comprobar la identidad al entregar. Si la respuesta es sí, se mira el documento en el mostrador sin registrarlo. Así el sistema guarda lo mínimo para funcionar.

## 7. Aprendizajes

**Qué sé hacer ahora que no sabía al empezar:**

- Escribir prompts con rol, contexto, tarea, formato y restricciones.
- Convertir una entrevista en historias con criterios que se pueden probar.
- Decidir una arquitectura con una matriz ponderada y dejarla en un ADR.
- Trabajar con pruebas primero.
- Diseñar casos con particiones, límites y tablas de decisión.
- Medir si una suite sirve rompiendo el código, no solo con la cobertura.
- Revisar un pipeline y un Dockerfile con una lista concreta.

**En qué confié de más en la IA:** en que una prueba en verde estaba bien. El borrador de la semana 7 tenía 50 pruebas en verde y varias no comprobaban nada; solo lo vi al romper el código. También confié en el contexto de prompts viejos: el IVA del prompt de la semana 2 reapareció en la semana 5.

**Qué haría distinto:**

- Escribiría la regla y los resultados esperados antes de pedirle código o pruebas a la IA.
- Pondría el pipeline con cobertura desde el primer commit.
- Haría al menos una entrevista con un taller real.
- Le daría a la IA la lista de revisión desde el primer prompt de configuración. El Dockerfile, que se pidió con la lista, salió con un solo pendiente; el pipeline, pedido con un prompt simple, tuvo seis hallazgos.

## 8. Anexos

- Bitácora de uso de IA: [bitacora_ia.md](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/bitacora_ia.md), 45 entradas de las semanas 5 a 10, más el recorrido de las semanas 2 a 4.
- Documentos de cada módulo: [índice de docs/](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/README.md).
  - [Propuesta](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/01_fundamentos/propuesta.md).
  - [Requisitos](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/02_requisitos/Trujillo_Juan_S3_Requisitos.pdf).
  - [Diseño](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/03_diseno/Trujillo_Juan_S4_Diseno.pdf) y ADR.
  - [Revisión de código y seguridad](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/revision_seguridad.md).
  - [Plan y registro de pruebas](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/registro_pruebas.md).
  - [Guía de despliegue](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/guia_despliegue.md).
  - [Plan de operación](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/plan_operacion.md).
  - [Revisión de configuración](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/revision_configuracion.md).
  - [Registro de despliegues](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/06_operacion/despliegue_realizado.md).
- Sustentación: [diapositivas en PDF](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/entrega_final/Trujillo_Juan_Sustentacion_Final.pdf) y [preparación de preguntas](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/main/docs/entrega_final/preguntas_sustentacion.md).
- Pipeline: [ejecuciones de GitHub Actions](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions).

### Referencias

Anthropic. (2026). *Claude* [Modelo de lenguaje grande]. https://claude.ai

Congreso de la República de Colombia. (2012, 17 de octubre). *Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales*. Diario Oficial 48.587.

Nygard, M. (2011, 15 de noviembre). *Documenting architecture decisions*. Cognitect. https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
