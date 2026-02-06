# Project Chimera — Task 3.2 Dockerfile
FROM python:3.12-slim

# Copy uv and uvx from the official image into /bin
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /bin/uvx

ENV UV_PROJECT_ENVIRONMENT=/usr/local/

WORKDIR /app

# Copy lockfiles first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install pinned dependencies using uv
RUN /bin/uv sync --frozen

# Copy application source after dependencies are installed
COPY . .

# Create a non-root user for security compliance
RUN groupadd -r governor && useradd -r -g governor -d /app -s /usr/sbin/nologin governor \
	&& chown -R governor:governor /app

ENV PYTHONPATH=/app

USER governor

CMD ["/bin/uv", "run", "pytest"]
