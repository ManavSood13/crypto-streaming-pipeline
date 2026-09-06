# ₿ Crypto Streaming Pipeline

A real-time cryptocurrency data engineering project that streams live trade data from Binance, processes and validates the incoming events, aggregates trades into 10-second OHLCV candles, stores the processed data in PostgreSQL, and presents the data through an interactive Streamlit dashboard.

The project demonstrates an end-to-end data pipeline covering **real-time ingestion, data processing, validation, aggregation, database storage, SQL analytics, Pandas analysis, visualization, testing, logging, and dashboard development**.

---

## 📌 Project Overview

The pipeline continuously receives real-time cryptocurrency trade events through the Binance WebSocket API.

Each incoming trade goes through the following stages:

1. Receive real-time trade data from Binance.
2. Parse and transform the raw WebSocket event.
3. Validate the transformed trade.
4. Aggregate trades into 10-second OHLCV candles.
5. Store completed candles in PostgreSQL.
6. Query the stored data using SQL.
7. Convert query results into Pandas DataFrames.
8. Visualize the data through a Streamlit dashboard.

### High-Level Architecture

```text
                    Binance
                       │
                       │ WebSocket Trade Streams
                       ▼
              ┌─────────────────┐
              │  Data Ingestion  │
              │ WebSocket Client │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Transformation  │
              │   & Validation   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Aggregation    │
              │   10-sec OHLCV   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   PostgreSQL     │
              │   ohlcv_10s      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  SQL Analytics   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Pandas Analysis  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Streamlit     │
              │    Dashboard     │
              └─────────────────┘
```

---

## 🚀 Features

### Real-Time Data Ingestion

- Connects to Binance using WebSockets.
- Streams live trade events.
- Supports multiple cryptocurrency pairs through a combined WebSocket stream.
- Automatically reconnects when the WebSocket connection is lost.
- Uses exponential backoff for reconnection attempts.
- Handles graceful shutdown through `SIGINT`.

### Data Processing

- Transforms raw Binance events into a consistent internal structure.
- Converts timestamps from milliseconds into timezone-aware UTC datetime objects.
- Converts price and quantity values into numeric types.
- Validates required fields.
- Rejects invalid prices and quantities.

### 10-Second OHLCV Aggregation

Incoming trades are grouped into 10-second time buckets.

Each candle contains:

| Field | Description |
|---|---|
| `symbol` | Cryptocurrency trading pair |
| `bucket_start` | Start time of the 10-second bucket |
| `open` | First trade price |
| `high` | Highest trade price |
| `low` | Lowest trade price |
| `close` | Last trade price |
| `volume` | Total traded quantity |
| `trade_count` | Number of trades in the bucket |

### PostgreSQL Storage

Processed OHLCV data is stored in PostgreSQL using the `ohlcv_10s` table.

The table uses:

```text
PRIMARY KEY (symbol, bucket_start)
```

This provides a unique candle for each cryptocurrency and time bucket.

Duplicate candles are safely ignored using PostgreSQL conflict handling.

### SQL Analytics

The project includes SQL queries for:

- Latest cryptocurrency prices
- Total trading volume
- Average volume per candle
- Price performance
- Trading activity
- Price volatility
- Historical price data
- Total number of stored candles
- Trading volume over time

### Pandas Analysis

SQL results are converted into Pandas DataFrames for:

- Dashboard display
- Data manipulation
- Analytical processing
- Visualization preparation

### Interactive Dashboard

The Streamlit dashboard provides:

- Real-time dashboard refresh
- LIVE status indicator
- BTC and ETH price KPIs
- Total candle count
- Highest-volume cryptocurrency
- Market overview table
- Cryptocurrency selector
- 10 / 30 / 60 minute price history
- Current selected cryptocurrency price
- Trading volume chart
- Price performance chart
- Trading activity chart
- Price volatility chart
- Trading volume over time chart
- Pipeline status section

---

## 🪙 Supported Cryptocurrencies

The pipeline currently streams the following USDT trading pairs:

| Cryptocurrency | Symbol |
|---|---|
| Bitcoin | BTCUSDT |
| Ethereum | ETHUSDT |
| BNB | BNBUSDT |
| Solana | SOLUSDT |
| XRP | XRPUSDT |
| Cardano | ADAUSDT |
| Dogecoin | DOGEUSDT |
| Avalanche | AVAXUSDT |
| Chainlink | LINKUSDT |
| Polkadot | DOTUSDT |

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Binance WebSocket API | Real-time market data |
| Binance REST API | API exploration/reference |
| PostgreSQL | Persistent data storage |
| psycopg | PostgreSQL database connectivity |
| Pandas | Data analysis and transformation |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| WebSocket Client | WebSocket communication |
| Git | Version control |
| GitHub | Source code hosting |

---

## 📂 Project Structure

```text
crypto-streaming-pipeline/
│
├── assets/
│   └── style.css
│
├── logs/
│   └── .gitkeep
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/
│   │   └── binance_rest.py
│   │
│   ├── analytics/
│   │   └── queries.py            # SQL aggregates
│   │
│   ├── analysis/
│   │   └── analyzer.py           # query results -> DataFrames
│   │
│   ├── dashboard/
│   │   ├── components.py         # page assembly
│   │   ├── data.py               # cached connection + data loading
│   │   ├── overview.py           # KPIs and market table
│   │   ├── price.py              # price history chart
│   │   ├── analytics.py          # analytics section
│   │   ├── charts.py             # Plotly figures
│   │   ├── status.py             # live pipeline health
│   │   ├── safe.py               # empty-data helpers
│   │   └── theme.py              # shared chart colours
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── repository.py
│   │
│   ├── ingestion/
│   │   └── binance_websocket.py
│   │
│   ├── processing/
│   │   ├── transformer.py
│   │   ├── validator.py
│   │   └── aggregator.py
│   │
│   └── utils/
│       └── logger.py
│
├── tests/
│   ├── test_aggregator.py
│   ├── test_processing.py
│   └── test_theme.py
│
├── .env.example
├── .gitignore
├── app.py
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## 🔄 Data Flow

### 1. Binance WebSocket

The ingestion service connects to Binance's combined WebSocket stream and subscribes to trade streams for the supported USDT pairs.

Example stream format:

```text
<symbol>@trade
```

Multiple streams are combined into a single WebSocket connection.

---

### 2. Raw Event

A Binance trade event contains information such as:

```text
Event type
Event time
Symbol
Trade ID
Price
Quantity
Trade time
Buyer market maker flag
```

The raw event is passed to the transformation layer.

---

### 3. Transformation

The transformer converts the Binance event into the project's internal trade representation:

```text
{
    symbol,
    price,
    quantity,
    trade_time,
    event_time
}
```

Timestamps are converted into timezone-aware UTC datetime values.

---

### 4. Validation

The validator checks:

- Required fields exist.
- Symbol is present.
- Price is greater than zero.
- Quantity is greater than zero.

Invalid trades are rejected and logged.

---

### 5. Aggregation

Valid trades are assigned to a 10-second time bucket.

For example:

```text
12:00:01
12:00:04
12:00:08
```

belong to:

```text
12:00:00 → 12:00:09
```

The resulting OHLCV candle contains:

```text
Open
High
Low
Close
Volume
Trade Count
```

---

### 6. PostgreSQL

Once a bucket is completed, the aggregated candle is inserted into PostgreSQL.

The primary key is:

```text
(symbol, bucket_start)
```

This prevents duplicate candles from being stored.

---

### 7. SQL Analytics

The dashboard queries PostgreSQL to calculate market-level metrics and historical data.

Examples include:

```text
Latest price
Total volume
Price change
Trading activity
Volatility
Volume over time
```

---

### 8. Pandas

The SQL query results are converted into DataFrames for analysis and dashboard rendering.

---

### 9. Streamlit

The Streamlit application refreshes the dashboard every few seconds and displays the latest information from PostgreSQL.

---

## 🗄️ Database Schema

The project uses the following PostgreSQL table:

```sql
CREATE TABLE ohlcv_10s (
    symbol VARCHAR(20) NOT NULL,
    bucket_start TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    trade_count INTEGER NOT NULL,
    PRIMARY KEY (symbol, bucket_start)
);

-- Supports the time-windowed dashboard aggregates.
CREATE INDEX ohlcv_10s_bucket_start_idx
    ON ohlcv_10s (bucket_start DESC);
```

### Why 10-Second Candles?

The project uses 10-second aggregation to demonstrate real-time stream processing while keeping the dashboard responsive and the dataset manageable.

The aggregation interval can be changed later if different analysis requirements are needed.

---

## ⚙️ Local Setup

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd crypto-streaming-pipeline
```

---

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it:

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows

```powershell
.venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3a. Configure the Database Connection (optional)

Connection settings are read from the standard PostgreSQL environment
variables, so no code changes are needed to run the project elsewhere:

| Variable | Default |
|---|---|
| `PGDATABASE` | `crypto_pipeline` |
| `PGUSER` | current OS user |
| `PGHOST` | `localhost` |
| `PGPORT` | `5432` |
| `PGPASSWORD` | unset |

Logging can be tuned with `LOG_LEVEL` (default `INFO`), `LOG_MAX_BYTES`
and `LOG_BACKUP_COUNT`.

---

### 4. Install PostgreSQL

Make sure PostgreSQL is installed and running locally.

Verify the installation:

```bash
psql --version
```

Check whether PostgreSQL is accepting connections:

```bash
pg_isready
```

---

### 5. Create the Database

Create the project database:

```bash
createdb crypto_pipeline
```

Or from `psql`:

```sql
CREATE DATABASE crypto_pipeline;
```

---

### 6. Create the OHLCV Table

Connect to the database:

```bash
psql crypto_pipeline
```

Then create the table:

```sql
CREATE TABLE ohlcv_10s (
    symbol VARCHAR(20) NOT NULL,
    bucket_start TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    trade_count INTEGER NOT NULL,
    PRIMARY KEY (symbol, bucket_start)
);
```

---

## ▶️ Running the Pipeline

The ingestion process can be started with:

```bash
python -m src.ingestion.binance_websocket
```

Once connected, the process will:

```text
Binance WebSocket
       ↓
Receive trades
       ↓
Transform
       ↓
Validate
       ↓
Aggregate
       ↓
Insert into PostgreSQL
```

You should see messages indicating that the WebSocket connection has been established and OHLCV records are being saved.

---

## 📊 Running the Dashboard

Start Streamlit with:

```bash
streamlit run app.py
```

The dashboard will open in your browser.

The dashboard reads processed data from PostgreSQL rather than directly consuming the Binance WebSocket stream.

### Important

The **WebSocket ingestion process and Streamlit dashboard are separate components**.

The ingestion process collects and stores data.

The Streamlit application reads and visualizes that stored data.

This separation allows the dashboard to be closed without stopping the data ingestion process, provided the ingestion worker remains running.

---

## 🔁 Reconnection Strategy

Real-time WebSocket connections can fail because of network problems or remote connection closures.

The ingestion service therefore includes automatic reconnection.

The current strategy starts with a short delay and increases the delay after repeated failures, up to a configured maximum.

Conceptually:

```text
Connection lost
      ↓
Wait 1 second
      ↓
Reconnect
      ↓
If failure
      ↓
Wait 2 seconds
      ↓
Reconnect
      ↓
If failure
      ↓
Wait 4 seconds
      ↓
...
      ↓
Maximum delay
```

This prevents the application from continuously attempting connections with no delay.

---

## 📝 Logging

The project uses Python's built-in `logging` module.

Logs are written to:

```text
logs/
```

The logging system records events such as:

- WebSocket connections
- WebSocket errors
- Reconnection attempts
- Invalid trades
- Completed OHLCV buckets
- Database connections
- Database insert failures
- Application shutdown

Log files rotate at 5 MB and keep three backups, so a long running
pipeline cannot fill the disk. Per-insert detail is logged at `DEBUG`
level; set `LOG_LEVEL=DEBUG` to see it.

Log files are excluded from Git using `.gitignore`.

---

## 🧪 Testing

The project uses `pytest`. Run the suite from the project root:

```bash
pytest -q
```

Tests live in `tests/` and cover:

### Data Validation

- Missing and `None` fields
- Empty symbols
- Invalid prices and quantities
- Malformed payloads reaching the validator rather than raising

### OHLCV Aggregation

- Open, high, low, close, volume and trade count
- 10-second bucket assignment and microsecond truncation
- Per-symbol isolation

### Regression Tests

These cover bugs that previously caused silent data loss:

- In-flight buckets are flushed on shutdown
- Buckets for symbols that stop trading are flushed once stale
- Out-of-order trades are discarded instead of leaking buckets
- Skipping ahead completes *every* open bucket, not just the newest

### Dashboard Safety

- Lookups against an empty database return placeholders
- `Decimal` columns are converted to `float64`

---

## 📈 Dashboard Analytics

The dashboard currently provides several analytical views.

### Market Overview

Displays:

- Symbol
- Latest price
- Price change
- Last update time

### Price History

Users can select a cryptocurrency and view recent price history for:

```text
10 minutes
30 minutes
60 minutes
```

### Trading Volume

Compares total stored trading volume across supported cryptocurrencies.

### Price Performance

Compares price movement across the stored dataset.

### Trading Activity

Compares the total number of trades represented by the stored OHLCV candles.

### Price Volatility

Displays the observed price range for each cryptocurrency.

### Trading Volume Over Time

Shows aggregated trading volume over time.

The bucket width adapts to how much history exists (1 minute, 5 minutes,
15 minutes or 1 hour), so the chart is readable immediately after the
pipeline starts rather than collapsing into a single point.

---

## 🧠 Engineering Concepts Demonstrated

This project was built to demonstrate practical data engineering concepts rather than only creating a visualization.

### Streaming Data

Handling continuously arriving events using WebSockets.

### Data Transformation

Converting external API data into a clean internal schema.

### Data Validation

Preventing invalid records from entering downstream processing.

### Stream Aggregation

Grouping individual events into time-based OHLCV windows.

### Database Design

Using a composite primary key to uniquely identify each cryptocurrency candle.

### SQL Analytics

Using:

- Aggregations
- `GROUP BY`
- `ORDER BY`
- CTEs
- Window functions
- `DISTINCT ON`
- `DATE_TRUNC`

### Data Analysis

Using Pandas to convert and prepare database results.

### Visualization

Creating interactive charts using Plotly and Streamlit.

### Reliability

Implementing:

- Logging
- Exception handling
- Database rollback
- WebSocket reconnection
- Graceful shutdown

### Software Structure

Separating ingestion, processing, database, analytics, analysis, and UI responsibilities into different modules.

---

## 🔐 Configuration & Security

The current local development configuration uses PostgreSQL connection settings in the database connection module.

For production deployment, database credentials should **not** be hard-coded.

A production version should use environment variables or Streamlit secrets, for example:

```text
DATABASE_URL
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Sensitive credentials should never be committed to GitHub.

---

## ☁️ Deployment Architecture

For a production-style deployment, the recommended architecture is:

```text
                 Binance
                    │
                    ▼
          ┌──────────────────┐
          │ Cloud Ingestion  │
          │      Worker      │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Cloud PostgreSQL │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │    Streamlit     │
          │    Dashboard     │
          └────────┬─────────┘
                   │
                   ▼
                Browser
```

The dashboard and ingestion worker should be treated as separate services.

A long-running WebSocket worker should run on infrastructure designed for persistent background processes, while the Streamlit application can serve the visualization layer.

---

## ⚠️ Current Limitations

This project is designed as a portfolio and learning project, so there are several areas that can be improved for production use.

### In-Memory Aggregation

The current aggregation state is held in memory by the ingestion process.

If the worker stops unexpectedly before a bucket is persisted, the current incomplete bucket can be lost.

### Out-of-Order Events

The aggregation logic primarily assumes that trade events arrive in chronological order.

A production-grade stream processor could handle late or out-of-order events more explicitly.

### Database Configuration

Local development currently uses local PostgreSQL configuration.

Production deployment requires environment-based database configuration.

### Worker Availability

The dashboard itself does not guarantee that the ingestion worker is running.

The dashboard's pipeline status represents the dashboard/database processing state available to the application, not an independent health check of the remote ingestion worker.

### Data Retention

The project currently keeps collected OHLCV data in PostgreSQL without an automated retention policy.

For a long-running production system, a retention or archival strategy would be useful.

---

## 🔮 Future Improvements

Potential improvements include:

- Deploy the ingestion worker to a cloud service.
- Move PostgreSQL to a managed cloud database.
- Use environment variables / secrets for production configuration.
- Add database connection pooling.
- Add automated data retention.
- Improve handling of out-of-order events.
- Add monitoring and health checks.
- Add more trading pairs.
- Add configurable aggregation intervals.
- Add candlestick visualizations.
- Add technical indicators.
- Add automated integration tests.
- Add CI/CD with GitHub Actions.
- Add containerization with Docker.
- Add production metrics and alerting.

---

## 📌 Project Goals

The main goal of this project is to demonstrate the complete lifecycle of a real-time data engineering system:

```text
External Data Source
        ↓
Real-Time Ingestion
        ↓
Data Transformation
        ↓
Data Validation
        ↓
Stream Aggregation
        ↓
Persistent Storage
        ↓
SQL Analytics
        ↓
Pandas Processing
        ↓
Visualization
        ↓
Deployment
```

Rather than treating each technology as an isolated skill, the project connects them into one end-to-end pipeline.

---

## 📚 Learning Outcomes

Through this project, the following concepts are practiced:

- Working with REST APIs
- Working with WebSockets
- Processing streaming data
- JSON parsing
- Data transformation
- Data validation
- Time-based aggregation
- OHLCV generation
- PostgreSQL database design
- SQL analytics
- Pandas DataFrames
- Plotly visualization
- Streamlit application development
- Python logging
- Exception handling
- Database transactions
- WebSocket reconnection
- Unit testing
- Git and GitHub
- Cloud deployment architecture

---

## ⚠️ Disclaimer

This project is intended for **educational and portfolio purposes only**.

The cryptocurrency data displayed by the application is market data and should not be considered financial advice, investment advice, or a recommendation to buy or sell any asset.

---

## 👨‍💻 Author

**Manav Sood**

Computer Science undergraduate focused on:

- Data Engineering
- Python
- SQL
- Data Processing
- AI / Machine Learning

---

## ⭐ Project Summary

**Crypto Streaming Pipeline** is an end-to-end real-time data engineering project that demonstrates how live cryptocurrency trade events can be transformed into structured analytical data and presented through an interactive dashboard.

```text
Binance WebSocket
        ↓
Python Streaming Pipeline
        ↓
10-Second OHLCV Aggregation
        ↓
PostgreSQL
        ↓
SQL Analytics
        ↓
Pandas
        ↓
Streamlit + Plotly
```

Built with Python, PostgreSQL, Pandas, Streamlit, Plotly, WebSockets, SQL, and Git.
