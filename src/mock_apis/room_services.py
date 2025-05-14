# src/mock_apis/room_services.py
import json
from pathlib import Path
from typing import List, Dict
from config import ROOMS_FILE
from helper import *
# from langchain_core.tools import tool

def check_room_availability_equipment(room: Dict, equipments: List[str]) -> bool:
    """
    Check if the room has all the specified equipment.
    """
    for eq in equipments:
        if eq == "nothing": 
            continue
        if eq not in room['equipments']:
            return False
    return True

# @tool("load_rooms", description="Load existing room options from external file. ")
def load_rooms(filepath: Path = ROOMS_FILE) -> List[Dict]:
    """
    Load existing room options from external file. 
    """
    existing_data: List[Dict] = [{}]
    try:
        with open(filepath, "r") as f:
            existing_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode existing JSON in {filepath}. Starting fresh.")
        existing_data = {}
    return existing_data


# @tool("find_matching_rooms", description="Find rooms that match the required capacity and equipment.")
def find_matching_rooms_tool(existing_rooms: List[Dict], capacity: int, equipments: List[str]) -> List[Dict]:
    """
    Find rooms that match the required capacity and equipment.
    """
    matching_rooms = []
    for room in existing_rooms:
        if room['capacity'] >= capacity and check_room_availability_equipment(room, equipments):
            matching_rooms.append(room)
    return matching_rooms

# @tool("find_similar_rooms", description="Find rooms with similar equipment and capacity.")
# def find_similar_rooms_tool(capacity: int, equipments: list, top_n: int = 3) -> List[Dict]:
#     rooms = load_rooms()
#     scored_rooms = []
#     for room in rooms:
#         if room.capacity >= capacity:
#             overlap = len(set(room.equipments) & set(equipments))
#             scored_rooms.append((overlap, room))
#     scored_rooms.sort(reverse=True, key=lambda x: x[0])
#     return [room for overlap, room in scored_rooms if overlap > 0][:top_n]

# @tool("find_rooms_by_equipments", description="Find rooms that have all the specified equipment.")
# def find_rooms_by_equipments_tool(equipments: List[str]) -> List[Room]:
#     rooms = load_rooms()
#     matching_rooms = []
#     for room in rooms:
#         if all(feature in room.equipments for feature in equipments):
#             matching_rooms.append(room)
#     return matching_rooms

# @tool("find_rooms_by_capacity", description="Find rooms that have a capacity greater than or equal to the specified value.")
# def find_rooms_by_capacity_tool(capacity: int) -> List[Room]:
#     rooms = load_rooms()
#     matching_rooms = []
#     for room in rooms:
#         if room.capacity >= capacity:
#             matching_rooms.append(room)
#     return matching_rooms
