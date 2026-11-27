@echo off
rem Despliegue local del Taller Dos Ruedas en Windows (guia de despliegue, opcion A).
rem Doble clic en este archivo: prepara el entorno, corre las pruebas y, solo si
rem pasan, arranca la version web y abre el navegador. Ctrl+C la detiene.
chcp 65001 >nul
cd /d "%~dp0"
echo === Taller Dos Ruedas: despliegue local ===
py --version
if errorlevel 1 (
  echo No se encontro Python. Instale Python 3.12 o 3.13 desde python.org.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -m venv .venv
call .venv\Scripts\activate.bat
echo --- Instalando las herramientas de prueba con version fijada ---
python -m pip install --disable-pip-version-check -q -r requirements-dev.txt
if errorlevel 1 (
  echo No se pudieron instalar las herramientas. Revise la conexion a internet.
  pause
  exit /b 1
)
echo --- Pruebas antes de desplegar ---
python -m pytest -q
if errorlevel 1 (
  echo Las pruebas fallaron: no se despliega esta version.
  pause
  exit /b 1
)
echo --- Arrancando en http://127.0.0.1:8000 ---
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000"
python -m app.web
pause
