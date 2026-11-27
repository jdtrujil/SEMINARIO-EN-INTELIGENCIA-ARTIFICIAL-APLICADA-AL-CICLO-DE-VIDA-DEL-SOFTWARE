# Informe de revisión de código y seguridad

Proyecto: Taller Dos Ruedas, sistema de control de ingreso de motos
Estudiante: Juan Diego Trujillo Rodriguez
Fecha: 2026-11-27
Commit revisado: e76b374 (cierre de la semana 5)

## 1. Herramientas y criterios

- **Linter:** ruff 0.16.9 con las reglas E, F, B y S. Configuración en `pyproject.toml`. Resultado final: "All checks passed!".
- **Auditoría de dependencias:** pip-audit 2.7.3 sobre `requirements-dev.txt`, ejecutado en GitHub Actions (ejecución 46039574878). Resultado: "No known vulnerabilities found". El sistema no tiene dependencias en tiempo de ejecución.
- **Lista de revisión:** la de la semana 6 (corrección y pruebas, diseño y legibilidad, seguridad).
- **Revisión con IA:** Claude, con el prompt de revisión de la semana (ver sección 3).
- **Pruebas:** 20 pruebas con unittest, todas en verde. Las 10 de la semana 5 no se modificaron.

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | No todavía: el módulo de cobros no consulta la base de datos ni arma comandos, y no hay SQL en el código | Sin hallazgos. Queda como pendiente para cuando se conecte PostgreSQL |
| Secretos (código, historial, .gitignore, .env.example) | Sí | No hay claves en el código ni en el historial; se buscó en `git log -p` de todo el repositorio, incluidos los commits anteriores. `.env` está ignorado. Faltaba `.env.example` y el patrón `.env.*` lo excluía: ver H-02 |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | No todavía: el sistema aún no guarda contraseñas | Sin hallazgos. El modelo de la semana 4 define `hashContrasena`; queda como pendiente |
| Control de acceso (rol verificado y prueba de abuso) | Sí | Registrar un cobro no verificaba quién lo hacía: ver H-05. Corregido con 4 pruebas de abuso |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | Sí | Ninguna dependencia en ejecución. Las herramientas de revisión quedaron fijadas (H-06) y pip-audit no encontró vulnerabilidades |

## 2. Tabla de hallazgos

| Id | Archivo y línea | Problema | Categoría (OWASP o tipo) | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | app/cobros/calculo.py:61 y 72 | Líneas de 93 y 91 caracteres (E501) | Estilo | Baja | Se dividieron las dos líneas | 8df8f4b |
| H-02 | .gitignore:3 | No existía `.env.example` y el patrón `.env.*` también lo habría ignorado | A05 Configuración de seguridad incorrecta | Baja | Se creó `.env.example` con valores de ejemplo y la excepción `!.env.example` | a9a2ada |
| H-03 | app/cobros/calculo.py:58 a 67 | No se validaba el tipo: un precio 18000.5 daba un total con decimales, `True` contaba como una unidad y un precio en texto lanzaba TypeError en lugar de ValueError | Validación de entradas | Media | `_es_entero` rechaza decimales, texto y booleanos. 4 pruebas nuevas | 4d79e2f |
| H-04 | app/cobros/calculo.py:67 | El mensaje "al menos 1" repetía a mano el valor de `CANTIDAD_MINIMA` | Valor mágico duplicado | Baja | El mensaje usa la constante | 7cc174a |
| H-05 | app/cobros (no existía la operación) | Nada impedía que un registrador o un mecánico no asignado agregara cobros a una orden, aunque la HU-07 es del mecánico y el diseño pide 403 | A01 Pérdida de control de acceso | Alta | `registrar_item` en `servicio.py` verifica rol y asignación antes de tocar la orden; `AccesoDenegado` hereda de PermissionError. 6 pruebas, 4 de abuso | ebddbcc |
| H-06 | pyproject.toml (no existía) | El linter no estaba configurado, las herramientas no tenían versión fijada y nada se revisaba al subir cambios | Proceso | Baja | Configuración de ruff, `requirements-dev.txt` y GitHub Actions con ruff, pip-audit y pruebas | ea32a15 y 5848e88 |
| H-07 | app/cobros/calculo.py:21 a 37 | Los modelos estaban dentro del cálculo, así que el control de acceso habría tenido que depender de él | Diseño y legibilidad | Baja | Los modelos pasan a `modelos.py`; `calculo.py` los reexporta | ec2a9cc |
| H-08 | app/cobros/calculo.py:40, 58 y 70 | Los docstrings no decían qué recibe, qué devuelve ni qué lanza cada función | Documentación | Baja | Docstrings completos, comparados con el código | 963b1b5 |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o riesgo con condiciones), baja (estilo o mantenibilidad).

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| E501 | tests/test_calculo_cobro.py:13, 21, 28, 34, 39, 42, 46 y 89 | Son las pruebas de la semana 5. Las líneas largas vienen de nombres de prueba descriptivos y de los datos del escenario. No se reformatean para no modificar ninguna prueba; se excluyen solo para ese archivo en `pyproject.toml` |

## 3. Revisión con IA

**Prompt usado:** "Actúa como revisor de código senior y de seguridad. Revisa app/cobros/calculo.py y sus pruebas con estos criterios: corrección frente al contrato del README (HU-07), casos límite, validación de entradas, control de acceso según la historia, manejo de errores, legibilidad y valores mágicos. Entrega una tabla con archivo y línea, problema, categoría, severidad (alta, media o baja) y corrección propuesta. Separa los problemas seguros de las sospechas que habría que comprobar. No reescribas el código." Le pegué el código, las pruebas, la HU-07 y la sección 6 del documento de diseño. Ver la bitácora, semana 6, entrada 1.

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| Seguro: no se valida el tipo de cantidad y precio | Real (H-03) | Ejecuté `calcular_cobro` con un precio de 18000.5 y devolvió un total de 18000.5; con cantidad `True` devolvió 18000 |
| Seguro: un precio en texto lanza TypeError y no el ValueError del contrato | Real (H-03) | Lo ejecuté con "18000" y salió TypeError |
| Seguro: el mensaje "al menos 1" duplica la constante | Real (H-04) | Leí la línea 67 del commit revisado |
| Seguro: registrar cobros no verifica que sea el mecánico asignado | Real (H-05) | El módulo no tenía ninguna verificación de rol ni de asignación |
| Sospecha: `MENSAJE_SIN_PRECIO[item.tipo]` puede lanzar KeyError | Falso positivo | El tipo se valida antes, en la línea 60. Probé un ítem de tipo "servicio" sin precio y salió el ValueError esperado |
| Sospecha: el mensaje de tipo inválido repite lo que escribió el usuario y podría servir para XSS | Falso positivo por ahora | La función devuelve texto plano, la API responderá JSON y React escapa el texto al mostrarlo. Queda en pendientes para revisarlo en la capa web |
| Sospecha: "Repuesto" con mayúscula se rechaza | Falso positivo | El contrato define los valores exactos y la API los enviará desde una lista fija. Normalizar escondería errores de quien llama |

**Lo que la IA no encontró:** que `.env.example` no existía y que el patrón `.env.*` de `.gitignore` lo habría ignorado (H-02); lo encontré al aplicar la lista de revisión y comprobarlo con `git check-ignore`. La IA tampoco revisó el historial de git en busca de claves, porque solo le pasé el código; esa búsqueda la hice yo con `git log -p` sobre todo el repositorio. Las líneas largas (H-01) las marcó ruff, no la IA.

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| Consultas con parámetros | El módulo aún no usa PostgreSQL | Usar siempre consultas con parámetros y agregar una prueba que envíe una placa con comillas y texto SQL |
| Contraseñas de los trabajadores | Todavía no hay inicio de sesión | Guardar solo el hash con argon2 o bcrypt con sal, nunca la contraseña |
| Bloqueo de la consulta del cliente (RNF-04) | La consulta pública aún no está implementada | Implementar el bloqueo de 15 minutos después de 5 números equivocados, con su prueba de abuso |
| Mensaje de error con texto del usuario | La capa web aún no existe | Verificar que la web muestre los errores como texto y no como HTML |

**Claves expuestas:** Ninguna. Se revisó todo el historial del repositorio y no hay claves, contraseñas ni archivos `.env`.
