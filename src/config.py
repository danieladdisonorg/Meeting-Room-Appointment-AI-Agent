# src/config.py
"""Configuration file for the booking agent."""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta, datetime

# Load Environment Variables
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
# load_dotenv(dotenv_path=dotenv_path, override=True)

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / '.env', override=True)

# App
PROJECT_NAME = os.environ["PROJECT_NAME"]
FLASK_SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

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

# File Paths
ROOMS_FILE = PROJECT_DIR / "data/rooms.json"
BOOKINGS_FILE = PROJECT_DIR / "data/bookings.json"
LOGS_DIR = PROJECT_DIR / "logs"


# Logging Configuration
recursion_limit = 50
# sys.setrecursionlimit(recursion_limit)
DELAY = timedelta(hours=0.5)

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Create log file with current date
current_date = datetime.now().strftime("%Y-%m-%d")
log_file_path = LOGS_DIR / f"log_{current_date}.log"

# Logging Configuration
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'  # Append mode to write in the same file for each run per day
)

logger = logging.getLogger(__name__)


class FlaskConfig:
    FLASK_APP = os.getenv('FLASK_APP', 'src.app')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)