# Variables
PYTHON := python3

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

# Install target
install:
	pip install -r requirements.txt
	pre-commit install --overwrite

# Test target
test:
	pytest -v

# Clean target
clean:
	@echo "Cleaning up repo.............................................................🧹"
	@pre-commit clean
	@make push-prep
	@echo "Repo cleaned up..............................................................✅"

# Pre-push cleanup target
push-prep:
	@echo "Removing temporary files.................................................... 🧹"
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
	@echo "Removed temporary files..................................................... ✅"
