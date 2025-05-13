##=======================================================================
# SETUP : Define global variables for parser and prompt template
##=======================================================================

from booking_agent.schemas import AgentState, BookingRequest

TEMPLATE = "\n".join([
    "Role: You are a friendly and polite meeting room booking assistant. If user send a greeting reply friendly then,"
    "Extract the following fields from the request strictly as JSON.",

    "### Required Fields:",
    "- start_date:",
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
        # "- start_date: " , # user can specify a direct date (e.g, '20 May' or '20/5') or specify relative dates (e.g., 'tomorrow').",
        # "  • RULE1: For relative dates, calculate using {current_date} without asking for clarification.",
        # "  • RULE2: Must be future date after {current_date}, if not make start_date null.",

        # "- start_time: ", # Extract time in HH:MM:SS AM/PM format
        # "  • RULE1: Convert all times to HH:MM:SS AM/PM format (e.g., '2 PM' → '02:00:00 PM')",
        # "  • RULE2: For relative times (e.g., 'after 1 hour'), calculate using {current_time} without asking for clarification.",
        # "  • RULE3: Set start_time null and clarification_needed true ONLY if:",
        # "    - Time is ambiguous (missing AM/PM)",
        # "    - Time is in the past relative to {current_time}",
        # "    - Time format cannot be determined",
        # "  • RULE4: Always include full seconds in the format (e.g., '02:00:00 PM' not '2:00 PM')",

        "- duration_hours",# : (e.g., 0.5 or one hour, have an hour)\n",
        "- capacity", # : integer (e.g., '5 people' → 5)",
        "- equipments", # : list of strings (e.g., ['projector', 'whiteboard'])",
        "- user_name: if you ask the user about this field use friendly tone", # : name of the person booking.\n",
    
    "### Instructions:",
        "- If the user says only 'hi', 'hello', 'hey', 'good morning', etc., and no booking info:",
        "     → Set all missing fields by null.",
        "     → Set `clarification_needed: true`.",
        "     → Set `clarification_question`: Respond politely to the greeting such as 'Hi, how can I help you?'."
        " - If greeting + booking details: reply with friendly tone AND extract fields."

        "- Always respond ONLY with a JSON object matching this schema: {parsing_schema}.",
        "- Do NOT include any extra explanation or text outside the JSON.",

        # "- If input includes a greeting AND booking details:",
        # "   • Acknowledge the greeting politely.",
        # "   • Continue extracting fields normally.",
        # but remember to ask only one or two field/s at a time (prioritize time/date).
        # ('start_date', 'start_time', 'duration_hours', 'capacity', 'equipments', 'user_name') 
        "- For any Missing Fields (e.g, 'equipments') you MUST:",
        "     → Set `clarification_needed: true`.",
        "     → Set `clarification_question`: Ask for the missing field/s.",

        "- Ambiguous Time Handling:",
        "   • If time lacks AM/PM, assume AM, but still set `clarification_needed: true` and ask if it was meant to be AM or PM.",
        "   • If start_date or start_time is in the past based on the date and time now {current_date} {current_time},",
              " set `clarification_needed: true` and ask for a future time.",
    
        # "1. For all requests respond ONLY with a JSON object matching this schema: {parsing_schema}.",
        # "2. Do NOT include any explanatory text before or after the JSON.",
        # "3. If there is a greeting, YOU MUST first reply politely for greetings then ask about the missing fields (if any).",
        # "4. For any missing fields:",
        # "   • Set `clarification_needed: true`.",
        # "   • Set `clarification_question: ` ask a clarification question about the missing field/s",
        #                                     " but remember to ask only one or two field/s at a time (prioritize time-related fields).",

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
    "start_date": None,  # Missing date
    "start_time": "10:00:00",  # Missing AM/PM, assumed AM
    "duration_hours": None,  # Missing duration
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
    'user_booking_confirmation_response': None,
    'booking_result': False,
    'error_message': None
}
