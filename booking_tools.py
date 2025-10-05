# booking_tools.py
import logging
from livekit.agents import function_tool, RunContext
from typing import Optional
from sheets import check_availability, append_booking

logger = logging.getLogger(__name__)

@function_tool()
async def check_availability_tool(
    context: RunContext,  # type: ignore
    check_in: str,
    check_out: str
) -> str:
    """
    Returns a friendly string: AVAILABLE or NOT_AVAILABLE or error.
    The agent (LLM) should call this function to validate dates.
    """
    try:
        ok = check_availability(check_in, check_out)
        if ok:
            return "AVAILABLE"
        else:
            return "NOT_AVAILABLE"
    except ValueError as e:
        logger.exception("Date parsing/validation error")
        return f"ERROR: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected error in check_availability_tool")
        return f"ERROR: {str(e)}"


@function_tool()
async def create_booking_tool(
    context: RunContext,  # type: ignore
    name: str,
    check_in: str,
    check_out: str,
    guests: Optional[str] = "",
    room_type: Optional[str] = "",
    contact: Optional[str] = ""
) -> str:
    """
    Creates a booking and returns a JSON-ish string with booking_id and fields.
    """
    try:
        booking = append_booking(
            name=name,
            check_in_text=check_in,
            check_out_text=check_out,
            guests=guests or "",
            room_type=room_type or "",
            contact=contact or "",
            status="CONFIRMED"
        )
        return f"BOOKED: {booking['booking_id']} | {booking['check_in']} -> {booking['check_out']}"
    except ValueError as e:
        logging.exception("Date parsing error while creating booking")
        return f"ERROR: {str(e)}"
    except Exception as e:
        logging.exception("Unexpected error in create_booking_tool")
        return f"ERROR: {str(e)}"
