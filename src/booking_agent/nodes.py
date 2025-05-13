# src/booking_agent/nodes.py

"""Individual nodes and conditions for the workflow of booking meeting rooms."""
import random
from datetime import datetime
from langgraph.graph import END
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime, timedelta

from helper import *
from config import logger
from mock_apis.booking_services import *
from mock_apis.room_services import *
from booking_agent.schemas import AgentState, BookingRequest


##==============================================================================
# NODE FUNCTIONS
##==============================================================================
# NODE [01]. Parsing user requests Node
def parse_request(state: AgentState) -> AgentState:
    logger.info(" ------------------ NODE: PARSE REQUEST ------------------ ")

    ######################## (1.) Initialization ######################
    current_date = datetime.now().strftime('%Y-%m-%d')    # e.g, 2025-05-12
    current_time = datetime.now().strftime('%I:%M:%S %p') # e.g, 02:45:30 PM
    logger.info(" >>>>> CURRENT DATE: %s", current_date)
    logger.info(" >>>>> CURRENT TIME: %s", current_time)
    # Initialize parser used for user request parsing
    parser = PydanticOutputParser(pydantic_object=BookingRequest)
    # Apply template to the inputrequest to inject the predefined template prompt
    prompt_template = apply_prompt_template(parser)
    # Initialize LLM
    llm = initialize_llm(name="groq")
    # Create chain
    chain = prompt_template | llm | parser

    ############## (2.) Update conversation history ##################
    # logger.info(" >>>>> USER INPUT : %s", state['user_input'])
    state["messages"].append(HumanMessage(content=state['user_input']))
    # Build full request context from conversation history ####
    conversation_context = "\n".join(
        f"{'USER' if isinstance(msg, HumanMessage) else 'AGENT'}: {msg.content}"
        for msg in state["messages"]
    )
    logger.info("\n>>>>> CONVERSION CONTEXT: %s", conversation_context)

    ######################## (3.) Invoke chain ########################
    parsed_data = chain.invoke({"user_request": conversation_context,
                                "current_date": current_date,
                                "current_time": current_time})
    
    logger.info("\n >>>>>>> PARSED REQUEST: %s", parsed_data.model_dump())
    state.update({
        "parsed_request": parsed_data.model_dump(),
        "user_name_for_booking": parsed_data.user_name,
        })
    return state

# NODE [02]. Ask Clarification Node
def ask_clarification(state: AgentState) -> AgentState:
    """
    Add Clarification question to messages.
    """
    logger.info(" ------------------ NODE: ASK CLARIFICATION ------------------ ")

    try:
        clarification_msg = state['parsed_request']['clarification_question']
    except Exception as e:
        logger.error(f"LLM didn't respond by clarification question: {str(e)}")
        missed_fields = get_missing_fields(state["parsed_request"])
        # Retrieve random question from predefined list
        msgs = load_clarification_msgs()
        clarification_msg = random.choice(msgs[missed_fields[0]])

    
    state["clarification_question"] = clarification_msg
    # state["clarification_needed"] = False
    logger.info(f">>> CLARIFICATION QUESTION: {state['clarification_question']}")
    state["messages"].append(SystemMessage(content=state["clarification_question"]))

    return state

# NODE [03]. Handle Error Node
def handle_error(state: AgentState) -> AgentState:
    """
    Handle errors and provide appropriate feedback to the user.
    """
    logger.info(" ------------------ NODE: HANDLE ERROR ------------------ ")
    
    # Default error message
    error_msg = state.get("error_message", "An unknown error occurred.")
    
    # Customize error message based on state
    if not state.get("matching_rooms", []):
        error_msg = (
            "I couldn't find any rooms matching your requirements. "
            "You might want to try:\n"
            "- Reducing the required capacity\n"
            "- Adjusting the equipment requirements\n"
            "- Checking different dates or times"
        )
    elif not state.get("available_rooms", []):
        error_msg = (
            "The matching rooms are not available at your requested time. "
            "Would you like to:\n"
            "- See alternative time slots\n"
            "- Check similar rooms\n"
            "- Try a different date or time"
        )
    elif state.get("booking_result") is False:
        error_msg = (
            "I couldn't complete the booking. This might be because:\n"
            "- The room was just booked by someone else\n"
            "- There was a system error\n"
            "Would you like to try booking a different room?"
        )
    
    logger.info(" >>>>>>> ERROR MESSAGE: %s", error_msg)
    state["llm_response"] = error_msg
    state["messages"].append(SystemMessage(content=state["llm_response"]))
    
    # Set flags for next steps
    state["clarification_needed"] = True
    state["clarification_question"] = "Would you like to try a different search?"
    
    return state

# def find_matching_rooms(state: AgentState) -> AgentState:
#     """
#     Find all rooms that match the user's requirements (capacity, equipment).
#     """
#     logger.info(" ------------------ NODE: GET MATCHING ROOMS ------------------ ")
 
#     try:
#         capacity = state["parsed_request"]["capacity"]
#         equipments = state["parsed_request"].get("equipments", [])
        
#         matching_rooms = find_matching_rooms_tool.run(
#             capacity=capacity,
#             equipments=equipments
#         )
        
#         state["matching_rooms"] = matching_rooms
#         logger.info(" >>>>>>> MATCHING ROOMS: %s", 
#                     "NO MATCHING ROOMS" if len(matching_rooms) == 0 else state["matching_rooms"])
#         return state
        
#     except Exception as e:
#         logger.error(f"Error finding matching rooms: {str(e)}")
#         state["error_message"] = f"Failed to find matching rooms: {str(e)}"
#         state["matching_rooms"] = []
#         return state

# def find_booking_options(state: AgentState) -> AgentState:
#     """
#     For each matching room, check if it's available at the requested time.
#     """
#     logger.info(" ------------------ NODE: GET AVAILABLE ROOMS ------------------ ")
    
#     available_rooms = []
#     unavailable_rooms = []
    
#     try:
#         for room in state["matching_rooms"]:
#             is_conflict = check_time_conflict_tool.run(
#                 room_id=room.id,
#                 start_time=state["parsed_request"]["start_time"],
#                 duration_hours=state["parsed_request"]["duration_hours"]
#             )
            
#             if not is_conflict: available_rooms.append(room)
#             else: unavailable_rooms.append(room)

#         logger.info(" >>>>>>> AVAILABLE ROOMS: %s",
#                    "NO AVAILABLE ROOMS" if not available_rooms else available_rooms)
        
#         state["available_rooms"] = available_rooms
#         state["unavailable_rooms"] = unavailable_rooms
        
#     except Exception as e:
#         logger.error(f"Error checking room availability: {str(e)}")
#         state["error_message"] = f"Failed to check room availability: {str(e)}"
#         state["available_rooms"] = []
#         state["unavailable_rooms"] = []

#     logger.info(" >>>>>>> UNAVAILABLE ROOMS:", state.get("un_available_rooms", "NO UNAVAILABLE ROOMS"))
#     logger.info(" >>>>>>> AVAILABLE ROOMS:", state.get("available_rooms", "NO FREE AVAILABLE ROOMS"))
#     # state["llm_response"] = format_booking_rooms_msg(state["available_rooms"])

#     return state

# def find_available_times(state: AgentState) -> AgentState:
#     """
#     Find available time slots for matching rooms.
#     """
#     logger.info(" ------------------ NODE: FIND AVAILABLE TIMES ------------------ ")
    
#     try:
#         available_times = {}
#         for room in state.get("matching_rooms", []):
#             times = check_time_conflict_tool.run(
#                 room_id=room.id,
#                 start_time=state["parsed_request"]["start_time"],
#                 duration_hours=state["parsed_request"]["duration_hours"]
#             )
#             if times:
#                 available_times[room.name] = times
                
#         if available_times:
#             state["llm_response"] = format_available_times_msg(available_times)
#         else:
#             state["llm_response"] = "I couldn't find any available time slots for the matching rooms."
#             state["error_message"] = "No available time slots found"
            
#     except Exception as e:
#         logger.error(f"Error finding available times: {str(e)}")
#         state["error_message"] = f"Failed to find available times: {str(e)}"
#         state["llm_response"] = "Sorry, I encountered an error while searching for available times."
    
#     state["messages"].append(SystemMessage(content=state["llm_response"]))
#     return state

# def select_room(state: AgentState) -> AgentState:
#     """
#     Select a room from the available alternatives.
#     """
#     logger.info(" ------------------ NODE: SELECT ROOM ------------------ ")
    
#     try:
#         available_rooms = state.get("alternative_rooms", [])
#         if available_rooms:
#             selected = available_rooms[0]
#             state["selected_room"] = selected
#             state["llm_response"] = (
#                 f"I've selected {selected.name} for you which has:\n"
#                 f"- Capacity: {selected.capacity} people\n"
#                 f"- Equipment: {', '.join(selected.equipments)}"
#             )
#         else:
#             state["selected_room"] = None
#             state["llm_response"] = "No suitable room found to select."
            
#     except Exception as e:
#         logger.error(f"Error selecting room: {str(e)}")
#         state["error_message"] = f"Failed to select room: {str(e)}"
#         state["selected_room"] = None
#         state["llm_response"] = "Sorry, I encountered an error while selecting a room."
    
#     state["messages"].append(SystemMessage(content=state["llm_response"]))
#     return state

# def suggest_alternative_times(state: AgentState) -> AgentState:
#     """
#     For rooms that match requirements but are not available at the requested time,
#     the agent should find and suggest their next available time slots.
#     """
#     logger.info(" ------------------ NODE: SEARCH ALTERNATIVE TIMES ------------------ ")
    
#     try:
#         if not state.get("selected_room"):
#             raise ValueError("No room selected to find alternatives for")
            
#         alternative_times = {}
#         for room in state.get("matching_rooms", []):
#             times = check_time_conflict_tool.run(
#                 room_id=room.id,
#                 start_time=state["parsed_request"]["start_time"],
#                 duration_hours=state["parsed_request"]["duration_hours"]
#             )
#             if times:
#                 alternative_times[room.id] = times

#         if alternative_times:
#             state["llm_response"] = format_available_times_msg(alternative_times)
#         else:
#             state["llm_response"] = "Sorry, I couldn't find any alternative times for the rooms."
#             state["error_message"] = "No alternative times available"
            
#     except Exception as e:
#         logger.error(f"Error finding alternative times: {str(e)}")
#         state["error_message"] = f"Failed to find alternative times: {str(e)}"
#         state["llm_response"] = "Sorry, I encountered an error while searching for alternative times."
    
#     state["messages"].append(SystemMessage(content=state["llm_response"]))
#     return state
# def confirm_booking(state: AgentState) -> AgentState:
#     """
#     Complete the booking process and save the booking record.
#     """
#     logger.info(" ------------------ NODE: CONFIRM BOOKING ------------------ ")
    
#     try:
#         if not state.get("selected_room"):
#             raise ValueError("No room selected for booking")
            
#         booking_data = state["parsed_request"]
#         room = state["selected_room"]
        
#         end_time = datetime.fromisoformat(booking_data["start_time"]) + \
#                    timedelta(hours=booking_data["duration_hours"])
        
#         # Create the booking using the tool
#         booking_result = book_room_tool.run(
#             room_id=room.id,
#             start_time=booking_data["start_time"],
#             end_time=end_time.isoformat(),
#             user_name=booking_data["user_name"]
#         )
        
#         state["booking_result"] = True if booking_result else False
#         if booking_result:
#             state["user_booking_confirmation"] = "yes"
#             state["llm_response"] = f"Successfully booked {room.name} for you!"
#         else:
#             raise ValueError("Booking creation failed")
            
#     except Exception as e:
#         logger.error(f"Booking failed: {str(e)}")
#         state["booking_result"] = False
#         state["error_message"] = f"Failed to complete the booking: {str(e)}"
#         state["user_booking_confirmation"] = "no"
    
#     return state

# def search_alternative_rooms(state: AgentState) -> AgentState:
#     """
#     Search for alternative rooms when no exact matches are found.
#     Uses similarity matching to find rooms with close specifications.
#     """
#     logger.info(" ------------------ NODE: SEARCH ALTERNATIVE ROOMS ------------------ ")
    
#     try:
#         capacity = state["parsed_request"]["capacity"]
#         equipments = state["parsed_request"].get("equipments", [])
        
#         # Find similar rooms using the similarity tool
#         alternative_rooms = find_similar_rooms_tool.run(
#             capacity=capacity,
#             equipments=equipments
#         )
        
#         state["alternative_rooms"] = alternative_rooms if alternative_rooms else []
        
#         if alternative_rooms:
#             logger.info(f" >>>>>>> FOUND {len(alternative_rooms)} ALTERNATIVE ROOMS")
#             state["llm_response"] = "I found some alternative rooms that might work for you: \n" + \
#                 "\n".join([f"- {room.name}: Capacity {room.capacity}, Equipment: {', '.join(room.equipments)}"
#                           for room in alternative_rooms])
#         else:
#             logger.info(" >>>>>>> NO ALTERNATIVE ROOMS FOUND")
#             state["llm_response"] = "I couldn't find any alternative rooms matching your requirements."
            
#     except Exception as e:
#         logger.error(f"Error finding alternative rooms: {str(e)}")
#         state["error_message"] = f"Failed to find alternative rooms: {str(e)}"
#         state["alternative_rooms"] = []
#         state["llm_response"] = "Sorry, I encountered an error while searching for alternative rooms."
    
#     state["messages"].append(SystemMessage(content=state["llm_response"]))
#     return state

# def inform_user(state: AgentState) -> AgentState:
#     """
#     Inform the user about the booking status and provide relevant information.
#     """
#     logger.info(" ------------------ NODE: INFORM USER ------------------ ")
    
#     try:
#         if state.get("booking_result"):
#             booking = state.get("parsed_request", {})
#             room = state.get("selected_room", {})
            
#             # Handle equipment list formatting
#             equipments = room.get("equipments", [])
#             equipment_str = ", ".join(equipments) if equipments else "No special equipment"
            
#             state["llm_response"] = (
#                 f"Great! I've successfully booked {room.get('name', 'the room')} for you:\n"
#                 f"- Date: {booking.get('start_date', 'N/A')}\n"
#                 f"- Time: {booking.get('start_time', 'N/A')} "
#                 f"(for {booking.get('duration_hours', 0)} hours)\n"
#                 f"- Booked under: {booking.get('user_name', 'N/A')}\n"
#                 f"- Room capacity: {room.get('capacity', 'N/A')} people\n"
#                 f"- Equipment: {equipment_str}\n\n"
#                 f"Your booking has been confirmed and saved. You'll receive a notification "
#                 f"with the booking details."
#             )
#         else:
#             state["llm_response"] = (
#                 "I'm sorry, but the booking couldn't be completed. "
#                 "Would you like to:\n"
#                 "- Try booking a different room\n"
#                 "- Check alternative time slots\n"
#                 "- Start a new search"
#             )
#             state["clarification_needed"] = True
            
#     except Exception as e:
#         logger.error(f"Error formatting user response: {str(e)}")
#         state["error_message"] = f"Failed to format response: {str(e)}"
#         state["llm_response"] = "Sorry, I encountered an error while preparing the booking confirmation."
    
#     state["messages"].append(SystemMessage(content=state["llm_response"]))
#     return state
