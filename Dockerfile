FROM python:3.10

RUN pip install poetry

WORKDIR /usr/src
COPY --chown=user:user pyproject.toml pyproject.toml
RUN poetry install

