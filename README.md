# FF2gether - Polymarket Crypto Arbitrage Bot

An educational trading bot that exploits timing inefficiencies between crypto spot markets and Polymarket prediction markets.

## Project Status

🚧 **Planning Phase** - See [MASTER_PLAN.md](./MASTER_PLAN.md) for complete implementation details.

## Strategy Overview

This bot trades 15-minute BTC up/down markets on Polymarket by exploiting latency arbitrage:

1. Wait 3-5 minutes after market opens
2. Analyze BTC spot momentum on Binance/Coinbase
3. Compare to Polymarket pricing (which often lags)
4. Execute trades when expected value exceeds threshold
5. Hold to settlement ($1 or $0)

**Key Insight**: We don't predict the future - we "buy what already happened" before Polymarket fully adjusts.

## Technology Stack

- **Python 3.11+** - Core language
- **PostgreSQL + TimescaleDB** - Time-series data storage
- **Redis** - Caching and rate limiting
- **FastAPI** - API and monitoring endpoints
- **Prometheus + Grafana** - Metrics and dashboards
- **ccxt** - Exchange API integration
- **py-clob-client** - Polymarket CLOB API

## Documentation

- **[MASTER_PLAN.md](./MASTER_PLAN.md)** - Complete system design and implementation roadmap

## Educational Goals

This project is designed for learning:

- Quantitative trading strategy development
- Market microstructure and latency arbitrage
- Risk management (Kelly Criterion, circuit breakers)
- Real-time data processing and system design
- API integration and async programming
- Backtesting and parameter optimization

## Important Disclaimers

⚠️ **This is an educational project**
- Start with paper trading
- Use small capital for initial testing
- Edge validation through backtesting is CRITICAL
- Transaction costs and fees significantly impact profitability
- Market conditions change - continuous monitoring required

## Getting Started

See [MASTER_PLAN.md](./MASTER_PLAN.md) for:
- Complete system architecture
- Implementation roadmap (6 phases)
- Database schema
- Risk management configuration
- Deployment guide

## Current Phase

**Phase 0: Planning** ✅ Complete
- System architecture designed
- Technology stack selected
- Master plan documented

**Phase 1: Foundation** 🚧 Next
- Project structure setup
- Docker environment configuration
- Database initialization

## License

This project is for educational purposes only.

## Contributing

This is a learning project. Contributions, questions, and discussions are welcome!

## Contact

For questions or collaboration: [GitHub Issues](https://github.com/himandy302/ff2gether/issues)
