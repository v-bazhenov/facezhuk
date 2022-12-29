from pathlib import Path

from environs import Env
from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings

env = Env()
env.read_env()


class Settings(BaseSettings):
    debug = env.bool('DEBUG')
    fastapi_log_level = env.str('FASTAPI_LOG_LEVEL')

    postgres_uri = env.str('POSTGRES_URI')
    test_postgres_uri = env.str('TEST_POSTGRES_URI')

    mongo_db_name = env.str('MONGO_DB_NAME')
    mongo_db_username = env.str('MONGO_DB_USERNAME')
    mongo_db_password = env.str('MONGO_DB_PASSWORD')
    mongo_db_messages_collection = env.str('MONGO_DB_MESSAGES_COLLECTION')
    mongo_db_chats_collection = env.str('MONGO_DB_CHATS_COLLECTION')
    mongo_db_uri = env.str('MONGO_DB_URI')

    cache_uri = env.str('CACHE_URI')
    broker_url = env.str('BROKER_URL')

    jwt_secret = env.str('JWT_SECRET')
    jwt_algorithm = env.str('JWT_ALGORITHM')
    jwt_expiration_seconds = env.int('JWT_EXPIRATION_SECONDS')
    jwt_refresh_expiration_seconds = env.int('JWT_REFRESH_EXPIRATION_SECONDS')

    google_client_secret = env.str('GOOGLE_CLIENT_SECRET')
    google_client_id = env.str('GOOGLE_CLIENT_ID')
    google_redirect_uri = env.str('GOOGLE_REDIRECT_URI')

    facebook_client_secret = env.str('FACEBOOK_CLIENT_SECRET')
    facebook_client_id = env.str('FACEBOOK_CLIENT_ID')
    facebook_redirect_uri = env.str('FACEBOOK_REDIRECT_URI')

    activation_token_duration = env.int('ACTIVATION_TOKEN_DURATION')
    reset_password_token_duration = env.int('RESET_PASSWORD_TOKEN_DURATION')


email_conf = ConnectionConfig(
    MAIL_USERNAME=env.str('MAIL_USERNAME'),
    MAIL_PASSWORD=env.str('MAIL_PASSWORD'),
    MAIL_FROM=env.str('MAIL_FROM'),
    MAIL_PORT=env.int('MAIL_PORT'),
    MAIL_SERVER=env.str('MAIL_SERVER'),
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

cfg = Settings()
