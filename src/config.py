"""Configuration module for Warren Finance MCP Server."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration."""

    database_url: str
    host: str
    port: int

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        return cls(
            database_url=database_url,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
        )


config = Config.from_env()
