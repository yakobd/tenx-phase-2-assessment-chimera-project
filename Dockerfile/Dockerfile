# Multi-stage Dockerfile for Project Chimera
# - Base: python:3.12-slim
# - Copies the `uv` client from its official image using a multi-stage COPY

FROM ghcr.io/pdm-project/uv:latest AS uv-builder

FROM python:3.12-slim

# Copy the uv executable from the official uv image into this image.
# If the upstream uv image changes location, replace the FROM reference above.
COPY --from=uv-builder /usr/local/bin/uv /usr/local/bin/uv

WORKDIR /app

# Copy lockfiles first to leverage Docker layer caching when dependencies don't change
COPY pyproject.toml uv.lock ./

# Ensure pip is modern and install pinned dependencies using uv for deterministic installs
RUN python -m pip install --no-cache-dir --upgrade pip \
    && uv sync --frozen

# Copy application source after dependencies are installed
COPY . .

ENV PYTHONPATH=/app

# Default to running tests for CI / TDD workflows
CMD ["pytest", "-q"]
