FROM python:3.10.0rc1-alpine3.13

ENV PYTHONUNBUFFERED 1

RUN apk add gcc musl-dev libffi-dev openssl-dev make postgresql-dev \
  && CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install -E all

COPY wol wol

EXPOSE 5000

CMD ["python", "-m", "wol.wsgi", "-d", "-b", "0.0.0.0"]
