# src/booking_agent/schemas.py
"""Pydantic models for data validation in booking meeting rooms."""
import re
from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict
from typing import Union, List, Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage

class Booking(BaseModel):
    room_id: int
    start_time: str
    end_time: str
    booked_by: str

class Room(BaseModel):
    id: int
    type: str
    capacity: int
    equipments: List[str]

## Agent State Definition as a TypedDict
class AgentState(TypedDict):
    user_input: str
    llm_response: Optional[str]

    messages: List[Union[HumanMessage, SystemMessage]]

    parsed_request: Optional[Dict]
    clarification_needed: bool
    clarification_question: Optional[str]
    user_name_for_booking: Optional[str]  # Extracted from the request

    matching_rooms: Optional[List[Dict]]
    available_rooms: Optional[List[Dict]]
    alternative_rooms: Optional[List[Dict]]
    selected_room: Optional[Room]
    user_booking_confirmation: Optional[str]  # e.g., "yes" or "no"
    booking_result: Optional[bool]

    error_message: Optional[str]

# YYYY-MM-DD (e.g., 2025-05-12)
# HH:MM:SS AM/PM (e.g., 02:45:30 PM).
class BookingRequest(BaseModel):
    start_date: Optional[str] = Field(
        None,
        description="The starting date for the booking in any format YYYY-MM-DD (e.g., 2025-05-12)" \
        "This can be a specific date or derived from relative terms like 'tomorrow' without asking for clarification again."
    )
    start_time: Optional[str] = Field(
        None,
        description="The starting time for the booking in the format HH:MM:SS AM/PM (e.g., 02:45:30 PM). " \
        "This can be a specific time or calculated from relative terms like 'after 1 hour' without asking for clarification again."
    )
    duration_hours: Optional[float] = Field(
        None,
        description="The duration of the booking in hours (e.g., 0.5 for 30 minutes, 1 for one hour)." \
        " Accepts fractional values for partial hours."
    )
    capacity: Optional[int] = Field(
        None,
        description="The number of people the room should accommodate (e.g., 5 for a room that fits 5 people)."
    )
    equipments: Optional[List[str]] = Field(
        default_factory=list,  # Default to an empty list if no value is provided
        # None,
        description="A list of equipment required for the booking (e.g., ['projector', 'whiteboard'])."
    )
    user_name: Optional[str] = Field(
        None,
        description="The name of the person making the booking to personalize the booking process."
    )
    clarification_needed: bool = Field(
        False,
        description="Indicates whether additional clarification is required to process the booking request"\
         " (e.g., True if the input is ambiguous or incomplete)."
    )
    clarification_question: Optional[str] = Field(
        None,
        description="A question to ask the user for clarification if required fields are nulls or ambiguous"\
             " (e.g., 'Could you specify the start time?')."
    )

    @field_validator("start_date")
    def validate_start_date(cls, v):
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("start_date must be in YYYY-MM-DD format")
        return v

    @field_validator("start_time")
    def normalize_start_time(cls, v):
        if not v:
            return v
        # Handle cases like "2 PM" or "10:30 PM"
        match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$", v, re.IGNORECASE)
        if match:
            hour, minute, period = match.groups()
            hour = hour.zfill(2)  # Pad hour to two digits
            minute = minute or "00"  # Default to 00 if no minutes
            return f"{hour}:{minute}:00 {period.upper()}"
        # Validate strict HH:MM:SS AM/PM
        if not re.match(r"^\d{2}:\d{2}:\d{2} (AM|PM)$", v, re.IGNORECASE):
            raise ValueError("start_time must be in HH:MM:SS AM/PM format")
        return v.upper()

## Tool Definitions (Pydantic models for Langchain tool calling)

