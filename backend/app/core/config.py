# app/core/config.py

from decouple import config

class Settings:
    MONGO_URI: str = config("MONGO_URI")
    MONGO_DB: str = config("MONGO_DB")

settings = Settings()

