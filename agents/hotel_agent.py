from agents.base_agent import BaseAgent
from dataclasses import dataclass

@dataclass
class HotelSearchRequest:
    destination: str
    check_in_date: str
    check_out_date: str
    travelers: int = 1
    preferences: str = ""

class HotelAgent(BaseAgent):
    def __init__(self, memory_type: str = "no_memory", sync_type: str = "direct_message"):
        super().__init__(name="HotelAgent", memory_type=memory_type, sync_type=sync_type)

    def search_hotels(self, request: HotelSearchRequest) -> str:
        system_prompt = (
            "You are the Hotel Specialist Agent. Provide accommodation recommendations and a simple cost summary "
            "based on the actual hotel search results provided."
        )
        
        try:
            import response
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import response
            
        actual_hotels = response.query_hotels(destination=request.destination)
        
        user_prompt = (
            f"Search hotels in {request.destination}. "
            f"Check-in: {request.check_in_date}, Check-out: {request.check_out_date}. "
            f"Travelers: {request.travelers}. Preferences: {request.preferences}.\n\n"
            f"Here are the actual available hotels from the database:\n{actual_hotels}"
        )
        return self.process_prompt(system_prompt, user_prompt)

    def search_hotels_stream(self, request: HotelSearchRequest):
        system_prompt = (
            "You are the Hotel Specialist Agent. Provide accommodation recommendations and a simple cost summary "
            "based on the actual hotel search results provided."
        )
        
        try:
            import response
        except ImportError:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import response
            
        actual_hotels = response.query_hotels(destination=request.destination)
        
        user_prompt = (
            f"Search hotels in {request.destination}. "
            f"Check-in: {request.check_in_date}, Check-out: {request.check_out_date}. "
            f"Travelers: {request.travelers}. Preferences: {request.preferences}.\n\n"
            f"Here are the actual available hotels from the database:\n{actual_hotels}"
        )
        return self.process_prompt_stream(system_prompt, user_prompt)
