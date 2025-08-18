## URL API
[link back-end](https://crud-react-python-mongo-back-end.onrender.com)
[link front-end](https://crud-react-python-mongo-front-end.onrender.com)

## Descripción del proyecto
Este proyecto es una API de autenticación y registro de usuarios utilizando FastAPI y MongoDB.

## Características
- Autenticación de usuarios mediante username y password
- Registro de usuarios con validación de datos
- Utiliza MongoDB como base de datos
- Implementa CORS para permitir solicitudes desde diferentes orígenes

## Uso
- Para registrar un usuario, envía una solicitud POST a /api/v1/auth/register con los siguientes datos:
    - username: nombre de usuario
    - password: contraseña
- Para autenticar un usuario, envía una solicitud POST a /api/v1/auth/login con los siguientes datos:
    - username: nombre de usuario
    - password: contraseña

## Documentación
La documentación de la API se encuentra en /docs