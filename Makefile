# Variables
PYTHON := python3
PIP := pip3
PIP_COMPILE := pip-compile

# Default target
.DEFAULT_GOAL := help

# Help target
help:
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install    Install the project dependencies"
	@echo "  test       Run tests"
	@echo "  clean      Clean up the project"
	@echo "  tox        Run tox environments"
	@echo "  compile    Compile requirements from requirements-dev.in"

# Install target
install:
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade setuptools
	$(PIP) install --upgrade wheel
	$(PIP) install --upgrade pip-tools
	$(PIP_COMPILE) requirements-dev.in
	$(PIP) install --upgrade -r requirements-dev.txt
	pre-commit install --overwrite

# Test target
test:
	$(PYTHON) -m pytest -v

# Clean target
clean:
	pre-commit clean
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .tox
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .aider*
	rm -rf requirements.txt
	rm -rf requirement-dev.txt

# Compile target
compile:
	$(PIP_COMPILE) requirements-dev.in
	@echo "  tox        Run tox environments using tox.ini"

tox:
	tox -c tox.ini
