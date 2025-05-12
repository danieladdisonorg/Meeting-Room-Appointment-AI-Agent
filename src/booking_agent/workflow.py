# src/booking_agent/workflow.py
"""Workflow using LangGraph for booking meeting rooms."""

from langgraph.graph import StateGraph, END
from booking_agent.schemas import AgentState
from booking_agent.nodes import (
    parse_request, ask_clarification, book_room, handle_error,
    is_clear_request
)

def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_request", parse_request)
    workflow.add_node("ask_clarification", ask_clarification)
    workflow.add_node("book_room", book_room)
    workflow.add_node("handle_error", handle_error)

    # Set edges
    workflow.set_entry_point("parse_request")
    
    workflow.add_conditional_edges(
        "parse_request",
        is_clear_request,
        {
            "ask_clarification": "ask_clarification",
            "book_room": "book_room",
            "handle_error": "handle_error"
        }
    )
    
    workflow.add_edge("ask_clarification", END)  # Pauses for user input
    workflow.add_edge("book_room", END)
    workflow.add_edge("handle_error", END)
    
    return workflow.compile()
