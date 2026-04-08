import os
from pymongo import MongoClient

def mongo_db():
    url = os.environ.get("MONGO_URL", "mongodb://mongo:27017")
    db_name = os.environ.get("MONGO_DB", "studytracker")
    client = MongoClient(url)
    return client[db_name]
