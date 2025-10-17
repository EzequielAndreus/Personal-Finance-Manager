# Imagen base: Ubuntu con Python
FROM python:3.13-slim

# Evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar e instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar las dependencias
RUN pip3 install --no-cache-dir -r requirements.txt

# Exponer el puerto de Flask
EXPOSE 5001

# Comando para ejecutar la aplicación
CMD ["python3", "src/app.py"]
