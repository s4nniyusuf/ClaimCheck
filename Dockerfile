FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PLAYWRIGHT_BROWSERS_PATH=/app/browsers

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

RUN playwright install chromium
RUN playwright install-deps chromium
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8000"]