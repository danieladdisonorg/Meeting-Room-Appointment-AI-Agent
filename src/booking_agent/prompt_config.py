##=======================================================================
# SETUP : Define global variables for parser and prompt template
##=======================================================================

REQUIRED_FIELDS = ["start_time", "duration_hours", "capacity", "equipments", "user_name"]


TEMPLATE = "\n".join([
    "Role: Meeting room booking assistant. Extract fields from the request strictly as JSON.",
    
    "### Required Fields:",
        "- start_date: user can specify a direct date (e.g, '20 May' or '20/5') or specify relative dates (e.g., 'tomorrow').",
        "     • RULE:  Relative dates → auto-calculate using {current_date} (no clarification)"

        "- start_time: user can specify a direct time (e.g, '7AM' or '5 PM') or give duration from now (e.g, 'after 1 hour')"
        "     • RULE1: Time WITHOUT includes AM/PM → ask for clarification (is it AM/PM)",
        "     • RULE2: Relative time → auto-calculate using {current_time} (no clarification)"

        "- duration_hours: (e.g., 0.5 or 2)\n",
        "- capacity: integer (e.g., '5 people' → 5)",
        "- equipments: list of strings (e.g., ['projector', 'whiteboard'])",
        "- user_name: name of the person booking.\n",

    "### Instructions:",
        "1. Respond ONLY with a JSON object matching this schema: {parsing_schema}",
        "2. You **MUST respond ONLY with this JSON directly** and Do NOT include any explanatory text before or after the JSON.",
        "3. Missing fields → set to null",
        "4. Ask about clarification if any field is missed:",
        "   • RULE1: Set clarification_needed: true", 
        "   • RULE2: And set clarification_question: ask about the messing feild",
        "   • RULE3: Ask ONE or TWO questions at time (prioritize time first)",

    "### Example Outputs:",
        "- Complete info:\n{successful_example}",
        "- Needs clarification:\n{missing_example}\n",
    
    "Now process this request:\n'{user_request}'"
    
    ])

# Example Python dicts
SUCCESS_EXAMPLE = {
    "start_date": "2025-07-16",
    "start_time":"10:00:00",
    "duration_hours": 1,
    "capacity": 3,
    "equipments": ["whiteboard"],
    "user_name": "Heba",
    "clarification_needed": False,
    "clarification_question": None
}

MISSING_EXAMPLE = {
    "start_date": "2025-07-16",
    "start_time":"10:00:00",
    "duration_hours": 1,
    "capacity": 4,
    "equipments": ["Projector"],
    "user_name": None,
    "clarification_needed": True,
    "clarification_question": "Could you tell me your name please?"
}

# Default agent state structure
DEFAULT_AGENT_STATE = {
    'user_input': None,
    'llm_response': None,
    'messages': [],
    'parsed_request': {
        'start_time': None,
        'duration_hours': None,
        'capacity': None,
        'equipments': None,
        'user_name': None
    },
    'clarification_needed': False,
    'clarification_question': None,
    'user_name_for_booking': None,
    'matching_rooms': None,
    'available_room_options': None,
    'selected_room_option_id': None,
    'user_booking_confirmation_response': None,
    'booking_result': None,
    'error_message': None
}
