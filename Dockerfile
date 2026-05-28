# Imagem da aplicação djangoSIGE.
# - base Python 3.12 (Debian slim) compatível com Django 5.2 LTS
# - usa uv para instalar deps a partir de pyproject.toml/uv.lock
# - venv em /opt/venv para não ser mascarado pelo bind mount do compose

FROM python:3.12-slim AS base

LABEL maintainer="lukasgarcya@hotmail.com"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev libxslt1-dev \
        libjpeg-dev zlib1g-dev \
        libpq-dev libffi-dev libssl-dev \
        # Dependências de sistema do WeasyPrint (geração de PDF)
        libpango-1.0-0 libpangoft2-1.0-0 \
        libcairo2 libgdk-pixbuf-2.0-0 \
        libharfbuzz0b libfontconfig1 \
        curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /opt/djangoSIGE/

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

RUN uv pip install --python /opt/venv gunicorn psycopg2-binary

COPY . .

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "djangosige.wsgi:application"]
