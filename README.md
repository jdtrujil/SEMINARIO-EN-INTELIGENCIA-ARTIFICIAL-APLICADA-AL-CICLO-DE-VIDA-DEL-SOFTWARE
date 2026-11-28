# Taller Dos Ruedas: control de ingreso de motos

## Qué es

Sistema web para el Taller Dos Ruedas (nombre ficticio), un taller de motos con un registrador, dos mecánicos y un ayudante. Registra el ingreso de cada moto, asigna el trabajo a los mecánicos, calcula el cobro de repuestos y mano de obra sin IVA y permite que el cliente consulte con su número de orden si la moto ya está lista. Es el proyecto final del Seminario Inteligencia Artificial Aplicada al Ciclo de Vida del Software.

La arquitectura es un monolito modular ([ADR-001](docs/03_diseno/adr/ADR-001-monolito-modular.md)): cada módulo vive en su propia carpeta dentro de `app`. Estado de la entrega final:

- `cobros`: calcula el cobro de una orden sin IVA (HU-07) y solo deja registrar cobros al mecánico asignado.
- `ingresos`: valida la placa de la moto (HU-01).
- `ordenes`: registra el ingreso con la fecha y hora, la placa, las observaciones y el mecánico. Lleva la moto por las etapas Recibida, En reparación y Terminada, con su historial, y guarda la factura al terminar. El cliente consulta la etapa y el total con su número de orden. Usa PostgreSQL 16, o un archivo SQLite si no hay PostgreSQL ([ADR-004](docs/03_diseno/adr/ADR-004-persistencia-y-etapas.md)).
- `web`: las páginas del taller y de la consulta del cliente ([ADR-003](docs/03_diseno/adr/ADR-003-version-web-local.md)), también disponibles como contenedor Docker.

El [informe final](informe_final.md) resume el proyecto y el uso de IA en cada fase, y los documentos de cada módulo están en [docs/](docs/README.md).

## Requisitos

- Python 3.8 o superior. En Windows se puede instalar desde Microsoft Store o python.org.
- Git, para clonar el repositorio.
- Para ejecutar el sistema no hace falta instalar ninguna librería.
- Para las pruebas y la revisión del código: las herramientas de `requirements-dev.txt` (ruff, pytest y pip-audit), con versión fijada.

## Instalación

```
git clone https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE.git
cd SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE
```

Herramientas de pruebas y revisión, dentro de un entorno virtual:

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # Linux o macOS
pip install -r requirements-dev.txt
```

Las variables de entorno que usará la API cuando se conecte la base de datos están en `.env.example`. Copia ese archivo como `.env` y pon tus valores; `.env` nunca se sube al repositorio.

## Ejecución

Versión web (con SQLite solo usa la biblioteca estándar; para PostgreSQL, `pip install -r requirements.txt` y `DATABASE_URL` en el archivo `.env`):

```
python -m app.web
```

Abre http://127.0.0.1:8000 para registrar motos, llevarlas por sus etapas y guardar la factura. El cliente consulta en http://127.0.0.1:8000/consulta. `http://127.0.0.1:8000/salud` responde `ok` si la base responde. Los nombres de los mecánicos, el nombre del taller y el logo se ponen en `.env` (`TALLER_MECANICOS`, `TALLER_NOMBRE` y `TALLER_LOGO`, con la imagen en la carpeta `marca/`). Ninguno se sube al repositorio. El servidor escucha solo en este equipo; el puerto se cambia con la variable `TALLER_PUERTO`. Pasos completos, verificación y cómo volver atrás: [guía de despliegue](docs/06_operacion/guia_despliegue.md).

En Windows, `desplegar_windows.bat` hace todo con doble clic: prepara el entorno, corre las pruebas y, solo si pasan, arranca la versión web y abre el navegador.

Con Docker:

```
docker build -t taller-dos-ruedas .
docker run --rm -p 127.0.0.1:8000:8000 taller-dos-ruedas
```

Ejemplo en la consola:

```
python -m app.cobros
```

Registra los ítems del escenario 1 de la HU-07 en la orden 48271936 y muestra el cobro: repuestos 50.000, mano de obra 35.000 y total sin IVA 85.000. Al final muestra que un mecánico que no tiene la orden recibe acceso denegado.

En Windows, si `python` no responde, usa `py` en su lugar.

## Pruebas

```
python -m pytest -v
```

Corre las 176 pruebas (en el pipeline, las de órdenes se repiten contra PostgreSQL 16):

- 10 de la semana 5 y 10 de la semana 6, escritas con unittest (pytest también las ejecuta).
- 50 de la semana 7, diseñadas con particiones de equivalencia, valores límite y una tabla de decisión, para tres funciones: `calcular_cobro`, `validar_placa` y `registrar_item`.
- 34 de la versión web (`tests/test_web.py`), con un servidor real en un puerto libre.
- 3 de aceptación (`tests/test_aceptacion.py`), una por cada escenario construido de las historias, con los datos exactos de sus criterios Gherkin.
- 69 de la entrega final con base de datos: reglas de las órdenes (`tests/test_ordenes.py`), páginas por HTTP (`tests/test_web_taller.py`) y 13 pruebas de aceptación más (`tests/test_aceptacion_taller.py`).

Cobertura de líneas y de ramas (semana 8):

```
python -m pytest --cov=app --cov-branch --cov-report=term-missing
```

Las reglas del negocio tienen 100 % de cobertura de líneas y de ramas. El detalle de la cobertura y de la mutación está en la sección 5 de `registro_pruebas.md`.

Las reglas, las tablas de casos, la revisión de las pruebas generadas por la IA, los errores introducidos a propósito y los datos sintéticos están en `registro_pruebas.md`. Sin pytest instalado, `python -m unittest discover -v` corre solo las 20 de las semanas 5 y 6.

En VS Code: menú Terminal, Ejecutar tarea, "Instalar herramientas de desarrollo" la primera vez, y después "Ejecutar pruebas".

Linter y auditoría de dependencias:

```
ruff check --select E,F,B,S .
pip-audit -r requirements-dev.txt
```

GitHub Actions corre todo esto en cada envío (`.github/workflows/calidad.yml`): el linter, pip-audit, las pruebas con cobertura en Python 3.12 y 3.13, el ejemplo y una prueba de humo de la versión web. Además, un trabajo de contenedor pasa hadolint y actionlint, construye la imagen y comprueba `/salud`. La revisión de esta configuración está en [revision_configuracion.md](docs/06_operacion/revision_configuracion.md).

## Estructura

```
app/
  cobros/
    modelos.py              ItemCobro, ResumenCobro, Trabajador y Orden
    calculo.py              calcular_cobro: total sin IVA (HU-07)
    servicio.py             registrar_item: solo el mecánico asignado
    errores.py              AccesoDenegado
    __main__.py             Ejemplo ejecutable
    formato.py              Pesos con punto de miles
  ingresos/
    placas.py               validar_placa: formatos ABC12D y ABC12 (HU-01)
  ordenes/
    modelos.py              Etapas, orden, historial y consulta del cliente
    repositorio.py          PostgreSQL 16 o SQLite, con las mismas consultas
    servicio.py             Ingreso, etapas, cobro, factura y consulta
  web/
    paginas.py              Calculadora de placa y cobro, sin guardar datos
    taller.py               Panel del taller, orden, factura y consulta
    servidor.py             Servidor con http.server, rutas y GET /salud
    __main__.py             python -m app.web
tests/
  test_calculo_cobro.py     Pruebas de la semana 5
  test_tipos_de_datos.py    Pruebas de cantidades y precios enteros
  test_permisos_cobro.py    Pruebas de control de acceso y abuso
  test_reglas_cobro.py      Particiones y límites de calcular_cobro (semana 7)
  test_placas.py            Particiones y límites de validar_placa (semana 7)
  test_tabla_decision_permisos.py  Tabla de decisión de registrar_item (semana 7)
  conftest.py               Fixtures con los datos sintéticos
  test_web.py               Pruebas de la versión web
  datos/datos_sinteticos.json  Datos de prueba sin personas reales
docs/                       Documentos de cada módulo (ver docs/README.md)
.github/workflows/          Revisión automática en GitHub Actions
Dockerfile, .dockerignore   Contenedor de la versión web
desplegar_windows.bat       Despliegue local en Windows con un doble clic
pyproject.toml              Datos del proyecto y configuración de ruff
requirements.txt            psycopg, solo para PostgreSQL
requirements-dev.txt        Herramientas de revisión con versión fijada
.env.example                Plantilla de variables de entorno
revision_seguridad.md       Informe de revisión de código y seguridad
registro_pruebas.md         Reglas, casos, revisión, mutación y cobertura (semanas 7 y 8)
bitacora_ia.md              Bitácora de uso de IA
informe_final.md            Informe final del proyecto integrador
```

## Uso de IA

El código se escribió con Claude como asistente. En las semanas 5 y 6 las pruebas se escribieron antes del código que las hace pasar, y en la semana 7 los casos de `validar_placa` se diseñaron desde la regla antes de implementarla. Ninguna prueba se modificó para que el código pasara. En la semana 6, Claude hizo una segunda revisión del código; cada hallazgo se verificó ejecutando el caso y se clasificó como real o falso positivo. Las correcciones se hicieron en la rama `semana-6-revision-seguridad`, con un commit por hallazgo, y se integraron después de revisar el diff. En la semana 7, la IA propuso casos de prueba y escribió un borrador de pruebas con pytest; cada caso y cada prueba se revisaron contra la regla antes de conservarlos, y el borrador sin revisar quedó en su propio commit para ver la diferencia. En la semana 8 la cobertura del pipeline mostró ramas de seguridad sin probar en la versión web, y se agregaron sus pruebas. En la semana 9 se revisaron el pipeline y el Dockerfile con la lista de la semana, y con hadolint y actionlint. El detalle está en `bitacora_ia.md`, `revision_seguridad.md`, `registro_pruebas.md`, `docs/06_operacion/revision_configuracion.md` y el [informe final](informe_final.md).

## Autor y licencia

Juan Diego Trujillo Rodriguez. Proyecto académico distribuido con licencia MIT (ver `LICENSE`).

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
| Precio con decimales o como texto (desde la semana 6) | El precio debe ser un número entero de pesos |
| Cantidad con decimales, texto, True o False (desde la semana 6) | La cantidad debe ser un número entero |
| Tipo distinto de repuesto o mano de obra | Tipo de ítem no válido: (tipo recibido). Use repuesto o mano de obra |

**Ejemplos.**

| Entrada | Salida |
|---|---|
| Filtro de aceite 1 x 18.000, aceite 1 x 32.000, mano de obra 1 x 35.000 | `ResumenCobro(total_repuestos=50000, total_mano_obra=35000, total=85000)` |
| Aceite 2 x 32.000, mano de obra 1 x 35.000 | `ResumenCobro(total_repuestos=64000, total_mano_obra=35000, total=99000)` |
| Lista vacía | `ResumenCobro(total_repuestos=0, total_mano_obra=0, total=0)` |
| Pastillas de freno 1 x sin precio | `ValueError: Escriba el precio del repuesto` |

### Cómo ejecutar las pruebas

Ver la sección Pruebas al inicio de este archivo.
