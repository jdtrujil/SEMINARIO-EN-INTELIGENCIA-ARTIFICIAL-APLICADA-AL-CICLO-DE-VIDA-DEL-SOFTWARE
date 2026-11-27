# Taller Dos Ruedas: control de ingreso de motos

Proyecto final del Seminario Inteligencia Artificial Aplicada al Ciclo de Vida del Software.
Estudiante: Juan Diego Trujillo Rodriguez.

El sistema registra el ingreso de motos a un taller, asigna el trabajo a los mecánicos, calcula el cobro de repuestos y mano de obra sin IVA y permite que el cliente consulte con su número de orden si la moto ya está lista. La arquitectura es un monolito modular (ADR-001 de la semana 4): cada módulo vive en su propia carpeta dentro de `app`.

## Estructura

```
app/
  cobros/
    calculo.py              Cálculo del cobro de una orden (HU-07)
tests/
  test_calculo_cobro.py     Pruebas de la HU-07
bitacora_ia.md              Bitácora de uso de IA
.vscode/tasks.json          Tareas de VS Code para ejecutar las pruebas
```

## Funcionalidad de la semana 5

### Historia de usuario

**HU-07** (prioridad Must). Como mecánico, quiero registrar los repuestos que usé y la mano de obra de cada orden para que el cobro al cliente salga de lo que de verdad se le hizo a la moto.

Necesidad de origen N-06. Registrador: "Aquí cobramos lo que lleve en repuestos más la mano de obra, no cobramos IVA".

Criterios de aceptación:

- **Escenario 1: total sin IVA.** Dado que en la orden 48271936 registro un filtro de aceite de 18.000 pesos, un litro de aceite de 32.000 pesos y una mano de obra de 35.000 pesos, cuando guardo, entonces la orden muestra repuestos por 50.000 pesos, mano de obra por 35.000 pesos y un total a cobrar de 85.000 pesos, sin IVA.
- **Escenario 2 (error): repuesto sin precio.** Dado que agrego el repuesto "pastillas de freno" sin escribir el precio, cuando intento guardarlo, entonces el sistema no lo agrega y muestra "Escriba el precio del repuesto".

Alcance de esta entrega: la regla de negocio del cálculo, dentro del módulo `cobros`. Guardar los ítems en la base de datos y exponer el endpoint `POST /api/ordenes/{numero}/items` del documento de diseño quedan para las siguientes semanas.

### Contrato

```python
def calcular_cobro(items: list[ItemCobro]) -> ResumenCobro
```

**Qué recibe.** Una lista de `ItemCobro`, cada uno con estos campos:

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo` | `str` | "repuesto" o "mano de obra" |
| `descripcion` | `str` | Nombre del repuesto o del trabajo |
| `cantidad` | `int` | Unidades, mínimo 1 |
| `precio_unitario` | `int` o `None` | Pesos colombianos, sin decimales |

**Qué devuelve.** Un `ResumenCobro` con tres enteros:

| Campo | Cálculo |
|---|---|
| `total_repuestos` | Suma de cantidad por precio unitario de los ítems de tipo repuesto |
| `total_mano_obra` | Suma de cantidad por precio unitario de los ítems de tipo mano de obra |
| `total` | `total_repuestos` más `total_mano_obra`. Nunca se suma IVA |

**Supuestos.**

- Los valores van en pesos enteros, como se definió en el modelo de datos de la semana 4.
- El taller no cobra IVA (N-06).
- Un precio de 0 es válido, por ejemplo cuando el cliente trae el repuesto. Queda como pregunta para confirmar con el taller.
- La función solo calcula: no guarda nada ni modifica la lista que recibe.

**Casos límite.**

- Lista vacía: devuelve 0 en los tres totales.
- Solo mano de obra: el total de repuestos es 0.
- Precio 0: se acepta y no suma.
- Cantidad 1: es el mínimo válido.

**Errores.** La función lanza `ValueError` con estos mensajes:

| Situación | Mensaje |
|---|---|
| Repuesto sin precio | Escriba el precio del repuesto |
| Mano de obra sin valor | Escriba el valor de la mano de obra |
| Precio negativo | El precio no puede ser negativo |
| Cantidad menor que 1 | La cantidad debe ser al menos 1 |
| Tipo distinto de repuesto o mano de obra | Tipo de ítem no válido: (tipo recibido). Use repuesto o mano de obra |

**Ejemplos.**

| Entrada | Salida |
|---|---|
| Filtro de aceite 1 x 18.000, aceite 1 x 32.000, mano de obra 1 x 35.000 | `ResumenCobro(total_repuestos=50000, total_mano_obra=35000, total=85000)` |
| Aceite 2 x 32.000, mano de obra 1 x 35.000 | `ResumenCobro(total_repuestos=64000, total_mano_obra=35000, total=99000)` |
| Lista vacía | `ResumenCobro(total_repuestos=0, total_mano_obra=0, total=0)` |
| Pastillas de freno 1 x sin precio | `ValueError: Escriba el precio del repuesto` |

### Cómo ejecutar las pruebas

Requisito: Python 3.8 o superior. No hay dependencias externas.

```
python -m unittest discover -v
```

Si tienes pytest instalado, también funciona `python -m pytest -v`.

En VS Code: menú Terminal, Ejecutar tarea, "Ejecutar pruebas".
