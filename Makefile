NAME := src.pac_man
SOURCE := ./src/pac_man/
PYTHON ?= python3 -m
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
    uv run $(PYTHON) $(NAME) $(CONFIG)

lint:
    $(FLAKE8) $(FLAKE8_FLAGS) $(SOURCE)*.py
    $(MYPY) $(SOURCE)*.py $(MYPY_FLAGS)

clean:
    rm -rf .mypy_cache .pytest_cache
    find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: all install run lint clean