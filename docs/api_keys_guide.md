# API Keys Setup Guide

## Overview

This guide explains what API keys you need and when you need them for the Polymarket arbitrage bot.

## Quick Answer: What Do I Need NOW?

**For Phase 2 (Data Collection & Testing)**: ✅ **NOTHING!**

You can start development and testing **without any API keys** because:
- Bybit and Coinbase provide **public market data** without authentication
- We'll use **paper trading mode** initially
- Real trading requires keys, but that's Phase 6 (weeks away)

---

## API Keys Breakdown

### 1. **Bybit API** - For BTC Spot Price Data

**Status**: ⚠️ Optional (Public data doesn't require keys)

**What it's for**:
- Real-time BTC spot price via WebSocket
- Historical OHLCV data for momentum calculation
- Market data aggregation

**Do I need it NOW?**
- ❌ **NO** - Public endpoints work without authentication
- ✅ **Later** - Only needed if you hit rate limits or want private account data

**How to get it** (when needed):
1. Go to https://www.bybit.com/app/user/api-management
2. Create API key with **Read-Only** permissions
3. Add to `.env`:
   ```
   BYBIT_API_KEY=your_api_key_here
   BYBIT_API_SECRET=your_api_secret_here
   ```

**Cost**: Free

---

### 2. **Coinbase API** - For Price Confirmation

**Status**: ⚠️ Optional (Public data doesn't require keys)

**What it's for**:
- Confirming BTC prices across multiple exchanges
- Reducing single-exchange risk
- Consensus price calculation

**Do I need it NOW?**
- ❌ **NO** - Public market data is free
- ✅ **Later** - Only for higher rate limits

**How to get it** (when needed):
1. Go to https://www.coinbase.com/settings/api
2. Create API key
3. Add to `.env`

**Cost**: Free

---

### 3. **Polymarket API** - For Real Trading

**Status**: 🔴 **REQUIRED for real trading** (Phase 6)

**What it's for**:
- Placing orders on Polymarket
- Reading your positions
- Executing trades

**Do I need it NOW?**
- ❌ **NO** - Not needed until Phase 6 (production deployment)
- ✅ **Phase 4-5** - For paper trading and backtesting
- 🔴 **Phase 6** - REQUIRED for real money trading

**How to get it**:
1. **Polymarket Account**:
   - Go to https://polymarket.com
   - Create account
   - Complete KYC (if required)

2. **Get API Credentials**:
   - Access Polymarket CLOB API documentation
   - Generate API key
   - **Important**: You also need an Ethereum private key (wallet) for signing transactions

3. **Setup Polygon Network**:
   - Polymarket runs on Polygon (MATIC)
   - Fund wallet with USDC on Polygon network
   - Bridge funds if needed: https://wallet.polygon.technology/

4. **Add to `.env`**:
   ```
   POLYMARKET_API_KEY=your_api_key
   POLYMARKET_PRIVATE_KEY=your_ethereum_private_key  # KEEP SECRET!
   POLYMARKET_CHAIN_ID=137  # Polygon mainnet
   ```

**Cost**:
- Account: Free
- Trading fees: 2% on profits
- Gas fees: Minimal on Polygon

**⚠️ Security Warning**:
- NEVER commit your private key to Git
- Use a separate wallet for trading bot
- Start with small amounts ($100-500)

---

## Timeline: When You Need Each Key

| Phase | What You're Doing | Keys Needed |
|-------|-------------------|-------------|
| **Phase 1** ✅ (Now) | Infrastructure setup | None |
| **Phase 2** (Next) | Data collection, WebSockets | **None** (public data) |
| **Phase 3** | Trading logic, signals | **None** (testing only) |
| **Phase 4** | Backtesting | **None** (historical data) |
| **Phase 5** | Paper trading | Polymarket (testnet or dry-run) |
| **Phase 6** | Real trading | **All keys** (Polymarket required) |

---

## What To Do NOW

### Immediate Next Steps (No API Keys Needed!)

1. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Start developing Phase 2**:
   - I'll create Bybit client for public WebSocket data
   - I'll create Coinbase client for public REST data
   - No authentication required!

3. **Test with paper trading mode**:
   - Already enabled in `.env`: `DRY_RUN_MODE=true`
   - Bot will simulate trades without real money
   - Perfect for development and testing

### Optional: Get Bybit API Key (For Higher Rate Limits)

If you want to prepare for later:

1. Create Bybit account: https://www.bybit.com/register
2. Enable API: https://www.bybit.com/app/user/api-management
3. Create **Read-Only** key (no trading permissions)
4. Add to `.env`:
   ```
   BYBIT_API_KEY=your_key
   BYBIT_API_SECRET=your_secret
   ```

---

## Bybit vs Binance

**Good news**: ccxt (the library we use) supports **both** Bybit and Binance with the same code interface!

**Why Bybit works great**:
- ✅ Full WebSocket support for real-time BTC prices
- ✅ Same data quality as Binance
- ✅ Lower fees in some cases
- ✅ Better for some regions
- ✅ Same ccxt API - just change exchange name!

**The only change needed**:
```python
# Instead of:
exchange = ccxt.binance()

# We'll use:
exchange = ccxt.bybit()
```

That's it! Everything else is identical.

---

## Security Best Practices

### When You Eventually Get API Keys:

1. **Use Read-Only Keys When Possible**
   - Bybit/Coinbase: Read-only is enough for price data
   - Only Polymarket needs write permissions

2. **Never Share Private Keys**
   - Don't commit `.env` to Git (already in `.gitignore`)
   - Don't screenshot with keys visible
   - Don't share in Discord/Telegram

3. **Use Separate Wallets**
   - Create a new Ethereum wallet just for the bot
   - Don't use your main crypto wallet
   - Start with small amounts ($100-500)

4. **Enable IP Whitelisting** (when available)
   - Restrict API keys to your server's IP
   - Adds extra security layer

5. **Rotate Keys Regularly**
   - Change API keys every 3-6 months
   - Immediately rotate if compromised

---

## FAQ

**Q: Can I start Phase 2 without any API keys?**
A: Yes! Public market data is free for both Bybit and Coinbase.

**Q: Do I need a Polymarket account now?**
A: No. Not until Phase 5 (paper trading) or Phase 6 (real trading).

**Q: How much money do I need for real trading?**
A: Start with $100-500 for testing. The master plan recommends $10,000 for full deployment, but start small!

**Q: Is Bybit as good as Binance for this strategy?**
A: Yes! Bybit has excellent WebSocket support and the same BTC price quality. Many traders prefer it.

**Q: What if I want to use both Bybit and Binance?**
A: Perfect! You can use multiple exchanges for price confirmation. Just add both to the price aggregator.

---

## Summary: Your Immediate Action Items

✅ **Required NOW**:
1. Nothing! You're ready for Phase 2.

⚠️ **Optional (Good to prepare)**:
1. Create Bybit account (free)
2. Generate read-only API key (for higher rate limits later)

🔴 **Required LATER (Phase 5-6)**:
1. Polymarket account + API key
2. Ethereum wallet with USDC on Polygon
3. Small amount of capital for testing ($100-500)

---

**Next Step**: I'll start implementing Phase 2 with Bybit public data - no keys needed!
