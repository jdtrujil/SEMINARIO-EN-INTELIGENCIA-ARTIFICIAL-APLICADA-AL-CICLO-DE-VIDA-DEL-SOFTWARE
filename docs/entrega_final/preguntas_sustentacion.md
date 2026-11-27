# Preparación de las preguntas de la sustentación

Proyecto Taller Dos Ruedas. Estudiante: Juan Diego Trujillo Rodriguez.

Estas preguntas las simuló Claude a partir de los ejemplos del PDF del proyecto final y del código del repositorio, como permite la tarea ([bitácora, entrada 42](../../bitacora_ia.md#entrada-42)). Las respuestas las verifiqué contra el código y los documentos; cada una dice dónde está la evidencia para abrirla en vivo.

## Del código

**1. "Abre `calcular_cobro` y explica la línea del precio que falta."**
[`app/cobros/calculo.py:73`](../../app/cobros/calculo.py): `if item.precio_unitario is None`. Compara con `None` y no con `not`, porque en Python `not 0` es verdadero. La primera versión de la IA usaba `not` y rechazaba una llanta que trae el cliente, con precio 0. La prueba de límite `test_precio_cero_se_acepta_y_no_suma` lo detectó (bitácora, entrada 4).

**2. "¿Por qué `_es_entero` excluye `bool`?"**
[`calculo.py:97`](../../app/cobros/calculo.py). En Python, `True` es un `int` que vale 1, así que una cantidad `True` pasaría como 1. Es la partición P17 del registro de pruebas y salió de la revisión de seguridad de la semana 6 (hallazgo H-03).

**3. "¿Por qué `registrar_item` calcula antes de agregar el ítem?"**
[`app/cobros/servicio.py:37-39`](../../app/cobros/servicio.py): primero verifica el permiso, después valida con `calcular_cobro([*orden.items, item])` y solo al final hace `append`. Si se agregara antes, un ítem inválido quedaría en la orden. La mutación M6 hizo justo eso y dos pruebas fallaron.

**4. "¿Qué hace `html.escape` en las páginas?"**
[`app/web/paginas.py:304`](../../app/web/paginas.py) y en cada lugar donde se muestra lo que escribe el usuario. Evita que una descripción como `<script>` se ejecute en el navegador. La prueba `test_descripcion_con_codigo_html_se_muestra_escapada` falla si se quita (mutación W1).

**5. "¿Por qué el servidor escucha en 127.0.0.1 y el contenedor en 0.0.0.0?"**
[`app/web/servidor.py:33`](../../app/web/servidor.py): por defecto solo el mismo equipo puede entrar, porque todavía no hay inicio de sesión. Dentro del contenedor hace falta 0.0.0.0 para que llegue el puerto publicado, y quién entra lo decide `-p 127.0.0.1:8000:8000` en el equipo. Si alguien cambia el valor por defecto en el código, ruff marca S104 y dos pruebas fallan (mutación W4).

**6. "¿Cómo valida la placa?"**
[`app/ingresos/placas.py:8`](../../app/ingresos/placas.py) y la línea 33: tres letras, dos números y una letra opcional, con `fullmatch`. Con `match`, "ABC12DE" pasaría por tener un comienzo válido. Antes de validar quita los espacios a los lados y pasa a mayúsculas, que fueron las decisiones A1 y A2.

## De la IA y la verificación

**7. "¿Qué te habría pasado si aceptabas la respuesta de la IA sin revisarla?"**

- Dos requisitos con citas que el cliente nunca dijo.
- Una arquitectura de microservicios para 25 motos al día.
- La cédula y la tarjeta del cliente guardadas sin necesidad.
- Una llanta con precio 0 rechazada.
- Pruebas en verde que no detectaban un IVA.
- Un pipeline sin límite de tiempo y con acciones que se pueden mover.

Cada caso está en la sección 4 del informe con su commit.

**8. "¿Cómo sabes que tus pruebas sirven?"**
Rompiendo el código a propósito: 11 mutantes hechos a mano, todos detectados al final. Uno (M5) sobrevivió con 100 % de cobertura y obligó a agregar los casos P18 y P19 (commit [a138743](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/commit/a138743)). Detalle en la sección 5 de [registro_pruebas.md](../../registro_pruebas.md).

**9. "¿Por qué 87 % de cobertura y no 100 %?"**
Las reglas del negocio tienen 100 % de líneas y de ramas. Lo que falta son los dos demos (`__main__.py`) y el ciclo que arranca el servidor y espera Ctrl+C. Esos los comprueban la prueba de humo y el trabajo del contenedor del pipeline. Subirlos al 100 % no comprobaría ninguna regla.

**10. "¿Cómo sabes que el pipeline falla si una prueba falla?"**
Lo probé en la rama `prueba-pipeline-rojo`, con una prueba que exigía el total con IVA: la [ejecución 46064652666](https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE/actions/runs/46064652666) salió en rojo. No hay `continue-on-error`.

## De ética y mantenimiento

**11. "¿Qué dato personal maneja tu sistema y cómo lo proteges?"**

- **El diseño:** guarda solo el nombre y el teléfono del cliente, para avisarle.
- **La consulta pública:** responde solo el estado y la fecha, con un número aleatorio de 8 dígitos y un bloqueo después de 5 intentos ([ADR-002](../03_diseno/adr/ADR-002-numero-de-orden.md)).
- **La versión desplegada:** no pide ni guarda datos personales. Su registro escribe solo el método, la ruta y el código ([`servidor.py:121`](../../app/web/servidor.py)).
- **Antes de guardar datos reales:** falta la autorización del titular que pide la Ley 1581.

**12. "Si mañana la IA que usaste dejara de existir, ¿podrías mantener este código?"**
Sí, por cuatro razones:

- Usa solo la biblioteca estándar de Python.
- Cada regla está escrita en `registro_pruebas.md` con su tabla de casos.
- 107 pruebas me avisan si rompo algo.
- Las decisiones están en los ADR y en la bitácora.

La IA aceleró el trabajo, pero cada línea pasó por una prueba o por una revisión mía.

**13. "¿Por qué no usaste FastAPI como decía el diseño?"**
[ADR-003](../03_diseno/adr/ADR-003-version-web-local.md): sin base de datos, FastAPI no aportaba nada a la entrega y exigía instalar paquetes en el equipo del taller. La versión local reutiliza las mismas reglas, así que pasar a FastAPI después no cambia la lógica.
