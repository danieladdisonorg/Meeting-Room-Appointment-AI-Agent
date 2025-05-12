
# src/helper.py
import json
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser

from booking_agent.schemas import AgentState

from config import (
    GROQ_MODEL_NAME, GROQ_API_KEY, 
    GEMINI_MODEL_NAME, GEMINI_API_KEY,
    OLLAMA_MODEL_NAME, OLLAMA_API_KEY,
)

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

def get_llm(name: str):

    if name.lower() == "ollama":
        return ChatOllama(model_name=OLLAMA_MODEL_NAME,
                          ollama_api_key=OLLAMA_API_KEY,
                          temperature=0.0)
    
    elif name.lower() == "gemini":
        return ChatGoogleGenerativeAI(model=GEMINI_MODEL_NAME,  # Explicitly pass the model
                                      google_api_key=GEMINI_API_KEY,
                                      temperature=0.0)
    elif name.lower() == "groq":
        return ChatGroq(model_name=GROQ_MODEL_NAME,
                        groq_api_key=GROQ_API_KEY,
                        temperature=0.0)
    

def apply_prompt_template(parsing_schema: PydanticOutputParser) -> PromptTemplate: 
    prompt_template = PromptTemplate(
    input_variables=["user_request", "current_date"],
    template=TEMPLATE,
    partial_variables= {
    "parsing_schema": parsing_schema,
    "successful_example": json.dumps(SUCCESS_EXAMPLE, indent=2),
    "missing_example": json.dumps(MISSING_EXAMPLE, indent=2)
    })
    return prompt_template

def message_to_dict(message):
    """Convert message objects to serializable dictionaries"""
    return {
        'type': message.type,
        'content': message.content,
        'additional_kwargs': message.additional_kwargs
    }

def dict_to_message(data):
    """Convert serializable dictionaries to message objects"""
    if data['type'] == 'human':
        return HumanMessage(**data)
    return SystemMessage(**data)

def get_clarification_question(state: AgentState) -> str:
    if not state["parsed_request"].get("start_time"):
        return "What time should I book the room for?"
    if not state["parsed_request"].get("duration_hours"):
        return "How many hours will the meeting last?"
    if not state["parsed_request"].get("capacity"):
        return "What is the capacity of the room?"
    if not state["parsed_request"].get("equipments"):
        return "What equipment do you need in the room?"
    if not state["user_name_for_booking"]:
        return "Could you please provide your name for the booking?"
    return "Could you please clarify your request?"
