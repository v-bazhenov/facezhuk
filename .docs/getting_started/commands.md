# Commands

## Application commands

Run uvicorn dev server

```shell
python main.py
```

Run all tests

```shell
pytest
```

Run locust tests

```shell
locust -f ./tests/locustfiles/chats.py
```

## Alembic commands

Run create migrations command

```shell
alembic revision --autogenerate 
```

Run apply migration command

```shell
alembic upgrade head
```

Run downgrade migration command

```shell
alembic downgrade <migration name>
```

Run migration history

```shell
alembic history
```

## Celery commands

Run celery

```shell
celery -A chat.tasks worker -l INFO
```

Run celery beat

```shell
celery -A chat.tasks beat -l INFO
```

