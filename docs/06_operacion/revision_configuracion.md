# Revisión del pipeline y del Dockerfile

Proyecto: Taller Dos Ruedas
Estudiante: Juan Diego Trujillo Rodriguez
Fecha: 2026-11-27

## 1. Cómo se generaron

**Herramienta de IA:** Claude (Anthropic), en modo agente con acceso a la terminal.

**Prompt del pipeline:** en la semana 6, el agente propuso un flujo de GitHub Actions que corriera ruff, pip-audit, las pruebas y el ejemplo en cada envío, con permisos de solo lectura ([bitácora, entrada 19](../../bitacora_ia.md#entrada-19); commit [5848e88](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/5848e88)). En la semana 7 se cambió a pytest, y en la entrega final se agregaron la cobertura y la prueba de humo. Esta revisión toma esa versión, la del commit [ebbc9bd](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/ebbc9bd).

**Prompt del Dockerfile:** "Escribe un Dockerfile para la versión web del Taller Dos Ruedas (python -m app.web, solo biblioteca estándar, puerto 8000) y su .dockerignore, siguiendo la lista de revisión de la semana 9: imagen base, secretos, usuario, .dockerignore, versiones y modo desarrollo" ([bitácora, entrada 35](../../bitacora_ia.md#entrada-35)). Como el prompt ya incluía la lista, la revisión del Dockerfile encontró menos problemas que la del pipeline, que se generó con un prompt simple.

## 2. Hallazgos

Las líneas del pipeline son las de la versión revisada ([ebbc9bd](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/blob/ebbc9bd/.github/workflows/calidad.yml)).

| Archivo y línea | Problema | Riesgo | Corrección |
|---|---|---|---|
| calidad.yml:15 y 17 | `actions/checkout@v4` y `actions/setup-python@v5`: etiquetas que se pueden mover | Si alguien mueve la etiqueta, el pipeline ejecuta otro código sin aviso | Acciones fijadas por commit, con la versión en un comentario |
| calidad.yml:15 y 17 | Esas versiones usan Node.js 20, que GitHub ya marca como obsoleto (aviso en la ejecución 46064439336) | El pipeline deja de funcionar cuando GitHub retire Node.js 20 | checkout v7.0.1 y setup-python v7.1.0, fijadas por commit ([58762b4](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/58762b4)) |
| calidad.yml:12-13 | Sin `timeout-minutes` | Un paso colgado, como un servidor que no arranca en la prueba de humo, puede gastar hasta 6 horas de minutos | `timeout-minutes: 10` en cada trabajo |
| calidad.yml:19 | Solo Python 3.12, aunque el PC del taller tiene Python 3.13 | Un error que solo pase en 3.13 aparecería por primera vez en el despliegue | Matriz con 3.12 y 3.13 |
| calidad.yml:40 y la espera del contenedor | Variable `intento` sin usar en los ciclos de espera (actionlint, SC2034) | Ninguno en la ejecución, pero es ruido que esconde avisos reales | `for _ in ...` ([58762b4](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/58762b4)) |
| Pipeline completo | Ningún paso construía ni probaba un contenedor | Un Dockerfile roto no se notaría hasta el despliegue | Trabajo `contenedor`: hadolint, actionlint, `docker build`, `docker run`, `/salud` y usuario 10001 |
| Dockerfile:7 | `python:3.13-slim` está fijada por etiqueta, no por digest | La imagen puede cambiar con un parche de seguridad sin aviso | Pendiente: fijar por digest y actualizarla a propósito cada mes |

**Revisado sin problemas, con la lista de la semana:**

- **Eventos:** `push` y `pull_request` en todas las ramas. La rama principal es `main` y sí corre.
- **Permisos:** `contents: read`.
- **Secretos:** ninguno en el pipeline, en el Dockerfile ni en el historial (`git log --all -p | grep -i -E "clave|secret|password|token"` solo muestra los valores de ejemplo de `.env.example` y textos de la documentación).
- **Dependencias:** fijadas en `requirements-dev.txt` y auditadas con pip-audit.
- **Fallo de pruebas:** no hay `continue-on-error`, así que una prueba que falla pone el pipeline en rojo.
- **Imagen base:** liviana, sin `latest`.
- **Usuario:** sin privilegios.
- **`.dockerignore`:** existe y deja fuera `.git`, `.env`, las pruebas y los documentos.
- **Modo desarrollo:** sin recarga automática ni depurador.

**Línea que parece un problema pero no lo es:** `ENV TALLER_HOST=0.0.0.0` en el Dockerfile. Dentro del contenedor, el servidor tiene que escuchar en todas sus interfaces para que llegue el puerto publicado. Quién puede entrar lo decide `-p 127.0.0.1:8000:8000` en el equipo anfitrión. Fuera del contenedor, el valor por defecto sigue siendo 127.0.0.1, y ruff marca S104 si alguien lo cambia en el código.

## 3. Lo que encontraron las herramientas

| Herramienta | Avisos | ¿Coinciden con mis hallazgos? | ¿Qué no encontró? |
|---|---|---|---|
| actionlint 1.7.12 | 2 avisos SC2034 de shellcheck: `intento` sin usar, en las líneas 44 y 72 | Es un hallazgo que la revisión manual no tenía | Las acciones por etiqueta, la falta de `timeout-minutes`, la versión única de Python y la falta del trabajo de contenedor |
| hadolint v2.12.0 | Ninguno | No aplica | La imagen fijada por etiqueta y no por digest; un `0.0.0.0` que sería peligroso fuera del contenedor |
| GitHub Actions | Aviso de Node.js 20 obsoleto en las dos acciones | Coincide con el hallazgo de las etiquetas, pero agrega la urgencia de actualizar | No aplica |

Ninguna herramienta encontró todo. Las decisiones que dependen del proyecto, como qué versión de Python tiene el taller o si debía probarse el contenedor, salieron de la revisión con la lista.

## 4. Verificación

- [x] El pipeline corregido se ejecutó en GitHub y salió en verde, con las dos versiones de Python y el contenedor: [ejecución 46064631239](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064631239).
- [x] Hice fallar una prueba a propósito y el pipeline salió en rojo: en la rama temporal `prueba-pipeline-rojo`, una prueba exigía el total con IVA (21.420) y el código dio 18.000. [Ejecución 46064652666](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064652666): las dos versiones de Python en rojo y el contenedor no se construyó. La rama no se integra.
- [x] La imagen se construye en el pipeline. El contenedor responde `ok` en `/salud` y corre con el usuario 10001.
- [x] No hay claves en `calidad.yml`, en el Dockerfile ni en el historial de Git.

## 5. Práctica de clase: código de Tienda La Esquina

Antes de revisar el proyecto, se practicó con el código de la semana 9 sin ejecutarlo, como pide su LEEME.

| Archivo | Hallazgos |
|---|---|
| ci.yml | 1. `branches: [ master ]`, pero la rama es `main`: el pipeline nunca corre. 2. `permissions: write-all`. 3. La clave escrita en `env` en lugar de `${{ secrets.CLAVE_RESPALDO }}`. 4. `python-version: 3.10` sin comillas, que YAML lee como 3.1. 5. `pip install pytest fastapi httpx` sin versiones, ignorando `requirements-dev.txt`. 6. `continue-on-error: true`: las pruebas pueden fallar y el pipeline sale en verde |
| Dockerfile | 1. `FROM python:latest`. 2. `ENV CLAVE_RESPALDO=...`: la clave queda dentro de la imagen. 3. `COPY . .` sin `.dockerignore` (el archivo que falta): copia `.env`, `.git` y las pruebas. 4. Corre como root, sin `USER`. 5. `--reload` es modo desarrollo. 6. `pip install` sin `--no-cache-dir` deja la caché en la imagen |
| La línea que no es un problema | `--host 0.0.0.0`: dentro del contenedor es necesario |
