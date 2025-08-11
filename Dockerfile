# # Usar una imagen base de Python
# FROM python:3.10-slim

# # Establecer el directorio de trabajo
# WORKDIR /app

# # Copiar los archivos de tu proyecto
# COPY . .

# # Instalar las dependencias
# RUN pip install pipenv && pipenv install --system --deploy

# # Exponer el puerto de la aplicación
# EXPOSE 8000

# # Comando para iniciar la aplicación
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]