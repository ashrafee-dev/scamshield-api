FROM ghcr.io/astral-sh/uv:0.12.19 AS uv
FROM python:3.13-slim-bookworm

COPY --from=uv /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 app

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" HOME=/home/app XDG_CACHE_HOME=/home/app/.cache \
    OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_CACHE_DIR=/root/.cache/uv uv sync --frozen --no-dev --no-install-project
COPY app ./app
COPY scripts/serve.sh /app/serve.sh
RUN mkdir -p /home/app/.cache && chown -R app:app /home/app/.cache \
    && chmod +x /app/serve.sh
USER app
EXPOSE 8000
CMD ["/app/serve.sh"]
