###################################
############### DOCKER ############
###################################
DOCKER_RUN=docker run --rm -it -v ${PWD}:/usr/src bibtexparser-dev

.PHONY: docker-build
docker-build: Dockerfile
	docker build -t bibtexparser-dev .

.PHONY: docker-check
docker-check: docker-build
	${DOCKER_RUN} make check

.PHONY: docker-shell
docker-shell: docker-build
	${DOCKER_RUN} /bin/bash

###################################
############# Development #########
###################################
.PHONY: check
check: poetry-dev-install format import-clean sort lint type

.PHONY: poetry-install
# Create poetry environment
poetry-install: pyproject.toml
	poetry install --without dev

.PHONY: poetry-dev-install
# Create poetry environment for development
poetry-dev-install: pyproject.toml
	poetry install


.PHONY: sort
# Sort imports
sort: poetry-dev-install
	poetry run isort bibtexparser

.PHONY: import-clean
import-clean: poetry-dev-install
	poetry run pycln bibtexparser

.PHONY: format
# Format all python files
format: poetry-dev-install
	poetry run black bibtexparser

.PHONY: lint
# Lint project
lint: poetry-dev-install
	poetry run flake8 bibtexparser

.PHONY: type
# Type check project
type: poetry-dev-install
	poetry run mypy bibtexparser

