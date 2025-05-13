# src/mock_apis/room_services.py
import json
from pathlib import Path
from booking_agent.schemas import Room
from typing import List, Optional
from config import ROOMS_FILE

from langchain_core.tools import tool

def find_room_by_name(name: str) -> Optional[Room]:
    rooms = load_rooms()
    for room in rooms:
        if room.name.lower() == name.lower():
            return room
    return None

def find_room_by_id(id: int) -> Optional[Room]:
    rooms = load_rooms()
    for room in rooms:
        if room.id == id:
            return room
    return None

def find_room_by_capacity(capacity: int) -> Optional[Room]:
    rooms = load_rooms()
    for room in rooms:
        if room.capacity == capacity:
            return room
    return None

def is_exist_equipment(room: Room, equipments: List[str]) -> bool:
    return any(eq in room.equipments for eq in equipments)


def load_rooms(file_path: Path = ROOMS_FILE) -> List[Room]:
    with open(file_path, 'r') as f:
        return [Room(**room) for room in json.load(f)]

@tool("find_matching_rooms", description="Find rooms that match the required capacity and equipment.")
def find_matching_rooms_tool( capacity: int, equipments: List[str]) -> List[Room]:

    rooms = load_rooms()
    matching_rooms = []
    for room in rooms:
        if room.capacity >= capacity and is_exist_equipment(room, equipments):
            matching_rooms.append(room)
    return matching_rooms

@tool("find_similar_rooms", description="Find rooms with similar equipment and capacity.")
def find_similar_rooms_tool(capacity: int, equipments: list, top_n: int = 3) -> List[Room]:
    rooms = load_rooms()
    scored_rooms = []
    for room in rooms:
        if room.capacity >= capacity:
            overlap = len(set(room.equipments) & set(equipments))
            scored_rooms.append((overlap, room))
    scored_rooms.sort(reverse=True, key=lambda x: x[0])
    return [room for overlap, room in scored_rooms if overlap > 0][:top_n]

@tool("find_rooms_by_equipments", description="Find rooms that have all the specified equipment.")
def find_rooms_by_equipments_tool(equipments: List[str]) -> List[Room]:
    rooms = load_rooms()
    matching_rooms = []
    for room in rooms:
        if all(feature in room.equipments for feature in equipments):
            matching_rooms.append(room)
    return matching_rooms

