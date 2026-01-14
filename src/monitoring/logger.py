"""
Structured logging configuration using structlog.

Provides JSON-formatted logs for production and human-readable logs for development.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

from src.config.settings import settings


def add_log_level(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dictionary."""
    event_dict["level"] = method_name.upper()
    return event_dict


def add_timestamp(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO timestamp to event dictionary."""
    import datetime
    event_dict["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    return event_dict


def censor_sensitive_data(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Censor sensitive information in logs."""
    sensitive_keys = [
        "password",
        "api_key",
        "secret",
        "private_key",
        "token",
        "authorization",
    ]

    def _censor_dict(d: dict) -> dict:
        """Recursively censor sensitive keys."""
        censored = {}
        for key, value in d.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                censored[key] = "***REDACTED***"
            elif isinstance(value, dict):
                censored[key] = _censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [
                    _censor_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                censored[key] = value
        return censored

    return _censor_dict(event_dict)


def configure_logging():
    """Configure structured logging for the application."""

    # Determine if we're in production
    is_production = settings.ENVIRONMENT == "production"

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )

    # Configure structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        add_log_level,
        add_timestamp,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        censor_sensitive_data,
    ]

    if is_production:
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Human-readable output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Usage:
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, ip_address="1.2.3.4")
        logger.error("trade_failed", market_id="abc", error="Insufficient funds")
    """
    return structlog.get_logger(name)


# Application-specific loggers

def log_trade(
    logger: structlog.stdlib.BoundLogger,
    action: str,
    market_id: str,
    outcome: str,
    **kwargs: Any
):
    """
    Log trading activity with consistent format.

    Args:
        logger: Structlog logger instance
        action: Trade action (e.g., "order_placed", "trade_filled")
        market_id: Polymarket market ID
        outcome: YES or NO
        **kwargs: Additional context (price, quantity, etc.)
    """
    logger.info(
        action,
        event_type="trading",
        market_id=market_id,
        outcome=outcome,
        **kwargs
    )


def log_signal(
    logger: structlog.stdlib.BoundLogger,
    action: str,
    market_id: str,
    **kwargs: Any
):
    """
    Log signal generation with consistent format.

    Args:
        logger: Structlog logger instance
        action: Signal action (e.g., "signal_generated", "signal_skipped")
        market_id: Polymarket market ID
        **kwargs: Signal details (ev, confidence, momentum, etc.)
    """
    logger.info(
        action,
        event_type="signal",
        market_id=market_id,
        **kwargs
    )


def log_system_event(
    logger: structlog.stdlib.BoundLogger,
    event_type: str,
    component: str,
    message: str,
    **kwargs: Any
):
    """
    Log system events with consistent format.

    Args:
        logger: Structlog logger instance
        event_type: Event type (e.g., "error", "warning", "info")
        component: System component (e.g., "price_monitor", "risk_manager")
        message: Event description
        **kwargs: Additional context
    """
    log_method = getattr(logger, event_type.lower(), logger.info)
    log_method(
        message,
        event_type="system",
        component=component,
        **kwargs
    )


def log_performance_metric(
    logger: structlog.stdlib.BoundLogger,
    metric_name: str,
    value: float,
    **kwargs: Any
):
    """
    Log performance metrics.

    Args:
        logger: Structlog logger instance
        metric_name: Metric name (e.g., "win_rate", "daily_pnl")
        value: Metric value
        **kwargs: Additional context
    """
    logger.info(
        "performance_metric",
        event_type="metric",
        metric_name=metric_name,
        value=value,
        **kwargs
    )


# Initialize logging on module import
configure_logging()
