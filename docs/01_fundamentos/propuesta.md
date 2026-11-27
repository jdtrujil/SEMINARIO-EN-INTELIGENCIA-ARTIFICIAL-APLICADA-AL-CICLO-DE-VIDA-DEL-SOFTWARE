# Propuesta del proyecto: Taller Dos Ruedas

Módulo 1, Fundamentos. Estudiante: Juan Diego Trujillo Rodriguez.
Este resumen reúne la definición del problema que se hizo en la semana 2 ([banco de prompts](Trujillo_Juan_S2_Banco.pdf)) con lo que confirmó la entrevista simulada de la semana 3 ([documento de requisitos](../02_requisitos/Trujillo_Juan_S3_Requisitos.pdf)).

## Problema

El Taller Dos Ruedas (nombre ficticio) es un taller de motos pequeño. Lo atienden un registrador, dos mecánicos y un ayudante, y recibe entre 20 y 25 motos al día de las marcas Kymco, Yamaha, Duke, Suzuki, Honda, Bajaj y AKT. Hoy el ingreso se anota en un cuaderno y al cliente se le entrega un papelito con un número consecutivo. Eso trae tres problemas:

- **Reclamos por el estado de llegada.** Cuando el cliente vuelve y dice que un rayón se lo hicieron en el taller, no hay un registro de cómo llegó la moto.
- **El cliente no sabe si la moto está lista.** Tiene que llamar o ir hasta el taller para preguntar.
- **El cobro se suma a mano.** Se cobran solo repuestos y mano de obra, sin IVA, y los errores de suma generan discusiones.

## Usuarios

| Usuario | Qué necesita |
|---|---|
| Registrador | Registrar la moto y su estado de llegada desde una tablet, de pie en la entrada |
| Mecánicos (2) | Ver sus órdenes, cambiar el estado y registrar repuestos y mano de obra |
| Cliente | Consultar con el número de orden si la moto ya está lista, sin crear una cuenta |
| Ayudante | No usa el sistema |

## Solución propuesta

Un sistema web que registra el ingreso con un número de orden que no se puede adivinar, asigna el trabajo a cada mecánico, calcula el cobro de repuestos y mano de obra sin IVA y deja que el cliente consulte el estado con su número.

## Herramienta de IA prevista

Claude (Anthropic) en todas las fases:

- En modo chat para los documentos: prompts, requisitos y diseño.
- En modo agente con terminal para el código, las pruebas, la revisión y la configuración del despliegue.

Cada uso queda en la [bitácora de IA](../../bitacora_ia.md) con lo que se aceptó, se cambió o se rechazó.

## Lo que se construyó en el seminario

- Módulo de cobros, HU-07:
  - Cálculo sin IVA.
  - Control de acceso: solo el mecánico asignado registra cobros.
- Validación de la placa al ingresar la moto, HU-01.
- Versión web local para validar la placa y calcular el cobro, con contenedor Docker y pipeline de GitHub Actions.

Lo que no se construyó está en la sección 5 del [informe final](../../informe_final.md).
