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
	@echo "Cleaning up repo.............................................................🧹"
	@make push-prep
	@pre-commit clean
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@rm -rf .aider*
	@rm -rf .coverage
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf .tox
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist
	@rm -rf htmlcov
	@rm -rf node_modules
	@echo "Repo cleaned up..............................................................✅"

# Pre-push cleanup target
push-prep:
	@echo "Removing temporary files.....................................................🧹"
	@find . -type f -name '*.pyc' -delete
	@if [ -f requirements.txt ]; then \
		echo "Resetting requirements.txt to empty state....................................✅"; \
		rm -rf requirements.txt; \
		touch requirements.txt; \
	fi
	@if [ -f requirements-dev.txt ]; then \
		echo "Resetting requirements-dev.txt to empty state................................✅"; \
		rm -rf requirements-dev.txt; \
		touch requirements-dev.txt; \
	fi
	@echo "Removed temporary files......................................................✅"

# Compile target
compile:
	$(PIP_COMPILE) requirements-dev.in
	@echo "  tox        Run tox environments using tox.ini"

tox:
	tox -c tox.ini
