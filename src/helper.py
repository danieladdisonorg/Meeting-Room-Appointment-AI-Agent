
# src/helper.py
# from langchain.prompts import PromptTemplate
# from pydantic_core import PydanticOutputParser
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

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
    
def validate_request(parser, request: str) -> bool:
    try:
        parser.parse(request)
        return True
    except Exception:
        return False