# ---- build ----
FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
COPY src ./src

# ---- runtime ----
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app/src ./src
ENV PYTHONPATH=/app/src
EXPOSE 8080
CMD ["uvicorn", "ingestion.main:app", "--host", "0.0.0.0", "--port", "8080"]
