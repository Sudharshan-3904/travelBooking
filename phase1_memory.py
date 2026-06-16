import argparse
from agents.mlflow_tracker import MLflowTracker
from agents.planner_agent import PlannerAgent, TravelRequest


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the TravelNet Phase 1 memory-enabled travel planner.")
    parser.add_argument("--origin", default="Seattle", help="Origin city for the travel request.")
    parser.add_argument("--destination", default="San Francisco", help="Destination city.")
    parser.add_argument("--departure", default="2026-09-15", help="Departure date (YYYY-MM-DD).")
    parser.add_argument("--return", default="2026-09-19", dest="return_date", help="Return date (YYYY-MM-DD).")
    parser.add_argument("--travelers", type=int, default=1, help="Number of travelers.")
    parser.add_argument("--budget", default="$1500", help="Budget guidance for the trip.")
    parser.add_argument("--preferences", default="Economy class, mid-range hotel, morning departure.", help="Traveler preferences.")
    parser.add_argument(
        "--memory", 
        default="conversation_memory", 
        choices=[
            "no_memory",
            "conversation_memory",
            "summary_memory",
            "vector_memory",
            "episodic_memory",
            "semantic_memory",
            "agent_specific_memory",
            "shared_memory",
            "hybrid_memory"
        ],
        help="Memory system architecture to activate."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    request = TravelRequest(
        origin=args.origin,
        destination=args.destination,
        departure_date=args.departure,
        return_date=args.return_date,
        travelers=args.travelers,
        budget=args.budget,
        preferences=args.preferences,
    )

    print(f"[*] Running Phase 1 (Memory Systems) with Memory: {args.memory}")
    planner = PlannerAgent()
    planner.load_config()
    planner.memory_type = args.memory
    
    plan = planner.plan_trip(request)
    itinerary = planner.build_itinerary(request, plan)

    print("\n=== Generated Itinerary ===")
    print(itinerary)

    with MLflowTracker() as tracker:
        tracker.log_params(
            {
                "origin": request.origin,
                "destination": request.destination,
                "departure_date": request.departure_date,
                "return_date": request.return_date,
                "travelers": request.travelers,
                "budget": request.budget,
                "preferences": request.preferences,
                "memory_system": args.memory,
                "build_phase": "Phase 1: Memory Systems"
            }
        )
        tracker.log_metrics(
            {
                "phases": 1,
                "agent_calls": 4,
                "memory_enabled": 1 if args.memory != "no_memory" else 0
            }
        )


if __name__ == "__main__":
    main()
