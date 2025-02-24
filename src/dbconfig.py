# Variables de Configuracion
import os
from pymongo import MongoClient
from datetime import datetime

# Configuración de MongoDB
MONGO_URI = f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongo:27017/"
DATABASE_NAME = os.getenv("DATABASE_NAME", "9now")

# Conectar a MongoDB
def get_mongo_db():
    """Establece la conexión con MongoDB y devuelve la base de datos"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        print(f"✅ Conectado a MongoDB en la base de datos '{DATABASE_NAME}'")
        return db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None

def guardar_channels(documento):
    """Guarda un nuevo documento en la colección 'channels', incluyendo un timestamp."""
    db = get_mongo_db()
    if db is not None:
        try:
            # Agregar timestamp al documento para diferenciar ejecuciones
            documento["timestamp"] = datetime.now()

            # Insertar el documento en la colección "channels"
            collection = db["channels"]
            result = collection.insert_one(documento)

            print(f"✅ Documento insertado con ID: {result.inserted_id}")
        except Exception as e:
            print(f"❌ Error al guardar en MongoDB: {e}")

def guardar_tv_guide(tv_guide_data):
    """Guarda un nuevo documento en la colección 'channels', incluyendo un timestamp."""
    db = get_mongo_db()
    if db is not None and isinstance(tv_guide_data, list):
        try:
            document = {
                "timestamp": datetime.now(),
                "data": tv_guide_data  # Guardar la lista dentro de un solo documento
            }

            # Insertar el documento en la colección "tv_guide"
            collection = db["tv_guide"]
            result = collection.insert_one(document)
            
            print(f"✅ Documento insertado con ID: {result.inserted_id}")
        except Exception as e:
            print(f"❌ Error al guardar en MongoDB: {e}")
