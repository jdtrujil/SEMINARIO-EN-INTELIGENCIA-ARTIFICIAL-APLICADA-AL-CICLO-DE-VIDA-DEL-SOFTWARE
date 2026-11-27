# Registro de despliegues

Módulo 6, Operación. Proyecto Taller Dos Ruedas. Estudiante: Juan Diego Trujillo Rodriguez.

Cada despliegue sigue la [guía de despliegue](guia_despliegue.md) y se comprueba con su tabla de verificación (sección 4).

## 1. Contenedor en GitHub Actions

- **Fecha:** 2026-11-27
- **Versión:** commit [d2c1d9d](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/d2c1d9d), rama `entrega-final`
- **Dónde:** trabajo `contenedor` del pipeline, en un equipo Ubuntu de GitHub
- **Pasos:**
  1. hadolint revisa el Dockerfile y actionlint revisa el pipeline.
  2. `docker build -t taller-dos-ruedas .`
  3. `docker run -d -p 127.0.0.1:8000:8000 taller-dos-ruedas`
- **Verificación:**
  - `/salud` respondió `ok`.
  - `docker exec taller id -u` dio `10001`, el usuario sin privilegios.
  - El registro del contenedor muestra solo el método, la ruta y el código.
- **Resultado:** en verde, [ejecución 46065039912](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46065039912). El pipeline repite este despliegue en cada envío.

## 2. Ejecución de verificación con Python, sin contenedor

- **Fecha:** 2026-11-27
- **Versión:** rama `entrega-final`, con las 104 pruebas en verde
- **Dónde:** el equipo de desarrollo del agente (Linux, Python 3.13), con la opción A de la guía
- **Pasos:** `python -m app.web`
- **Verificación:**

  | Paso de la guía | Resultado |
  |---|---|
  | `GET /salud` | 200 y `ok` |
  | Página de inicio | 200, con los formularios `/placa` y `/cobro` ([captura](../evidencias/web_inicio.png)) |
  | Cobro con 18.000, 32.000 y 35.000 | 200, total sin IVA $ 85.000 ([captura](../evidencias/web_cobro.png)) |
  | Cobro con -32.000 en la fila 2 | 422, "Fila 2: El precio no puede ser negativo" ([captura](../evidencias/web_cobro_error.png)) |
  | Placa `ABC-12D` | 422, "Placa no válida: use el formato ABC12D o, si es antigua, ABC12" ([captura](../evidencias/web_placa_error.png)) |
  | Placa `abc12d` | 200, "Placa válida: ABC12D" |

- **Registro de la consola** (sin la fecha y la hora):
  ```
  INFO GET /salud 200
  INFO GET / 200
  INFO POST /cobro 200
  INFO POST /cobro 422
  INFO POST /placa 422
  INFO POST /placa 200
  ```
  El registro no muestra placas, descripciones ni precios.

- **Incidente durante la verificación:** al arrancar el servidor una segunda vez sin detener el primero, la consola mostró "No se pudo iniciar el servidor: [Errno 98] Address already in use" y la sugerencia de usar otro puerto. Es el primer caso de la tabla de incidentes del [plan de operación](plan_operacion.md). Se resolvió deteniendo el proceso anterior.

## 3. PC con Windows del estudiante

Pendiente. Se hará con la opción A de la guía (Python 3.13, `py -m app.web`) y se registrará aquí con la fecha, la versión, el resultado de las pruebas y las capturas.
