"""Warren Finance MCP Server.

Exposes read-only finance tools over HTTP using the MCP protocol.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from .config import config
from .database import db


@dataclass
class AppContext:
    """Application context with database connection."""

    db: type


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle - connect/disconnect database."""
    await db.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()

# Create MCP server with HTTP transport configuration
mcp = FastMCP(
    name="Warren Finance",
    instructions="Personal finance agent. Use tools to query spending data. Never generate SQL.",
    stateless_http=True,
    json_response=True,
    lifespan=app_lifespan,
    host=config.host,
    port=config.port,
)

# Import and register tools
from .tools.spend_summary import get_spend_summary
from .tools.spend_by_category import get_spend_by_category
from .tools.spend_by_merchant import get_spend_by_merchant
from .tools.recent_transactions import get_recent_transactions

# Register tools with the MCP server
mcp.tool(name="finance.get_spend_summary")(get_spend_summary)
mcp.tool(name="finance.get_spend_by_category")(get_spend_by_category)
mcp.tool(name="finance.get_spend_by_merchant")(get_spend_by_merchant)
mcp.tool(name="finance.get_recent_transactions")(get_recent_transactions)


def main() -> None:
    """Run the MCP server with streamable HTTP transport."""
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
