# syntax=docker/dockerfile:1
FROM python:3.12-slim AS deps
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Train stage: generate data + train the model so the image is self-contained
FROM deps AS train
WORKDIR /app
COPY data/ data/
COPY backend/ml/ backend/ml/
WORKDIR /app/backend/ml
RUN python generate_data.py && python train.py

# Runtime stage
FROM deps AS runtime
WORKDIR /app
ENV PYTHONPATH=/app/backend
COPY backend/app/ backend/app/
COPY backend/ml/ backend/ml/
COPY --from=train /app/backend/ml/artifacts/ backend/ml/artifacts/
COPY --from=train /app/backend/ml/reports/ backend/ml/reports/
COPY --from=train /app/data/ data/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
