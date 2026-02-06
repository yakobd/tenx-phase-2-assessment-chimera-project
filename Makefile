.PHONY: setup test docker-build docker-test spec-check

UV=uv
IMAGE_NAME=chimera-governor
DOCKERFILE_PATH="Docker Folder/Dockerfile"

setup:
	@echo "Installing dependencies with uv (frozen lock)..."
	$(UV) sync --frozen

test:
	@echo "Running pytest..."
	pytest -q

docker-build:
	@echo "Building Docker image $(IMAGE_NAME) using $(DOCKERFILE_PATH)..."
	docker build -f $(DOCKERFILE_PATH) -t $(IMAGE_NAME) .

docker-test: docker-build
	@echo "Running tests inside Docker image $(IMAGE_NAME)..."
	docker run --rm $(IMAGE_NAME) pytest -q

spec-check:
	@echo "Running spec check script..."
	python scripts/spec_check.py
