"""Database module for Warren Finance MCP Server.

Provides async PostgreSQL connection pool using asyncpg.
All queries are parameterized for security.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator

import asyncpg

from .config import config


class Database:
    """Async PostgreSQL database connection pool."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Initialize the connection pool."""
        self._pool = await asyncpg.create_pool(
            config.database_url,
            min_size=2,
            max_size=10,
        )

    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        """Get the connection pool."""
        if not self._pool:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._pool

    async def fetch_all(
        self,
        query: str,
        *args: Any,
    ) -> list[dict[str, Any]]:
        """Execute a query and return all rows as dictionaries."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetch_one(
        self,
        query: str,
        *args: Any,
    ) -> dict[str, Any] | None:
        """Execute a query and return one row as dictionary."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetch_val(
        self,
        query: str,
        *args: Any,
    ) -> Any:
        """Execute a query and return a single value."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database instance
db = Database()


@asynccontextmanager
async def get_db() -> AsyncIterator[Database]:
    """Context manager for database access."""
    yield db
