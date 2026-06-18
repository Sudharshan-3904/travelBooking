import streamlit as st
import os
import time
import json
import ast
import re
import socket
import subprocess
import random
from datetime import datetime
import pandas as pd
from datasets import load_dataset

# Import TravelNet agent components
from agents.planner_agent import PlannerAgent, TravelRequest
from agents.flight_agent import FlightSearchRequest
from agents.hotel_agent import HotelSearchRequest
from agents.mlflow_tracker import MLflowTracker
from agents.base_agent import parse_thinking_and_output, BaseAgent

CSV_PATH = "evaluation_runs.csv"

# Page Configuration with premium styling
st.set_page_config(
    page_title="TravelNet AI Random Benchmark Studio",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;500;700&display=swap');
    
    /* Font overrides */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        background: linear-gradient(90deg, #60A5FA, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Main container background */
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }
    
    /* Glassmorphism containers */
    div[data-testid="stVerticalBlock"] > div:has(div.agent-card) {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Custom agent badges */
    .agent-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .agent-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #60A5FA;
    }
    .agent-badge {
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 12px;
        background: rgba(96, 165, 250, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .agent-content {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #E5E7EB;
        background: rgba(0, 0, 0, 0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 3px solid #60A5FA;
        white-space: pre-line;
    }
    
    /* Streamlit sidebar overrides */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Customized Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.025em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        color: white;
    }
    div.stButton > button:active {
        transform: translateY(0);
    }
    
    /* Group Chat Styling overrides */
    .chat-container {
        background: rgba(17, 24, 39, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.5);
    }
    
    /* Evaluation-specific Styles */
    .metric-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    .metric-value-pass {
        font-size: 1.6rem;
        font-weight: 700;
        color: #10B981; /* emerald green */
    }
    .metric-value-fail {
        font-size: 1.6rem;
        font-weight: 700;
        color: #EF4444; /* rose red */
    }
    .metric-label {
        font-size: 0.8rem;
        color: #9CA3AF;
        text-transform: uppercase;
        margin-top: 6px;
        letter-spacing: 0.05em;
    }
    .overall-score-display {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10B981, #3B82F6, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 5px 0;
    }
    .badge-easy { background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-medium { background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-hard { background-color: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    </style>
""", unsafe_allow_html=True)

# Helper function to check if port is open
def is_port_open(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

# Helper function to start MLflow server in background
def ensure_mlflow_server(port=5000):
    if not is_port_open(port):
        # We start the server asynchronously and let it run using python -m mlflow
        cmd = f'python -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 127.0.0.1 --port {port} --x-frame-options NONE'
        try:
            subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                shell=True
            )
            time.sleep(3.0) # Give it time to bind the port
        except Exception as e:
            st.error(f"Failed to start MLflow server: {e}")

# Run MLflow server at startup
ensure_mlflow_server(port=5000)

# Helper to fetch active Ollama models
def get_ollama_models():
    try:
        import ollama
        client = ollama.Client()
        models_data = client.list()
        model_names = []
        if models_data and hasattr(models_data, "models"):
            for m in models_data.models:
                model_name = getattr(m, "model", None) or getattr(m, "name", None)
                if not model_name:
                    if hasattr(m, "model_dump"):
                        model_name = m.model_dump().get("model") or m.model_dump().get("name")
                    elif hasattr(m, "dict"):
                        model_name = m.dict().get("model") or m.dict().get("name")
                if model_name and "embed" not in model_name.lower():
                    model_names.append(model_name)
        if not model_names:
            return None
        return model_names
    except Exception as e:
        print(e)
        return None

# Cache the dataset loading using Hugging Face datasets module
@st.cache_data
def load_travel_planner_dataset(config_name: str):
    dataset_dict = load_dataset('osunlp/TravelPlanner', config_name)
    return dataset_dict[config_name]

# Helper to extract query details if missing (e.g. in test split)
def extract_query_details(sample):
    details = {
        "org": sample.get("org"),
        "dest": sample.get("dest"),
        "days": sample.get("days", 3),
        "people_number": sample.get("people_number"),
        "budget": sample.get("budget"),
        "date": sample.get("date"),
        "local_constraint": sample.get("local_constraint"),
        "query": sample.get("query", ""),
        "level": sample.get("level", "easy")
    }
    
    query = details["query"]
    
    # Extract origin & destination if missing
    if not details["org"]:
        from_to_match = re.search(r'from\s+([A-Za-z\s\.\'\-]+?)\s+to\s+([A-Za-z\s\.\'\-]+?)(?:\s+spanning|\s+from|\s+for|\s+with|\s+budget|\.|\,|$)', query, re.IGNORECASE)
        if from_to_match:
            details["org"] = from_to_match.group(1).strip()
            details["dest"] = from_to_match.group(2).strip()
        else:
            from_match = re.search(r'(?:from|departing from)\s+([A-Za-z\s\.\'\-]+?)(?:\s+to|\s+spanning|\s+from|\s+for|\s+with|\.|\,|$)', query, re.IGNORECASE)
            if from_match:
                details["org"] = from_match.group(1).strip()
            to_match = re.search(r'(?:to|heading to|destination of)\s+([A-Za-z\s\.\'\-]+?)(?:\s+from|\s+spanning|\s+for|\s+with|\.|\,|$)', query, re.IGNORECASE)
            if to_match:
                details["dest"] = to_match.group(1).strip()

    if not details["org"]:
        details["org"] = "Seattle"
    if not details["dest"]:
        details["dest"] = "San Francisco"

    # Extract budget
    if details["budget"] is None:
        budget_match = re.search(r'\$\s*([0-9,]+)', query)
        if budget_match:
            details["budget"] = int(budget_match.group(1).replace(',', ''))
        else:
            details["budget"] = 1500

    # Extract travelers (people_number)
    if details["people_number"] is None:
        if "single" in query.lower() or "one person" in query.lower() or " 1 person" in query.lower():
            details["people_number"] = 1
        else:
            people_match = re.search(r'([0-9]+)\s*(?:people|person|traveler|party)', query, re.IGNORECASE)
            if people_match:
                details["people_number"] = int(people_match.group(1))
            else:
                details["people_number"] = 1

    # Extract dates
    if not details["date"]:
        year_match = re.search(r'\b(202[0-9])\b', query)
        year = year_match.group(1) if year_match else "2022"
        
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
                  "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        
        found_days = re.findall(r'\b([0-9]{1,2})(?:st|nd|rd|th)?\b', query)
        found_months = [m for m in months if m in query.lower()]
        
        if len(found_months) >= 1 and len(found_days) >= 2:
            month_name = found_months[0]
            month_num = months.index(month_name) % 12 + 1
            day1 = int(found_days[0])
            day2 = int(found_days[1])
            details["date"] = str([f"{year}-{month_num:02d}-{day1:02d}", f"{year}-{month_num:02d}-{day2:02d}"])
        else:
            iso_dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', query)
            if len(iso_dates) >= 2:
                details["date"] = str(iso_dates[:2])
            elif len(iso_dates) == 1:
                details["date"] = str([iso_dates[0], iso_dates[0]])
            else:
                details["date"] = str(["2026-09-15", f"2026-09-{15 + int(details['days'])}"])

    # Extract local constraints (dict)
    if not details["local_constraint"]:
        details["local_constraint"] = "{'house rule': None, 'cuisine': None, 'room type': None, 'transportation': None}"

    return details

# Heuristic programmatic evaluation
def run_heuristic_evaluation(sample, plan_text):
    # 1. Relevance: Destination check
    dest_clean = sample['dest'].strip().lower()
    try:
        dest_list = ast.literal_eval(dest_clean)
        if isinstance(dest_list, list):
            dest_checks = [d.strip().lower() in plan_text.lower() for d in dest_list]
            dest_pass = all(dest_checks)
        else:
            dest_pass = dest_clean in plan_text.lower()
    except Exception:
        dest_pass = dest_clean in plan_text.lower()

    # 2. Relevance: Origin check
    org_clean = sample['org'].strip().lower()
    org_pass = org_clean in plan_text.lower()

    # 3. Temporal coverage check
    days = int(sample['days'])
    days_pattern = rf"({days}\s*day|day\s*{days})"
    days_mentioned = re.search(days_pattern, plan_text, re.IGNORECASE) is not None
    
    dates_list = []
    try:
        dates_list = ast.literal_eval(sample['date'])
    except Exception:
        pass
    
    dates_pass = False
    if dates_list and isinstance(dates_list, list):
        dates_pass = any(d in plan_text for d in [dates_list[0], dates_list[-1]])
    
    duration_pass = days_mentioned or dates_pass

    # 4. Budget check
    dollar_amounts = [float(val.replace(',', '')) for val in re.findall(r'\$([0-9,]+)', plan_text)]
    budget_limit = float(sample['budget'])
    
    budget_pass = True
    budget_details = ""
    if dollar_amounts:
        total_costs = []
        for line in plan_text.split('\n'):
            if 'total' in line.lower() or 'estimated cost' in line.lower() or 'budget' in line.lower():
                costs = [float(val.replace(',', '')) for val in re.findall(r'\$([0-9,]+)', line)]
                total_costs.extend(costs)
        
        if total_costs:
            max_total = max(total_costs)
            budget_pass = max_total <= budget_limit
            budget_details = f"Parsed total cost: ${max_total:.2f}. Budget limit: ${budget_limit:.2f}."
        else:
            max_val = max(dollar_amounts)
            if max_val > budget_limit:
                if "within the requested budget" in plan_text.lower() or "within budget" in plan_text.lower():
                    budget_pass = True
                    budget_details = f"Heuristically passed: Itinerary explicitly states it is within budget."
                else:
                    budget_pass = False
                    budget_details = f"Warning: Found price ${max_val:.2f} which exceeds budget of ${budget_limit:.2f}."
            else:
                budget_pass = True
                budget_details = f"All mentioned prices are below budget limit of ${budget_limit:.2f}."
    else:
        if "within the requested budget" in plan_text.lower() or "within budget" in plan_text.lower():
            budget_pass = True
            budget_details = "Passed: Text explicitly states it is within budget."
        else:
            budget_pass = False
            budget_details = "Failed: No prices found and no budget confirmation statement found."

    # 5. Local Constraints check (e.g. room type, cuisine, transportation)
    constraints_pass = True
    constraints_details = []
    local_con = {}
    try:
        local_con = ast.literal_eval(sample['local_constraint'])
    except Exception:
        pass
    
    if isinstance(local_con, dict):
        for con_key, con_val in local_con.items():
            if con_val and con_val != "None" and con_val != None:
                if str(con_val).lower() in plan_text.lower():
                    constraints_details.append(f"Constraint '{con_key}: {con_val}' met.")
                else:
                    constraints_pass = False
                    constraints_details.append(f"Constraint '{con_key}: {con_val}' not found in plan.")
    
    if not constraints_details:
        constraints_details.append("No local constraints specified.")

    # Calculate overall score (out of 100)
    relevance_score = 30 if (dest_pass and org_pass) else (15 if (dest_pass or org_pass) else 0)
    duration_score = 20 if duration_pass else 0
    budget_score = 30 if budget_pass else 0
    constraints_score = 20 if constraints_pass else 0
    
    overall_score = relevance_score + duration_score + budget_score + constraints_score
    
    return {
        "destination_pass": dest_pass,
        "origin_pass": org_pass,
        "duration_pass": duration_pass,
        "budget_pass": budget_pass,
        "constraints_pass": constraints_pass,
        "overall_score": overall_score,
        "reasoning": f"Programmatic Check Summary:\n"
                     f"Dest: {'PASS' if dest_pass else 'FAIL'}, Org: {'PASS' if org_pass else 'FAIL'}, "
                     f"Duration: {'PASS' if duration_pass else 'FAIL'}, Budget: {'PASS' if budget_pass else 'FAIL'} ({budget_details}), "
                     f"Constraints: {'PASS' if constraints_pass else 'FAIL'} ({', '.join(constraints_details)})"
    }

# LLM-based evaluation
def run_llm_evaluation(selected_model, sample, plan_text):
    eval_agent = BaseAgent(name="EvaluatorAgent")
    eval_agent.set_model(selected_model)
    eval_agent.temperature = 0.1
    
    sys_prompt = (
        "You are an expert travel plan auditor. Evaluate the itinerary against the user request. "
        "Provide your output strictly in JSON format without any markdown wrapper."
    )
    
    local_con = {}
    try:
        local_con = ast.literal_eval(sample['local_constraint'])
    except Exception:
        pass
    con_str = ", ".join([f"{k}: {v}" for k, v in local_con.items() if v and v != "None"]) if local_con else "None"
    
    user_prompt = f"""
Analyze the generated travel plan and determine if it meets each requirement.
Original Query: {sample['query']}
Requested Details:
- Origin: {sample['org']}
- Destination: {sample['dest']}
- Dates: {sample['date']} (Days: {sample['days']})
- Travelers: {sample['people_number']}
- Budget Limit: ${sample['budget']}
- Local Constraints: {con_str}

Generated Travel Plan:
{plan_text}

You must respond with a JSON object containing the following keys and NO other text:
- "destination_pass": true or false (Is destination correct?)
- "origin_pass": true or false (Is origin correct?)
- "budget_pass": true or false (Is total cost of the itinerary <= ${sample['budget']}?)
- "duration_pass": true or false (Does the itinerary cover the requested days/dates?)
- "constraints_pass": true or false (Are local constraints satisfied?)
- "overall_score": integer (0 to 100 representing plan quality and constraint satisfaction)
- "reasoning": text (concise summary of findings)

Response JSON:
"""
    try:
        raw_res = eval_agent.process_prompt(sys_prompt, user_prompt)
        json_match = re.search(r'\{.*\}', raw_res, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            # Strip comments (single-line and multi-line)
            comment_pattern = r'("(?:\\.|[^"\\])*")|//.*|/\*(?:[^*]|\*(?!/))*\*/'
            cleaned_text = re.sub(comment_pattern, lambda m: m.group(1) if m.group(1) is not None else "", json_text)
            
            # Try parsing with standard json
            data = None
            try:
                data = json.loads(cleaned_text)
            except Exception:
                # Fallback to python literal evaluation for lenient parsing
                try:
                    py_str = cleaned_text.replace("true", "True").replace("false", "False").replace("null", "None")
                    data = ast.literal_eval(py_str)
                except Exception:
                    pass
            
            if data and isinstance(data, dict):
                required_keys = ["destination_pass", "origin_pass", "budget_pass", "duration_pass", "constraints_pass", "overall_score", "reasoning"]
                if all(k in data for k in required_keys):
                    return {
                        "destination_pass": bool(data["destination_pass"]),
                        "origin_pass": bool(data["origin_pass"]),
                        "duration_pass": bool(data["duration_pass"]),
                        "budget_pass": bool(data["budget_pass"]),
                        "constraints_pass": bool(data["constraints_pass"]),
                        "overall_score": int(data["overall_score"]),
                        "reasoning": f"LLM Audit: {data['reasoning']}"
                    }
    except Exception as e:
        print(f"LLM evaluation failed: {e}")
    
    return None

# Save results locally to CSV
def save_runs_to_csv(runs):
    df_new = pd.DataFrame(runs)
    if os.path.exists(CSV_PATH):
        try:
            df_existing = pd.read_csv(CSV_PATH)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(CSV_PATH, index=False)
        except Exception:
            df_new.to_csv(CSV_PATH, index=False)
    else:
        df_new.to_csv(CSV_PATH, index=False)

# Header with premium aesthetic
st.markdown("""
    <div style='margin-bottom: 25px;'>
        <h1 style='margin: 0; padding: 0;'>TravelNet Random Benchmark Studio</h1>
        <p style='color: #9CA3AF; margin-top: 5px; font-size: 1.1rem;'>
            Run 'n' random test cases from <strong>osunlp/TravelPlanner</strong> and track performance metrics
        </p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR INTERFACE ---
with st.sidebar:
    st.markdown("### ⚙️ Model Settings")
    available_models = get_ollama_models() or ["llama3.2:latest", "qwen3.5:4b", "gemma4:e2b"]
    selected_model = st.selectbox("Select Main LLM", options=available_models, index=0)
    
    st.markdown("---")
    
    st.markdown("### 📦 Dataset Settings")
    dataset_split = st.selectbox(
        "Select Dataset Split",
        options=["validation", "train", "test"],
        index=0
    )
    
    with st.spinner("Loading TravelPlanner dataset..."):
        try:
            dataset = load_travel_planner_dataset(dataset_split)
            st.success(f"Loaded {len(dataset)} records from {dataset_split} split!")
        except Exception as e:
            st.error(f"Failed to load dataset: {e}")
            st.stop()
            
    # Level Filter
    levels = ["All"] + sorted(list(set(dataset['level'])))
    selected_level = st.selectbox("Filter Pool by Level", options=levels, index=0)
    
    if selected_level != "All":
        filtered_indices = [i for i, lvl in enumerate(dataset['level']) if lvl == selected_level]
    else:
        filtered_indices = list(range(len(dataset)))
        
    st.caption(f"Available pool size: {len(filtered_indices)} samples")
    
    st.markdown("---")
    
    st.markdown("### 🧪 Benchmark Configuration")
    # Number of random test cases (n)
    max_cases = max(1, len(filtered_indices))
    default_cases = max(1, int(max_cases * 0.1))
    n_cases = st.number_input(
        "Number of Random Cases (n)",
        min_value=1,
        max_value=max_cases,
        value=default_cases,
        step=1
    )
    
    st.markdown("---")
    st.markdown("### 🛠️ Agent settings")
    memory_type = st.selectbox(
        "Memory System",
        options=[
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
        index=0
    )
    sync_type = st.selectbox("Sync Protocol", options=["direct_message", "shared_blackboard", "event_driven"], index=0)
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# --- MAIN SCREEN INTERFACE ---
tab1, tab2, tab3 = st.tabs(["⚡ Random Benchmark Runner", "📂 Local CSV History", "📊 MLflow Experiments"])

with tab1:
    st.markdown("### 🚀 Execute Random Benchmark")
    st.markdown(f"""
        This will select **{n_cases}** random test cases from the pool of {len(filtered_indices)} records (filtered: Level = *{selected_level}*), 
        execute the multi-agent travel planner on each query, compute the metrics, and log them to `{CSV_PATH}`.
    """)
    
    col_run_btn, col_blank = st.columns([1, 3])
    with col_run_btn:
        run_benchmark = st.button("🚀 Run Random Benchmark")
        
    if run_benchmark:
        # Sample n random indices
        sampled_indices = random.sample(filtered_indices, int(n_cases))
        st.write(f"🎯 **Selected Random Sample Row Indices:** `{sampled_indices}`")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize PlannerAgent
        planner = PlannerAgent(memory_type=memory_type, sync_type=sync_type)
        planner.load_config()
        planner.temperature = temperature
        planner.set_model(selected_model)
        
        runs_completed = []
        
        for idx, row_idx in enumerate(sampled_indices):
            sample = extract_query_details(dataset[row_idx])
            status_text.markdown(f"🏃 **[ {idx+1} / {n_cases} ]** Executing Row **{row_idx}** ({sample['level']} level)...")
            
            dates_list = []
            try:
                dates_list = ast.literal_eval(sample['date'])
            except Exception:
                pass
            
            dep_date_str = dates_list[0] if dates_list else "2022-03-13"
            ret_date_str = dates_list[-1] if dates_list else "2022-03-15"
            
            req = TravelRequest(
                origin=sample['org'],
                destination=sample['dest'],
                departure_date=dep_date_str,
                return_date=ret_date_str,
                travelers=int(sample['people_number']),
                budget=f"${sample['budget']}",
                preferences=sample['query'],
            )
            
            try:
                # Run the travel planning agent network
                plan = planner.plan_trip(req)
                itinerary = planner.build_itinerary(req, plan)
                
                # Heuristic evaluate
                heur_eval = run_heuristic_evaluation(sample, itinerary)
                
                # LLM evaluate (if model is available/selected)
                llm_eval = None
                try:
                    llm_eval = run_llm_evaluation(selected_model, sample, itinerary)
                except Exception:
                    pass
                
                eval_res = llm_eval if llm_eval else heur_eval
                
                run_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model": selected_model,
                    "dataset_split": dataset_split,
                    "row_index": int(row_idx),
                    "level": sample['level'],
                    "origin": sample['org'],
                    "destination": sample['dest'],
                    "budget_limit": float(sample['budget']),
                    "people_number": int(sample['people_number']),
                    "overall_score": float(eval_res['overall_score']),
                    "destination_pass": bool(eval_res['destination_pass']),
                    "origin_pass": bool(eval_res['origin_pass']),
                    "budget_pass": bool(eval_res['budget_pass']),
                    "duration_pass": bool(eval_res['duration_pass']),
                    "constraints_pass": bool(eval_res['constraints_pass']),
                    "reasoning": eval_res['reasoning'],
                    "itinerary": itinerary
                }
                
                runs_completed.append(run_data)
                
                # Log individual run to MLflow
                try:
                    with MLflowTracker() as tracker:
                        tracker.log_params({
                            "run_mode": "random_benchmark_run",
                            "model": selected_model,
                            "dataset_split": dataset_split,
                            "row_index": row_idx,
                            "level": sample['level']
                        })
                        tracker.log_metrics({
                            "overall_score": float(eval_res['overall_score']),
                            "destination_pass": 1.0 if eval_res['destination_pass'] else 0.0,
                            "origin_pass": 1.0 if eval_res['origin_pass'] else 0.0,
                            "budget_pass": 1.0 if eval_res['budget_pass'] else 0.0,
                            "duration_pass": 1.0 if eval_res['duration_pass'] else 0.0,
                            "constraints_pass": 1.0 if eval_res['constraints_pass'] else 0.0
                        })
                except Exception:
                    pass
                    
            except Exception as e:
                st.error(f"Error testing index {row_idx}: {e}")
                
            progress_bar.progress(int(((idx + 1) / n_cases) * 100))
            
        status_text.markdown("✅ **Benchmark run completed!** saving and compiling results...")
        
        if runs_completed:
            # Save runs to local CSV
            save_runs_to_csv(runs_completed)
            st.success(f"Results successfully saved and appended to `{CSV_PATH}`!")
            
            # Compute session aggregates
            total_runs = len(runs_completed)
            avg_score = sum(r['overall_score'] for r in runs_completed) / total_runs
            dest_pr = sum(1 for r in runs_completed if r['destination_pass']) / total_runs * 100
            orig_pr = sum(1 for r in runs_completed if r['origin_pass']) / total_runs * 100
            budget_pr = sum(1 for r in runs_completed if r['budget_pass']) / total_runs * 100
            duration_pr = sum(1 for r in runs_completed if r['duration_pass']) / total_runs * 100
            constraints_pr = sum(1 for r in runs_completed if r['constraints_pass']) / total_runs * 100
            
            # Log aggregate run details to MLflow
            try:
                with MLflowTracker() as tracker:
                    tracker.log_params({
                        "run_mode": "random_benchmark_aggregate",
                        "model": selected_model,
                        "batch_size": total_runs,
                        "dataset_split": dataset_split
                    })
                    tracker.log_metrics({
                        "avg_overall_score": avg_score,
                        "destination_pass_rate": dest_pr,
                        "origin_pass_rate": orig_pr,
                        "budget_pass_rate": budget_pr,
                        "duration_pass_rate": duration_pr,
                        "constraints_pass_rate": constraints_pr
                    })
            except Exception:
                pass
                
            # Display results dashboard
            st.markdown("### 📊 Benchmark Scoreboard")
            col_score, col_relevance, col_budget, col_duration, col_constraints = st.columns(5)
            
            with col_score:
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='overall-score-display'>{avg_score:.1f}</div>
                        <div class='metric-label'>Average Score</div>
                    </div>
                """, unsafe_allow_html=True)
                
            def render_pass_rate_metric(label, rate):
                color_class = "metric-value-pass" if rate >= 70.0 else ("metric-value-fail" if rate < 40.0 else "metric-value-pass")
                if rate < 70.0 and rate >= 40.0:
                    color_style = "color: #F59E0B;" # Orange
                else:
                    color_style = ""
                return f"""
                    <div class='metric-card'>
                        <div class='{color_class}' style='{color_style}'>{rate:.1f}%</div>
                        <div class='metric-label'>{label}</div>
                    </div>
                """
                
            with col_relevance:
                st.markdown(render_pass_rate_metric("Destination Match", dest_pr), unsafe_allow_html=True)
            with col_budget:
                st.markdown(render_pass_rate_metric("Budget Pass Rate", budget_pr), unsafe_allow_html=True)
            with col_duration:
                st.markdown(render_pass_rate_metric("Duration Pass Rate", duration_pr), unsafe_allow_html=True)
            with col_constraints:
                st.markdown(render_pass_rate_metric("Constraints Pass", constraints_pr), unsafe_allow_html=True)
                
            # Session results table
            st.markdown("#### 📋 Detailed Session Output")
            df_runs = pd.DataFrame(runs_completed).drop(columns=['itinerary'])
            st.dataframe(df_runs, use_container_width=True)
            
            # Download button for session results
            session_csv = pd.DataFrame(runs_completed).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Session Results (CSV)",
                data=session_csv,
                file_name=f"benchmark_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

with tab2:
    st.markdown("### 📂 Historical Evaluation Database (`evaluation_runs.csv`)")
    
    if os.path.exists(CSV_PATH):
        try:
            df_hist = pd.read_csv(CSV_PATH)
            
            # Global historical aggregates
            total_hist_runs = len(df_hist)
            st.markdown(f"Total historical evaluation records loaded: **{total_hist_runs}** runs.")
            
            col_filter_model, col_clear = st.columns([3, 1])
            with col_filter_model:
                historical_models = ["All"] + list(df_hist['model'].unique())
                filter_hist_model = st.selectbox("Filter Historical Data by Model", options=historical_models, index=0)
                
            with col_clear:
                st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
                clear_btn = st.button("🗑️ Reset Local Database")
                
            if clear_btn:
                os.remove(CSV_PATH)
                st.warning("Local CSV database deleted successfully. Refresh the page.")
                st.stop()
                
            # Apply filter
            if filter_hist_model != "All":
                df_filtered = df_hist[df_hist['model'] == filter_hist_model]
            else:
                df_filtered = df_hist
                
            if not df_filtered.empty:
                # Calculations
                hist_avg = df_filtered['overall_score'].mean()
                hist_dest = (df_filtered['destination_pass'].sum() / len(df_filtered)) * 100
                hist_budget = (df_filtered['budget_pass'].sum() / len(df_filtered)) * 100
                hist_duration = (df_filtered['duration_pass'].sum() / len(df_filtered)) * 100
                hist_con = (df_filtered['constraints_pass'].sum() / len(df_filtered)) * 100
                
                # Scoreboard
                st.markdown("#### 📊 Historical Aggregates (Filtered)")
                col_h_score, col_h_relevance, col_h_budget, col_h_duration, col_h_constraints = st.columns(5)
                
                with col_h_score:
                    st.markdown(f"""
                        <div class='metric-card'>
                            <div class='overall-score-display'>{hist_avg:.1f}</div>
                            <div class='metric-label'>Avg Hist Score</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col_h_relevance:
                    st.markdown(render_pass_rate_metric("Dest Match Rate", hist_dest), unsafe_allow_html=True)
                with col_h_budget:
                    st.markdown(render_pass_rate_metric("Budget Pass Rate", hist_budget), unsafe_allow_html=True)
                with col_h_duration:
                    st.markdown(render_pass_rate_metric("Duration Pass Rate", hist_duration), unsafe_allow_html=True)
                with col_h_constraints:
                    st.markdown(render_pass_rate_metric("Constraints Pass", hist_con), unsafe_allow_html=True)
                    
                # Chart
                st.markdown("#### 📈 Model Performance Trend (Overall Scores)")
                chart_data = df_filtered[['timestamp', 'overall_score']].copy()
                chart_data = chart_data.sort_values(by='timestamp')
                st.line_chart(data=chart_data, x='timestamp', y='overall_score')
                
                # Detailed view
                st.markdown("#### 📋 Database Records")
                st.dataframe(df_filtered, use_container_width=True)
                
                # Download full CSV
                full_csv_data = df_hist.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Full Database (CSV)",
                    data=full_csv_data,
                    file_name="evaluation_runs_full.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No records found for model: {filter_hist_model}")
                
        except Exception as e:
            st.error(f"Error reading local CSV file: {e}")
    else:
        st.info("No local evaluation database found. Run a benchmark test to create `evaluation_runs.csv`.")

with tab3:
    st.markdown("### 📊 MLflow Experiment Tracking Dashboard")
    st.markdown("""
        All model executions are automatically logged into `mlflow.db`. 
        Compare experiment performance, view parameters, and analyze test statistics below.
    """)
    
    # Ensure MLflow server runs in background
    ensure_mlflow_server(port=5000)
    
    st.markdown("[🔗 Open MLflow dashboard in New Tab](http://127.0.0.1:5000)", unsafe_allow_html=True)
    st.iframe(src="http://127.0.0.1:5000", height=800)
