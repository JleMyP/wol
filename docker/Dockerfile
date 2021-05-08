FROM python:3.8-alpine3.12

RUN apk add gcc musl-dev libffi-dev openssl-dev make \
  && pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry install

COPY . .

ENV PYTHONUNBUFFERED 1
EXPOSE 5000

CMD ["python", "-m", "wol.wsgi", "-d", "-b", "0.0.0.0"]
