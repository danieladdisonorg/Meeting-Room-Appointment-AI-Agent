##=======================================================================
# SETUP : Define global variables for parser and prompt template
##=======================================================================

# from booking_agent.schemas import AgentState, BookingRequest

REQUEST_TEMPLATE = "\n".join([
    # If user send a greeting reply friendly then,
    "Role: You are a meeting room booking assistant. Speak with a friendly tone with some emojis if needed."
    "Extract the following fields from the request strictly as JSON.",

    "### Required Fields:",
    "- start_date: if used say relative date such as the following scenarios",
                   "you must calculate exact date based on {current_date} and no ask for clarification.",
        "  • 'today' → {current_date}",
        "  • 'tomorrow' → {current_date} + 1 day",
        "  • For any relative date such as 'next [weekday]' → ",
            "calculate exact date based on {current_date} and no ask for clarification.",
        "  • Convert all to Format as YYYY-MM-DD",
        
        "- start_time:",
        "  • If time includes AM/PM → parse to HH:MM:SS AM/PM directly",
        "  • If time does NOT include AM/PM → assume AM by default, but set `clarification_needed: true` and set a `clarification_question`",
        "  • For any relative time such as 'after 1 hour' → ",
            "calculate exact time based on {current_time} and no ask for clarification.",
        "  • Convert all to HH:MM:SS AM/PM",

        "- duration_hours",
        "- capacity",
        "- equipments",
        "- user_name: if you ask the user about this field use friendly tone", 
    
    "### Instructions:",
        "- If the user says ONLY greeting, e.g., 'hi', 'hello', 'hey', 'good morning', etc., and no booking info:",
        "     → Set all missing fields by null.",
        "     → Set `clarification_needed: true`.",
        "     → Set `clarification_question`: Respond politely to the greeting such as 'Hi, how can I help you?'."
        " - If greeting + booking details: reply with friendly tone AND extract fields."

        "- Always respond ONLY with a JSON object matching this schema: {parsing_schema}.",
        "- Do NOT include any extra explanation or text outside the JSON.",
        "- For any Missing Fields (e.g, 'equipments') you MUST:",
        "     → Set `clarification_needed: true`.",
        "     → Set `clarification_question`: Ask for the missing field/s prioritize date and time specifically the past date or time.",

        "- Ambiguous Date and Time Handling:",
        "   • If time lacks AM/PM, assume AM, but still set `clarification_needed: true` and ask the user if it was meant to be AM or PM.",
        "   • If you found that the data and time together is in the past, set `clarification_needed: true` and inform the user in `clarification_question`.",
        "   • If start_date or start_time together (check this using iso format) is in the past",
             " based on the date and time now {current_date} {current_time} you MUST Set them nulls and inform the user",

        "- For out of context requests try to reply wisely. these are examples of such requests:",
        "   • Non-booking inquiries (e.g., 'What's the weather?')",
        "   • Historical data queries",
        "   • Multi-room bookings",
        
    "### Example Outputs:",
        "- Complete info:\n{successful_example}",
        "- Needs clarification:\n{missing_example}\n",
    
    "Now process this request:\n'{user_request}'"
    
    ])


# Example Python dicts
SUCCESS_EXAMPLE = {
    "start_date": "2025-07-16",
    "start_time": "10:00:00 PM", 
    "duration_hours": 1,
    "capacity": 3,
    "equipments": ["whiteboard"],
    "user_name": "Heba",
    "clarification_needed": False,
    "clarification_question": None
}

MISSING_EXAMPLE = {
    "start_date": None, 
    "start_time": "10:00:00",  
    "duration_hours": None,
    "capacity": 4,
    "equipments": ["projector"],
    "user_name": None,
    "clarification_needed": True,
    "clarification_question": "Could you confirm if you meant 10:00:00 AM or PM, and provide the date for the booking?"
}


# Default agent state structure
DEFAULT_AGENT_STATE={
    'user_input': "",
    'llm_response': "",
    'messages': [],
    'parsed_request': {
        'start_date': None,
        'start_time': None,
        'duration_hours': None,
        'capacity': None,
        'equipments': [],
        'user_name': None
    },
    'clarification_needed': False,
    'clarification_question': None,
    'user_name_for_booking': None,

    'matching_rooms': [],
    'available_rooms': [],
    'alternative_rooms': [],
    'selected_room': None,
    'user_confirmation': None,
    'booking_result': False,

    'error_message': None
}

ROOM_TEMPLATE = "\n".join([
    "Please politely inform the user by the rooms info your friendly style."
    "Here are the available rooms: {rooms}",
])