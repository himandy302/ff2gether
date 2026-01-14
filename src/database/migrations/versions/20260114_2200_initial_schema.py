"""Initial schema with TimescaleDB hypertables

Revision ID: 001_initial
Revises:
Create Date: 2026-01-14 22:00:00

Creates all tables from the master plan including:
- markets, market_data, polymarket_orderbook (time-series)
- signals, orders, trades, positions
- account_balance, system_events, performance_metrics

Enables TimescaleDB extension and creates hypertables for time-series data.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    # ==========================================
    # Markets table
    # ==========================================
    op.create_table(
        'markets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('market_id', sa.String(length=100), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('market_type', sa.String(length=50)),
        sa.Column('open_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('close_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolution_time', sa.DateTime(timezone=True)),
        sa.Column('status', sa.String(length=20)),
        sa.Column('winning_outcome', sa.String(length=10)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('market_id')
    )
    op.create_index('idx_markets_status', 'markets', ['status'])
    op.create_index('idx_markets_open_time', 'markets', ['open_time'])
    op.create_index(op.f('ix_markets_market_id'), 'markets', ['market_id'])

    # ==========================================
    # Market Data (time-series)
    # ==========================================
    op.create_table(
        'market_data',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('exchange', sa.String(length=20), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('volume', sa.Numeric(precision=20, scale=8)),
        sa.PrimaryKeyConstraint('time', 'exchange', 'symbol')
    )
    op.create_index('idx_market_data_time_exchange', 'market_data', ['time', 'exchange'])

    # Convert to hypertable
    op.execute("""
        SELECT create_hypertable('market_data', 'time',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
    """)

    # ==========================================
    # Polymarket Orderbook (time-series)
    # ==========================================
    op.create_table(
        'polymarket_orderbook',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('market_id', sa.String(length=100), nullable=False),
        sa.Column('outcome', sa.String(length=10), nullable=False),
        sa.Column('best_bid', sa.Numeric(precision=10, scale=4)),
        sa.Column('best_ask', sa.Numeric(precision=10, scale=4)),
        sa.Column('bid_size', sa.Numeric(precision=20, scale=2)),
        sa.Column('ask_size', sa.Numeric(precision=20, scale=2)),
        sa.Column('mid_price', sa.Numeric(precision=10, scale=4)),
        sa.PrimaryKeyConstraint('time', 'market_id', 'outcome')
    )
    op.create_index('idx_polymarket_orderbook_market', 'polymarket_orderbook', ['market_id', 'time'])

    # Convert to hypertable
    op.execute("""
        SELECT create_hypertable('polymarket_orderbook', 'time',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
    """)

    # ==========================================
    # Signals table
    # ==========================================
    op.create_table(
        'signals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('market_id', sa.String(length=100), nullable=False),
        sa.Column('signal_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('minutes_since_open', sa.Integer()),
        sa.Column('spot_price_start', sa.Numeric(precision=20, scale=8)),
        sa.Column('spot_price_current', sa.Numeric(precision=20, scale=8)),
        sa.Column('price_change_pct', sa.Numeric(precision=10, scale=6)),
        sa.Column('momentum_score', sa.Numeric(precision=10, scale=6)),
        sa.Column('pm_yes_price', sa.Numeric(precision=10, scale=4)),
        sa.Column('pm_no_price', sa.Numeric(precision=10, scale=4)),
        sa.Column('recommended_outcome', sa.String(length=10)),
        sa.Column('confidence_score', sa.Numeric(precision=10, scale=6)),
        sa.Column('expected_value', sa.Numeric(precision=10, scale=6)),
        sa.Column('executed', sa.Boolean(), server_default='false'),
        sa.Column('execution_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['market_id'], ['markets.market_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_signals_market_id', 'signals', ['market_id'])
    op.create_index('idx_signals_executed', 'signals', ['executed'])

    # ==========================================
    # Orders table
    # ==========================================
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.String(length=100)),
        sa.Column('market_id', sa.String(length=100), nullable=False),
        sa.Column('signal_id', sa.Integer()),
        sa.Column('order_type', sa.String(length=20)),
        sa.Column('side', sa.String(length=10)),
        sa.Column('outcome', sa.String(length=10)),
        sa.Column('quantity', sa.Numeric(precision=20, scale=2)),
        sa.Column('price', sa.Numeric(precision=10, scale=4)),
        sa.Column('status', sa.String(length=20)),
        sa.Column('placed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('filled_at', sa.DateTime(timezone=True)),
        sa.Column('cancelled_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['market_id'], ['markets.market_id']),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index('idx_orders_status', 'orders', ['status'])

    # ==========================================
    # Trades table
    # ==========================================
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('trade_id', sa.String(length=100)),
        sa.Column('order_id', sa.String(length=100)),
        sa.Column('market_id', sa.String(length=100), nullable=False),
        sa.Column('outcome', sa.String(length=10)),
        sa.Column('quantity', sa.Numeric(precision=20, scale=2)),
        sa.Column('avg_price', sa.Numeric(precision=10, scale=4)),
        sa.Column('cost', sa.Numeric(precision=20, scale=2)),
        sa.Column('fee', sa.Numeric(precision=20, scale=2)),
        sa.Column('filled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['market_id'], ['markets.market_id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trade_id')
    )

    # ==========================================
    # Positions table
    # ==========================================
    op.create_table(
        'positions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('market_id', sa.String(length=100), nullable=False),
        sa.Column('trade_id', sa.String(length=100)),
        sa.Column('outcome', sa.String(length=10)),
        sa.Column('quantity', sa.Numeric(precision=20, scale=2)),
        sa.Column('avg_entry_price', sa.Numeric(precision=10, scale=4)),
        sa.Column('cost_basis', sa.Numeric(precision=20, scale=2)),
        sa.Column('status', sa.String(length=20)),
        sa.Column('resolution_outcome', sa.String(length=10)),
        sa.Column('payout', sa.Numeric(precision=20, scale=2)),
        sa.Column('realized_pnl', sa.Numeric(precision=20, scale=2)),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['market_id'], ['markets.market_id']),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.trade_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_positions_status', 'positions', ['status'])

    # ==========================================
    # Account Balance (time-series)
    # ==========================================
    op.create_table(
        'account_balance',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('balance', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('equity', sa.Numeric(precision=20, scale=2)),
        sa.Column('available', sa.Numeric(precision=20, scale=2)),
        sa.PrimaryKeyConstraint('time')
    )

    # Convert to hypertable
    op.execute("""
        SELECT create_hypertable('account_balance', 'time',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        );
    """)

    # ==========================================
    # System Events table
    # ==========================================
    op.create_table(
        'system_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.String(length=50)),
        sa.Column('component', sa.String(length=50)),
        sa.Column('message', sa.Text()),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_events_type', 'system_events', ['event_type'])

    # ==========================================
    # Performance Metrics table
    # ==========================================
    op.create_table(
        'performance_metrics',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_trades', sa.Integer()),
        sa.Column('winning_trades', sa.Integer()),
        sa.Column('losing_trades', sa.Integer()),
        sa.Column('win_rate', sa.Numeric(precision=10, scale=4)),
        sa.Column('total_pnl', sa.Numeric(precision=20, scale=2)),
        sa.Column('avg_trade_pnl', sa.Numeric(precision=20, scale=2)),
        sa.Column('max_drawdown', sa.Numeric(precision=20, scale=2)),
        sa.Column('sharpe_ratio', sa.Numeric(precision=10, scale=4)),
        sa.PrimaryKeyConstraint('date')
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('performance_metrics')
    op.drop_table('system_events')
    op.drop_table('account_balance')
    op.drop_table('positions')
    op.drop_table('trades')
    op.drop_table('orders')
    op.drop_table('signals')
    op.drop_table('polymarket_orderbook')
    op.drop_table('market_data')
    op.drop_table('markets')

    # Note: We don't drop the TimescaleDB extension in downgrade
    # as it might be used by other applications
