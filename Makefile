PYTHON ?= python3

.PHONY: run test lint clean

run:
	$(PYTHON) src/main.py --config examples/test_simple.ini

test:
	$(PYTHON) -m pytest -v

lint:
	$(PYTHON) -m flake8 src tests

clean:
	rm -rf build .pytest_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
