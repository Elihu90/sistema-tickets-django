# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . /app/

# Crear usuario sin privilegios
RUN adduser --disabled-password appuser || true
USER appuser

# Copiar entrypoint
COPY entrypoint.sh /entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Ejecutar entrypoint con sh directamente (evita chmod en Windows)
CMD ["sh", "/entrypoint.sh", "gunicorn", "sgtr.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
