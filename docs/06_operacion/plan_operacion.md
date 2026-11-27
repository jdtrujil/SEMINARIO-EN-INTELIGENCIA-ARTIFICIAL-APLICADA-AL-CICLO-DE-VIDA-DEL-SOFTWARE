# Plan de operación

Módulo 6, Operación. Proyecto Taller Dos Ruedas. Estudiante: Juan Diego Trujillo Rodriguez.

## 1. Qué se opera

La versión web local (`python -m app.web`, ADR-003) corre en el equipo del taller o en un contenedor. No guarda datos: cada página calcula el resultado y lo olvida.

## 2. Monitoreo

| Qué | Cómo | Cada cuánto | Señal de alarma |
|---|---|---|---|
| El servidor está arriba | `GET /salud` responde `ok`. En Docker lo revisa el `HEALTHCHECK` | Al abrir el taller y cada 30 segundos en Docker | No responde, o el contenedor aparece `unhealthy` |
| Errores de uso | Registro en la consola: fecha, método, ruta y código, por ejemplo `POST /cobro 422` | Revisión al cierre del día | Muchos 422 seguidos: un formulario confuso o datos mal escritos |
| Errores del sistema | Códigos 500 en el registro | Al aparecer | Cualquier 500: se abre un incidente |
| Calidad del código | Pipeline Calidad en cada envío: ruff, pip-audit, pruebas con cobertura, prueba de humo y contenedor | Cada envío | Pipeline en rojo: no se despliega esa versión |
| Vulnerabilidades | `pip-audit` en el pipeline | Cada envío y al menos una vez al mes | Cualquier vulnerabilidad en las herramientas fijadas |

El registro nunca incluye el contenido de los formularios. Escribe solo el método, la ruta y el código, así que no guarda placas, descripciones ni precios.

## 3. Indicadores

- **Disponibilidad en horario del taller:** que `/salud` responda durante toda la jornada.
- **Tiempo de respuesta:** menos de 2 segundos por página (RNF-02).
- **Pipeline:** la última ejecución de `main` en verde antes de cada despliegue.

## 4. Respuesta a incidentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| "No se pudo iniciar el servidor" al arrancar | El puerto 8000 está ocupado | `set TALLER_PUERTO=8001` y arrancar de nuevo |
| La página no abre | El servidor no está corriendo o se cerró la consola | Arrancar `py -m app.web` y comprobar `/salud` |
| Un cálculo da un valor que no cuadra | Error en una regla | Reproducir el caso, escribir la prueba que falla, corregir y desplegar. Mientras tanto se calcula a mano |
| Pipeline en rojo en `main` | Una prueba, el linter o pip-audit fallaron | No desplegar. Revisar el paso que falló. Si hace falta, volver a la versión anterior (guía de despliegue, sección 5) |
| pip-audit reporta una vulnerabilidad | Una herramienta de desarrollo con una falla conocida | Subir a la versión corregida en `requirements-dev.txt` y verificar en el pipeline |

## 5. Respaldo

Desde el ADR-004 el sistema guarda órdenes y facturas, así que hay que respaldarlas a diario al cerrar el taller:

- **Con PostgreSQL:** `pg_dump -U taller -F c -f respaldo_AAAA-MM-DD.dump taller`, y copiar el archivo a una memoria USB o a una carpeta en la nube del taller. Para restaurarlo: `pg_restore -U taller -d taller respaldo.dump`.
- **Con SQLite:** detener el servidor y copiar `taller.db`.

Una vez al mes se prueba restaurar un respaldo en otra base, para comprobar que sirve. El lugar definitivo depende de la pregunta pendiente P-04 para el cliente.

## 6. Responsables

| Rol | Persona | Responde por |
|---|---|---|
| Desarrollador y operador | Juan Diego Trujillo Rodriguez | El código, las pruebas, el pipeline, los despliegues y la corrección de errores |
| Dueño del taller | Por definir con el cliente | Aprobar cada versión antes de usarla con clientes y decidir sobre los datos |
| Asistente de IA (Claude) | No es responsable | Propone; toda propuesta se revisa y se registra en la bitácora |

## 7. Cambios y versiones

Cada cambio sigue el mismo camino:

1. Se hace en una rama.
2. El pipeline lo revisa.
3. Se integra a `main` con una solicitud de cambios revisada.

Las herramientas tienen la versión fijada en `requirements-dev.txt`, y las acciones del pipeline están fijadas por commit. La revisión de la configuración con la lista de la semana 9 está en [revision_configuracion.md](revision_configuracion.md).
