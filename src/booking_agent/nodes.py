# src/booking_agent/nodes.py

"""Individual nodes and conditions for the workflow of booking meeting rooms."""

from datetime import datetime
from langgraph.graph import END
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from mock_apis import booking_services, room_services
from booking_agent.schemas import AgentState, BookingRequest, Room
from helper import get_llm, apply_prompt_template
from config import logger

##=======================================================================
# NODE FUNCTIONS
##=======================================================================
# NODE [01]. Parsing user requests Node
def parse_request(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: PARSE REQUEST ------------------ ")
    # initialize parser
    parser = PydanticOutputParser(pydantic_object=BookingRequest)
    # apply my predefined prompt template
    prompt_template = apply_prompt_template(parser)
    # get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S') # AM or PM?

    # define LLM and the Chain
    llm = get_llm(name="groq")
    chain = prompt_template | llm | parser

    logger.info(">>>>>>>>>>>>>>> CURRENT DATE:", current_date)
    logger.info(">>>>>>>>>>>>>>> CURRENT TIME:", current_date)

    state["messages"].append(HumanMessage(content=state['user_input']))
    # Build full request context from conversation history
    conversation_context = "\n".join(
        f"{'USER' if isinstance(msg, HumanMessage) else 'AGENT'}: {msg.content}"
        for msg in state["messages"]
    )
    parsed_data = chain.invoke({"user_request": conversation_context,
                                "current_date": current_date,
                                "current_time": current_time})
    
    logger.info(f"PARSED REQUEST: {state['parsed_request']}")

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
    logger.info(" ------------------ NODE: HANDLE ERROR ------------------ ")
    state["llm_response"] = state.get("error_message", "An unknown error occurred.")
    state["messages"].append(SystemMessage(content=state["llm_response"]))
    state["clarification_needed"] = False
    return END

def find_matching_rooms(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: GET MATCHING ROOMS ------------------ ")
    capacity = state["parsed_request"]["capacity"]
    equipments = state["parsed_request"]["equipments"]
    matching_rooms = room_services.find_matching_rooms(capacity, equipments)
    state["matching_rooms"] = matching_rooms if len(matching_rooms) > 0 else None
    return state

def find_booking_options(state: AgentState) -> bool:
    logger.info(" ------------------ NODE: GET AVAILABLE ROOMS ------------------ ")
    
    available_rooms = []
    for room in state["matching_rooms"]:
        is_conflict = booking_services.is_time_conflict(room['id'],
                                                        state["parsed_request"]["start_time"],
                                                        state["parsed_request"]["duration_hours"])
        if is_conflict: continue
        else: available_rooms.append(room)
    
    state["available_room_options"] = available_rooms if len(available_rooms)>0 else None
    
    return state

def select_room(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: SELECT ROOM ------------------ ")
    state["selected_room"] = state["available_room_options"][0]
    return state

def search_alternative_rooms(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: SEARCH ALTERNATIVE ROOMS ------------------ ")
    return state

def confirm_booking(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: CONFIRM BOOKING ------------------ ")
    state["user_booking_confirmation"] = "yes"
    state["llm_response"] = "Booking Confirmed for room {}".format(state["selected_room"])
    return state

def find_booking_options(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: GET AVAILABLE ROOMS ------------------ ")
    state = find_booking_options(state)
    state = select_room(state)
    state = confirm_booking_node(state)
    return state

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
        logger.info("----> Error detected")
        return "handle_error"
    elif state.get("clarification_needed"):
        logger.info("----> Clarification needed")
        return "ask_clarification"
    else:
        logger.info("----> Ready to book room")
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

