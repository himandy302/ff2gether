# Polymarket Crypto Arbitrage Bot - Master Plan

**Project Goal**: Build an educational trading bot that exploits timing inefficiencies between crypto spot markets and Polymarket prediction markets.

**Last Updated**: 2026-01-14

---

## Table of Contents

1. [Strategy Overview](#strategy-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Integrations](#api-integrations)
6. [Trading Logic & Signal Detection](#trading-logic--signal-detection)
7. [Risk Management](#risk-management)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Project Structure](#project-structure)
11. [Key Considerations](#key-considerations)
12. [Probability of Success](#probability-of-success)
13. [Plan Upgrades](#plan-upgrades)

---

## Strategy Overview

### Core Concept

The strategy exploits the temporal lag between crypto spot price movements on centralized exchanges (Binance, Coinbase) and Polymarket's binary prediction market pricing for 15-minute BTC up/down outcomes.

### The Edge

**Information Asymmetry in Time**
- Polymarket asks: "Will BTC go up or down in the next 15 minutes?"
- Most traders predict at market open (speculative)
- Our bot waits 3-5 minutes, then "buys what already happened"
- By minute 3-5, spot exchanges show clear directional momentum
- Polymarket pricing often lags behind, creating arbitrage opportunities

### Key Insight

**This is NOT prediction trading. This is latency arbitrage.**
- We don't predict BTC's future direction
- We wait for confirmation on spot markets
- We exploit Polymarket's slower price discovery
- We "rent the certainty" of the final minutes

### Reference Strategy

Based on successful implementation by [@Mikocrypto11](https://x.com/mikocrypto11):
- Turned $500 → $233,000 using a Python bot
- Traded exclusively BTC 15-minute markets
- No stop loss, no take profit - hold to settlement
- No leverage, no macro analysis, pure execution

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                             │
│              (Main coordination loop)                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   MARKET     │    │    PRICE     │    │   SIGNAL     │
│  DISCOVERY   │───▶│   MONITOR    │───▶│  GENERATOR   │
│              │    │              │    │              │
│ Find 15-min  │    │ Track spot   │    │ Analyze      │
│ BTC markets  │    │ on CEXs      │    │ momentum     │
└──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │    RISK      │
                                        │  MANAGER     │
                                        │              │
                                        │ Position     │
                                        │ sizing       │
                                        └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │   TRADE      │
                                        │  EXECUTOR    │
                                        │              │
                                        │ Place orders │
                                        └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │  POSITION    │
                                        │  MANAGER     │
                                        │              │
                                        │ Track P&L    │
                                        └──────────────┘
                            ┌───────────────────┘
                            ▼
                    ┌──────────────┐
                    │   DATABASE   │
                    │              │
                    │ TimescaleDB  │
                    │ PostgreSQL   │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  MONITORING  │
                    │              │
                    │ Grafana +    │
                    │ Prometheus   │
                    └──────────────┘
```

### Core Components

1. **Market Discovery Service**
   - Continuously scan Polymarket for new 15-minute BTC markets
   - Filter markets by criteria (liquidity, timing, etc.)
   - Queue markets for monitoring

2. **Price Monitor**
   - WebSocket connections to Binance & Coinbase
   - Real-time BTC spot price tracking
   - Calculate consensus price across exchanges
   - Store tick data for momentum analysis

3. **Signal Generator**
   - Wait 3-5 minutes after market opens
   - Analyze spot price momentum in that window
   - Compare to Polymarket pricing
   - Calculate expected value (EV)
   - Decide: EXECUTE, SKIP, or WAIT

4. **Risk Manager**
   - Position sizing (Kelly Criterion)
   - Exposure limits
   - Circuit breakers (max loss, drawdown)
   - Portfolio risk tracking

5. **Trade Executor**
   - Place orders on Polymarket CLOB
   - Handle order fills and errors
   - Retry logic with exponential backoff

6. **Position Manager**
   - Track open positions
   - Monitor until market resolution
   - Calculate P&L on settlement
   - Update account balance

7. **Orchestrator**
   - Main event loop coordinating all services
   - Async task management
   - Error handling and recovery
   - Graceful shutdown

---

## Technology Stack

### Backend Core

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.11+ | Async support, rich ecosystem, fast prototyping |
| Framework | FastAPI | Modern async API framework, auto documentation |
| Async Runtime | asyncio + aiohttp | Concurrent operations, non-blocking I/O |

### Data Storage

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Primary DB | PostgreSQL 15+ | ACID compliance, mature, reliable |
| Time-Series Extension | TimescaleDB | Optimized for time-series data (prices, metrics) |
| Cache Layer | Redis 7+ | Rate limiting, pub/sub, session management |

### API Integration

| Library | Purpose |
|---------|---------|
| `py-clob-client` | Polymarket CLOB API integration |
| `ccxt` | Unified crypto exchange API (Binance, Coinbase) |
| `web3.py` | Ethereum blockchain interactions (if needed) |
| `websockets` | Real-time price feeds |

### Data Processing

| Library | Purpose |
|---------|---------|
| `pandas` / `polars` | Data manipulation and analysis |
| `numpy` | Numerical computations |
| `ta-lib` or `pandas-ta` | Technical indicators (momentum, trends) |
| `scikit-learn` | Probability model calibration |

### Monitoring & Observability

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Logging | `structlog` | Structured JSON logging |
| Metrics | Prometheus | Time-series metrics collection |
| Visualization | Grafana | Real-time dashboards |
| Alerting | Alertmanager | Alert routing and deduplication |
| Notifications | Discord/Telegram webhooks | Instant alerts |

### Infrastructure

| Component | Technology |
|-----------|-----------|
| Containerization | Docker + Docker Compose |
| Orchestration | Kubernetes (optional, production) |
| CI/CD | GitHub Actions |
| Secrets Management | `.env` files (dev), AWS Secrets Manager (prod) |

---

## Database Schema

### Tables Overview

| Table | Purpose | Type |
|-------|---------|------|
| `markets` | Polymarket market metadata | Relational |
| `market_data` | CEX spot price ticks | Time-series |
| `polymarket_orderbook` | Polymarket orderbook snapshots | Time-series |
| `signals` | Trading signals generated | Relational |
| `orders` | Orders placed | Relational |
| `trades` | Filled trades | Relational |
| `positions` | Open and closed positions | Relational |
| `account_balance` | Balance history | Time-series |
| `system_events` | System logs and events | Relational |
| `performance_metrics` | Daily performance summary | Relational |

### Complete Schema

```sql
-- Markets table: Track Polymarket 15-min BTC markets
CREATE TABLE markets (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(100) UNIQUE NOT NULL,
    question TEXT NOT NULL,
    market_type VARCHAR(50),  -- 'btc_15min_up_down'
    open_time TIMESTAMPTZ NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    resolution_time TIMESTAMPTZ,
    status VARCHAR(20),  -- 'active', 'closed', 'resolved'
    winning_outcome VARCHAR(10),  -- 'YES', 'NO'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market data: Time-series price data from CEXs
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(20) NOT NULL,  -- 'binance', 'coinbase'
    symbol VARCHAR(20) NOT NULL,  -- 'BTC/USDT'
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8),
    PRIMARY KEY (time, exchange, symbol)
);

SELECT create_hypertable('market_data', 'time');

-- Polymarket orderbook snapshots
CREATE TABLE polymarket_orderbook (
    time TIMESTAMPTZ NOT NULL,
    market_id VARCHAR(100) NOT NULL,
    outcome VARCHAR(10) NOT NULL,  -- 'YES', 'NO'
    best_bid DECIMAL(10, 4),
    best_ask DECIMAL(10, 4),
    bid_size DECIMAL(20, 2),
    ask_size DECIMAL(20, 2),
    mid_price DECIMAL(10, 4),
    PRIMARY KEY (time, market_id, outcome)
);

SELECT create_hypertable('polymarket_orderbook', 'time');

-- Signals: Detected trading opportunities
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(100) NOT NULL,
    signal_time TIMESTAMPTZ NOT NULL,
    minutes_since_open INTEGER,

    -- Spot price analysis
    spot_price_start DECIMAL(20, 8),
    spot_price_current DECIMAL(20, 8),
    price_change_pct DECIMAL(10, 6),
    momentum_score DECIMAL(10, 6),

    -- Polymarket pricing
    pm_yes_price DECIMAL(10, 4),
    pm_no_price DECIMAL(10, 4),

    -- Signal decision
    recommended_outcome VARCHAR(10),  -- 'YES', 'NO', 'NONE'
    confidence_score DECIMAL(10, 6),
    expected_value DECIMAL(10, 6),

    -- Execution
    executed BOOLEAN DEFAULT FALSE,
    execution_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders: All orders placed
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE,
    market_id VARCHAR(100) NOT NULL,
    signal_id INTEGER REFERENCES signals(id),

    order_type VARCHAR(20),  -- 'MARKET', 'LIMIT'
    side VARCHAR(10),  -- 'BUY', 'SELL'
    outcome VARCHAR(10),  -- 'YES', 'NO'

    quantity DECIMAL(20, 2),
    price DECIMAL(10, 4),

    status VARCHAR(20),  -- 'pending', 'filled', 'cancelled', 'failed'

    placed_at TIMESTAMPTZ NOT NULL,
    filled_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trades: Filled orders
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100) UNIQUE,
    order_id VARCHAR(100) REFERENCES orders(order_id),
    market_id VARCHAR(100) NOT NULL,

    outcome VARCHAR(10),
    quantity DECIMAL(20, 2),
    avg_price DECIMAL(10, 4),
    cost DECIMAL(20, 2),
    fee DECIMAL(20, 2),

    filled_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Positions: Open positions tracking
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(100) NOT NULL,
    trade_id VARCHAR(100) REFERENCES trades(trade_id),

    outcome VARCHAR(10),
    quantity DECIMAL(20, 2),
    avg_entry_price DECIMAL(10, 4),
    cost_basis DECIMAL(20, 2),

    status VARCHAR(20),  -- 'open', 'resolved'

    -- Resolution
    resolution_outcome VARCHAR(10),
    payout DECIMAL(20, 2),
    realized_pnl DECIMAL(20, 2),

    opened_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Account balance history
CREATE TABLE account_balance (
    time TIMESTAMPTZ NOT NULL,
    balance DECIMAL(20, 2) NOT NULL,
    equity DECIMAL(20, 2),
    available DECIMAL(20, 2),
    PRIMARY KEY (time)
);

SELECT create_hypertable('account_balance', 'time');

-- System events and logs
CREATE TABLE system_events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50),  -- 'error', 'warning', 'info'
    component VARCHAR(50),
    message TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics (daily summary)
CREATE TABLE performance_metrics (
    date DATE PRIMARY KEY,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(10, 4),
    total_pnl DECIMAL(20, 2),
    avg_trade_pnl DECIMAL(20, 2),
    max_drawdown DECIMAL(20, 2),
    sharpe_ratio DECIMAL(10, 4)
);

-- Indexes for performance
CREATE INDEX idx_markets_status ON markets(status);
CREATE INDEX idx_markets_open_time ON markets(open_time);
CREATE INDEX idx_signals_market_id ON signals(market_id);
CREATE INDEX idx_signals_executed ON signals(executed);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_positions_status ON positions(status);
CREATE INDEX idx_system_events_type ON system_events(event_type);
```

---

## API Integrations

### 1. Polymarket CLOB API

**Library**: `py-clob-client`

**Key Endpoints**:
- `GET /markets` - Discover active markets
- `GET /book?token_id=X` - Get orderbook for specific outcome
- `POST /order` - Place limit/market orders
- `GET /trades` - Track trade fills
- `WebSocket /ws` - Real-time orderbook updates

**Client Implementation Pattern**:

```python
class PolymarketClient:
    def __init__(self, api_key, private_key):
        # Initialize CLOB client with credentials
        # Setup web3 wallet for signing transactions

    async def discover_btc_15min_markets(self):
        # Filter for BTC 15-minute up/down markets
        # Return markets opening in next N minutes

    async def get_orderbook(self, market_id, outcome):
        # Get best bid/ask for YES or NO
        # Calculate mid price, spread

    async def place_market_order(self, market_id, outcome, size):
        # Execute market buy
        # Return order ID and fill details

    async def get_position(self, market_id):
        # Check current position size
        # Calculate unrealized P&L
```

**Rate Limits**: 100 requests per 10 seconds

### 2. Binance API

**Library**: `ccxt`

**Key Endpoints**:
- `GET /api/v3/ticker/price?symbol=BTCUSDT` - Current spot price
- `WebSocket wss://stream.binance.com:9443/ws/btcusdt@trade` - Real-time trades
- `GET /api/v3/klines` - OHLCV data for momentum calculation

**Client Implementation Pattern**:

```python
class BinanceClient:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

    async def get_btc_price(self):
        # Fetch current BTC/USDT price

    async def stream_btc_prices(self, callback):
        # WebSocket for real-time tick data
        # Call callback(price, timestamp) on each update

    async def get_momentum_window(self, start_time, end_time):
        # Get all trades/ticks in 3-5 minute window
        # Calculate price change, volatility, direction
```

**Rate Limits**: 1200 requests per minute

### 3. Coinbase API

**Library**: `ccxt`

**Key Endpoints**:
- `GET /products/BTC-USD/ticker` - Current price
- `WebSocket wss://ws-feed.exchange.coinbase.com` - Real-time matches

**Client Implementation Pattern**:

```python
class CoinbaseClient:
    def __init__(self):
        self.exchange = ccxt.coinbase({
            'enableRateLimit': True
        })

    async def get_btc_price(self):
        # Fetch BTC/USD price

    async def stream_btc_prices(self, callback):
        # WebSocket for real-time data
```

**Rate Limits**: 10 requests/sec (public), 15 requests/sec (private)

### 4. Multi-Exchange Price Aggregator

```python
class PriceAggregator:
    def __init__(self):
        self.binance = BinanceClient()
        self.coinbase = CoinbaseClient()
        self.prices = {}

    async def start_streaming(self):
        # Collect prices from multiple exchanges
        # Calculate consensus price (median/average)
        # Detect arbitrage opportunities across exchanges

    def get_consensus_btc_price(self):
        # Return weighted average price
        # Flag if exchange prices diverge significantly
```

---

## Trading Logic & Signal Detection

### Signal Generation Algorithm

**Core Decision Flow**:

```
Market Opens (T=0)
    ↓
Wait 3-5 minutes (observation window)
    ↓
Calculate spot momentum from T=0 to T=now
    ↓
Get Polymarket pricing
    ↓
Calculate Expected Value (EV)
    ↓
Decision: EXECUTE / SKIP / WAIT
```

### Momentum Calculation

**Metrics to Calculate**:

1. **Price Change**: `(current_price - start_price) / start_price`
2. **Direction**: `UP` if positive, `DOWN` if negative
3. **Momentum Consistency**: R² score from linear regression (0-1)
   - Higher R² = more consistent trend
   - Lower R² = choppy, sideways movement
4. **Volatility**: `(high - low) / start_price`

**Implementation**:

```python
async def _calculate_spot_momentum(self, start_time, end_time):
    # Get price series from aggregator
    prices = await self.price_aggregator.get_price_series(
        symbol='BTC',
        start=start_time,
        end=end_time
    )

    start_price = prices.iloc[0]['price']
    current_price = prices.iloc[-1]['price']
    high = prices['price'].max()
    low = prices['price'].min()

    # Price change percentage
    price_change_pct = (current_price - start_price) / start_price

    # Momentum consistency (R² score)
    from sklearn.linear_model import LinearRegression
    X = np.arange(len(prices)).reshape(-1, 1)
    y = prices['price'].values
    model = LinearRegression().fit(X, y)
    r_squared = model.score(X, y)

    return {
        'direction': 'UP' if price_change_pct > 0 else 'DOWN',
        'magnitude': abs(price_change_pct),
        'consistency': r_squared,
        'volatility': (high - low) / start_price,
        'start_price': start_price,
        'current_price': current_price
    }
```

### Expected Value Calculation

**Formula**:

```
Implied Win Probability = f(momentum_magnitude, momentum_consistency)
Polymarket Price = best_ask for outcome
Expected Value (EV) = implied_prob - pm_price
```

**Example**:
- BTC moved +0.6% in 4 minutes with R² = 0.85
- Historical data shows this results in UP 72% of the time
- Polymarket YES price = $0.58
- EV = 0.72 - 0.58 = 0.14 (14% edge)

### Execution Criteria

**Execute trade if ALL conditions met**:

1. ✅ `minutes_elapsed >= 3 AND <= 5`
2. ✅ `momentum_magnitude >= min_threshold` (e.g., 0.3%)
3. ✅ `momentum_consistency >= 0.70` (R² score)
4. ✅ `expected_value >= min_edge` (e.g., 15%)
5. ✅ `liquidity >= min_size` (e.g., $100)
6. ✅ Risk manager approves position size
7. ✅ No circuit breakers triggered

### Key Parameters to Tune

| Parameter | Default | Description |
|-----------|---------|-------------|
| `entry_delay_min` | 3 min | Earliest entry time |
| `entry_delay_max` | 5 min | Latest entry time |
| `min_momentum_threshold` | 0.003 | Min price move (0.3%) |
| `min_edge_threshold` | 0.15 | Min EV to trade (15%) |
| `momentum_consistency_threshold` | 0.70 | Min R² score |
| `min_liquidity` | 100 | Min orderbook depth ($) |

**Note**: These parameters MUST be calibrated through backtesting with historical data.

---

## Risk Management

### Position Sizing: Kelly Criterion

**Formula**:

```
Kelly % = (p × b - q) / b

Where:
p = win probability (from momentum model)
q = 1 - p (loss probability)
b = win/loss ratio = (1 - price) / price

Fractional Kelly = Kelly % × 0.25  (use 1/4 Kelly for safety)
```

**Implementation**:

```python
async def calculate_position_size(self, signal: SignalResult):
    win_prob = signal.confidence
    loss_prob = 1 - win_prob

    win_amount = 1.0 - signal.price
    loss_amount = signal.price

    kelly_fraction = (win_prob * win_amount - loss_prob * loss_amount) / loss_amount
    fractional_kelly = max(0, kelly_fraction * 0.25)

    # Apply hard limits
    kelly_size = current_balance * fractional_kelly
    max_size = min(
        current_balance * 0.02,  # 2% max per trade
        200  # $200 absolute max
    )

    position_size = min(kelly_size, max_size)

    return position_size
```

### Exposure Limits

| Limit | Value | Description |
|-------|-------|-------------|
| Max per trade | 2% of capital | Single position size |
| Max absolute | $200 | Hard cap per trade |
| Max concurrent | 5 positions | Open positions at once |
| Max exposure | 20% of capital | Total capital deployed |

### Circuit Breakers

**Automatic trading halt conditions**:

1. **Daily Loss Limit**
   - Trigger: Daily P&L < -5% of starting capital
   - Action: Stop all new trades until next day
   - Severity: HIGH

2. **Maximum Drawdown**
   - Trigger: Drawdown from peak > 15%
   - Action: Stop all trading, require manual review
   - Severity: CRITICAL

3. **Consecutive Losses**
   - Trigger: 5 losing trades in a row
   - Action: Pause trading for 1 hour, review system
   - Severity: MEDIUM

4. **API Failures**
   - Trigger: >10% API error rate for 5 minutes
   - Action: Stop trading, check connectivity
   - Severity: HIGH

### Risk Configuration

```yaml
risk_config:
  # Capital
  total_capital: 10000

  # Position sizing
  max_per_trade_pct: 0.02      # 2% per trade
  max_per_trade_abs: 200       # $200 max
  kelly_multiplier: 0.25       # Use 1/4 Kelly

  # Exposure
  max_concurrent: 5            # Max 5 open positions
  max_exposure_pct: 0.20       # Max 20% deployed

  # Circuit breakers
  max_daily_loss_pct: 0.05     # Stop at -5% daily
  max_drawdown_pct: 0.15       # Stop at -15% from peak
  max_consecutive_losses: 5    # Stop after 5 losses

  # Recovery
  cooldown_period_minutes: 60  # Wait 1hr after circuit breaker
```

---

## Monitoring & Alerting

### Prometheus Metrics

**Key Metrics to Track**:

```python
# Counters
signals_generated_total{action, outcome}
trades_executed_total{outcome, market_type}
trades_resolved_total{outcome, result}  # result: win/loss
api_calls_total{exchange, endpoint, status}

# Gauges
open_positions_current
account_balance_usdt
daily_pnl_usdt
current_drawdown_pct
consecutive_losses_count

# Histograms
trade_pnl_usdt
signal_latency_seconds
order_execution_seconds

# Summaries
win_rate_pct
sharpe_ratio
```

### Grafana Dashboard Design

**Row 1: Overview**
- Total P&L (big number)
- Win Rate % (gauge: 0-100%)
- Active Positions (number)
- Daily P&L (number with trend)

**Row 2: Performance**
- Cumulative P&L over time (line chart)
- Daily P&L (bar chart)
- Drawdown from peak (filled area chart)
- Win/Loss distribution (pie chart)

**Row 3: Trading Activity**
- Signals per hour (bar chart by action)
- Trades executed (time series)
- Average trade size (line chart)
- Position holding time (histogram)

**Row 4: Signal Quality**
- Expected Value distribution (histogram)
- Confidence score distribution (histogram)
- Momentum magnitude vs Win Rate (scatter plot)
- Signal-to-execution latency (heatmap)

**Row 5: System Health**
- API call rates by exchange (multi-line chart)
- Error rates by component (stacked area)
- CPU/Memory usage (line charts)
- WebSocket connection status (status indicators)

**Row 6: Risk Metrics**
- Exposure % (gauge)
- Consecutive losses (number)
- Largest losing trade (number)
- Kelly fraction used (histogram)

### Alert Rules

**Critical Alerts** (Immediate notification to all channels):
- Daily loss limit exceeded (> -5%)
- Max drawdown exceeded (> 15%)
- Database connection lost
- Polymarket API authentication failed

**High Priority Alerts** (Discord + Telegram):
- 5 consecutive losses
- High API error rate (>10% for 5 min)
- WebSocket disconnected
- Insufficient account balance

**Warning Alerts** (Discord only):
- No trades executed in 30 minutes (during market hours)
- Unusual slippage detected
- Low liquidity on target market

**Info Alerts** (Log only):
- New market discovered
- Signal generated (SKIP)
- Position opened/closed

### Notification Channels

```python
class AlertManager:
    async def send_alert(self, severity, message, data):
        if severity == "CRITICAL":
            await self._send_discord(message, color="red")
            await self._send_telegram(message)
            await self._send_email(message)
        elif severity == "HIGH":
            await self._send_discord(message, color="orange")
            await self._send_telegram(message)
        elif severity == "WARNING":
            await self._send_discord(message, color="yellow")

        await self._log_to_db(severity, message, data)
```

### Daily Summary Report

**Sent every day at midnight**:

```
📊 Daily Trading Summary

Date: 2026-01-14
P&L: $+127.50
Trades: 18 (13W / 5L)
Win Rate: 72.2%
Avg Trade: $+7.08

Best Trade: $+35.20
Worst Trade: $-18.40

Current Balance: $10,127.50
Current Drawdown: 0.0%
Peak Balance: $10,127.50

Signals Generated: 45
  - EXECUTE: 18 (40%)
  - SKIP: 22 (49%)
  - WAIT: 5 (11%)

System Health: ✅ All systems operational
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Deliverables**:
- [ ] Project structure initialized
- [ ] Docker Compose environment setup
- [ ] PostgreSQL + TimescaleDB + Redis running
- [ ] Database schema created
- [ ] SQLAlchemy models defined
- [ ] Alembic migrations configured
- [ ] Basic logging and config management

**Files to Create**:
- `docker-compose.yml`
- `requirements.txt` or `pyproject.toml`
- `src/database/models.py`
- `src/database/migrations/`
- `src/config/settings.py`
- `.env.example`

### Phase 2: Data Collection (Week 2-3)

**Deliverables**:
- [ ] Polymarket CLOB client wrapper
- [ ] Binance client (ccxt + WebSocket)
- [ ] Coinbase client (ccxt + WebSocket)
- [ ] Price aggregator service
- [ ] Market discovery service
- [ ] Data storage to TimescaleDB
- [ ] Rate limiting implemented

**Files to Create**:
- `src/clients/polymarket.py`
- `src/clients/binance.py`
- `src/clients/coinbase.py`
- `src/clients/price_aggregator.py`
- `src/services/market_discovery.py`
- `src/services/price_monitor.py`

**Testing**:
- Verify WebSocket connections stay alive
- Confirm price data is being stored
- Test rate limiting behavior

### Phase 3: Core Trading Logic (Week 3-4)

**Deliverables**:
- [ ] Signal generator implementation
- [ ] Momentum calculation algorithm
- [ ] Probability model (initial version)
- [ ] Expected value calculation
- [ ] Risk manager with Kelly sizing
- [ ] Circuit breakers
- [ ] Trade executor
- [ ] Position manager

**Files to Create**:
- `src/services/signal_generator.py`
- `src/services/risk_manager.py`
- `src/services/trade_executor.py`
- `src/services/position_manager.py`
- `src/config/risk_params.yaml`

**Testing**:
- Unit tests for momentum calculation
- Test position sizing with various scenarios
- Verify circuit breakers trigger correctly

### Phase 4: Backtesting (Week 4-5)

**Deliverables**:
- [ ] Historical data collection scripts
- [ ] Backtest engine implementation
- [ ] Parameter optimization framework
- [ ] Performance metrics calculation
- [ ] Probability model calibration
- [ ] Strategy validation report

**Files to Create**:
- `src/backtesting/backtest_engine.py`
- `src/backtesting/data_loader.py`
- `src/backtesting/optimizer.py`
- `scripts/collect_historical_data.py`
- `scripts/run_backtest.py`

**Critical Tasks**:
- Collect 6+ months of historical data
- Backtest with various parameter sets
- Calculate Sharpe ratio, max drawdown, win rate
- **Validate that edge still exists**
- Optimize entry timing, thresholds, position sizing

### Phase 5: Monitoring & Paper Trading (Week 5-6)

**Deliverables**:
- [ ] Prometheus metrics integration
- [ ] Grafana dashboards configured
- [ ] Alertmanager rules defined
- [ ] Discord/Telegram webhooks
- [ ] Dry-run mode (paper trading)
- [ ] Performance tracking
- [ ] API endpoint for status checks

**Files to Create**:
- `src/monitoring/metrics.py`
- `src/monitoring/alerts.py`
- `src/api/main.py`
- `infrastructure/monitoring/prometheus.yml`
- `infrastructure/monitoring/grafana_dashboards/`

**Testing**:
- Run paper trading for 2+ weeks
- Monitor for edge degradation
- Validate risk controls work as expected
- Compare paper results to backtest

### Phase 6: Production Deployment (Week 6+)

**Deliverables**:
- [ ] Small capital test ($500-1000)
- [ ] Real-money validation (1-2 weeks)
- [ ] Gradual capital scaling
- [ ] Continuous monitoring
- [ ] Model retraining pipeline
- [ ] Documentation for students

**Critical Milestones**:
- Week 6-7: Deploy with $500, monitor closely
- Week 8-9: If positive, scale to $2,000
- Week 10+: If still profitable, scale to $10,000
- Ongoing: Retrain models monthly, monitor edge

**Red Flags to Watch**:
- Win rate drops below 55%
- Average EV per trade drops below 5%
- Execution latency increases significantly
- Polymarket introduces new fee structures

---

## Project Structure

```
polymarket-arbitrage-bot/
├── README.md
├── MASTER_PLAN.md                # This document
├── docker-compose.yml
├── requirements.txt              # or pyproject.toml
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py           # Configuration management
│   │   └── risk_params.yaml      # Risk parameters
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── polymarket.py         # Polymarket CLOB client
│   │   ├── binance.py            # Binance client
│   │   ├── coinbase.py           # Coinbase client
│   │   └── price_aggregator.py   # Multi-exchange aggregator
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── repository.py         # Data access layer
│   │   └── migrations/           # Alembic migrations
│   │       ├── env.py
│   │       └── versions/
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── market_discovery.py   # Find tradeable markets
│   │   ├── price_monitor.py      # Track spot prices
│   │   ├── signal_generator.py   # Generate trading signals
│   │   ├── risk_manager.py       # Risk management
│   │   ├── trade_executor.py     # Execute trades
│   │   └── position_manager.py   # Track positions
│   │
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── backtest_engine.py    # Backtesting framework
│   │   ├── data_loader.py        # Historical data
│   │   └── optimizer.py          # Parameter optimization
│   │
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── metrics.py            # Prometheus metrics
│   │   ├── alerts.py             # Alert manager
│   │   └── logger.py             # Structured logging
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── routes/               # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── status.py
│   │   │   ├── trades.py
│   │   │   └── metrics.py
│   │   └── websocket.py          # Real-time updates
│   │
│   └── orchestrator.py           # Main coordination loop
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_signal_generator.py
│   │   ├── test_risk_manager.py
│   │   └── test_momentum_calculation.py
│   ├── integration/
│   │   ├── test_api_clients.py
│   │   └── test_database.py
│   └── e2e/
│       └── test_full_trade_flow.py
│
├── scripts/
│   ├── setup_database.py
│   ├── collect_historical_data.py
│   ├── run_backtest.py
│   └── deploy.sh
│
├── notebooks/
│   ├── exploratory_analysis.ipynb
│   ├── strategy_research.ipynb
│   └── model_calibration.ipynb
│
├── infrastructure/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── kubernetes/               # For production
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── monitoring/
│       ├── prometheus.yml
│       ├── alertmanager.yml
│       └── grafana_dashboards/
│           ├── overview.json
│           ├── performance.json
│           └── system_health.json
│
└── docs/
    ├── architecture.md
    ├── strategy.md
    ├── api_reference.md
    └── deployment_guide.md
```

---

## Key Considerations

### 1. Edge Validation - CRITICAL

**⚠️ The most important task: Validate the edge exists**

- The strategy assumes Polymarket lags CEX spot prices
- This may be crowded (many bots already exploit this)
- Polymarket recently introduced dynamic fees to combat latency arbitrage
- **You MUST backtest with recent data (last 3-6 months) to confirm edge**

**Action Items**:
- [ ] Collect historical Polymarket 15-min BTC market data
- [ ] Collect corresponding Binance/Coinbase spot price data
- [ ] Simulate the strategy with realistic execution delays
- [ ] Calculate historical win rate, average EV, Sharpe ratio
- [ ] Determine if edge > transaction costs

**Red Flags**:
- Historical win rate < 55%
- Average EV per trade < 5%
- Edge has declined significantly in recent months
- Polymarket fees + slippage eat all profits

### 2. Execution Speed Matters

**Latency arbitrage is a speed game**

- Every millisecond counts when exploiting pricing lags
- Consider VPS/cloud server close to exchange data centers
- Use WebSocket connections, not REST polling
- Optimize order placement code path
- Monitor execution latency continuously

**Recommendations**:
- Deploy to AWS us-east-1 or similar low-latency region
- Use async I/O throughout the stack
- Pre-warm connections to APIs
- Consider using Polymarket's WebSocket for instant orderbook updates

### 3. Transaction Costs - Factor Into Every Decision

**Costs that erode edge**:
- Polymarket: 2% fee on profits
- Blockchain gas fees (if settling on-chain)
- Slippage in thin markets
- Opportunity cost of capital

**Example**:
```
Trade size: $100
Entry price: $0.60
Win: $100 / $0.60 = 166.67 shares × $1.00 = $166.67
Profit: $166.67 - $100 = $66.67
Fee (2%): $66.67 × 0.02 = $1.33
Net profit: $65.34

Loss: Lose entire $100

For breakeven: Need win rate > 60.6%
```

### 4. Parameter Calibration - Use Real Data

**DO NOT use the example parameters blindly**

The momentum-to-probability model needs real calibration:
- Collect 1000+ historical market outcomes
- Train a logistic regression or gradient boosting model
- Features: momentum magnitude, consistency (R²), volatility, time-of-day
- Target: binary outcome (UP/DOWN)
- Cross-validate to prevent overfitting
- Retrain monthly as market dynamics change

**Tunable Parameters**:
| Parameter | Requires Backtesting | Impact |
|-----------|---------------------|--------|
| Entry timing (3-5 min) | ✅ Yes | Win rate, edge decay |
| Min momentum threshold | ✅ Yes | Trade frequency, win rate |
| Min EV threshold | ✅ Yes | Trade frequency, profitability |
| Position sizing | ✅ Yes | Risk, drawdown, Kelly fraction |
| Circuit breaker thresholds | ⚠️ Moderate | Risk control vs opportunity cost |

### 5. Market Dynamics - Expect Changes

**The market will adapt**:
- More bots enter → faster price discovery → edge shrinks
- Polymarket may adjust fees or introduce latency penalties
- Liquidity may dry up during volatile periods
- Regulatory changes could impact operations

**Adaptation Strategy**:
- Monitor key metrics weekly (win rate, EV, latency)
- Set up alerts for edge degradation
- Be prepared to pivot strategy or shut down
- Explore other markets (ETH, SOL, index futures)
- Consider providing liquidity instead of taking it

### 6. Educational Goals - Share Knowledge

**This is a learning project**:
- Document every decision and outcome
- Explain the math behind Kelly Criterion, EV calculation
- Share code with clear comments
- Create case studies of winning and losing trades
- Discuss when to stop trading (if edge disappears)

**Student Learning Outcomes**:
- Understanding market microstructure
- Quantitative trading strategy development
- Risk management in practice
- API integration and system design
- Real-time data processing
- The importance of backtesting and validation

### 7. Risk Management - Non-Negotiable

**Educational does not mean reckless**:
- Start with paper trading (2+ weeks minimum)
- Use small capital initially ($500 max)
- Respect circuit breakers - never override them
- Never increase position sizes after losses
- Accept when the edge is gone and shut down gracefully

**Mental Model**:
> "We're not trying to get rich. We're trying to learn if this edge exists, how to exploit it systematically, and when to stop."

### 8. Legal and Regulatory Considerations

**Before deploying with real money**:
- Verify Polymarket is legal in your jurisdiction
- Understand tax implications of prediction market profits
- Comply with any KYC/AML requirements
- Consider forming an educational entity/club for group trading
- Consult with a lawyer if trading with student funds

### 9. Technical Debt - Start Clean

**Best practices from day one**:
- Write tests for critical logic (momentum calc, position sizing)
- Use type hints throughout Python code
- Document API client methods
- Version control everything (Git)
- Keep secrets out of code (use .env files)
- Set up CI/CD for automated testing

### 10. Exit Criteria - Know When to Stop

**Stop trading if**:
- Win rate drops below 52% for 2 consecutive weeks
- Average EV per trade < 5% for 1 month
- Circuit breakers trigger more than 3 times per week
- Polymarket changes fee structure unfavorably
- You can't explain why trades are winning/losing
- You're no longer learning anything new

---

## Probability of Success

### Bottom-Line Assessment (Qualitative)

**Current probability of achieving sustained profitability after full costs**: **Low to Medium (20-40%)**

**Why not higher**:
- This edge is widely known; competition compresses pricing quickly.
- Polymarket fees and dynamic fee changes directly target latency arbitrage.
- Execution latency, partial fills, and thin liquidity can erase small edges.
- 15-minute markets are noisy; short-term momentum can mean-revert fast.

**Why not lower**:
- Spot price movement does contain short-term persistence during high momentum.
- Many retail Polymarket participants still price based on intuition rather than microstructure.
- A disciplined system with strict filters may find occasional high-EV opportunities.

### Key Success Drivers (Ranked)

1. **Realistic backtest + paper trading results** that show edge survives fees/slippage.
2. **Execution speed and reliability** (order placement latency, orderbook freshness).
3. **Liquidity-aware trade sizing** that avoids moving the market.
4. **Calibration of the momentum → win probability model** using recent data only.
5. **Monitoring edge decay** and stopping quickly when it degrades.

### Failure Modes to Plan Around

- **False edge**: backtest overstates performance due to data leakage or survivorship bias.
- **Latency mismatch**: price feed shows momentum, but order placement hits stale pricing.
- **Liquidity traps**: best ask is tiny; real fill price is worse than expected.
- **Dynamic fee changes**: Polymarket fee increases reduce net EV to negative.
- **Regime shifts**: volatility spikes or flat periods break momentum assumptions.

### Go / No-Go Gates (Objective)

**Go** only if all are true after paper trading:
- Net win rate (after fees/slippage) ≥ 58% over 300+ trades.
- Average net EV per trade ≥ 5%.
- Max drawdown ≤ 12%.
- Order execution success ≥ 98% with median latency < 2 seconds.

**No-Go** if any are true:
- Win rate < 55% for 3 consecutive weeks.
- Average net EV < 3% for 1 month.
- Slippage > 1.5x modeled slippage for 2 weeks.

---

## Plan Upgrades

### 1) Data & Backtesting Upgrades (Critical)

- **Use tick-level data alignment**: Match Polymarket orderbook snapshots with exchange ticks by timestamp, not just minute bars.
- **Model execution realistically**: Use best-ask/bid sizes, partial fills, and a slippage model.
- **Include dynamic fees**: Encode Polymarket fee schedule historically, or test ranges.
- **Holdout evaluation**: 60/20/20 split (train/validate/test) by time, not random.
- **Walk-forward testing**: Monthly rolling retrain + evaluate the next month.

### 2) Signal Model Improvements

- **Feature expansion** (low complexity first): 
  - Momentum slope, volatility, range compression, orderbook imbalance, time-of-day.
  - Cross-exchange divergence (Binance vs Coinbase) as a shock indicator.
- **Probability calibration**:
  - Use Platt scaling or isotonic regression to calibrate outputs.
  - Track calibration drift weekly.
- **Confidence gating**:
  - Trade only when model confidence is in top X percentile for that day.

### 3) Execution & Infrastructure Upgrades

- **Event-driven order placement**: Trigger by orderbook update, not polling.
- **Latency telemetry**: Measure end-to-end latency (signal → order accepted → fill).
- **Smart order sizing**:
  - Cap by visible liquidity at best price to reduce slippage.
  - Split orders if market depth supports it.
- **Resilience**:
  - Automatic failover between data sources.
  - Graceful degradation if a data feed drops.

### 4) Risk & Capital Controls

- **Volatility-based position scaling**: Reduce size when short-term volatility spikes.
- **Trade frequency governor**: Max trades per hour to prevent overtrading.
- **Profit lockout**: After a large winning streak, reduce size for the next N trades.

### 5) Market Selection Expansion (Optional)

- Test additional markets with similar structure (ETH 15-min, top altcoins).
- Only expand once BTC strategy is positive for 6+ weeks.
- Keep separate models per asset to avoid mixing regimes.

### 6) Operational Safety & Compliance

- **Legal check** per jurisdiction before live trading.
- **Account hygiene**: Rotate API keys, enforce IP allowlisting.
- **Incident runbook**: Document steps for outages, API bans, or abnormal fills.

---

## Success Metrics

### Performance Metrics

| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| Win Rate | > 65% | > 55% |
| Average EV per Trade | > 10% | > 5% |
| Sharpe Ratio | > 2.0 | > 1.0 |
| Max Drawdown | < 10% | < 15% |
| Daily Trade Count | 10-20 | 5-30 |
| Execution Latency | < 2 sec | < 5 sec |

### System Health Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| API Error Rate | < 1% | > 5% |
| WebSocket Uptime | > 99.5% | < 95% |
| Database Query Time | < 100ms | > 500ms |
| Signal Generation Latency | < 1 sec | > 5 sec |

### Learning Metrics (Educational Value)

- Number of students actively monitoring the bot
- Quality of questions and discussions generated
- Understanding of key concepts (Kelly, EV, backtesting)
- Ability of students to explain strategy to others
- Student-generated improvements or variations

---

## Conclusion

This master plan provides a comprehensive blueprint for building a Polymarket crypto arbitrage bot. The strategy exploits temporal information asymmetry between CEX spot markets and Polymarket's prediction markets.

**Critical Success Factors**:

1. **Validate the edge exists** through rigorous backtesting
2. **Optimize for speed** - latency arbitrage requires fast execution
3. **Factor in all costs** - fees and slippage matter
4. **Calibrate parameters** using real historical data
5. **Respect risk limits** - circuit breakers are non-negotiable
6. **Monitor continuously** - edges can disappear quickly
7. **Focus on learning** - knowledge > profits for this project

**Next Steps**:

1. Review and approve this plan
2. Set up development environment (Phase 1)
3. Begin API client implementation (Phase 2)
4. Start collecting historical data in parallel
5. Implement core trading logic (Phase 3)
6. **Critical: Backtest to validate edge (Phase 4)**
7. Paper trade to verify strategy (Phase 5)
8. Cautiously deploy with small capital (Phase 6)

**Remember**: This is an educational project. The goal is to learn about quantitative trading, market microstructure, and systematic strategy development. If the edge doesn't exist or disappears, that's a valuable learning experience too.

---

**Document Version**: 1.0
**Last Updated**: 2026-01-14
**Status**: Planning Phase
**Next Review**: After Phase 4 (Backtesting Results)
