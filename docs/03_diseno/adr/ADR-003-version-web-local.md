# ADR-003. Versión web local con la biblioteca estándar antes de FastAPI

**Estado:** Aceptada, temporal. Se reemplaza cuando se conecte PostgreSQL (ADR-001).
**Fecha:** 2026-11-27

## Contexto

Para la entrega final había que desplegar el sistema en un equipo y mostrarlo funcionando. El ADR-001 prevé FastAPI, PostgreSQL y React, pero de eso solo existen los módulos de reglas: el cobro (HU-07), el permiso de cobro y la validación de la placa (HU-01). La base de datos, los usuarios y la consulta pública no existen todavía. El equipo donde se despliega es un PC con Windows y Python 3.13, sin Docker. Desde la semana 5, el proyecto no tiene dependencias en tiempo de ejecución.

## Decisión

Construir una versión web local con `http.server` de la biblioteca estándar (`python -m app.web`) que:

- Muestre los formularios de la placa y del cobro.
- Reutilice `validar_placa` y `calcular_cobro`, sin duplicar reglas.
- Escuche solo en 127.0.0.1 por defecto.
- No guarde datos ni pida datos personales.
- Tenga una ruta `/salud` para la operación.

## Alternativas consideradas

- **FastAPI ahora:** descartada para esta entrega. Exige instalar paquetes en el equipo del taller, y sin base de datos no aporta nada que la versión local no tenga.
- **Solo el demo de consola (`python -m app.cobros`):** descartada. No deja usar el sistema desde el navegador ni sirve como despliegue.

## Consecuencias

**Positivas:**

- Se instala con copiar la carpeta y tener Python.
- Corre igual en el pipeline, en un contenedor y en el PC.
- Las reglas se prueban una sola vez.

**Negativas:**

- `http.server` no es un servidor para internet. Por eso escucha solo en el equipo local, limita el tamaño de los formularios y queda detrás de FastAPI cuando llegue la base de datos.
- No tiene usuarios, así que el permiso de cobro (H-05) no se aplica en la página: la página solo calcula el cobro, no lo registra en ninguna orden.

## Uso de IA

Claude escribió el módulo y sus pruebas (bitácora, entradas 32 y 33). La prueba de la cabecera `Server` encontró un espacio de sobra en el código generado, y la cobertura del pipeline mostró cuatro ramas de seguridad sin probar.
