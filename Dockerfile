FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./ /app

WORKDIR /app

RUN pip install pipenv
RUN pipenv install
