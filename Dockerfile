# Versión web del Taller Dos Ruedas en un contenedor.
# Construir: docker build -t taller-dos-ruedas .
# Ejecutar:  docker run --rm -p 127.0.0.1:8000:8000 taller-dos-ruedas
# Revisado con la lista de la semana 9: docs/06_operacion/revision_configuracion.md

# Imagen oficial liviana con versión fijada, no latest.
FROM python:3.13-slim

# Sin archivos .pyc y con el registro en la salida al instante.
# Dentro del contenedor el servidor escucha en todas sus interfaces para que el
# puerto publicado llegue; quién puede entrar lo decide -p 127.0.0.1:8000:8000.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TALLER_HOST=0.0.0.0 \
    TALLER_PUERTO=8000 \
    TALLER_BD_ARCHIVO=/home/taller/taller.db

WORKDIR /app

# Solo el código de la aplicación: sin pruebas, documentos, .git ni .env.
# Sin DATABASE_URL usa SQLite de la biblioteca estándar, así que no hay pip install.
COPY app ./app

# Usuario sin privilegios.
RUN useradd --create-home --uid 10001 taller
USER taller

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD ["python", "-c", "import sys, urllib.request; sys.exit(urllib.request.urlopen('http://127.0.0.1:8000/salud', timeout=2).read() != b'ok')"]

# Modo normal, sin recarga automática de desarrollo.
CMD ["python", "-m", "app.web"]
