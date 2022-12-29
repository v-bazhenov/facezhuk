from databases import Database
from motor import motor_asyncio
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import cfg

# SQLAlchemy Metadata instance
Base = declarative_base()

# Database instance
db = Database(f"postgresql://{cfg.postgres_uri}",
              min_size=1,
              max_size=5)

engine = create_engine(f"postgresql://{cfg.postgres_uri}")
Session = sessionmaker(bind=engine)
session = Session()

mongo_client_async = motor_asyncio.AsyncIOMotorClient(cfg.mongo_db_uri,
                                                      username=cfg.mongo_db_username,
                                                      password=cfg.mongo_db_password)

mongo_client = MongoClient(cfg.mongo_db_uri,
                           username=cfg.mongo_db_username,
                           password=cfg.mongo_db_password)

mongo_db = mongo_client[cfg.mongo_db_name]
mongo_db_async = mongo_client_async[cfg.mongo_db_name]

mongo_db_messages_collection = mongo_db.get_collection(cfg.mongo_db_messages_collection)
mongo_db_chats_collection = mongo_db.get_collection(cfg.mongo_db_chats_collection)

async_mongo_db_messages_collection = mongo_db_async.get_collection(cfg.mongo_db_messages_collection)
async_mongo_db_chats_collection = mongo_db_async.get_collection(cfg.mongo_db_chats_collection)
