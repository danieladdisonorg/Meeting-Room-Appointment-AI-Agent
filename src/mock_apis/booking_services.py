# src/mock_apis/booking_services.py
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict

from langchain_core.tools import tool

from config import BOOKINGS_FILE, DELAY


# @tool("load_bookings", description="Load existing bookings from external file.")
def load_bookings(
        filepath: Path = BOOKINGS_FILE
    ) -> Dict[str, List[Dict[str, Union[str, datetime]]]]:
    """Load existing bookings from external file."""
    existing_data: Dict[str, List[Dict[str, Union[str, datetime]]]] = {}
    try:
        with open(filepath, "r") as f:
            existing_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode existing JSON in {filepath}. Starting fresh.")
        existing_data = {}
    return existing_data


# @tool("save_bookings", description="Save bookings to the database.")
def save_bookings_tool(
        room_id: Union[int, str], 
        booking: Dict, file_path: Path = BOOKINGS_FILE
    ):
    """Save bookings to the database."""
    bookings = load_bookings(file_path=file_path)
    room_id = str(room_id)
    room_bookings = bookings.get(room_id, [])
    print(f"Current bookings for room {room_id}: {room_bookings}")
    room_bookings.append(booking)
    bookings[room_id] = room_bookings

    with open(file_path, "w") as f:
        json.dump(bookings, f, indent=4)

# @tool("check_time_conflict", description="Check if a room has a time conflict for the requested time.")
def check_time_conflict_tool(
        existing_bookings: List[Dict[str, Union[str, datetime]]],
        room_id: int, start_time:  Union[str, datetime],
        end_time: Optional[Union[str, datetime]] = None, duration_hours: Optional[float]=None,
    ) -> bool:
    """ 
    Check if a room has a time conflict for the requested time. 
    """
    start_time = datetime.fromisoformat(start_time)
    end_time = end_time or (start_time + timedelta(hours=duration_hours))

    room_bookings = existing_bookings.get(room_id, [])
    if not room_bookings:
        return False
    for booking in room_bookings:
        booking_start = datetime.fromisoformat(booking['start_time'])
        booking_end = datetime.fromisoformat(booking['end_time']) + DELAY
        if start_time < booking_end and end_time > booking_start:
            return True
    return False

# def get_room_reserved_time_slots(
#         room_id: Union[int, str], 
#         existing_bookings: Dict[str, List[Dict[str, Union[str, datetime]]]]) -> List[Dict]:
    
#     free_time_slots = []
#     room_id = str(room_id)
    
#     return free_time_slots


# @tool("book_room", description="Book a room for the specified time and user.")
# def book_room_tool(
#         room_id: int, start_time: str, 
#         end_time: str, user_name: str
#     ) -> Optional[Booking]:
#     """Book a room for the specified time and user."""
#     existing_bookings = load_bookings()
#     if check_time_conflict_tool(
#         room_id, start_time, duration_hours=int((datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds() / 3600)
#     ):
#         return None
#     booking = Booking(
#         room_id=room_id,
#         start_time=start_time,
#         end_time=end_time,
#         booked_by=user_name,
#     )
#     existing_bookings.append(booking)
#     save_bookings_tool(existing_bookings)
#     return booking

