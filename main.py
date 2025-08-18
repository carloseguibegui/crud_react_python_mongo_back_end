from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from bson import ObjectId
from passlib.context import CryptContext
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from bcrypt import checkpw

# Cargar variables de entorno
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL, server_api=ServerApi("1"))
load_dotenv()

# Configuración de la base de datos MongoDB
# MONGO_URL = "mongodb://localhost:27017"
db = client.get_database('python-react-app')
print('------------------------')
print('database connected',db)
print('------------------------')

# Inicializar la aplicación
app = FastAPI()


app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InventoryItem(BaseModel):
    name: str
    quantity: int
    description: str
    user_id: str
    id: str | None = None

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para cifrar contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar contraseñas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoint de autenticación (MongoDB)
@app.post("/api/v1/auth/login")
def login(username: str = Form(...), password: str = Form(...)) -> Dict[str, str]:
    print("Entrando en la función de login")
    print(f"Username: {username}")
    print(f"Password: {password}")
    # user = db.users.find_one({"username": username})
    try:
        user = db.get_collection('users').find_one({"username": username})
        if user is None:
            print("Usuario no encontrado")
            raise HTTPException(status_code=400, detail="Usuario no encontrado")

        print("verificando contraseña")
        if not verify_password(password, user["password"]):
            print("contraseña inválida")
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
        if not (password == user["password"]):
            raise HTTPException(status_code=400, detail={"error": "Contraseña incorrecta"})
        # if not checkpw(password, user["password"]):
        #     print("Contraseña incorrecta")
        
        # Generar JWT
        expiration = datetime.now(timezone.utc) + timedelta(hours=1)
        token = jwt.encode({"sub": str(user["_id"]), "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
        print("autenticación exitosa, token generado")
        return {"message": "Inicio de sesión exitoso", "token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Endpoint para subir archivos
@app.post("/api/v1/upload")
def upload_file(file: UploadFile) -> Dict[str, str]:
    try:
        # content = file.file.read()
        filename = file.filename or "archivo_desconocido"
        # Aquí puedes procesar el archivo (por ejemplo, guardar en la base de datos o analizar datos)
        return {"filename": filename, "message": "Archivo subido exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {e}")

# Endpoint para registrar usuarios (MongoDB)
@app.post("/api/v1/auth/register")
def register(username: str = Form(...), password: str = Form(...)):
    existing_user = db.users.find_one({"username": username})
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso. Elige otro.")

    hashed_password = hash_password(password)  # Cifrar la contraseña
    new_user = {"username": username, "password": hashed_password}
    db.users.insert_one(new_user)
    return {"message": "Usuario registrado exitosamente"}

# Endpoint para obtener todos los usuarios (ejemplo)
@app.get("/api/v1/users")
def get_users() -> Dict[str, Any]:
    users = db.users.find().to_list(length=100)
    for user in users:
        user["_id"] = str(user["_id"])
    return {"users": users}

@app.get("/api/v1/db-status")
def db_status() -> Dict[str, Any]:
    try:
        collections =  db.list_collection_names()
        return {"status": "connected", "collections": collections}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Endpoints de inventario
@app.get("/api/v1/inventory", response_model=List[InventoryItem])
def get_inventory(current_user: str = Depends(get_current_user)):
    items = db.inventory.find({"user_id": current_user}).to_list(100)
    for item in items:
        item["id"] = str(item["_id"])
    return items

@app.post("/api/v1/inventory", response_model=InventoryItem)
def create_inventory_item(item: InventoryItem):
    result = db.inventory.insert_one(item.model_dump())
    item.id = str(result.inserted_id)
    return item

@app.put("/api/v1/inventory/{item_id}", response_model=InventoryItem)
def update_inventory_item(item: InventoryItem):
    result = db.inventory.update_one({"_id": ObjectId(item.id)}, {"$set": item.model_dump()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/api/v1/inventory/{item_id}")
def delete_inventory_item(item_id: str):
    result = db.inventory.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


@app.get("/docs")
async def get_docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Mi API",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.24.2/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.24.2/swagger-ui.css",
    )