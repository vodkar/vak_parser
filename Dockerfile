# syntax=docker/dockerfile:1
FROM python:3.11-alpine

RUN apk add --no-cache gcc g++ ghostscript libressl-dev musl-dev libffi-dev
ENV LD_LIBRARY_PATH=/usr/lib/jvm/java-11-openjdk/jre/lib/server/

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install poetry requirements   
ENV POETRY_VERSION==1.6.1
RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN --mount=type=cache,target=/root/.cache/ poetry install --only main --no-interaction --no-ansi --no-root

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "vak_journals/main.py"]
