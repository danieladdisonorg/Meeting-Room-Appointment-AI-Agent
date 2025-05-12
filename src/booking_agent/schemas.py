# src/booking_agent/schemas.py
"""Pydantic models for data validation in booking meeting rooms."""

from pydantic import BaseModel, Field
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

# Pydantic model for parsing (from Choice 2)
class BookingRequest(BaseModel):
    start_date: Optional[str] = Field(
        ...,
        description="The starting date for the booking in the format YYYY-MM-DD (e.g., 2025-05-12). " \
        "This can be a specific date or derived from relative terms like 'tomorrow' without asking for clarification again."
    )
    start_time: Optional[str] = Field(
        ...,
        description="The starting time for the booking in the format HH:MM:SS AM/PM (e.g., 02:45:30 PM). " \
        "This can be a specific time or calculated from relative terms like 'after 1 hour' without asking for clarification again."
    )
    duration_hours: Optional[float] = Field(
        ...,
        description="The duration of the booking in hours (e.g., 0.5 for 30 minutes, 1 for one hour)." \
        " Accepts fractional values for partial hours."
    )
    capacity: Optional[int] = Field(
        ...,
        description="The number of people the room should accommodate (e.g., 5 for a room that fits 5 people)."
    )
    equipments: Optional[List[str]] = Field(
        ...,
        description="A list of equipment required for the booking (e.g., ['projector', 'whiteboard'])."
    )
    user_name: Optional[str] = Field(
        ...,
        description="The name of the person making the booking to personalize the booking process."
    )
    clarification_needed: bool = Field(
        ...,
        description="Indicates whether additional clarification is required to process the booking request"\
         " (e.g., True if the input is ambiguous or incomplete)."
    )
    clarification_question: Optional[str] = Field(
        ...,
        description="A question to ask the user for clarification if required fields are nulls or ambiguous"\
             " (e.g., 'Could you specify the start time?')."
    )

## Tool Definitions (Pydantic models for Langchain tool calling)

