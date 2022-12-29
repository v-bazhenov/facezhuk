from celery.schedules import crontab

from config import cfg

CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "127.0.0.1",
    "port": 27017,
    "database": cfg.mongo_db_name,
    "username": cfg.mongo_db_username,
    "password": cfg.mongo_db_password,
    "taskmeta_collection": "stock_taskmeta_collection",
}

# used to schedule tasks periodically and passing optional arguments
# Can be very useful. Celery does not seem to support scheduled task but only periodic
CELERYBEAT_SCHEDULE = {
    'save-message-into-postgresql': {
        'task': 'chat.tasks.save_message_into_postgresql',
        'schedule': crontab(minute='*/1'),
    },
}
