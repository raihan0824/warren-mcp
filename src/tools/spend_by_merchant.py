"""finance.get_spend_by_merchant tool.

Returns top merchants by spend for a given time range.
"""

from typing import Literal

from pydantic import BaseModel, Field

from ..database import db
from ..time_utils import get_time_range


class MerchantSpendItem(BaseModel):
    """Individual merchant spend item."""

    merchant: str = Field(description="Merchant name")
    spend_total_rp: float = Field(description="Total spend in Rupiah")
    tx_count: int = Field(description="Number of transactions")


class SpendByMerchantOutput(BaseModel):
    """Output schema for get_spend_by_merchant."""

    range: str = Field(description="The time range queried")
    items: list[MerchantSpendItem] = Field(description="Top merchants by spend")


async def get_spend_by_merchant(
    range: Literal["today", "this_week", "this_month"],
    limit: int = 5,
) -> SpendByMerchantOutput | dict:
    """
    Get top merchants by spend for a time range.

    Args:
        range: One of "today", "this_week", "this_month"
        limit: Maximum number of merchants to return (default: 5)

    Returns:
        SpendByMerchantOutput with range and items list
    """
    try:
        start_ts, end_ts = get_time_range(range)

        query = """
            SELECT 
                merchant,
                COALESCE(SUM(spend_total_rp), 0) as spend_total_rp,
                COALESCE(SUM(tx_count), 0) as tx_count
            FROM v_spend_by_merchant_daily
            WHERE date >= $1::date AND date <= $2::date
            GROUP BY merchant
            ORDER BY spend_total_rp DESC
            LIMIT $3
        """
        rows = await db.fetch_all(query, start_ts.date(), end_ts.date(), limit)

        items = [
            MerchantSpendItem(
                merchant=row["merchant"],
                spend_total_rp=float(row["spend_total_rp"]),
                tx_count=int(row["tx_count"]),
            )
            for row in rows
        ]

        return SpendByMerchantOutput(range=range, items=items)

    except ValueError as e:
        return {
            "error": {
                "code": "INVALID_INPUT",
                "message": str(e),
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Failed to fetch spend by merchant: {str(e)}",
            }
        }
