# src//booking_agent/schemas.py
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
    name: str
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
    user_name_for_booking: Optional[str] # Extracted from the request
    
    matching_rooms: Optional[List[Dict]]
    available_room_options: Optional[List[Dict]]
    selected_room_option_id: Optional[str] 
    user_booking_confirmation_response: Optional[str] # e.g., "yes" or "no"
    
    booking_result: Optional[Dict]
    error_message: Optional[str]

# Pydantic model for parsing (from Choice 2)
class BookingRequest(BaseModel):
    start_time: Optional[str] = Field(None, description="ISO format, e.g., 2025-07-16T10:00:00")
    duration_hours: Optional[int] = Field(None, description="Duration in hours")
    capacity: Optional[int] = Field(None, description="Room capacity")
    equipments: Optional[List[str]] = Field(None, description="List of equipment")
    user_name: Optional[str] = Field(None, description="Name of the user")
    clarification_needed: bool = Field(False, description="Whether clarification is needed")
    clarification_question: Optional[str] = Field(None, description="Question for clarification")

## Tool Definitions (Pydantic models for Langchain tool calling)
