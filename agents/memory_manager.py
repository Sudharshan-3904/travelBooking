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
            
        # Legacy migrations/safeguards
        self.store.setdefault("conversations", [])
        self.store.setdefault("summaries", {})
        self.store.setdefault("semantic_facts", {})
        self.store.setdefault("episodes", [])
        self.store.setdefault("agent_semantic_facts", {})

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
            "episodes": [],            # List of {problem, solution, outcome}
            "agent_semantic_facts": {}  # Dict of agent_name -> Dict of fact_key -> fact_value
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
        
        # 3. Extract agent-specific localized facts
        self.extract_agent_specific_facts(agent_name, query, output_text)
        
        # 4. Extract episodes (especially for negotiation/budget conflicts)
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
        if agent_name in self.store["summaries"]:
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

    def extract_agent_specific_facts(self, agent_name: str, query: str, output_text: str):
        if "agent_semantic_facts" not in self.store:
            self.store["agent_semantic_facts"] = {}
        if agent_name not in self.store["agent_semantic_facts"]:
            self.store["agent_semantic_facts"][agent_name] = {}
            
        agent_facts = self.store["agent_semantic_facts"][agent_name]
        
        # Flight Agent specific extraction
        if agent_name == "FlightAgent":
            airline_match = re.findall(r'\b(Delta|United|Alaska|American Airlines|Southwest|JetBlue|Spirit)\b', output_text, re.IGNORECASE)
            if airline_match:
                agent_facts["preferred_airlines"] = list(set([a.title() for a in airline_match]))[:3]
            
            # Flight patterns (e.g. morning, evening, nonstop)
            patterns = []
            if "morning" in output_text.lower() or "morning" in query.lower():
                patterns.append("Morning departures")
            if "evening" in output_text.lower() or "evening" in query.lower():
                patterns.append("Evening departures")
            if "nonstop" in output_text.lower() or "direct" in output_text.lower() or "non-stop" in output_text.lower():
                patterns.append("Nonstop/Direct flights preferred")
            if patterns:
                agent_facts["flight_patterns"] = patterns

        # Hotel Agent specific extraction
        elif agent_name == "HotelAgent":
            prefs = []
            if "breakfast" in output_text.lower() or "breakfast" in query.lower():
                prefs.append("Breakfast included")
            if "city center" in output_text.lower() or "downtown" in output_text.lower():
                prefs.append("Central location / City center")
            if "mid-range" in output_text.lower() or "mid-range" in query.lower():
                prefs.append("Mid-range hotel preference")
            if "luxury" in output_text.lower() or "premium" in output_text.lower():
                prefs.append("Premium/Luxury hotel preference")
            if prefs:
                agent_facts["accommodation_preferences"] = prefs
                
        # Budget Agent specific extraction
        elif agent_name == "BudgetAgent":
            budget_match = re.search(r'\$\s*([0-9,]+)', query)
            if budget_match:
                try:
                    budget_val = int(budget_match.group(1).replace(",", ""))
                    if budget_val < 1000:
                        agent_facts["budget_tier"] = "Economy/Budget (<$1000)"
                    elif budget_val <= 2500:
                        agent_facts["budget_tier"] = "Mid-Range ($1000-$2500)"
                    else:
                        agent_facts["budget_tier"] = "Premium/Luxury (>$2500)"
                except Exception:
                    pass

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

    def retrieve_context(self, agent_name: str, query: str, memory_type: str, window_size: int = 5) -> str:
        if memory_type == "no_memory":
            return ""

        context_blocks = []

        # 1. Filtered conversations
        convs = self.store.setdefault("conversations", [])
        
        # Determine agent filter: conversation_memory and shared_memory are shared pools
        is_shared = (memory_type in ["conversation_memory", "shared_memory"])
        if is_shared:
            agent_convs = convs
        else:
            agent_convs = [c for c in convs if c["agent_name"] == agent_name]

        # Handle different memory types
        if memory_type == "conversation_memory":
            recent = agent_convs[-window_size:]
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

        elif memory_type == "agent_specific_memory":
            # 1. Local agent conversations
            recent = agent_convs[-window_size:]
            if recent:
                context_blocks.append("=== Agent Local Conversation History ===")
                for r in recent:
                    context_blocks.append(
                        f"Timestamp: {r['timestamp']}\n"
                        f"Query: {r['query']}\n"
                        f"Response: {r['output']}\n"
                        f"---"
                    )
            # 2. Localized agent facts
            agent_facts = self.store.setdefault("agent_semantic_facts", {}).setdefault(agent_name, {})
            if agent_facts:
                context_blocks.append(f"=== Isolated {agent_name} Preferences ===")
                for k, v in agent_facts.items():
                    val_str = ", ".join(v) if isinstance(v, list) else str(v)
                    context_blocks.append(f"- {k.replace('_', ' ').title()}: {val_str}")

        elif memory_type == "summary_memory":
            summary = self.store.setdefault("summaries", {}).get(agent_name, "")
            if summary:
                context_blocks.append("=== Running History Summary ===")
                context_blocks.append(summary)
            # Key user preferences from semantic facts
            facts = self.store.setdefault("semantic_facts", {})
            if facts:
                context_blocks.append("=== Key User Preferences ===")
                for k, v in facts.items():
                    context_blocks.append(f"- {k.replace('_', ' ').title()}: {v}")

        elif memory_type == "shared_memory":
            context_blocks.append("=== Global Shared Memory Pool ===")
            
            # 1. Recent global conversations
            recent = agent_convs[-window_size:]
            if recent:
                context_blocks.append("--- Recent Cross-Agent Activity ---")
                for r in recent:
                    context_blocks.append(f"{r['agent_name']}: {r['output'][:200]}...")
            
            # 2. All agent summaries
            summaries = self.store.setdefault("summaries", {})
            if summaries:
                context_blocks.append("--- Collaborative Summaries ---")
                for ag, summ in summaries.items():
                    if summ:
                        context_blocks.append(f"[{ag}]: {summ}")
            
            # 3. Global semantic facts
            facts = self.store.setdefault("semantic_facts", {})
            if facts:
                context_blocks.append("--- Global Semantic Facts ---")
                for k, v in facts.items():
                    context_blocks.append(f"- {k.replace('_', ' ').title()}: {v}")

            # 4. Global negotiation episodes
            episodes = self.store.setdefault("episodes", [])
            if episodes:
                context_blocks.append("--- Collaborative Negotiation Episodes ---")
                for ep in episodes[-2:]:
                    context_blocks.append(
                        f"- Problem: {ep['problem']}\n"
                        f"  Solution: {ep['solution']}\n"
                        f"  Outcome: {ep['outcome']}"
                    )

        elif memory_type == "vector_memory":
            query_emb = self.get_embedding(query)
            if query_emb and agent_convs:
                scored_convs = []
                for c in agent_convs:
                    if c.get("embedding"):
                        score = cosine_similarity(query_emb, c["embedding"])
                        scored_convs.append((score, c))
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
            episodes = self.store.setdefault("episodes", [])
            if episodes:
                context_blocks.append("=== Past Resolved Issues/Episodes ===")
                for ep in episodes[-3:]:
                    context_blocks.append(
                        f"- Problem: {ep['problem']}\n"
                        f"  Solution: {ep['solution']}\n"
                        f"  Outcome: {ep['outcome']}\n"
                    )

        elif memory_type == "semantic_memory":
            facts = self.store.setdefault("semantic_facts", {})
            if facts:
                context_blocks.append("=== Long-term User Profiles & Facts ===")
                for k, v in facts.items():
                    key_title = k.replace("_", " ").title()
                    context_blocks.append(f"- {key_title}: {v}")

        elif memory_type == "hybrid_memory":
            # Agent Memory + Shared Memory + Episodic Memory + Semantic Memory
            
            # 1. Agent Memory: Local agent conversations
            local_convs = [c for c in convs if c["agent_name"] == agent_name]
            recent = local_convs[-3:]
            if recent:
                context_blocks.append("=== Agent Local Memory (Recent History) ===")
                for r in recent:
                    context_blocks.append(f"Query: {r['query']}\nResponse: {r['output']}\n---")

            # 2. Shared Memory: Collaborative summaries of other agents
            summaries = self.store.setdefault("summaries", {})
            other_summaries = {ag: summ for ag, summ in summaries.items() if ag != agent_name and summ}
            if other_summaries:
                context_blocks.append("=== Shared Memory (Other Agents' Summaries) ===")
                for ag, summ in other_summaries.items():
                    context_blocks.append(f"[{ag}]: {summ}")
            
            # 3. Semantic Memory: Global user profile/facts
            facts = self.store.setdefault("semantic_facts", {})
            if facts:
                context_blocks.append("=== Semantic Memory (User Profile) ===")
                for k, v in facts.items():
                    context_blocks.append(f"- {k.replace('_', ' ').title()}: {v}")

            # 4. Episodic Memory: Resolved negotiation episodes
            episodes = self.store.setdefault("episodes", [])
            if episodes:
                context_blocks.append("=== Episodic Memory (Resolved Issues) ===")
                for ep in episodes[-2:]:
                    context_blocks.append(f"- Problem: {ep['problem']}\n  Solution: {ep['solution']}")
            
            # 5. Vector memory top 1 (global semantic search)
            query_emb = self.get_embedding(query)
            if query_emb and convs:
                scored = []
                for c in convs:
                    if c.get("embedding"):
                        score = cosine_similarity(query_emb, c["embedding"])
                        scored.append((score, c))
                scored.sort(key=lambda x: x[0], reverse=True)
                if scored:
                    context_blocks.append("\n=== Semantic Vector Case Retrieval ===")
                    score, r = scored[0]
                    context_blocks.append(
                        f"Past Query: {r['query']}\n"
                        f"Past Response: {r['output']}\n"
                    )

        return "\n".join(context_blocks)
