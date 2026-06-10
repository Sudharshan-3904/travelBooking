from agents.base_agent import BaseAgent
from dataclasses import dataclass

@dataclass
class FlightSearchRequest:
    origin: str
    destination: str
    departure_date: str
    return_date: str
    travelers: int = 1
    preferences: str = ""

class FlightAgent(BaseAgent):
    def __init__(self, memory_type: str = "no_memory", sync_type: str = "direct_message"):
        super().__init__(name="FlightAgent", memory_type=memory_type, sync_type=sync_type)

    def search_flights(self, request: FlightSearchRequest) -> str:
        system_prompt = (
            "You are the Flight Specialist Agent. Provide a concise flight itinerary recommendation "
            "based on the traveler request and the actual search results provided."
        )
        
        try:
            import response
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import response
            
        actual_flights = response.query_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date
        )
        
        user_prompt = (
            f"Search flights from {request.origin} to {request.destination}. "
            f"Departure date: {request.departure_date}, Return date: {request.return_date}. "
            f"Travelers: {request.travelers}. Preferences: {request.preferences}.\n\n"
            f"Here are the actual available flights from the database:\n{actual_flights}"
        )
        return self.process_prompt(system_prompt, user_prompt)

    def search_flights_stream(self, request: FlightSearchRequest):
        system_prompt = (
            "You are the Flight Specialist Agent. Provide a concise flight itinerary recommendation "
            "based on the traveler request and the actual search results provided."
        )
        
        try:
            import response
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import response
            
        actual_flights = response.query_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date
        )
        
        user_prompt = (
            f"Search flights from {request.origin} to {request.destination}. "
            f"Departure date: {request.departure_date}, Return date: {request.return_date}. "
            f"Travelers: {request.travelers}. Preferences: {request.preferences}.\n\n"
            f"Here are the actual available flights from the database:\n{actual_flights}"
        )
        return self.process_prompt_stream(system_prompt, user_prompt)
