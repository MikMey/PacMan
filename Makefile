NAME := src/pacman/pac-man.py
SOURCE := ./src/pacman/
PYTHON ?= python3
FLAKE8 := uv run -m flake8
FLAKE8_FLAGS := --count --show-source --filename [./*.py]
MYPY := uv run mypy
MYPY_FLAGS := --warn-return-any \
			  --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
			  --check-untyped-defs
UV_VENV := uv sync
CONFIG ?= data/config.json

all: install run

install:
	$(UV_VENV)

run:
	uv run $(PYTHON) -m $(NAME) $(CONFIG)

lint:
	$(FLAKE8) $(FLAKE8_FLAGS) $(SOURCE)*.py
	$(MYPY) $(SOURCE)*.py $(MYPY_FLAGS)

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: all install run lint clean