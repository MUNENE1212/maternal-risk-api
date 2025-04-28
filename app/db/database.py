# app/db/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGO_URI = config("MONGO_URI")
MONGO_DB = config("MONGO_DB")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
users_collection = db.get_collection("users")
patients_collection = db.get_collection("patients")
predictions_collection = db.get_collection("predictions")

