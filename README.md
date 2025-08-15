## Descripción del proyecto
Este proyecto es una API de autenticación y registro de usuarios utilizando FastAPI y MongoDB.

## Características
- Autenticación de usuarios mediante username y password
- Registro de usuarios con validación de datos
- Utiliza MongoDB como base de datos
- Implementa CORS para permitir solicitudes desde diferentes orígenes

## Instalación
- Clona el repositorio: git clone https://github.com/tu-usuario/tu-repositorio.git
- Instala las dependencias: pipenv install
- Inicia el servidor: uvicorn main:app --host 0.0.0.0 --port 8000

## Uso
- Para registrar un usuario, envía una solicitud POST a /api/v1/auth/register con los siguientes datos:
    - username: nombre de usuario
    - password: contraseña
- Para autenticar un usuario, envía una solicitud POST a /api/v1/auth/login con los siguientes datos:
    - username: nombre de usuario
    - password: contraseña

## Documentación
La documentación de la API se encuentra en /docs