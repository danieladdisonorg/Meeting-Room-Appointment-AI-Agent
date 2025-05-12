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

def create_workflow():
    workflow = StateGraph(AgentState)
    
    # 1. Add nodes
    workflow.add_node("parse_request_node", parse_request)
    workflow.add_node("ask_clarification_node", ask_clarification)
    workflow.add_node("handle_error_node", handle_error)
    workflow.add_node("find_matching_rooms_node", find_matching_rooms)
    workflow.add_node("find_booking_options_node", find_booking_options)
    workflow.add_node("search_alternative_rooms_node", search_alternative_rooms)
    workflow.add_node("choose_alternative_rooms_node", select_room)
    workflow.add_node("confirm_booking_node", confirm_booking)
    workflow.add_node("Inform_user_node", inform_user)
    # 2. Set edges    
    workflow.add_conditional_edges(
        "parse_request_node",
        is_clear_request,
        {
            "ask_clarification": "ask_clarification_node",
            "find_matching_rooms": "find_matching_rooms_node",
            "handle_error": "handle_error_node"
        }
    )

    workflow.add_conditional_edges(
        "find_matching_rooms_node",
        lambda state: state["matching_rooms"] is not None,
        {
            True: "find_booking_options_node",
            False: "search_alternative_rooms_node"
        }
    )

    workflow.add_conditional_edges(
        "find_booking_options_node",
        lambda state: state["available_room_options"] is not None,
        {
            True: "confirm_booking_node",
            False: "handle_error_node"
        }
    )

    workflow.add_conditional_edges(
        "confirm_booking_node",
        is_confirmed,
        {
            True: "Inform_user_node",
            False: "handle_error_node"
        }
    )

    workflow.add_conditional_edges(
        "search_alternative_rooms_node",
        lambda state: state["alternative_rooms"] is not None,
        {
            True: "choose_alternative_rooms_node",
            False: "handle_error_node"
        }
    )

    workflow.add_conditional_edges(
        "choose_alternative_rooms_node",
        lambda state: state["alternative_rooms"] is not None,
        {
            True: "confirm_booking_node",
            False: "handle_error_node"
        }
    )


    workflow.add_conditional_edges(
        "choose_alternative_rooms_node",
        is_confirmed,{
            True: "Inform_user_node",
            False: "handle_error_node"
        }
    )

    workflow.add_edge("Inform_user_node", END)

    # 3. Set entry point
    workflow.set_entry_point("parse_request_node")

    return workflow.compile()
