##=======================================================================
# SETUP : Define global variables for parser and prompt template
##=======================================================================

REQUIRED_FIELDS = ["start_date", "start_time", "duration_hours", "capacity", "equipments", "user_name"]

TEMPLATE = "\n".join([
    "Role: Meeting room booking assistant. Extract fields from the request strictly as JSON.",
    
    "### Required Fields:",
        "- start_date: " , # user can specify a direct date (e.g, '20 May' or '20/5') or specify relative dates (e.g., 'tomorrow').",
        "  • RULE1: For relative dates, calculate using {current_date} without asking for clarification.",
        "  • RULE2: Must be future date after {current_date}, if not make start_date null.",

        "- start_time: ", #Can be a specific time (e.g., '7 AM', '5 PM', or '7 pm') or a specific duration from now (e.g., 'after 1 hour').",
        # "  • RULE1: Normalize time formats (e.g., '7 pm' → '07:00 PM', '19' → '07:00 PM') without asking for clarification.",
        "  • RULE1: If the time is ambiguous (e.g., missing AM/PM or unclear phrasing), make start_time null and set `clarification_needed: true` and ask for this ambiguity.",
        "  • RULE2: For relative times (e.g., 'after 1 hour'), calculate the exact time using {current_time} and include it in the response without asking for clarification.",
        "  • RULE3: Must be future Time after this time {current_time}, if not make start_time null.",
        "  • RULE4: If User not sure about time, make start_time null.",

        "- duration_hours",# : (e.g., 0.5 or one hour, have an hour)\n",
        "- capacity", # : integer (e.g., '5 people' → 5)",
        "- equipments", # : list of strings (e.g., ['projector', 'whiteboard'])",
        "- user_name", # : name of the person booking.\n",

    "### Instructions:",
        "1. Respond ONLY with a JSON object matching this schema: {parsing_schema}.",
        "2. Do NOT include any explanatory text before or after the JSON.",
        "3. If the user input is irrelevant , ambiguous or unconfident reply ('might'). ",
            "Set `clarification_needed: true` and provide a clarification question.",
        "   • For time-related fields, only ask for clarification if the input is ambiguous (e.g., missing AM/PM).",
        "4. For missing fields:",
        "   • Set `clarification_needed: true`.",
        "   • Provide a clarification question for the missing field.",
        "   • Ask about one or two fields at a time (prioritize time-related fields).",

    "### Example Outputs:",
        "- Complete info:\n{successful_example}",
        "- Needs clarification:\n{missing_example}\n",
    
    "Now process this request:\n'{user_request}'"
    
    ])

# Example Python dicts
SUCCESS_EXAMPLE = {
    "start_date": "2025-07-16",
    "start_time":"10 pm",
    "duration_hours": 1,
    "capacity": 3,
    "equipments": ["whiteboard"],
    "user_name": "Heba",
    "clarification_needed": False,
    "clarification_question": None
}

MISSING_EXAMPLE = {
    "start_date": None,  # Missing date
    "start_time": None,  # Missing time
    "duration_hours": None,  # Missing duration
    "capacity": 4,
    "equipments": ["Projector"],
    "user_name": None,
    "clarification_needed": True,
    "clarification_question": "Could you provide the date and time for the booking? For example, 'tomorrow at 10 AM' or '20 May at 7 PM'."
}

# Default agent state structure
DEFAULT_AGENT_STATE = {
    'user_input': None,
    'llm_response': None,
    'messages': [],
    'parsed_request': {
        'start_date': None,
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
    'available_rooms': None,
    'alternative_rooms': None,
    'selected_room': None,
    'user_booking_confirmation_response': None,
    'booking_result': None,
    'error_message': None
}

