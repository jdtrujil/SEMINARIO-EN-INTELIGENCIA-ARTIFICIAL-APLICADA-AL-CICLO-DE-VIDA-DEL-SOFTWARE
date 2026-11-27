# ADR-001. Monolito modular web con FastAPI y PostgreSQL

Tomado del [documento de diseño de la semana 4](../Trujillo_Juan_S4_Diseno.pdf), sección 4.

**Estado:** Aceptada. La implementación sigue la estructura modular (`app/cobros`, `app/ingresos`, `app/web`). FastAPI, PostgreSQL y React siguen pendientes; ver [ADR-003](ADR-003-version-web-local.md).

## Contexto

El taller recibe entre 20 y 25 motos al día, con picos de unas 10 seguidas en la mañana. A ese ritmo, 20.000 órdenes son más de dos años de trabajo.

- **Usuarios:** 3 trabajadores (el registrador y dos mecánicos) desde una tablet de 10 pulgadas y navegadores. Los clientes consultan desde su celular sin crear cuenta.
- **Conexión:** el internet sale del celular del dueño y a veces se cae.
- **Negocio:** el cobro es repuestos más mano de obra, sin IVA, y no hay sistemas externos.
- **Equipo y presupuesto:** el desarrollo lo hace una sola persona y el presupuesto se asume bajo.

Los requisitos que más pesan son RNF-01, RNF-03, RNF-04 y RNF-05.

## Decisión

Construir el sistema como un monolito modular:

- Una sola API en Python con FastAPI, dividida en módulos de ingresos, órdenes y estados, cobros, consulta pública y usuarios.
- Una base de datos PostgreSQL 16.
- Una aplicación web en React que se entrega desde el mismo despliegue, en un solo servidor en la nube.

## Alternativas consideradas

- **Microservicios:** descartada.
  - Con 25 motos al día no hay carga que repartir.
  - Multiplica los despliegues y las bases de datos para un solo desarrollador.
  - Deja la auditoría de RNF-05 repartida entre servicios.
- **Aplicación local primero, con sincronización:** descartada por ahora.
  - Guarda datos de clientes en la tablet, lo que debilita RNF-03.
  - La sincronización hace difícil saber quién cambió qué y cuándo (RNF-05).
  - Se revisará cuando el cliente responda la pregunta P-05.
- **Backend como servicio, por ejemplo Supabase:** lo propuso la IA y se descartó. Los permisos por rol y la auditoría quedarían en reglas del proveedor, y el taller dependería de él.

## Consecuencias

**Positivas:**

- Un solo lugar para validar roles, limitar los intentos de consulta y guardar la auditoría.
- Transacciones simples en una sola base de datos.
- Despliegue y costo bajos, que una sola persona puede mantener.

**Negativas:**

- Sin internet no se pueden crear órdenes.
- Si la API falla, se cae todo el sistema.
- Crecer a varias sedes exigiría separar módulos.

La decisión se revisaría en tres casos: si las caídas de internet duran más de una hora varias veces por semana, si el taller abre otra sede o si pasa de 100 motos al día.

## Uso de IA

Claude propuso cuatro alternativas y recomendó microservicios en Kubernetes por escalabilidad. No se aceptó la recomendación, porque la escalabilidad pesa 1 en la matriz de atributos de calidad.
