# Imagen base con la última versión (slim) de Python
# Nota: "python:slim" rastrea la última estable; para fijar usa "python:3.13-slim".
FROM python:slim

# Evitar prompts interactivos y configurar entorno predecible
ENV DEBIAN_FRONTEND=noninteractive \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	MPLBACKEND=Agg \
	TZ=Etc/UTC \
	LANG=C.UTF-8 \
	LC_ALL=C.UTF-8

WORKDIR /app

# Paquetes del sistema mínimos (fuentes para matplotlib)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends fonts-dejavu tzdata \
	&& rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python primero para aprovechar la capa de caché
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Asegura que existan directorios de salida y sean escribibles
RUN mkdir -p Extract/Files Docs \
	&& useradd --create-home --shell /bin/bash appuser \
	&& chown -R appuser:appuser /app

# Declara volúmenes para persistir artefactos (CSV/DB y gráficas)
VOLUME ["/app/Extract/Files", "/app/Docs"]

# Ejecutar como usuario no root
USER appuser

# Comando por defecto: ejecutar el pipeline
CMD ["python", "main.py"]

