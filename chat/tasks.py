from celery import Celery

from chat.models import chat_message
from common.utils import prepare_object_for_postgresql
from config import cfg
from database.core import mongo_db_messages_collection, engine

BROKER_URL = cfg.broker_url

celery = Celery('EOD_TASKS', broker=BROKER_URL)

# Loads settings for Backend to store results of jobs
celery.config_from_object('celeryconfig')


@celery.task
def save_message_into_postgresql():
    collection = mongo_db_messages_collection
    messages = collection.find({'isBackupCreated': False})
    for message in messages:
        inserted = chat_message.insert().values(**prepare_object_for_postgresql(message))
        engine.execute(inserted)
    collection.update_many(
        {"isBackupCreated": False},
        {'$set': {'isBackupCreated': True}}
    )
