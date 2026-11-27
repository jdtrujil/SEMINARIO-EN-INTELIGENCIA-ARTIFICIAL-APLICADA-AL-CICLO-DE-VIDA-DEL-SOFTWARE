# ADR-002. Consulta del cliente con número de orden aleatorio y límite de intentos

Tomado del [documento de diseño de la semana 4](../Trujillo_Juan_S4_Diseno.pdf), sección 4.

**Estado:** Aceptada. Pendiente de implementar: la consulta pública todavía no está construida (ver la sección 5 del informe final).

## Contexto

El cliente no tiene cuenta y solo recibe el número de orden (N-03 y N-10). La clienta de la entrevista dijo que con el número le basta, pero que no quiere que otra persona vea su moto o su teléfono. Hoy los números del talonario son consecutivos, como el 0457, así que se pueden adivinar. Se crean unas 25 órdenes al día.

## Decisión

- Cada orden recibe un número de ocho dígitos al azar que no se repite.
- La consulta pública no pide usuario ni contraseña.
- Solo responde el estado de la moto y la fecha de la última actualización.
- Bloquea durante 15 minutos al dispositivo que escribe 5 números equivocados seguidos (RNF-03 y RNF-04).

## Alternativas consideradas

- **Cuenta de cliente con usuario y contraseña:** descartada. La clienta pidió consultar solo con el número, y la cuenta agrega un paso al ingreso, que ya es el cuello de botella de la mañana.
- **Número consecutivo, como el del talonario:** descartado. Cualquiera podría recorrer los números y ver el estado de motos ajenas.

## Consecuencias

**Positivas:**

- La clienta consulta en segundos desde su celular.
- Hay 90 millones de números posibles y solo se permiten 5 intentos cada 15 minutos, así que adivinar un número es muy poco probable.

**Negativas:**

- Quien tenga el papel puede ver el estado de la moto.
- Un bloqueo afecta a todas las personas que comparten la misma red.
- El contador de intentos se reinicia si se reinicia el servidor.

## Uso de IA

La IA propuso validar al cliente con un código enviado por mensaje de texto. Se descartó porque no tiene apoyo en la entrevista y cada mensaje tiene un costo.
