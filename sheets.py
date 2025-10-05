# sheets.py
import os
import json
import uuid
import logging
from datetime import datetime, date
import gspread
import dateparser

# Configure logging
logging.basicConfig(level=logging.INFO)

# Expected env:
# GSPREAD_SERVICE_ACCOUNT_JSON -> JSON string of service account credentials OR path to json file
# BOOKINGS_SHEET_ID -> Google Sheet ID (the long id in the sheet URL)
# BOOKINGS_WORKSHEET_NAME -> defaults to "bookings"

GSERVICE_JSON = os.getenv("GSPREAD_SERVICE_ACCOUNT_JSON")
SHEET_ID = os.getenv("BOOKINGS_SHEET_ID")
WORKSHEET_NAME = os.getenv("BOOKINGS_WORKSHEET_NAME", "bookings")


def _load_gspread_client():
    """
    Supports either a path to credentials json file or the JSON string in env var.
    """
    if not GSERVICE_JSON:
        raise EnvironmentError("GSPREAD_SERVICE_ACCOUNT_JSON not set")

    try:
        # If looks like a file path, load the file
        if os.path.exists(GSERVICE_JSON):
            client = gspread.service_account(filename=GSERVICE_JSON)
        else:
            # assume JSON string
            cred = json.loads(GSERVICE_JSON)
            client = gspread.service_account_from_dict(cred)
    except Exception as e:
        logging.exception("Failed to initialize gspread client: %s", e)
        raise
    return client


def _get_worksheet():
    client = _load_gspread_client()
    if not SHEET_ID:
        raise EnvironmentError("BOOKINGS_SHEET_ID not set")
    sht = client.open_by_key(SHEET_ID)
    try:
        worksheet = sht.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        # attempt to create headers if missing
        worksheet = sht.add_worksheet(title=WORKSHEET_NAME, rows="1000", cols="20")
        headers = [
            "booking_id", "name", "check_in", "check_out", "guests",
            "room_type", "contact", "status", "created_at"
        ]
        worksheet.insert_row(headers, 1)
    return worksheet


def parse_date_natural(text, base=None):
    """
    Parse natural date in English/Hindi/Hinglish.
    Returns a date object or raises ValueError.
    """
    if text is None:
        raise ValueError("No date text provided")
    text = text.strip()
    # Try strict ISO first
    try:
        dt = datetime.strptime(text, "%Y-%m-%d").date()
        return dt
    except Exception:
        pass

    # Use dateparser with languages preference and future bias for relative dates
    settings = {
        "PREFER_DAY_OF_MONTH": "first",
        "RETURN_AS_TIMEZONE_AWARE": False,
        "PREFER_DATES_FROM": "future"  # helps with "next friday"
    }
    # try both english and hindi
    dt = dateparser.parse(text, settings=settings, languages=["en", "hi"])
    if dt:
        return dt.date()

    # As a last resort, try some common dd-mm-yyyy formats
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d %B %Y"):
        try:
            dt = datetime.strptime(text, fmt).date()
            return dt
        except Exception:
            continue

    raise ValueError(f"Could not parse date: {text}")


def _row_to_booking(row):
    """
    Convert a worksheet row (list) to a dict. Assumes header exists.
    """
    headers = ["booking_id", "name", "check_in", "check_out", "guests",
               "room_type", "contact", "status", "created_at"]
    # pad row
    row = row + [""] * (len(headers) - len(row))
    data = dict(zip(headers, row))
    # parse dates to date objects if possible
    try:
        data["check_in_date"] = datetime.strptime(data["check_in"], "%Y-%m-%d").date()
    except Exception:
        data["check_in_date"] = None
    try:
        data["check_out_date"] = datetime.strptime(data["check_out"], "%Y-%m-%d").date()
    except Exception:
        data["check_out_date"] = None
    return data


def check_availability(check_in_text: str, check_out_text: str) -> bool:
    """
    Returns True if the date range [check_in, check_out) is available.
    Assumes check_in and check_out are inclusive/exclusive as per your policy.
    We'll treat booking as inclusive of check_in, exclusive of check_out.
    """
    ws = _get_worksheet()
    # parse dates
    try:
        new_start = parse_date_natural(check_in_text)
        new_end = parse_date_natural(check_out_text)
    except ValueError as e:
        raise

    if new_end <= new_start:
        raise ValueError("check_out must be after check_in")

    rows = ws.get_all_values()
    if len(rows) <= 1:
        # no bookings
        return True

    # header at rows[0], data follows
    for i in range(1, len(rows)):
        booking = _row_to_booking(rows[i])
        if booking["status"].upper() != "CONFIRMED":
            continue
        es = booking["check_in_date"]
        ee = booking["check_out_date"]
        if not es or not ee:
            continue
        # overlap if not (new_end <= es or new_start >= ee)
        if not (new_end <= es or new_start >= ee):
            # overlapping confirmed booking found
            logging.info("Overlap found with booking %s (%s - %s)", booking["booking_id"], booking["check_in"], booking["check_out"])
            return False
    return True


def append_booking(
    name: str,
    check_in_text: str,
    check_out_text: str,
    guests: str = "",
    room_type: str = "",
    contact: str = "",
    status: str = "CONFIRMED"
) -> dict:
    """
    Append a booking row and return the booking dict.
    """
    ws = _get_worksheet()
    booking_id = str(uuid.uuid4())
    try:
        check_in = parse_date_natural(check_in_text)
        check_out = parse_date_natural(check_out_text)
    except ValueError as e:
        raise

    created_at = datetime.utcnow().isoformat() + "Z"
    row = [
        booking_id,
        name,
        check_in.strftime("%Y-%m-%d"),
        check_out.strftime("%Y-%m-%d"),
        guests,
        room_type,
        contact,
        status,
        created_at
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")
    logging.info("Appended booking %s for %s", booking_id, name)
    return {
        "booking_id": booking_id,
        "name": name,
        "check_in": check_in.strftime("%Y-%m-%d"),
        "check_out": check_out.strftime("%Y-%m-%d"),
        "guests": guests,
        "room_type": room_type,
        "contact": contact,
        "status": status,
        "created_at": created_at
    }
