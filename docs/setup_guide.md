# Setup Guide - Polymarket Arbitrage Bot

## Phase 1: Foundation Setup ✅

This guide will help you set up the development environment for the Polymarket arbitrage bot.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git
- 8GB+ RAM recommended

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/himandy302/ff2gether.git
cd ff2gether
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Configure Environment

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

**Important**: Edit `.env` and set at least these values:
- `POSTGRES_PASSWORD` - Change from default
- `REDIS_PASSWORD` - Change from default
- `POLYMARKET_API_KEY` - Your Polymarket API key (for production)
- `POLYMARKET_PRIVATE_KEY` - Your Ethereum private key (for production)

### 5. Start Infrastructure Services

Start PostgreSQL, Redis, Prometheus, and Grafana:

```bash
docker-compose up -d
```

Verify services are running:

```bash
docker-compose ps
```

You should see:
- ✅ `polymarket-db` (PostgreSQL + TimescaleDB)
- ✅ `polymarket-redis` (Redis)
- ✅ `polymarket-prometheus` (Prometheus)
- ✅ `polymarket-grafana` (Grafana)

### 6. Run Database Migrations

```bash
alembic upgrade head
```

This will create all tables and TimescaleDB hypertables.

### 7. Verify Setup

Check database connection:

```bash
python -c "from src.database.connection import db_manager; import asyncio; asyncio.run(db_manager.initialize()); print('✅ Database connected')"
```

## Access Services

### PostgreSQL
- **Host**: localhost:5432
- **Database**: polymarket_trading
- **Username**: polymarket
- **Password**: (from .env)

Connect with psql:
```bash
psql -h localhost -U polymarket -d polymarket_trading
```

### Redis
- **Host**: localhost:6379
- **Password**: (from .env)

Test connection:
```bash
redis-cli -a <your-password> ping
```

### Prometheus
- **URL**: http://localhost:9090
- Monitor system metrics and trading performance

### Grafana
- **URL**: http://localhost:3000
- **Default credentials**: admin / admin
- Import dashboards from `infrastructure/monitoring/grafana_dashboards/`

## Development Workflow

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/
```

### Database Migrations

Create a new migration after modifying models:

```bash
alembic revision --autogenerate -m "description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback last migration:

```bash
alembic downgrade -1
```

## Project Structure

```
ff2gether/
├── src/
│   ├── config/          # Configuration management
│   ├── clients/         # API clients (Polymarket, Binance, Coinbase)
│   ├── database/        # Models, migrations, connections
│   ├── services/        # Core business logic
│   ├── backtesting/     # Backtesting engine
│   ├── monitoring/      # Logging, metrics, alerts
│   └── api/             # FastAPI endpoints
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── notebooks/           # Jupyter notebooks for analysis
├── infrastructure/      # Docker, K8s, monitoring configs
└── docs/                # Documentation
```

## Next Steps

Now that Phase 1 is complete, proceed to:

1. **Phase 2**: Data Collection
   - Implement Polymarket CLOB client
   - Setup WebSocket connections to Binance/Coinbase
   - Store real-time price data

2. **Phase 3**: Core Trading Logic
   - Signal generation
   - Risk management
   - Trade execution

3. **Phase 4**: Backtesting (CRITICAL)
   - Collect historical data
   - Validate edge exists
   - Optimize parameters

See [MASTER_PLAN.md](../MASTER_PLAN.md) for the complete roadmap.

## Troubleshooting

### Docker services won't start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Clean restart
docker-compose down && docker-compose up -d
```

### Database connection errors

1. Ensure PostgreSQL is running: `docker-compose ps`
2. Check credentials in `.env` match `docker-compose.yml`
3. Test connection: `psql -h localhost -U polymarket -d polymarket_trading`

### Import errors

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

## Resources

- [Master Plan](../MASTER_PLAN.md) - Complete project roadmap
- [README](../README.md) - Project overview
- [Polymarket Docs](https://docs.polymarket.com)
- [TimescaleDB Docs](https://docs.timescale.com)

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/himandy302/ff2gether/issues)
- Check existing issues for solutions
- Review the MASTER_PLAN.md for detailed architecture

---

**Status**: Phase 1 Complete ✅
**Next**: Phase 2 - Data Collection
**Last Updated**: 2026-01-14
