import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import ollama
except ImportError:
    ollama = None

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(a * a for a in v2) ** 0.5
    if norm1 * norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class MemoryManager:
    def __init__(self):
        self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
            except Exception:
                self.store = self.get_default_store()
        else:
            self.store = self.get_default_store()

    def save_memory(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.store, f, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")

    def get_default_store(self) -> Dict[str, Any]:
        return {
            "conversations": [],      # List of {agent_name, query, input, output, timestamp, embedding}
            "summaries": {},          # Dict of agent_name -> summary string
            "semantic_facts": {},      # Dict of fact_key -> fact_value (e.g., preferred_airlines, budget_tier)
            "episodes": []            # List of {problem, solution, outcome}
        }

    def get_embedding(self, text: str) -> Optional[List[float]]:
        if not ollama:
            return None
        try:
            # Clean text a bit to save token length
            cleaned = text.strip()[:1000]
            client = ollama.Client()
            res = client.embeddings(model="embeddinggemma:latest", prompt=cleaned)
            return res.get("embedding")
        except Exception as e:
            print(f"Failed to fetch embedding: {e}")
            return None

    def add_interaction(self, agent_name: str, query: str, input_text: str, output_text: str):
        # We calculate embedding on the query details
        embedding = self.get_embedding(query)
        
        interaction = {
            "agent_name": agent_name,
            "query": query,
            "input": input_text,
            "output": output_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "embedding": embedding
        }
        
        self.store["conversations"].append(interaction)
        
        # 1. Update summary for the agent dynamically
        self.update_agent_summary(agent_name, query, output_text)
        
        # 2. Extract semantic facts from the output
        self.extract_semantic_facts(query, output_text)
        
        # 3. Extract episodes (especially for negotiation/budget conflicts)
        self.extract_episodes(agent_name, query, output_text)
        
        self.save_memory()

    def update_agent_summary(self, agent_name: str, query: str, output_text: str):
        current_summary = self.store["summaries"].get(agent_name, "")
        
        # We can extract key points and append them
        lines = output_text.split("\n")
        key_recommendations = []
        for line in lines:
            if "recommend" in line.lower() or "prefer" in line.lower() or "total cost" in line.lower() or "budget" in line.lower():
                cleaned = line.strip("* -#").strip()
                if cleaned and len(cleaned) > 10:
                    key_recommendations.append(cleaned)
                    
        rec_str = "; ".join(key_recommendations[:3])
        if rec_str:
            new_addition = f"For query '{query[:100]}': {rec_str}."
            if current_summary:
                self.store["summaries"][agent_name] = current_summary + "\n" + new_addition
            else:
                self.store["summaries"][agent_name] = new_addition
        
        # Cap the summary length to avoid context explosion
        if len(self.store["summaries"][agent_name]) > 1000:
            self.store["summaries"][agent_name] = "..." + self.store["summaries"][agent_name][-800:]

    def extract_semantic_facts(self, query: str, output_text: str):
        # Simple regex heuristics to extract facts
        # Airlines
        airline_match = re.findall(r'\b(Delta|United|Alaska|American Airlines|Southwest|JetBlue|Spirit)\b', output_text, re.IGNORECASE)
        if airline_match:
            preferred = self.store["semantic_facts"].get("preferred_airlines", [])
            for air in airline_match:
                air_title = air.title()
                if air_title not in preferred:
                    preferred.append(air_title)
            self.store["semantic_facts"]["preferred_airlines"] = preferred[:5]

        # Budget tier
        budget_match = re.search(r'\$\s*([0-9,]+)', query)
        if budget_match:
            try:
                budget_val = int(budget_match.group(1).replace(",", ""))
                self.store["semantic_facts"]["last_known_budget"] = f"${budget_val}"
                if budget_val < 1000:
                    self.store["semantic_facts"]["traveler_budget_tier"] = "Economy/Budget"
                elif budget_val <= 2500:
                    self.store["semantic_facts"]["traveler_budget_tier"] = "Mid-Range"
                else:
                    self.store["semantic_facts"]["traveler_budget_tier"] = "Premium/Luxury"
            except Exception:
                pass

        # Home location
        home_match = re.search(r'from\s+([A-Za-z\s]+?)\s+to', query, re.IGNORECASE)
        if home_match:
            self.store["semantic_facts"]["user_home_city"] = home_match.group(1).strip().title()

    def extract_episodes(self, agent_name: str, query: str, output_text: str):
        # Focus on budget conflicts or tradeoffs
        if "exceed" in output_text.lower() or "over budget" in output_text.lower() or "alternative" in output_text.lower() or "trade-off" in output_text.lower():
            # Extract conflict resolution
            lines = output_text.split("\n")
            problems = []
            solutions = []
            for line in lines:
                l_lower = line.lower()
                if "exceed" in l_lower or "conflict" in l_lower or "over budget" in l_lower:
                    problems.append(line.strip("* -").strip())
                elif "instead" in l_lower or "recommend" in l_lower or "choose" in l_lower or "switch" in l_lower:
                    solutions.append(line.strip("* -").strip())
            
            prob_str = " ".join(problems[:2])
            sol_str = " ".join(solutions[:2])
            
            if prob_str and sol_str:
                self.store["episodes"].append({
                    "problem": prob_str[:200],
                    "solution": sol_str[:200],
                    "outcome": "Resolved via negotiation"
                })
                # Cap episodes
                self.store["episodes"] = self.store["episodes"][-10:]

    def retrieve_context(self, agent_name: str, query: str, memory_type: str) -> str:
        if memory_type == "no_memory":
            return ""

        context_blocks = []

        # 1. Filtered conversations
        convs = self.store["conversations"]
        
        # Determine agent filter
        is_shared = (memory_type == "shared_memory" or memory_type == "hybrid_memory")
        if is_shared:
            agent_convs = convs
        else:
            agent_convs = [c for c in convs if c["agent_name"] == agent_name]

        # Handle different memory types
        if memory_type in ["conversation_memory", "agent_specific_memory", "shared_memory"]:
            # Get last 3 conversations
            recent = agent_convs[-3:]
            if recent:
                context_blocks.append("=== Recent Conversation History ===")
                for r in recent:
                    context_blocks.append(
                        f"Timestamp: {r['timestamp']}\n"
                        f"Agent: {r['agent_name']}\n"
                        f"Query: {r['query']}\n"
                        f"Response: {r['output']}\n"
                        f"---"
                    )

        elif memory_type == "summary_memory":
            summary = self.store["summaries"].get(agent_name, "")
            if summary:
                context_blocks.append("=== Running History Summary ===")
                context_blocks.append(summary)

        elif memory_type == "vector_memory":
            # Semantic search
            query_emb = self.get_embedding(query)
            if query_emb and agent_convs:
                scored_convs = []
                for c in agent_convs:
                    if c.get("embedding"):
                        score = cosine_similarity(query_emb, c["embedding"])
                        scored_convs.append((score, c))
                # Sort by score descending
                scored_convs.sort(key=lambda x: x[0], reverse=True)
                top_2 = scored_convs[:2]
                if top_2:
                    context_blocks.append("=== Similar Past Travel Planning Cases ===")
                    for score, r in top_2:
                        context_blocks.append(
                            f"Similarity: {score:.2f}\n"
                            f"Past Query: {r['query']}\n"
                            f"Past Response: {r['output']}\n"
                            f"---"
                        )
            else:
                # Fallback to last 2 conversations if no embeddings available
                recent = agent_convs[-2:]
                if recent:
                    context_blocks.append("=== Past Cases (Keyword Fallback) ===")
                    for r in recent:
                        context_blocks.append(
                            f"Query: {r['query']}\n"
                            f"Response: {r['output']}\n"
                            f"---"
                        )

        elif memory_type == "episodic_memory":
            episodes = self.store["episodes"]
            if episodes:
                context_blocks.append("=== Past Resolved Issues/Episodes ===")
                for ep in episodes[-3:]:
                    context_blocks.append(
                        f"- Problem: {ep['problem']}\n"
                        f"  Solution: {ep['solution']}\n"
                        f"  Outcome: {ep['outcome']}\n"
                    )

        elif memory_type == "semantic_memory":
            facts = self.store["semantic_facts"]
            if facts:
                context_blocks.append("=== Long-term User Profiles & Facts ===")
                for k, v in facts.items():
                    key_title = k.replace("_", " ").title()
                    context_blocks.append(f"- {key_title}: {v}")

        elif memory_type == "hybrid_memory":
            # Combine conversation memory, semantic memory, and vector memory
            # Semantic facts
            facts = self.store["semantic_facts"]
            if facts:
                context_blocks.append("=== User Profile ===")
                for k, v in facts.items():
                    context_blocks.append(f"- {k.replace('_', ' ').title()}: {v}")
            
            # Vector memory top 1
            query_emb = self.get_embedding(query)
            if query_emb and agent_convs:
                scored = []
                for c in agent_convs:
                    if c.get("embedding"):
                        score = cosine_similarity(query_emb, c["embedding"])
                        scored.append((score, c))
                scored.sort(key=lambda x: x[0], reverse=True)
                if scored:
                    context_blocks.append("\n=== Most Relevant Past Case ===")
                    score, r = scored[0]
                    context_blocks.append(
                        f"Past Query: {r['query']}\n"
                        f"Past Response: {r['output']}\n"
                    )

        return "\n".join(context_blocks)
