# src/booking_services.py
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from booking_agent.schemas import Booking
from config import BOOKINGS_FILE, DELAY

from langgraph.tools import tool


def load_bookings(file_path: Path = BOOKINGS_FILE) -> List[Booking]:
    with open(file_path, "r") as f:
        return [Booking(**booking) for booking in json.load(f)]

@tool(name="save_bookings", description="Save bookings to the database.")
def save_bookings_tool(bookings: List[Booking]):
    with open(BOOKINGS_FILE, "w") as f:
        json_list = [booking.model_dump() for booking in bookings]
        json.dump(json_list, f, indent=4)

@tool(name="check_time_conflict", description="Check if a room has a time conflict for the requested time.")
def check_time_conflict_tool(room_id: int, start_time: str, duration_hours: int) -> bool:
    existing_bookings = load_bookings()
    start_time = datetime.fromisoformat(start_time)
    end_time = start_time + timedelta(hours=duration_hours)

    for booking in existing_bookings:
        if booking.room_id != room_id:
            continue
        booking_start = datetime.fromisoformat(booking.start_time)
        booking_end = datetime.fromisoformat(booking.end_time) + DELAY
        if start_time < booking_end and end_time > booking_start:
            return True
    return False

@tool(name="book_room", description="Book a room for the specified time and user.")
def book_room(room_id: int, start_time: str, end_time: str, user_name: str) -> Optional[Booking]:
    existing_bookings = load_bookings()
    if check_time_conflict_tool(room_id, start_time, end_time):
        return None
    booking = Booking(
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        booked_by=user_name
    )
    existing_bookings.append(booking)
    save_bookings_tool(existing_bookings)
    return booking