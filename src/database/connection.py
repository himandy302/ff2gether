"""
Database connection management with async support.

Handles PostgreSQL + TimescaleDB connections using SQLAlchemy async engine.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from src.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages async database connections and sessions."""

    def __init__(self):
        """Initialize database connection manager."""
        self._engine = None
        self._session_factory = None

    def initialize(self):
        """Create async engine and session factory."""
        if self._engine is not None:
            logger.warning("Database engine already initialized")
            return

        # Create async engine
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.LOG_LEVEL == "DEBUG",
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
        )

        # Create session factory
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info("Database engine initialized successfully")

    async def close(self):
        """Close database engine and all connections."""
        if self._engine is None:
            return

        await self._engine.dispose()
        logger.info("Database engine closed")
        self._engine = None
        self._session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            async with db_manager.session() as session:
                result = await session.execute(query)
                await session.commit()
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            bool: True if healthy, False otherwise
        """
        if self._engine is None:
            return False

        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    @property
    def engine(self):
        """Get the async engine instance."""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._engine


# Global database manager instance
db_manager = DatabaseManager()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session.

    Usage in FastAPI:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_session)):
            result = await session.execute(query)
    """
    async with db_manager.session() as session:
        yield session


async def init_database():
    """Initialize database on application startup."""
    logger.info("Initializing database...")
    db_manager.initialize()

    # Verify connection
    is_healthy = await db_manager.health_check()
    if not is_healthy:
        raise RuntimeError("Database health check failed during initialization")

    logger.info("Database initialized and healthy")


async def close_database():
    """Close database connections on application shutdown."""
    logger.info("Closing database connections...")
    await db_manager.close()
