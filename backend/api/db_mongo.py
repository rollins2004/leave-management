import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def get_client():
    global _client
    if _client is None:
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MONGODB_URI not set in .env file")
        _client = MongoClient(uri)
        _client.admin.command('ping')
    return _client


def get_db():
    global _db
    if _db is None:
        client = get_client()
        db_name = os.getenv('DB_NAME', 'leave_management')
        _db = client[db_name]
    return _db


def get_collection(name):
    return get_db()[name]

def users_col():
    return get_collection('users')

def leaves_col():
    return get_collection('leaves')