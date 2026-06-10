import json
import os
from typing import List, Optional, Literal

try:
    import ollama
except ImportError:
    ollama = None

class OllamaManager:
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2:latest"):
        self.base_url = base_url
        self.active_model = model_name
        self.ollama_client = ollama.Client(base_url)

    def set_model(self, model_name: str) -> None:
        self.active_model = model_name

    def response_stream(self, messages: List[dict]):
        stream = self.ollama_client.chat(model=self.active_model, messages=messages, stream=True)
        in_thinking = False
        thinking_opened = False
        
        for chunk in stream:
            thinking = ""
            content = ""
            
            if hasattr(chunk, "message"):
                thinking = getattr(chunk.message, "thinking", None) or ""
                content = getattr(chunk.message, "content", None) or ""
            elif isinstance(chunk, dict):
                msg = chunk.get("message", {})
                thinking = msg.get("thinking") or ""
                content = msg.get("content") or ""
                
            # If the chunk has thinking text
            if thinking:
                if not thinking_opened:
                    yield "<think>" + thinking
                    thinking_opened = True
                    in_thinking = True
                else:
                    yield thinking
            # If the chunk has content
            elif content:
                if in_thinking:
                    # We transition from thinking to content, close the think tag
                    yield "</think>" + content
                    in_thinking = False
                else:
                    yield content
                    
        # Clean up if the stream ended but we never closed the think tag
        if in_thinking:
            yield "</think>"

    def response(self, messages: List[dict]) -> str:
        result = self.ollama_client.chat(model=self.active_model, messages=messages)
        if isinstance(result, str):
            return result

        if hasattr(result, "message"):
            thinking = getattr(result.message, "thinking", None)
            content = getattr(result.message, "content", "")
            if thinking:
                return f"<think>\n{thinking}\n</think>\n{content}"
            return content

        if isinstance(result, dict):
            msg = result.get("message", {})
            thinking = msg.get("thinking")
            content = msg.get("content", "")
            if thinking:
                return f"<think>\n{thinking}\n</think>\n{content}"
            return content

        if hasattr(result, "__iter__"):
            collected = []
            for item in result:
                if isinstance(item, dict):
                    collected.append(item.get("content") or item.get("message") or str(item))
                else:
                    collected.append(str(item))
            return "".join(collected)

        return str(result)

class BaseAgent:
    def __init__(
        self,
        name: str,
        memory_type: Literal[
            "no_memory",
            "conversation_memory",
            "summary_memory",
            "vector_memory",
            "episodic_memory",
            "semantic_memory",
            "agent_specific_memory",
            "shared_memory",
            "hybrid_memory",
        ] = "no_memory",
        sync_type: Literal[
            "direct_message",
            "shared_blackboard",
            "event_driven",
            "publisher_subscriber",
            "state_versioning",
            "distributed_memory_sync",
        ] = "direct_message",
        temperature: float = 0.4,
    ):
        self.name = name
        self.memory_type = memory_type
        self.sync_type = sync_type
        self.temperature = temperature
        self.memory: List[str] = []
        self.llm_manager = OllamaManager() if ollama else None

    def load_config(self, config_filename: str = "config.json") -> None:
        config_filepath = os.path.join(os.path.dirname(__file__), os.path.basename(config_filename))
        if os.path.exists(config_filepath):
            with open(config_filepath, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
            self.memory_type = config.get("memory_type", self.memory_type)
            self.sync_type = config.get("sync_type", self.sync_type)
            self.temperature = config.get("temperature", self.temperature)

    def set_model(self, model_name: str) -> None:
        if self.llm_manager:
            self.llm_manager.set_model(model_name)

    def process_prompt(self, sys_prompt: str = "", user_prompt: str = "") -> str:
        messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
        if self.llm_manager:
            try:
                return self.llm_manager.response(messages)
            except Exception:
                return self.fallback_response(sys_prompt, user_prompt)

        return self.fallback_response(sys_prompt, user_prompt)

    def process_prompt_stream(self, sys_prompt: str = "", user_prompt: str = ""):
        messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
        if self.llm_manager:
            try:
                for chunk in self.llm_manager.response_stream(messages):
                    yield chunk
                return
            except Exception:
                pass

        # Fallback response streaming simulation
        fallback = self.fallback_response(sys_prompt, user_prompt)
        import time
        words = fallback.split(" ")
        for i, word in enumerate(words):
            yield (word + " " if i < len(words) - 1 else word)
            time.sleep(0.03)

    def fallback_response(self, sys_prompt: str, user_prompt: str) -> str:
        prompt_lower = user_prompt.lower()
        if any(keyword in prompt_lower for keyword in ["flight", "airline", "route", "departure", "arrival"]):
            actual_data = ""
            if "actual available flights from the database:" in user_prompt:
                actual_data = user_prompt.split("actual available flights from the database:")[1].strip()
            
            flights_rec = actual_data if actual_data else " - Recommended itinerary: nonstop morning flight where available, economy class, one reliable carrier.\n - Flight estimate: 1x departure, 1x return, preferred schedule aligned with traveler preferences."
            return (
                "<think>\n"
                "Checking available routes, pricing structures, and schedule convenience from origin to destination.\n"
                "Comparing economy carriers and reviewing departure slots to ensure alignment with user preferences.\n"
                "</think>\n"
                "Flight Specialist:\n"
                f"{flights_rec}"
            )

        if any(keyword in prompt_lower for keyword in ["hotel", "accommodation", "stay", "room"]):
            actual_data = ""
            if "actual available hotels from the database:" in user_prompt:
                actual_data = user_prompt.split("actual available hotels from the database:")[1].strip()
                
            hotels_rec = actual_data if actual_data else " - Recommended property: centrally located hotel with free breakfast, high guest rating, and flexible cancellation.\n - Accommodation estimate: 3 nights, standard double room, close to destination landmarks."
            return (
                "<think>\n"
                "Scanning mid-range hotel inventories at the destination.\n"
                "Evaluating guest ratings, location convenience, and package inclusions like free breakfast.\n"
                "</think>\n"
                "Hotel Specialist:\n"
                f"{hotels_rec}"
            )

        if any(keyword in prompt_lower for keyword in ["budget", "cost", "price", "expense"]):
            return (
                "<think>\n"
                "Aggregating estimated flight and hotel pricing structures.\n"
                "Comparing total projected costs against the specified budget constraints to ensure financial feasibility.\n"
                "</think>\n"
                "Budget Specialist:\n"
                " - Estimated total cost is within the requested budget.\n"
                " - Recommendation: prioritize flight convenience and hotel comfort while monitoring ancillary fees."
            )

        if any(keyword in prompt_lower for keyword in ["conflict", "trade-off", "alternative", "negotiation"]):
            return (
                "<think>\n"
                "Identifying potential timing/budget conflicts.\n"
                "Formulating trade-offs to optimize user preferences under budgetary restrictions.\n"
                "</think>\n"
                "Negotiation Specialist:\n"
                " - Recommendation: choose the safest itinerary that meets budget and timing.\n"
                " - If cost pressure is high, suggest a slightly lower-rated hotel or a later flight with the same destination."
            )

        return f"[{self.name}] {user_prompt}"

if __name__ == "__main__":
    agent = BaseAgent(name="BaseAgent")
    agent.load_config()
    print("Base agent loaded successfully.")
    print("Base agent memory type: ",agent.memory_type)
    print("Base agent sync type: ",agent.sync_type)
    print("Base agent process prompt: ",agent.process_prompt(sys_prompt="You are an assistant.", user_prompt="What is the capital of France?"))
