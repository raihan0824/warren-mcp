"""finance.get_spend_summary tool.

Returns total spend and transaction count for a given time range.
"""

from typing import Literal

from pydantic import BaseModel, Field

from ..database import db
from ..time_utils import get_time_range, TimeRange


class SpendSummaryInput(BaseModel):
    """Input schema for get_spend_summary."""

    range: Literal["today", "yesterday", "this_week", "last_week", "this_month"] = Field(
        description="Time range for the spend summary"
    )


class SpendSummaryOutput(BaseModel):
    """Output schema for get_spend_summary."""

    range: str = Field(description="The time range queried")
    spend_total_rp: float = Field(description="Total spend in Rupiah")
    tx_count: int = Field(description="Number of transactions")


async def get_spend_summary(
    range: Literal["today", "yesterday", "this_week", "last_week", "this_month"],
) -> SpendSummaryOutput | dict:
    """
    Get total spend and transaction count for a time range.

    Args:
        range: One of "today", "yesterday", "this_week", "last_week", "this_month"

    Returns:
        SpendSummaryOutput with range, spend_total_rp, and tx_count
    """
    try:
        start_ts, end_ts = get_time_range(range)

        # Use daily view for all ranges
        query = """
            SELECT 
                COALESCE(SUM(spend_total_rp), 0) as spend_total_rp,
                COALESCE(SUM(tx_count), 0) as tx_count
            FROM v_spend_daily
            WHERE date_jakarta >= $1::date AND date_jakarta <= $2::date
        """
        result = await db.fetch_one(query, start_ts.date(), end_ts.date())

        if result:
            return SpendSummaryOutput(
                range=range,
                spend_total_rp=float(result["spend_total_rp"]),
                tx_count=int(result["tx_count"]),
            )
        else:
            return SpendSummaryOutput(
                range=range,
                spend_total_rp=0.0,
                tx_count=0,
            )

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
                "message": f"Failed to fetch spend summary: {str(e)}",
            }
        }
