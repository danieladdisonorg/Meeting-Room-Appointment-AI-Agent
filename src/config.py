# src/config.py
"""Configuration file for the booking agent."""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta, datetime

# Load Environment Variables

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / '.env', override=True)

# App
PROJECT_NAME = os.environ["PROJECT_NAME"]
FLASK_SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

# LLM Configuration
TEMPERATURE = float(os.environ["TEMPERATURE"])
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

# File Paths
ROOMS_FILE = PROJECT_DIR / "data/rooms.json"
BOOKINGS_FILE = PROJECT_DIR / "data/bookings.json"
MSG_JSON_FILE = PROJECT_DIR / "data/clarification_messages.json"
LOGS_DIR = PROJECT_DIR / "logs"


# Logging Configuration
recursion_limit = 50
# sys.setrecursionlimit(recursion_limit)
DELAY = timedelta(hours=0.5)

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Create log file with current date
current_time = datetime.now().strftime('%Y-%m-%d_%H')
log_file_path = LOGS_DIR / f"{current_time}.log"

# Logging Configuration
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'  # Append mode to write in the same file for each run per day
)

logger = logging.getLogger(__name__)


class FlaskConfig:
    """Flask application configuration."""
    FLASK_APP = os.getenv('FLASK_APP', 'src.app')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    PORT = os.getenv('PORT', '5000')
    HOST = os.getenv('HOST', '127.0.0.1')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=5)