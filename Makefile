.PHONY: setup test docker-build docker-test spec-check

UV=uv
IMAGE_NAME=chimera-agent
DOCKERFILE_PATH=Dockerfile/Dockerfile

setup:
	@echo "Installing dependencies with uv (frozen lock)..."
	$(UV) sync

test:
	@echo "Running pytest..."
	PYTHONPATH=. $(UV) run pytest

docker-build:
	@echo "Building Docker image $(IMAGE_NAME) using $(DOCKERFILE_PATH)..."
	docker build -f $(DOCKERFILE_PATH) -t $(IMAGE_NAME) .

docker-test: docker-build
	@echo "Running tests inside Docker image $(IMAGE_NAME)..."
	docker run --rm $(IMAGE_NAME)

spec-check:
	@echo "Running spec check script..."
	python scripts/spec_check.py
