"""finance.get_spend_by_category tool.

Returns spend breakdown per category for a given time range.
"""

from typing import Literal

from pydantic import BaseModel, Field

from ..database import db
from ..time_utils import get_time_range


class CategorySpendItem(BaseModel):
    """Individual category spend item."""

    category_code: str = Field(description="Category code")
    category_name: str = Field(description="Human-readable category name")
    spend_total_rp: float = Field(description="Total spend in Rupiah")
    tx_count: int = Field(description="Number of transactions")


class SpendByCategoryOutput(BaseModel):
    """Output schema for get_spend_by_category."""

    range: str = Field(description="The time range queried")
    items: list[CategorySpendItem] = Field(description="Spend breakdown by category")


async def get_spend_by_category(
    range: Literal["today", "this_week", "this_month"],
) -> SpendByCategoryOutput | dict:
    """
    Get spend breakdown per category for a time range.

    Args:
        range: One of "today", "this_week", "this_month"

    Returns:
        SpendByCategoryOutput with range and items list
    """
    try:
        start_ts, end_ts = get_time_range(range)

        query = """
            SELECT 
                category_code,
                category_name,
                COALESCE(SUM(spend_total_rp), 0) as spend_total_rp,
                COALESCE(SUM(tx_count), 0) as tx_count
            FROM v_spend_by_category_daily
            WHERE date >= $1::date AND date <= $2::date
            GROUP BY category_code, category_name
            ORDER BY spend_total_rp DESC
        """
        rows = await db.fetch_all(query, start_ts.date(), end_ts.date())

        items = [
            CategorySpendItem(
                category_code=row["category_code"],
                category_name=row["category_name"],
                spend_total_rp=float(row["spend_total_rp"]),
                tx_count=int(row["tx_count"]),
            )
            for row in rows
        ]

        return SpendByCategoryOutput(range=range, items=items)

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
                "message": f"Failed to fetch spend by category: {str(e)}",
            }
        }
