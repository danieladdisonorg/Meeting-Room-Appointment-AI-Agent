
# src/helper.py
import json
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser

from booking_agent.schemas import AgentState
from booking_agent.prompt_config import TEMPLATE, SUCCESS_EXAMPLE, MISSING_EXAMPLE

from config import (
    GROQ_MODEL_NAME, GROQ_API_KEY, 
    GEMINI_MODEL_NAME, GEMINI_API_KEY,
    OLLAMA_MODEL_NAME, OLLAMA_API_KEY,
)

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

#### Deprecated: Let LLM handle the clarifications ####
# def get_clarification_question(state: AgentState) -> str:
#     if not state["parsed_request"].get("start_time"):
#         return "What time should I book the room for?"
#     if not state["parsed_request"].get("duration_hours"):
#         return "How many hours will the meeting last?"
#     if not state["parsed_request"].get("capacity"):
#         return "What is the capacity of the room?"
#     if not state["parsed_request"].get("equipments"):
#         return "What equipment do you need in the room?"
#     if not state["user_name_for_booking"]:
#         return "Could you please provide your name for the booking?"
#     return "Could you please clarify your request?"
