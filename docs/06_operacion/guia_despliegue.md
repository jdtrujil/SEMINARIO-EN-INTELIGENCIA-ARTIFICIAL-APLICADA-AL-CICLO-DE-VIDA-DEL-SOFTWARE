# Guía de despliegue

Módulo 6, Operación. Proyecto Taller Dos Ruedas. Estudiante: Juan Diego Trujillo Rodriguez.

La versión que se despliega es la web local (ADR-003). Muestra dos formularios: uno valida la placa de la moto (HU-01) y otro calcula el cobro de repuestos y mano de obra sin IVA (HU-07). Usa solo la biblioteca estándar de Python, así que no hace falta instalar paquetes para ejecutarla.

## 1. Requisitos

| Qué | Versión | Para qué |
|---|---|---|
| Python | 3.12 o 3.13 (las dos se prueban en el pipeline) | Ejecutar el sistema |
| Git | Cualquiera reciente | Descargar y actualizar el código. También sirve el ZIP de GitHub |
| Docker | Opcional | Solo para la opción B |

## 2. Opción A: en el equipo del taller, con Python (Windows)

1. Descargar el código en una carpeta, por ejemplo `C:\TallerDosRuedas`:
   ```
   git clone https://github.com/jdtrujil/SEMINARIO-EN-INTELIGENCIA-ARTIFICIAL-APLICADA-AL-CICLO-DE-VIDA-DEL-SOFTWARE.git C:\TallerDosRuedas
   cd C:\TallerDosRuedas
   ```
2. Opcional, pero recomendado antes del primer uso: comprobar el código con las pruebas.
   ```
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements-dev.txt
   python -m pytest -q
   ```
   Deben pasar todas las pruebas.
3. Arrancar el servidor:
   ```
   py -m app.web
   ```
   La consola muestra `Taller Dos Ruedas en http://127.0.0.1:8000`.
4. Abrir http://127.0.0.1:8000 en el navegador del mismo equipo.
5. Para detenerlo: Ctrl+C en la consola.

Si el puerto 8000 está ocupado, se usa otro:

```
set TALLER_PUERTO=8001
py -m app.web
```

El servidor escucha solo en 127.0.0.1, así que nadie más en la red puede entrar. Abrirlo a la red del taller (`TALLER_HOST`) no se recomienda hasta que exista el inicio de sesión de los trabajadores.

### Atajo: un doble clic

`desplegar_windows.bat`, en la raíz del repositorio, hace los pasos 2 a 4 en orden:

1. Crea el entorno virtual.
2. Instala las herramientas con versión fijada.
3. Corre las pruebas y **no despliega si alguna falla**.
4. Arranca el servidor y abre el navegador.

Se usa con doble clic sobre el archivo, dentro de la carpeta del proyecto.

## 3. Opción B: en un contenedor Docker

```
docker build -t taller-dos-ruedas .
docker run --rm -p 127.0.0.1:8000:8000 taller-dos-ruedas
```

La imagen:

- Usa `python:3.13-slim`.
- Corre con un usuario sin privilegios (uid 10001).
- No lleva pruebas, documentos, `.git` ni `.env` (`.dockerignore`).
- Tiene un `HEALTHCHECK` que consulta `/salud`.

El pipeline construye y prueba la imagen en cada envío (trabajo `contenedor`).

## 4. Verificación después de desplegar

| Paso | Resultado esperado |
|---|---|
| Abrir http://127.0.0.1:8000/salud | `ok` |
| Abrir http://127.0.0.1:8000 | Página "Taller Dos Ruedas" con los formularios de placa y cobro |
| Escribir la placa `abc12d` y validar | "Placa válida: ABC12D" |
| Cobro con filtro 18.000, aceite 32.000 y mano de obra 35.000 | Repuestos $ 50.000, mano de obra $ 35.000, total sin IVA $ 85.000 |
| Cobro con un precio de -1 | "Fila 1: El precio no puede ser negativo" |

## 5. Actualizar y volver atrás

- **Actualizar:** detener el servidor, ejecutar `git pull`, correr las pruebas y arrancar de nuevo.
- **Volver a la versión anterior** si algo falla:
  ```
  git log --oneline
  git checkout <commit anterior>
  py -m app.web
  ```
  Como la versión local no guarda datos, volver atrás no pierde información.

## 6. Despliegue realizado

El registro del despliegue en el PC del estudiante, con fecha, versión, resultado de las pruebas y capturas, está en [despliegue_realizado.md](despliegue_realizado.md).
