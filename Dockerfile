FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/data_pipeline/staging_cache /app/chroma_db_store /app/static /app/backups

EXPOSE 8000

CMD ["sh", "-c", "python bin/init_db.py && python manage.py runserver 0.0.0.0:8000"]
