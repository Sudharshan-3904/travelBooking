from dataclasses import dataclass
from typing import Dict

from agents.base_agent import BaseAgent
from agents.budget_agent import BudgetAgent
from agents.flight_agent import FlightAgent, FlightSearchRequest
from agents.hotel_agent import HotelAgent, HotelSearchRequest
from agents.negotiation_agent import NegotiationAgent

@dataclass
class TravelRequest:
    origin: str
    destination: str
    departure_date: str
    return_date: str
    travelers: int = 1
    budget: str = ""
    preferences: str = ""

class PlannerAgent(BaseAgent):
    def __init__(self, memory_type: str = "no_memory", sync_type: str = "direct_message"):
        super().__init__(name="PlannerAgent", memory_type=memory_type, sync_type=sync_type)
        self.flight_agent = FlightAgent(memory_type=memory_type, sync_type=sync_type)
        self.hotel_agent = HotelAgent(memory_type=memory_type, sync_type=sync_type)
        self.budget_agent = BudgetAgent(memory_type=memory_type, sync_type=sync_type)
        self.negotiation_agent = NegotiationAgent(memory_type=memory_type, sync_type=sync_type)

    def set_model(self, model_name: str) -> None:
        super().set_model(model_name)
        self.flight_agent.set_model(model_name)
        self.hotel_agent.set_model(model_name)
        self.budget_agent.set_model(model_name)
        self.negotiation_agent.set_model(model_name)

    def plan_trip(self, request: TravelRequest) -> Dict[str, str]:
        flight_request = FlightSearchRequest(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            travelers=request.travelers,
            preferences=request.preferences,
        )

        hotel_request = HotelSearchRequest(
            destination=request.destination,
            check_in_date=request.departure_date,
            check_out_date=request.return_date,
            travelers=request.travelers,
            preferences=request.preferences,
        )

        flight_summary = self.flight_agent.search_flights(flight_request)
        hotel_summary = self.hotel_agent.search_hotels(hotel_request)
        budget_summary = self.budget_agent.analyze_budget(
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            travelers=request.travelers,
            flight_summary=flight_summary,
            hotel_summary=hotel_summary,
            user_budget=request.budget,
        )
        negotiation_summary = self.negotiation_agent.resolve_conflicts(
            flight_summary=flight_summary,
            hotel_summary=hotel_summary,
            budget_summary=budget_summary,
        )

        return {
            "destination": request.destination,
            "travel_window": f"{request.departure_date} to {request.return_date}",
            "flight_recommendation": flight_summary,
            "hotel_recommendation": hotel_summary,
            "budget_analysis": budget_summary,
            "negotiation_summary": negotiation_summary,
        }

    def build_itinerary(self, request: TravelRequest, plan: Dict[str, str]) -> str:
        return (
            "=== TravelNet Phase 0 Baseline Itinerary ===\n"
            f"Origin: {request.origin}\n"
            f"Destination: {request.destination}\n"
            f"Dates: {request.departure_date} -> {request.return_date}\n"
            f"Travelers: {request.travelers}\n"
            f"Budget guidance: {request.budget or 'default'}\n\n"
            "Flight Recommendation:\n"
            f"{plan['flight_recommendation']}\n\n"
            "Hotel Recommendation:\n"
            f"{plan['hotel_recommendation']}\n\n"
            "Budget Analysis:\n"
            f"{plan['budget_analysis']}\n\n"
            "Negotiation Summary:\n"
            f"{plan['negotiation_summary']}\n"
        )
