from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
from bson import ObjectId
import asyncio

fake = Faker()

async def populate_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_database

    # Insertar usuarios de prueba
    # users = [{"username": fake.user_name(), "password": fake.password()} for _ in range(10)]
    # await db.user.insert_many(documents=users)

    # Obtener usuarios existentes
    users = await db.user.find().to_list(length=10)

    # Insertar inventario de prueba enlazado a usuarios
    inventory = [
        {
            "name": fake.word(),
            "quantity": fake.random_int(min=1, max=100),
            "description": fake.sentence(),
            "user_id": str(fake.random_element(users)["_id"])
        }
        for _ in range(20)
    ]
    await db.inventory.insert_many(documents=inventory)

    print("Datos de prueba insertados")

asyncio.run(populate_db())