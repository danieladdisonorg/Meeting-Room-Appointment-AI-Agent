# src/booking_services.py
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from schemas import Booking
from draft.config_new import Config

configs = Config()

def load_bookings(file_path: Path=configs.BOOKINGS_FILE):
    with open(file_path, "r") as f:
        return [Booking(**booking) for booking in json.load(f)]

def save_bookings(bookings: List[Booking]):
    with open(configs.BOOKINGS_FILE, "w") as f:
        json_list = [booking.model_dump() for booking in bookings]
        json.dump(json_list, f, indent=4)

def is_time_conflict(room_id: int, 
                     start_time: str, 
                     duration_hours: int, 
                     existing_bookings: List[Booking]) -> bool:
    
    start_time = datetime.fromisoformat(start_time)
    end_time = start_time + timedelta(hours=duration_hours)

    for booking in existing_bookings:
        # Skip if this room id already has a booking
        if booking.room_id != room_id:
            continue
        
        booking_start = datetime.fromisoformat(booking.start_time)
        booking_end = datetime.fromisoformat(booking.end_time) + configs.DELAY

        # Check if the booking time conflicts with the new booking
        if start_time < booking_end and end_time > booking_start:
            return True
    
    return False

def book_room(room_id: int, 
              start_time: str, 
              end_time: str, 
              user_name: str) -> Optional[Booking]:
    
    existing_bookings = load_bookings()
    if is_time_conflict(room_id, start_time, end_time, existing_bookings):
        return None

    booking = Booking(
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        booked_by=user_name
    )
    existing_bookings.append(booking)
    save_bookings(existing_bookings)
    
    return booking