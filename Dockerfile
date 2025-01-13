FROM python:3.11.10

RUN pip  install poetry --no-root

WORKDIR /backend/

COPY poetry.lock pyproject.toml /backend/

RUN poetry config virtualenvs.create false && poetry install

COPY ./src/ /backend/src/
COPY ./tests/ /backend/tests/
COPY ./migrations /backend/migrations/
COPY ./alembic.ini /backend/alembic.ini
COPY .env /backend/
COPY README.md /backend/