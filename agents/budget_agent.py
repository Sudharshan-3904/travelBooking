from agents.base_agent import BaseAgent
from typing import Optional

class BudgetAgent(BaseAgent):
    def __init__(self, memory_type: str = "no_memory", sync_type: str = "direct_message"):
        super().__init__(name="BudgetAgent", memory_type=memory_type, sync_type=sync_type)

    def analyze_budget(
        self,
        destination: str,
        departure_date: str,
        return_date: str,
        travelers: int,
        flight_summary: str,
        hotel_summary: str,
        user_budget: Optional[str] = None,
    ) -> str:
        system_prompt = (
            "You are the Budget Specialist Agent. Analyze the estimated travel cost and indicate if the itinerary fits the budget."
        )
        user_prompt = (
            f"Destination: {destination}. Departure date: {departure_date}. Return date: {return_date}. "
            f"Travelers: {travelers}. Budget guidance: {user_budget or 'not specified'}. "
            f"Flight summary: {flight_summary}. Hotel summary: {hotel_summary}."
        )
        return self.process_prompt(system_prompt, user_prompt)

    def analyze_budget_stream(
        self,
        destination: str,
        departure_date: str,
        return_date: str,
        travelers: int,
        flight_summary: str,
        hotel_summary: str,
        user_budget: Optional[str] = None,
    ):
        system_prompt = (
            "You are the Budget Specialist Agent. Analyze the estimated travel cost and indicate if the itinerary fits the budget."
        )
        user_prompt = (
            f"Destination: {destination}. Departure date: {departure_date}. Return date: {return_date}. "
            f"Travelers: {travelers}. Budget guidance: {user_budget or 'not specified'}. "
            f"Flight summary: {flight_summary}. Hotel summary: {hotel_summary}."
        )
        return self.process_prompt_stream(system_prompt, user_prompt)
