# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Load Environment Variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

project_dir = Path(__file__).resolve().parent.parent
os.chdir(project_dir)

# LLM Configuration
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL_NAME = os.environ["GROQ_MODEL_NAME"]

OLLAMA_MODEL_NAME = os.environ["OLLAMA_MODEL_NAME"]
OLLAMA_API_KEY = os.environ["OLLAMA_API_KEY"]

GEMINI_MODEL_NAME = os.environ["GEMINI_MODEL_NAME"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# LangSmith Configuration
LANGCHAIN_TRACING_V2 = os.environ["LANGCHAIN_TRACING_V2"]
LANGCHAIN_ENDPOINT = os.environ["LANGCHAIN_ENDPOINT"]
LANGCHAIN_API_KEY = os.environ["LANGCHAIN_API_KEY"]
LANGCHAIN_PROJECT = os.environ["LANGCHAIN_PROJECT"]

# File Paths
ROOMS_FILE = Path("data/rooms.json")
BOOKINGS_FILE = Path("data/bookings.json")

recursion_limit = 100
DELAY = timedelta(hours=0.5)
