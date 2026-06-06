FROM python:3.11-slim

RUN apt-get update -q && apt-get install -y git -q && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "dlt[gs,parquet]" \
    kaggle \
    tenacity \
    pandas

WORKDIR /app

COPY ingestion/ ./ingestion/
