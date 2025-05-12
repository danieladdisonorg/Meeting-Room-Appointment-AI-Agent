# src/booking_agent/nodes.py

"""Individual nodes and conditions for the workflow of booking meeting rooms."""

from datetime import datetime
from langgraph.graph import END
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from booking_agent.schemas import AgentState, BookingRequest
from helper import get_llm, apply_prompt_template

REQUIRED_FIELDS = ["start_time", "duration_hours", "capacity", "equipments", "user_name"]

########################################################################
# NODES: 
########################################################################
def parse_request(state: AgentState) -> AgentState:
    print("---NODE: PARSE REQUEST---")
    # initialize parser
    parser = PydanticOutputParser(pydantic_object=BookingRequest)
    # apply my predefined prompt template
    prompt_template = apply_prompt_template(parser)
    # get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    # define LLM and the Chain
    llm = get_llm(name="groq")
    chain = prompt_template | llm | parser

    state["messages"].append(HumanMessage(content=state['user_input']))
    # Build full request context from conversation history
    conversation_context = "\n".join(
        f"{'USER' if isinstance(msg, HumanMessage) else 'AGENT'}: {msg.content}"
        for msg in state["messages"]
    )

    parsed_data = chain.invoke({"user_request": conversation_context,
                                "current_date": current_date})
    state.update({
            "parsed_request": parsed_data.model_dump(),
            "clarification_needed": parsed_data.clarification_needed,
            "clarification_question": parsed_data.clarification_question,
            "user_name_for_booking": parsed_data.user_name,
            "error_message": None
        })
        
    return state

def ask_clarification(state: AgentState) -> AgentState:
    print("---NODE: ASK CLARIFICATION---")
    state["clarification_question"] = state["clarification_question"]
    state["messages"].append(SystemMessage(content=state["clarification_question"]))    
    return state


def handle_error(state: AgentState) -> AgentState:
    state["llm_response"] = state.get("error_message", "An unknown error occurred.")
    state["messages"].append(SystemMessage(content=state["llm_response"]))
    state["clarification_needed"] = False
    return END
   
def book_room(state: AgentState) -> AgentState:
    # In a real workflow, you'd call your booking API here
    state["final_response_to_user"] = "Booking room..."
    return state

########################################################################
# CONDITIONS: 
########################################################################

# Check if request is valid and clear
def is_clear_request(state: AgentState) -> str:
    print("---CONDITION: Check Valid and Clear Request---")
    if state.get("error_message"):
        print("----> Error detected")
        return "handle_error"
    elif state.get("clarification_needed"):
        print("----> Clarification needed")
        return "ask_clarification"
    else:
        print("----> Ready to book room")
        return "book_room"
