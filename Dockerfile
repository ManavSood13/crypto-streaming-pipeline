# Container for the ingestion worker.
# The Streamlit dashboard is deployed separately (see README).

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# DATABASE_URL is supplied by the hosting platform.
CMD ["python", "-m", "src.ingestion.binance_websocket"]
