FROM python:3.12-alpine AS base

WORKDIR /app

# Install system dependencies including DNS utilities
RUN apk add --no-cache gcc musl-dev curl bind-tools

# Install poetry
RUN pip install --upgrade pip && pip install poetry

# Configure poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8000
COPY scripts/script.sh ./scripts/script.sh

CMD ["/bin/sh", "scripts/script.sh"]
