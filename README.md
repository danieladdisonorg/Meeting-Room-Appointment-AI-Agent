# Meeting Room Booking Agent

A LangGraph-based AI agent to help users find and reserve meeting rooms. The system uses Groq API (with support for other LLMs like Ollama) and implements a complete booking workflow with room availability checks.

<p align="center">
  <img src="docs\chatbot.jpg" alt="chatbot" width="80%"/>
</p>

## Features

- Natural language processing for meeting room requests
- Room availability checking and booking
- Flexible workflow with user clarification loops
- Simple web interface for interaction
- JSON-based database for prototyping

## Components

1. **User Interface (UI):** For interacting with the user. I used simple html ans css template for prototyping.
2. **AI Agent :** Use `LangGraph` with LLM for booking rooms using main `Groq API` and support other LLMs like Ollama.
3. **Room and Booking Database:** Simple Json files as a dummy NoSQL data.
4. **Calendar Booking System:** Mock API for availability and bookings.

<p align="center">
  <img src="docs\system_architecture.svg" alt="System Architecture" width="80%"/>
</p>

## Setup
### Prerequisites
- Python 3.11.0 or higher
- Conda (Miniconda or Anaconda)

### 1. Create Conda Environment

```bash
conda create -n agentic_env python=3.11 -y
conda activate agentic_env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root with your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
```

### Running the Application

```bash
conda activate agentic_env
flask run
```

The web interface will be available at `http://localhost:5000`

## Project Structure

```
room_booking_agent/
│   app.py                - Main Flask application
│   config.py             - Configuration settings
│   helper.py             - Utility functions
│   
├───booking_agent         - Core agent components
│       conditions.py      - Transition conditions
│       nodes.py           - Nodes defination
│       prompt_config.py   - System prompts template text
│       schemas.py         - Pydantic models
│       workflow.py        - LangGraph workflow definition
│
├───mock_apis             - Mock services
│       booking_services.py - Booking API simulation
│       room_services.py   - Room data service
│
├───static                 - Web assets
│       style.css       
│
└───templates             - HTML templates
        index.html        - Main interface
```

## Supported LLMs

The system primarily uses Groq API with LLaMA3-8b, but can be configured to use:

1. Groq (default)
2. Ollama (local models)
3. Other compatible LLMs via LangChain


## Data Storage

The system uses JSON files for prototyping:

- `data/rooms.json` - Room definitions
- `data/bookings.json` - Current bookings
- `data/clarification_messages.json` - clarification messages for each un-defined field to cover the `clarification_question` response in case of no response from the LLM.

## Workflow Diagram

<p align="center">
  <img src="docs\flowchart.svg" alt="Agent Flowchart" width="80%"/>
</p>
