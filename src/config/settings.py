"""
Application configuration management using Pydantic settings.

Loads configuration from environment variables and .env file.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================
    # Database Configuration
    # ==========================================
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="polymarket")
    POSTGRES_PASSWORD: str = Field(default="polymarket_password")
    POSTGRES_DB: str = Field(default="polymarket_trading")
    DATABASE_URL: Optional[str] = Field(default=None)
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: Optional[str], info) -> str:
        """Construct DATABASE_URL if not provided."""
        if v:
            return v
        return (
            f"postgresql+asyncpg://{info.data['POSTGRES_USER']}:"
            f"{info.data['POSTGRES_PASSWORD']}@{info.data['POSTGRES_HOST']}:"
            f"{info.data['POSTGRES_PORT']}/{info.data['POSTGRES_DB']}"
        )

    # ==========================================
    # Redis Configuration
    # ==========================================
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="redis_password")
    REDIS_URL: Optional[str] = Field(default=None)
    REDIS_MAX_CONNECTIONS: int = Field(default=50)

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info) -> str:
        """Construct REDIS_URL if not provided."""
        if v:
            return v
        return (
            f"redis://:{info.data['REDIS_PASSWORD']}@"
            f"{info.data['REDIS_HOST']}:{info.data['REDIS_PORT']}/0"
        )

    # ==========================================
    # Polymarket API
    # ==========================================
    POLYMARKET_API_KEY: str = Field(default="")
    POLYMARKET_PRIVATE_KEY: str = Field(default="")
    POLYMARKET_CHAIN_ID: int = Field(default=137)  # Polygon mainnet
    POLYMARKET_CLOB_API_URL: str = Field(default="https://clob.polymarket.com")

    # ==========================================
    # Exchange APIs
    # ==========================================
    BINANCE_API_KEY: str = Field(default="")
    BINANCE_API_SECRET: str = Field(default="")
    COINBASE_API_KEY: str = Field(default="")
    COINBASE_API_SECRET: str = Field(default="")

    # ==========================================
    # Risk Management
    # ==========================================
    INITIAL_CAPITAL: float = Field(default=10000.0)
    MAX_POSITION_SIZE_PCT: float = Field(default=0.02)  # 2%
    MAX_POSITION_SIZE_ABS: float = Field(default=200.0)  # $200
    MAX_CONCURRENT_POSITIONS: int = Field(default=5)
    MAX_EXPOSURE_PCT: float = Field(default=0.20)  # 20%
    MAX_DAILY_LOSS_PCT: float = Field(default=0.05)  # 5%
    MAX_DRAWDOWN_PCT: float = Field(default=0.15)  # 15%
    MAX_CONSECUTIVE_LOSSES: int = Field(default=5)
    KELLY_MULTIPLIER: float = Field(default=0.25)  # 1/4 Kelly

    # ==========================================
    # Trading Strategy
    # ==========================================
    ENTRY_DELAY_MIN: int = Field(default=3)  # minutes
    ENTRY_DELAY_MAX: int = Field(default=5)  # minutes
    MIN_MOMENTUM_THRESHOLD: float = Field(default=0.003)  # 0.3%
    MIN_EDGE_THRESHOLD: float = Field(default=0.15)  # 15%
    MOMENTUM_CONSISTENCY_THRESHOLD: float = Field(default=0.70)  # R² score
    MIN_LIQUIDITY: float = Field(default=100.0)  # $100

    # ==========================================
    # Monitoring & Alerting
    # ==========================================
    PROMETHEUS_PORT: int = Field(default=9090)
    GRAFANA_PORT: int = Field(default=3000)
    GRAFANA_USER: str = Field(default="admin")
    GRAFANA_PASSWORD: str = Field(default="admin")
    DISCORD_WEBHOOK_URL: str = Field(default="")
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    TELEGRAM_CHAT_ID: str = Field(default="")

    # ==========================================
    # Application Settings
    # ==========================================
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    DRY_RUN_MODE: bool = Field(default=True)
    API_PORT: int = Field(default=8000)

    # ==========================================
    # GitHub
    # ==========================================
    GITHUB_TOKEN: str = Field(default="")

    # ==========================================
    # Feature Flags
    # ==========================================
    ENABLE_PAPER_TRADING: bool = Field(default=True)
    ENABLE_BACKTESTING: bool = Field(default=True)
    ENABLE_TELEGRAM_ALERTS: bool = Field(default=False)
    ENABLE_DISCORD_ALERTS: bool = Field(default=False)
    ENABLE_PROMETHEUS_METRICS: bool = Field(default=True)

    # ==========================================
    # Performance Tuning
    # ==========================================
    WEBSOCKET_RECONNECT_DELAY: int = Field(default=5)  # seconds
    API_RATE_LIMIT_PER_SECOND: int = Field(default=10)

    # ==========================================
    # Validators
    # ==========================================

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v_upper

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v_lower

    # ==========================================
    # Helper Methods
    # ==========================================

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def should_trade_real_money(self) -> bool:
        """Check if bot should trade with real money."""
        return not self.DRY_RUN_MODE and self.is_production()


# Global settings instance
settings = Settings()
