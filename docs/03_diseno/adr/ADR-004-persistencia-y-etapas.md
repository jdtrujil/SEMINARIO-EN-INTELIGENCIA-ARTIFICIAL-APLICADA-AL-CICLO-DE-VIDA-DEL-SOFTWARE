# ADR-004. Guardar las órdenes en PostgreSQL, con SQLite cuando no hay servidor

**Estado:** Aceptada
**Fecha:** 2026-11-27

## Contexto

Después de desplegar la versión web local, el cliente pidió cuatro cosas:

1. Guardar la fecha y hora de ingreso, la placa, las observaciones y la factura.
2. Elegir al registrar la moto cuál de los dos mecánicos la toma.
3. Llevar la moto por las etapas Recibida, En reparación y Terminada, con su historial.
4. Guardar la factura al terminar, para que el cliente consulte el total con su número de orden.

El ADR-001 ya preveía PostgreSQL 16. El equipo del taller tiene Windows y Python 3.13, y PostgreSQL todavía no está instalado.

## Decisión

- Las órdenes se guardan en **PostgreSQL 16** cuando existe `DATABASE_URL=postgresql://...`, con el paquete psycopg fijado en `requirements.txt`.
- Si esa variable no existe, se guardan en un **archivo SQLite** (`taller.db`) de la biblioteca estándar, con las mismas consultas. Así el sistema funciona desde el primer día y pasa a PostgreSQL sin cambiar el código.
- Las etapas son **Recibida → En reparación → Terminada**, sin saltos. Cada cambio queda en la tabla `historial` con su fecha y hora. "Lista para entregar", de las historias de la semana 3, pasa a llamarse Terminada.
- Los repuestos y la mano de obra solo se registran **En reparación**, y solo los registra el mecánico asignado (H-05). Para terminar hace falta al menos una mano de obra (HU-06). Al terminar se calcula y se guarda la factura, y ya no se pueden agregar ítems.
- El número de orden sigue el ADR-002: ocho dígitos al azar y 5 consultas cada 15 minutos por equipo. Por pedido del cliente, la consulta muestra también el detalle y el total cuando la moto está Terminada. Nunca muestra la placa.
- **No se guardan datos personales del cliente.** Los nombres reales de los mecánicos se configuran en el `.env` de cada equipo (`TALLER_MECANICOS`), que no se sube al repositorio. En el repositorio solo hay nombres ficticios.

## Alternativas consideradas

- **Solo PostgreSQL:** descartada por ahora. El sistema no arrancaría en el PC hasta instalarlo y configurarlo.
- **Solo SQLite:** descartada. No cumple el ADR-001 ni lo que pidió el cliente.
- **Un ORM (SQLAlchemy):** descartada. Agrega una dependencia grande para cuatro tablas.

## Consecuencias

- **Pruebas:** las de las órdenes corren contra SQLite en el equipo y también contra PostgreSQL 16 en el pipeline, con un servicio desechable.
- **Respaldo:** ahora hay datos que respaldar. Ver la sección 5 del plan de operación.
- **Pendientes:**
  - Los usuarios con inicio de sesión. Hoy quien registra un cobro elige su nombre en una lista, y el permiso se comprueba con esa elección.
  - El kilometraje y los datos del dueño de la HU-01, que el cliente decidió no guardar por ahora.
