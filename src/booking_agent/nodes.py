# src/booking_agent/nodes.py

"""Individual nodes and conditions for the workflow of booking meeting rooms."""

from datetime import datetime
from langgraph.graph import END
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.tools import tool

from mock_apis.booking_services import (
    save_bookings_tool, check_time_conflict_tool
)

from mock_apis.room_services import (
    find_matching_rooms_tool, find_rooms_by_equipments_tool, 
    find_similar_rooms_tool, find_matching_rooms_tool
)

from booking_agent.schemas import AgentState, BookingRequest, Room
from helper import (
    get_llm, apply_prompt_template, 
    format_booking_rooms_msg, format_available_times_msg
)
from config import logger

##=======================================================================
# NODE FUNCTIONS
##=======================================================================
# NODE [01]. Parsing user requests Node
def parse_request(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: PARSE REQUEST ------------------ ")
    # initialization
    parser = PydanticOutputParser(pydantic_object=BookingRequest)
    prompt_template = apply_prompt_template(parser)
    llm = get_llm(name="groq")
    chain = prompt_template | llm | parser
    
    # get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')    # e.g, 2025-05-12
    current_time = datetime.now().strftime('%I:%M:%S %p') # e.g, 02:45:30 PM

    # logger.info(prompt_template)
    logger.info(" >>>>>>> CURRENT DATE:", current_date)
    logger.info(" >>>>>>> CURRENT TIME:", current_time)

    state["messages"].append(HumanMessage(content=state['user_input']))
    # Build full request context from conversation history
    conversation_context = "\n".join(
        f"{'USER' if isinstance(msg, HumanMessage) else 'AGENT'}: {msg.content}"
        for msg in state["messages"]
    )
    parsed_data = chain.invoke({"user_request": conversation_context,
                                "current_date": current_date,
                                "current_time": current_time})
    
    logger.info(f"PARSED REQUEST: {parsed_data.model_dump()}")

    state.update({
            "parsed_request": parsed_data.model_dump(),
            "clarification_needed": parsed_data.clarification_needed,
            "clarification_question": parsed_data.clarification_question,
            "user_name_for_booking": parsed_data.user_name,
            "error_message": None
        })
    
    return state

# NODE [02]. Ask Clarification Node
def ask_clarification(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: ASK CLARIFICATION ------------------ ")
    state["clarification_question"] = state["clarification_question"]
    state["messages"].append(SystemMessage(content=state["clarification_question"]))    
    return state

# NODE [03]. Handle Error Node
def handle_error(state: AgentState) -> AgentState:
    """
    Handle errors and provide feedback to the user.
    """
    logger.info(" ------------------ NODE: HANDLE ERROR ------------------ ")

    if state["matching_rooms"] is None:
        state["error_message"] = "No matching rooms found."

    elif state["available_rooms"] is None:
        state["error_message"] = "No available rooms found."
    else:
        state["error_message"] = "An unknown error occurred."

    logger.info(state["error_message"])
    state["llm_response"] = state.get("error_message", "An unknown error occurred.")
    state["messages"].append(SystemMessage(content=state["llm_response"]))
    state["clarification_needed"] = False
    return state

def find_matching_rooms(state: AgentState) -> AgentState:
    """
    Find all rooms that match the user's requirements (capacity, equipment).
    """
    logger.info(" ------------------ NODE: GET MATCHING ROOMS ------------------ ")
    
    capacity = state["parsed_request"]["capacity"]
    equipments = state["parsed_request"]["equipments"]
    matching_rooms = find_matching_rooms_tool(capacity, equipments)

    state["matching_rooms"] = matching_rooms # if len(matching_rooms) > 0 else None
    logger.info(" >>>>>>> MATCHING ROOMS: %s", state.get("matching_rooms", "NO MATCHING ROOMS"))
    
    return state

def find_booking_options(state: AgentState) -> bool:
    """
    For each matching room, check if it's available at the requested time.
    """
    logger.info(" ------------------ NODE: GET AVAILABLE ROOMS ------------------ ")
    
    available_rooms = []
    unavailable_rooms = []
    for room in state["matching_rooms"]:
        is_conflict = check_time_conflict_tool.run(
            room_id=room.id,
            start_time=state["parsed_request"]["start_time"],
            duration_hours=state["parsed_request"]["duration_hours"]
        )
        if not is_conflict: available_rooms.append(room)
        else: unavailable_rooms.append(room)

    state["available_rooms"] = available_rooms
    state["un_available_rooms"] = unavailable_rooms

    logger.info(" >>>>>>> UNAVAILABLE ROOMS:", state.get("un_available_rooms", "NO UNAVAILABLE ROOMS"))
    logger.info(" >>>>>>> AVAILABLE ROOMS:", state.get("available_rooms", "NO FREE AVAILABLE ROOMS"))
    # state["llm_response"] = format_booking_rooms_msg(state["available_rooms"])

    return state

def find_available_times(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: FIND AVAILABLE TIMES ------------------ ")

    available_times = {}
    for room in state["matching_rooms"]:
        available_times[room['type']] = booking_services.get_available_times(room['id'])

    state["llm_response"] = format_available_times_msg(available_times)
    state["messages"].append(SystemMessage(content=state["llm_response"]))

    return state

def select_room(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: SELECT ROOM ------------------ ")
    state["selected_room"] = state["available_rooms"][0]
    state["llm_response"] = format_booking_rooms_msg([state["selected_room"]])
    state["messages"].append(SystemMessage(content=state["llm_response"]))

    return state

def suggest_alternative_times(state: AgentState) -> AgentState:
    """
    For rooms that match requirements but are not available at the requested time, 
    the agent should find and suggest their next available time slots.
    """
    logger.info(" ------------------ NODE: SEARCH ALTERNATIVE TIMES ------------------ ")
    
    alternative_times = {}
    for room in state["matching_rooms"]:
        if room.type == state["selected_room"]["type"]:
            times = check_time_conflict_tool(room.id, 
                                             state["parsed_request"]["start_time"], 
                                             state["parsed_request"]["duration_hours"])
            alternative_times[room.id] = times

    state["llm_response"] = format_available_times_msg(alternative_times)
    state["messages"].append(SystemMessage(content=state["llm_response"]))

    return state

def confirm_booking(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: CONFIRM BOOKING ------------------ ")
    state["user_booking_confirmation"] = "yes"
    state["llm_response"] = "Booking Confirmed for room {}".format(state["selected_room"])
    return state

def find_booking_options(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: GET AVAILABLE ROOMS ------------------ ")
    pass

def inform_user(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: INFORM USER ------------------ ")
    state["messages"].append(SystemMessage(content=state["llm_response"]))
    return state
########################################################################
# CONDITIONS: 
########################################################################
# CONDITION [1]. Check Valid Request Condition
def is_clear_request(state: AgentState) -> str:
    logger.info(" --->>>> CONDITION: Check Valid and Clear Request <<<<--- ")
    if state.get("error_message"):
        logger.info(" >>>>>>> Error detected")
        return "handle_error"
    elif state.get("clarification_needed"):
        logger.info(" >>>>>>> Clarification needed")
        return "ask_clarification"
    else:
        logger.info(" >>>>>>> Ready to book room")
        return "find_matching_rooms"

# CONDITION [2]. Check if user confirm booking
def is_confirmed(state: AgentState) -> bool:
    logger.info(" --->>>> CONDITION: Check if user confirm booking <<<<--- ")
    if state["user_booking_confirmation"].lower() in ["yes", "y"]:
        return True
    else:
        state["clarification_needed"] = True
        state["clarification_question"] = "Booking Not Confimed. Do you want to book another room?"
        return False

def should_suggest_alternatives(state: AgentState) -> bool:
    
    return len(state.get("available_rooms", [])) == 0