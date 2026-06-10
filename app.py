import streamlit as st
import os
import time
import socket
import subprocess
from datetime import datetime, date

# Import TravelNet agent components
from agents.planner_agent import PlannerAgent, TravelRequest
from agents.flight_agent import FlightSearchRequest
from agents.hotel_agent import HotelSearchRequest
from agents.mlflow_tracker import MLflowTracker
from agents.base_agent import parse_thinking_and_output

# Page Configuration with premium styling
st.set_page_config(
    page_title="TravelNet AI Multi-Agent Studio",
    page_icon="✈️",
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
    .chat-message-row {
        display: flex;
        align-items: flex-start;
        margin-bottom: 20px;
        animation: fadeInChat 0.3s ease-out;
    }
    @keyframes fadeInChat {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        margin-right: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        flex-shrink: 0;
    }
    .avatar-planner {
        background: linear-gradient(135deg, #6B7280, #374151);
        border: 1.5px solid #9CA3AF;
    }
    .avatar-flight {
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        border: 1.5px solid #60A5FA;
    }
    .avatar-hotel {
        background: linear-gradient(135deg, #059669, #047857);
        border: 1.5px solid #34D399;
    }
    .avatar-budget {
        background: linear-gradient(135deg, #D97706, #B45309);
        border: 1.5px solid #FBBF24;
    }
    .avatar-negotiation {
        background: linear-gradient(135deg, #7C3AED, #6D28D9);
        border: 1.5px solid #A78BFA;
    }
    .chat-bubble {
        background: rgba(17, 24, 39, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        border-top-left-radius: 2px;
        padding: 15px 20px;
        flex-grow: 1;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .bubble-planner { border-left: 3.5px solid #9CA3AF; }
    .bubble-flight { border-left: 3.5px solid #60A5FA; }
    .bubble-hotel { border-left: 3.5px solid #34D399; }
    .bubble-budget { border-left: 3.5px solid #FBBF24; }
    .bubble-negotiation { border-left: 3.5px solid #A78BFA; }
    
    .chat-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    }
    .chat-agent-name {
        font-weight: 700;
        font-size: 1.0rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .chat-agent-role {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 700;
    }
    .role-planner { background: rgba(156, 163, 175, 0.12); color: #D1D5DB; }
    .role-flight { background: rgba(59, 130, 246, 0.12); color: #60A5FA; }
    .role-hotel { background: rgba(16, 185, 129, 0.12); color: #34D399; }
    .role-budget { background: rgba(245, 158, 11, 0.12); color: #FBBF24; }
    .role-negotiation { background: rgba(139, 92, 246, 0.12); color: #A78BFA; }
    
    .chat-time {
        font-size: 0.75rem;
        color: #6B7280;
    }
    .chat-text {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #E5E7EB;
        white-space: pre-wrap;
    }
    
    /* Thinking Container Styling */
    .chat-thinking-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
        font-size: 0.85rem;
    }
    .chat-thinking-summary {
        color: #9CA3AF;
        font-weight: 600;
        cursor: pointer;
        outline: none;
        user-select: none;
    }
    .chat-thinking-text {
        color: #9CA3AF;
        margin-top: 8px;
        white-space: pre-wrap;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Helper to convert basic markdown elements to HTML
def format_markdown_to_html(text: str) -> str:
    import re
    # Escape standard HTML tags except think tags
    html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = html.replace("&lt;think&gt;", "<think>").replace("&lt;/think&gt;", "</think>")
    
    # Bold: **text** -> <strong>text</strong>
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Italics: *text* -> <em>text</em>
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    # Inline code: `code` -> <code>code</code>
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Convert lists
    lines = html.split("\n")
    formatted_lines = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:]
            if not in_list:
                formatted_lines.append("<ul>")
                in_list = True
            formatted_lines.append(f"<li>{content}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            formatted_lines.append(line)
    if in_list:
        formatted_lines.append("</ul>")
        
    return "\n".join(formatted_lines)

# Helper function to render a chat message bubble
def render_chat_message(agent_name: str, role_class: str, avatar: str, avatar_class: str, bubble_class: str, content: str, is_done: bool = False):
    color_map = {
        "flight": "#60A5FA",
        "hotel": "#34D399",
        "budget": "#FBBF24",
        "negotiation": "#A78BFA",
        "planner": "#9CA3AF"
    }
    color = color_map.get(role_class, "#D1D5DB")
    current_time = datetime.now().strftime('%H:%M:%S')
    
    thinking, main_output = parse_thinking_and_output(content, is_done)
    
    formatted_thinking = format_markdown_to_html(thinking) if thinking else ""
    formatted_main = format_markdown_to_html(main_output) if main_output else ""
    
    thinking_html = ""
    if thinking:
        # Collapse the thinking details if the block is fully finished (indicated by </think> or is_done)
        is_thinking_finished = is_done or ("</think>" in content)
        open_attr = "" if is_thinking_finished else " open"
        thinking_html = f"""<details class="chat-thinking-container"{open_attr}>
<summary class="chat-thinking-summary">🧠 Thinking process...</summary>
<div class="chat-thinking-text">{formatted_thinking}</div>
</details>"""
        
    return f"""<div class="chat-message-row">
<div class="chat-avatar avatar-{avatar_class}">{avatar}</div>
<div class="chat-bubble bubble-{bubble_class}">
<div class="chat-meta">
<span class="chat-agent-name" style="color: {color};">{agent_name}</span>
<span class="chat-agent-role role-{role_class}">{role_class.upper()}</span>
<span class="chat-time">{current_time}</span>
</div>
{thinking_html}
<div class="chat-text">{formatted_main}</div>
</div>
</div>"""

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
        # We start the server asynchronously and let it run
        cmd = [
            "mlflow", "server",
            "--backend-store-uri", "sqlite:///mlflow.db",
            "--default-artifact-root", "./mlruns",
            "--host", "127.0.0.1",
            "--port", str(port)
        ]
        try:
            subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                shell=True
            )
            time.sleep(2.5) # Give it time to bind the port
        except Exception as e:
            st.error(f"Failed to start MLflow server: {e}")

# Helper to fetch active Ollama models
def get_ollama_models():
    try:
        import ollama
        client = ollama.Client()
        models_data = client.list()
        model_names = []
        if models_data and hasattr(models_data, "models"):
            for m in models_data.models:
                # Retrieve the model name using attribute or dictionary dump
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
        # Return sensible defaults if ollama client is not running/installed
        return None

# Title header with premium aesthetic
st.markdown("""
    <div style='margin-bottom: 25px;'>
        <h1 style='margin: 0; padding: 0;'>TravelNet AI</h1>
        <p style='color: #9CA3AF; margin-top: 5px; font-size: 1.1rem;'>
            Peer-to-Peer Multi-Agent Travel Planner & Research Studio
        </p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR INTERFACE ---
with st.sidebar:
    st.markdown("### 🗺️ Evolution Phase")
    phase_selection = st.selectbox(
        "Select Active Build Phase",
        options=[
            "Phase 0: Baseline System (Direct Flow)",
            "Phase 1: Memory Systems (Locked)",
            "Phase 2: Adaptive Routing (Locked)",
            "Phase 3: Event Synchronization (Locked)"
        ],
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Agent Configuration")
    
    # Model Selection
    available_models = get_ollama_models() or ["llama3.2:latest", "qwen3.5:4b", "gemma4:e2b"]
    selected_model = st.selectbox("Select LLM Model", options=available_models, index=0)
    
    # Memory and Sync Configurations
    memory_type = st.selectbox(
        "Memory System Type",
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
    
    sync_type = st.selectbox(
        "Synchronization Protocol",
        options=[
            "direct_message",
            "shared_blackboard",
            "event_driven",
            "publisher_subscriber",
            "state_versioning",
            "distributed_memory_sync"
        ],
        index=0
    )
    
    temperature = st.slider("LLM Temperature", min_value=0.0, max_value=1.0, value=0.4, step=0.1)
    
    st.markdown("---")
    
    st.markdown("### ✈️ Travel Details")
    
    # Inputs for travel planning
    origin = st.text_input("Origin City", value="Seattle")
    destination = st.text_input("Destination City", value="San Francisco")
    
    col_dates = st.columns(2)
    with col_dates[0]:
        dep_date = st.date_input("Departure Date", value=date(2026, 9, 15))
    with col_dates[1]:
        ret_date = st.date_input("Return Date", value=date(2026, 9, 19))
        
    travelers = st.number_input("Number of Travelers", min_value=1, max_value=10, value=1)
    budget = st.text_input("Total Budget", value="$1500")
    
    preferences = st.text_area(
        "Traveler Preferences", 
        value="Economy class, mid-range hotel, morning departure."
    )

# --- MAIN SCREEN INTERFACE ---
tab1, tab2 = st.tabs(["✈️ Trip Planner Dashboard", "📊 MLflow Experiment Tracking"])

with tab1:
    st.markdown("### 🚀 Phase 0: Baseline Planner")
    st.markdown("""
        In Phase 0, travel recommendations are constructed sequentially through a fixed flow of four specialized agents:
        **Flight Agent** ➔ **Hotel Agent** ➔ **Budget Agent** ➔ **Negotiation Agent**.
    """)
    
    # Run button
    if st.button("Generate Travel Plan"):
        # Parameter validation
        if not origin or not destination:
            st.error("Origin and Destination cities cannot be empty!")
        elif dep_date >= ret_date:
            st.error("Departure Date must be before the Return Date!")
        else:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Setup travel request
            request = TravelRequest(
                origin=origin,
                destination=destination,
                departure_date=dep_date.strftime("%Y-%m-%d"),
                return_date=ret_date.strftime("%Y-%m-%d"),
                travelers=int(travelers),
                budget=budget,
                preferences=preferences,
            )
            
            # Initialize Planner Agent with sidebar config
            planner = PlannerAgent(memory_type=memory_type, sync_type=sync_type)
            planner.load_config()
            # Set temperature and active model on agents
            planner.temperature = temperature
            planner.set_model(selected_model)
            
            # 1. FLIGHT SPECIALIST AGENT
            status_text.text("Flight Specialist Agent is researching...")
            progress_bar.progress(10)
            
            flight_summary = ""
            flight_search_req = FlightSearchRequest(
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=request.return_date,
                travelers=request.travelers,
                preferences=request.preferences,
            )
            for chunk in planner.flight_agent.search_flights_stream(flight_search_req):
                flight_summary += chunk
            
            # Clean and verify flight summary
            _, clean_flight = parse_thinking_and_output(flight_summary, is_done=True)
            if not clean_flight or len(clean_flight.strip()) < 30:
                clean_flight = planner.flight_agent.search_flights(flight_search_req)
            
            # 2. HOTEL SPECIALIST AGENT
            status_text.text("Hotel Specialist Agent is finding lodging...")
            progress_bar.progress(35)
            
            hotel_summary = ""
            hotel_search_req = HotelSearchRequest(
                destination=request.destination,
                check_in_date=request.departure_date,
                check_out_date=request.return_date,
                travelers=request.travelers,
                preferences=request.preferences,
            )
            for chunk in planner.hotel_agent.search_hotels_stream(hotel_search_req):
                hotel_summary += chunk
                
            # Clean and verify hotel summary
            _, clean_hotel = parse_thinking_and_output(hotel_summary, is_done=True)
            if not clean_hotel or len(clean_hotel.strip()) < 30:
                clean_hotel = planner.hotel_agent.search_hotels(hotel_search_req)
                
            # 3. BUDGET SPECIALIST AGENT
            status_text.text("Budget Specialist Agent is calculating expenses...")
            progress_bar.progress(60)
            
            budget_summary = ""
            for chunk in planner.budget_agent.analyze_budget_stream(
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=request.return_date,
                travelers=request.travelers,
                flight_summary=clean_flight,
                hotel_summary=clean_hotel,
                user_budget=request.budget,
            ):
                budget_summary += chunk
                
            # Clean and verify budget summary
            _, clean_budget = parse_thinking_and_output(budget_summary, is_done=True)
            if not clean_budget or len(clean_budget.strip()) < 30:
                clean_budget = planner.budget_agent.analyze_budget(
                    destination=request.destination,
                    departure_date=request.departure_date,
                    return_date=request.return_date,
                    travelers=request.travelers,
                    flight_summary=clean_flight,
                    hotel_summary=clean_hotel,
                    user_budget=request.budget,
                )
                
            # 4. NEGOTIATION SPECIALIST AGENT
            status_text.text("Negotiation Specialist Agent is aligning options...")
            progress_bar.progress(80)
            
            negotiation_summary = ""
            for chunk in planner.negotiation_agent.resolve_conflicts_stream(
                flight_summary=clean_flight,
                hotel_summary=clean_hotel,
                budget_summary=clean_budget,
            ):
                negotiation_summary += chunk
            
            # Clean and verify negotiation summary
            _, clean_negotiation = parse_thinking_and_output(negotiation_summary, is_done=True)
            if not clean_negotiation or len(clean_negotiation.strip()) < 30:
                clean_negotiation = planner.negotiation_agent.resolve_conflicts(
                    flight_summary=clean_flight,
                    hotel_summary=clean_hotel,
                    budget_summary=clean_budget,
                )
            
            # Compile final plan with clean agent summaries
            plan = {
                "destination": request.destination,
                "travel_window": f"{request.departure_date} to {request.return_date}",
                "flight_recommendation": clean_flight,
                "hotel_recommendation": clean_hotel,
                "budget_analysis": clean_budget,
                "negotiation_summary": clean_negotiation,
            }
            
            status_text.text("Building final itinerary...")
            progress_bar.progress(95)
            
            itinerary = planner.build_itinerary(request, plan)
            
            progress_bar.progress(100)
            status_text.text("Plan generated successfully!")
            
            # Display final itinerary
            st.markdown("### 📋 Final Compiled Itinerary")
            st.code(itinerary, language="markdown", wrap_lines=True)
            
            # Log run metrics and parameters to MLflow
            status_text.text("Logging metrics to MLflow tracker...")
            with MLflowTracker() as tracker:
                tracker.log_params(
                    {
                        "model": selected_model,
                        "memory_type": memory_type,
                        "sync_type": sync_type,
                        "temperature": temperature,
                        "origin": request.origin,
                        "destination": request.destination,
                        "departure_date": request.departure_date,
                        "return_date": request.return_date,
                        "travelers": request.travelers,
                        "budget": request.budget,
                    }
                )
                tracker.log_metrics(
                    {
                        "phases": 0,
                        "agent_calls": 4,
                        "completion_status": 1
                    }
                )
            status_text.text("Travel itinerary finalized. Runs logged to MLflow.")

with tab2:
    st.markdown("### 📊 MLflow Tracking Dashboard")
    st.markdown("""
        View all historical travel planning agent executions, parameters, and metrics recorded in `mlflow.db`.
    """)
    
    # Ensure MLflow server runs in background
    ensure_mlflow_server(port=5000)
    
    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        st.markdown("[🔗 Open MLflow in New Tab](http://127.0.0.1:5000)", unsafe_allow_html=True)
        
    st.iframe(src="http://127.0.0.1:5000", height=800)
