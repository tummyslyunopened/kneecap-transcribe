FROM ghcr.io/astral-sh/uv:python3.13-alpine AS base
ENV VIRTUAL_ENV=/app/.venv
FROM base AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv venv 
RUN uv sync 
FROM base AS runtime
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
WORKDIR /app
COPY . .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

