from agents.base_agent import BaseAgent

class NegotiationAgent(BaseAgent):
    def __init__(self, memory_type: str = "no_memory", sync_type: str = "direct_message"):
        super().__init__(name="NegotiationAgent", memory_type=memory_type, sync_type=sync_type)

    def resolve_conflicts(self, flight_summary: str, hotel_summary: str, budget_summary: str) -> str:
        system_prompt = (
            "You are the Negotiation Specialist Agent. Identify any conflicts between the proposed flight, hotel, and budget recommendations, "
            "then propose a small set of practical alternatives."
        )
        user_prompt = (
            f"Flight summary: {flight_summary}. Hotel summary: {hotel_summary}. Budget summary: {budget_summary}."
        )
        return self.process_prompt(system_prompt, user_prompt)

    def resolve_conflicts_stream(self, flight_summary: str, hotel_summary: str, budget_summary: str):
        system_prompt = (
            "You are the Negotiation Specialist Agent. Identify any conflicts between the proposed flight, hotel, and budget recommendations, "
            "then propose a small set of practical alternatives."
        )
        user_prompt = (
            f"Flight summary: {flight_summary}. Hotel summary: {hotel_summary}. Budget summary: {budget_summary}."
        )
        return self.process_prompt_stream(system_prompt, user_prompt)
