# src/booking_agent/workflow.py
"""Workflow using LangGraph for booking meeting rooms."""

from langgraph.graph import StateGraph, END
from booking_agent.schemas import AgentState
from booking_agent.nodes import (
    parse_request, ask_clarification, handle_error,
    find_matching_rooms, find_booking_options, 
    search_alternative_rooms, confirm_booking,
    select_room, inform_user,
    is_clear_request, is_confirmed
)

# Define constants for node names
PARSE_REQUEST = "parse_request_node"
ASK_CLARIFICATION = "ask_clarification_node"
HANDLE_ERROR = "handle_error_node"
FIND_MATCHING_ROOMS = "find_matching_rooms_node"
FIND_BOOKING_OPTIONS = "find_booking_options_node"
SEARCH_ALTERNATIVE_ROOMS = "search_alternative_rooms_node"
CHOOSE_ALTERNATIVE_ROOMS = "choose_alternative_rooms_node"
CONFIRM_BOOKING = "confirm_booking_node"
INFORM_USER = "inform_user_node"


def create_workflow():

    #########################################################################
    # SET WORKFLOW
    #########################################################################
    workflow = StateGraph(AgentState)
    workflow.set_state(AgentState.INITIAL)
    workflow.set_transition_logger(lambda from_node, to_node: print(f"Transition: {from_node} -> {to_node}"))

    #########################################################################
    # SET NODES
    #########################################################################
    workflow.add_node(PARSE_REQUEST, parse_request)
    workflow.add_node(ASK_CLARIFICATION, ask_clarification)
    workflow.add_node(HANDLE_ERROR, handle_error)
    workflow.add_node(FIND_MATCHING_ROOMS, find_matching_rooms)
    workflow.add_node(FIND_BOOKING_OPTIONS, find_booking_options)
    workflow.add_node(SEARCH_ALTERNATIVE_ROOMS, search_alternative_rooms)
    workflow.add_node(CHOOSE_ALTERNATIVE_ROOMS, select_room)
    workflow.add_node(CONFIRM_BOOKING, confirm_booking)
    workflow.add_node(INFORM_USER, inform_user)

    #########################################################################
    # SET EDGES
    #########################################################################
    # Edge: Parse request -> Clarify or Find matching rooms
    workflow.add_conditional_edges(
        PARSE_REQUEST,
        is_clear_request,
        {
            "ask_clarification": ASK_CLARIFICATION,
            "find_matching_rooms": FIND_MATCHING_ROOMS,
            "handle_error": HANDLE_ERROR
        }
    )

    # Edge: Find matching rooms -> Booking options or Alternative rooms
    workflow.add_conditional_edges(
        FIND_MATCHING_ROOMS,
        lambda state: True if len(state.get("matching_rooms", [])) > 0 else False,
        {
            True: FIND_BOOKING_OPTIONS,
            False: SEARCH_ALTERNATIVE_ROOMS
        }
    )

    # Edge: Find booking options -> Confirm booking or Handle error
    workflow.add_conditional_edges(
        FIND_BOOKING_OPTIONS,
        lambda state: True if len(state.get("available_rooms", [])) > 0 else False,
        {
            True: CONFIRM_BOOKING,
            False: HANDLE_ERROR
        }
    )

    # Edge: Confirm booking -> Inform user or Handle error
    workflow.add_conditional_edges(
        CONFIRM_BOOKING,
        is_confirmed,
        {
            True: INFORM_USER,
            False: HANDLE_ERROR
        }
    )
    
    # Edge: Search alternative rooms -> Choose alternative or Handle error
    workflow.add_conditional_edges(
        SEARCH_ALTERNATIVE_ROOMS,
        lambda state: True if len(state.get("alternative_rooms", [])) > 0 else False,
        {
            True: CHOOSE_ALTERNATIVE_ROOMS,
            False: HANDLE_ERROR
        }
    )

    # Edge: Choose alternative rooms -> Confirm booking or Handle error
    workflow.add_conditional_edges(
        CHOOSE_ALTERNATIVE_ROOMS,
        lambda state: True if len(state.get("alternative_rooms", [])) > 0 else False,
        {
            True: CONFIRM_BOOKING,
            False: HANDLE_ERROR
        }
    )

    # Edge: Confirm booking -> Inform user or Handle error
    # workflow.add_conditional_edges(
    #     CONFIRM_BOOKING,
    #     is_confirmed,
    #     {
    #         True: INFORM_USER,
    #         False: HANDLE_ERROR
    #     }
    # )
    # Edge: Inform user -> End
    workflow.add_edge(INFORM_USER, END)

    #########################################################################
    # SET ENTRY POINT
    #########################################################################
    workflow.set_entry_point(PARSE_REQUEST)

    return workflow.compile()
