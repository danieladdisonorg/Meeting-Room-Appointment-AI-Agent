##=======================================================================
# SETUP : Define global variables for parser and prompt template
##=======================================================================

REQUIRED_FIELDS = ["start_time", "duration_hours", "capacity", "equipments", "user_name"]


TEMPLATE = "\n".join([
        "You are a meeting room assistant. Extract the following fields from the user request.",
        
        "#### Required fields:",
            "- start_time: If the user not specifies the date, (e.g., \"tomorrow\" or something similar), calculate the time from {current_date}.",
            "- duration_hours: (e.g., 2)\n",
            "- capacity: integer (e.g., \"for 5 people\" → 5)",
            "- equipments: list of strings (e.g., [\"projector\", \"whiteboard\"])",
            "- user_name: name of the person booking.\n",

        "### Instructions:",
            "1. Respond ONLY with a JSON object matching this schema: {parsing_schema}",
            "2. You **MUST respond ONLY with this JSON directly**.",
            "3. Do NOT include any explanatory text before or after the JSON.",
            "4. If fields are missing, set them to null.",
            "5. If start_time, capacity, equipments, user_name, or duration_hours is missing/unclear:",
            "   - Set \"clarification_needed\": true and ",
            "   - Set \"clarification_question\", ask for clarification about the missing fields\n",

        "### Example Outputs:",
            "- Complete info:\n{successful_example}",
            "- Needs clarification:\n{missing_example}\n",
        
        "Now process this request:\n\"{user_request}\""
        
    ])

# Example Python dicts
SUCCESS_EXAMPLE = {
    "start_time": "2025-07-16T10:00:00",
    "duration_hours": 1,
    "capacity": 3,
    "equipments": ["whiteboard"],
    "user_name": "Heba",
    "clarification_needed": False,
    "clarification_question": None
}

MISSING_EXAMPLE = {
    "start_time": None,
    "duration_hours": None,
    "capacity": 5,
    "equipments": ["whiteboard"],
    "user_name": "Heba",
    "clarification_needed": True,
    "clarification_question": "Could you tell me the meeting's start time and duration?" 
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
