# Configure

The settings are inside `config.py`
file.

Also, we use environment variables for convenience and additional security layer. Here is the list of them :arrow_down:

??? note "List of .env variables to copy-paste"

    ```shell
        DEBUG=True
        FASTAPI_LOG_LEVEL=info
        
        POSTGRES_URI=facezhuk:facezhuk@localhost:5432/facezhuk
        TEST_POSTGRES_URI=facezhuk:facezhuk@localhost:5432/facezhuk_test
        
        MONGO_DB_NAME=facezhuk
        MONGO_DB_USERNAME=facezhuk
        MONGO_DB_PASSWORD=facezhuk
        MONGO_DB_MESSAGES_COLLECTION=messages
        MONGO_DB_CHATS_COLLECTION=chats
        MONGO_DB_URI=mongodb://localhost:27017
        
        CACHE_URI=redis://127.0.0.1:6379
        
        JWT_SECRET=secret
        JWT_ALGORITHM=HS256
        JWT_EXPIRATION_SECONDS=90000
        JWT_REFRESH_EXPIRATION_SECONDS=1209600
        
        GOOGLE_CLIENT_SECRET=test
        GOOGLE_CLIENT_ID=test
        GOOGLE_REDIRECT_URI=test
        
        FACEBOOK_CLIENT_ID=test
        FACEBOOK_CLIENT_SECRET=test
        FACEBOOK_REDIRECT_URI=test
        
        ACTIVATION_TOKEN_DURATION=600
        RESET_PASSWORD_TOKEN_DURATION=100
    ```

## Application

Variable | Default | Description
:---------|:--|:------------
`JWT_EXPIRATION_SECONDS` | 90000 | JWT Access token lifetime
`JWT_REFRESH_EXPIRATION_SECONDS` | 1209600 | JWT Refresh token lifetime
`ACTIVATION_TOKEN_DURATION` | 600 | Activation token lifetime
`RESET_PASSWORD_TOKEN_DURATION` | 100 | Reset Password token lifetime
`DEBUG` | True | Development mode switcher

## PostgreSQL

Variable | Default | Description
:---------|:---------|:------------
`POSTGRES_URI` | facezhuk:facezhuk@localhost:5432/facezhuk | PostgreSQL URI

## MongoDB

Variable | Default | Description
:---------|:---------|:------------
`MONGO_DB_NAME` | facezhuk | MongoDB Name
`MONGO_DB_USERNAME` | facezhuk | MongoDB Username
`MONGO_DB_PASSWORD` | facezhuk | MongoDB Password
`MONGO_DB_MESSAGES_COLLECTION` | messages | MongoDB Messages Collection
`MONGO_DB_CHATS_COLLECTION` | chats | MongoDB Chats Collection
`MONGO_DB_URI` | mongodb://localhost:27017 | MongoDB URI

## Celery

Variable | Default | Description
:---------|:---------|:------------
`BROKER_URL` | mongodb://facezhuk:facezhuk@localhost:27017/?authMechanism=DEFAULT | Background processing broker URL

## Mail Provider

Variable | Default | Description
:---------|:---------|:------------
`MAIL_USERNAME` |  | Mail provider username
`MAIL_PASSWORD` |  | Mail provider password
`MAIL_FROM` |  | Mail provider from email
`MAIL_PORT` |  | Mail provider provider
`MAIL_SERVER` |  | Mail provider server

## Google

Variable | Default | Description
:---------|:---------|:------------
`GOOGLE_CLIENT_SECRET` | test | Google Client Secret
`GOOGLE_CLIENT_ID` | test | Google Client ID
`GOOGLE_REDIRECT_URI` | test | Google Redirect URI

## Facebook

Variable | Default | Description
:---------|:---------|:------------
`FACEBOOK_CLIENT_ID` | test | Facebook Client ID
`FACEBOOK_CLIENT_SECRET` | test | Facebook Client Secret
`FACEBOOK_REDIRECT_URI` | test | Facebook Redirect URI

#### You need to provide real values for Google and Facebook from your Development Application or Console.