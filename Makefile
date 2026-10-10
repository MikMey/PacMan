NAME := src.pac_man
SOURCE := src/pac_man
PYTHON ?= python3 -m
FLAKE8 := uv run -m flake8
FLAKE8_FLAGS := --count --show-source
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
	uv run $(PYTHON) $(NAME) $(CONFIG)

source:
	find $(SOURCE) -type f -name '*.py' -print0 | xargs -0

lint:
	$(FLAKE8) $(FLAKE8_FLAGS) $(SOURCE)
	$(MYPY) $(SOURCE) $(MYPY_FLAGS)

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +

.PHONY: all install run source lint clean