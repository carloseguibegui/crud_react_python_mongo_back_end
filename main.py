from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from pymongo.database import Database
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from bson import ObjectId
from passlib.context import CryptContext
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL, server_api=ServerApi("1"))

# run app
# uvicorn main:app --host 0.0.0.0 --port 8000


# Cargar variables de entorno
load_dotenv()
# Configuración de la base de datos MongoDB
# MONGO_URL = "mongodb://localhost:27017"
db  = client.crudReactPythonMongo
print('------------------------')
print('database connected',db)
print('------------------------')

# Inicializar la aplicación
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos
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

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
async def login(username: str = Form(...), password: str = Form(...)) -> Dict[str, str]:
    user = await db.users.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):  # Verificar contraseña
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    # Generar JWT
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode({"sub": str(user["_id"]), "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

    return {"message": "Inicio de sesión exitoso", "token": token}

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
async def register(username: str = Form(...), password: str = Form(...)):
    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = hash_password(password)  # Cifrar la contraseña
    new_user = {"username": username, "password": hashed_password}
    await db.users.insert_one(new_user)
    return {"message": "Usuario registrado exitosamente"}

# Endpoint para obtener todos los usuarios (ejemplo)
@app.get("/api/v1/users")
async def get_users() -> Dict[str, Any]:
    users = await db.users.find().to_list(length=100)  # Limitar a 100 usuarios
    for user in users:
        user["_id"] = str(user["_id"])
    return {"users": users}

@app.get("/api/v1/db-status")
async def db_status() -> Dict[str, Any]:
    try:
        collections = await db.list_collection_names()
        return {"status": "connected", "collections": collections}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Endpoints de inventario
@app.get("/api/v1/inventory", response_model=List[InventoryItem])
async def get_inventory(current_user: str = Depends(get_current_user)):
    items = await db.inventory.find({"user_id": current_user}).to_list(100)
    for item in items:
        item["id"] = str(item["_id"])
    return items

@app.post("/api/v1/inventory", response_model=InventoryItem)
async def create_inventory_item(item: InventoryItem):
    result = await db.inventory.insert_one(item.model_dump())
    item.id = str(result.inserted_id)
    return item

@app.put("/api/v1/inventory/{item_id}", response_model=InventoryItem)
async def update_inventory_item(item: InventoryItem):
    result = await db.inventory.update_one({"_id": ObjectId(item.id)}, {"$set": item.model_dump()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/api/v1/inventory/{item_id}")
async def delete_inventory_item(item_id: str):
    result = await db.inventory.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}