"""finance.get_recent_transactions tool.

Returns the latest transactions.
"""

from pydantic import BaseModel, Field

from ..database import db
from ..time_utils import format_datetime_jakarta


class TransactionItem(BaseModel):
    """Individual transaction item."""

    datetime_jakarta: str = Field(description="Transaction datetime in Asia/Jakarta timezone")
    merchant: str = Field(description="Merchant name")
    category_code: str = Field(description="Category code")
    total_rp: float = Field(description="Transaction amount in Rupiah")
    notes: str | None = Field(default=None, description="Transaction notes/details")


class RecentTransactionsOutput(BaseModel):
    """Output schema for get_recent_transactions."""

    items: list[TransactionItem] = Field(description="List of recent transactions")


async def get_recent_transactions(
    limit: int = 5,
) -> RecentTransactionsOutput | dict:
    """
    Get the latest transactions.

    Args:
        limit: Maximum number of transactions to return (default: 5)

    Returns:
        RecentTransactionsOutput with items list
    """
    try:
        query = """
            SELECT 
                datetime_jakarta,
                merchant,
                category_code,
                total_rp,
                notes
            FROM v_tx_clean
            ORDER BY datetime_jakarta DESC
            LIMIT $1
        """
        rows = await db.fetch_all(query, limit)

        items = [
            TransactionItem(
                datetime_jakarta=format_datetime_jakarta(row["datetime_jakarta"]),
                merchant=row["merchant"],
                category_code=row["category_code"],
                total_rp=float(row["total_rp"]),
                notes=row["notes"],
            )
            for row in rows
        ]

        return RecentTransactionsOutput(items=items)

    except Exception as e:
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Failed to fetch recent transactions: {str(e)}",
            }
        }
