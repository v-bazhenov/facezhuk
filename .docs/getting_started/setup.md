# Setup Project

## Clone the project

At first, you need to clone the project and go to the project folder

```shell
git clone https://github.com/v-bazhenov/facezhuk

cd facezhuk/
```

Create a file `.env` in the root directory and fill it with required env variables. See [configuration](./configuration.md) section.

## Install packages

We're using [Pipenv](https://pipenv.pypa.io/) package manager

You need to install it in your virtual environment.

To create a new one please run:

```shell
python -m venv venv
source venv/bin/activate
```

Then you can install poetry

```shell
pip install pipenv
```

After that you can install all required packages

```shell
pipenv install
pipenv install --dev
```

## Docker

We're using docker as a container engine, to run postgres, redis, mongodb, and so on, without installing it on local machine.

to run docker for dev purposes you need to run:

```shell
docker-compose -f docker-compose-dev.yml up -d
```

## First steps

After you set up docker and project, next step will be to migrate all migrations.

As a migration engine we're using `alembic`. It is base sqlalchemy-orm migration engine
to migrate all migrations run:
```shell 
alembic upgrade head
```

And last but not least you should run your local server:

```shell 
python main.py
```
