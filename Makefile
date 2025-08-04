.PHONY: setup test test-unit test-integration coverage lint format clean

# 虛擬環境設定
setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt

# 測試相關
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/unit/ -v -m unit

test-integration:
	python -m pytest tests/integration/ -v -m integration

coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# 程式碼品質
lint:
	flake8 src/ tests/
	pylint src/

format:
	black src/ tests/
	isort src/ tests/

# 清理
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

# Yocto 相關
yocto-build:
	cd yocto && bitbake fermenting-box-minimal