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
        models_data = client.list().get("models", [])
        model_names = [m["name"] for m in models_data if "embed" not in m["name"].lower()]
        if not model_names:
            return ["llama3.2:latest", "qwen3.5:4b", "gemma4:e2b"]
        return model_names
    except Exception:
        # Return sensible defaults if ollama client is not running/installed
        return ["llama3.2:latest", "qwen3.5:4b", "gemma4:e2b"]

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
    available_models = get_ollama_models()
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
            
            st.markdown("#### 🔄 Agent Workflow Execution")
            
            # 1. FLIGHT SPECIALIST AGENT
            status_text.text("Invoking Flight Specialist Agent...")
            progress_bar.progress(10)
            
            flight_container = st.container()
            with flight_container:
                st.markdown(
                    "<div class='agent-header'><span class='agent-title'>✈️ Flight Specialist Agent</span><span class='agent-badge'>Active</span></div>", 
                    unsafe_allow_html=True
                )
                flight_stream_area = st.empty()
                
            flight_summary = ""
            flight_search_req = FlightSearchRequest(
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=request.return_date,
                travelers=request.travelers,
                preferences=request.preferences,
            )
            
            # Stream Flight Agent Output
            for chunk in planner.flight_agent.search_flights_stream(flight_search_req):
                flight_summary += chunk
                flight_stream_area.markdown(f"<div class='agent-content'>{flight_summary}</div>", unsafe_allow_html=True)
            
            # 2. HOTEL SPECIALIST AGENT
            status_text.text("Invoking Hotel Specialist Agent...")
            progress_bar.progress(35)
            
            hotel_container = st.container()
            with hotel_container:
                st.markdown(
                    "<div class='agent-header'><span class='agent-title'>🏨 Hotel Specialist Agent</span><span class='agent-badge'>Active</span></div>", 
                    unsafe_allow_html=True
                )
                hotel_stream_area = st.empty()
                
            hotel_summary = ""
            hotel_search_req = HotelSearchRequest(
                destination=request.destination,
                check_in_date=request.departure_date,
                check_out_date=request.return_date,
                travelers=request.travelers,
                preferences=request.preferences,
            )
            
            # Stream Hotel Agent Output
            for chunk in planner.hotel_agent.search_hotels_stream(hotel_search_req):
                hotel_summary += chunk
                hotel_stream_area.markdown(f"<div class='agent-content'>{hotel_summary}</div>", unsafe_allow_html=True)
                
            # 3. BUDGET SPECIALIST AGENT
            status_text.text("Invoking Budget Specialist Agent...")
            progress_bar.progress(60)
            
            budget_container = st.container()
            with budget_container:
                st.markdown(
                    "<div class='agent-header'><span class='agent-title'>💰 Budget Specialist Agent</span><span class='agent-badge'>Active</span></div>", 
                    unsafe_allow_html=True
                )
                budget_stream_area = st.empty()
                
            budget_summary = ""
            # Stream Budget Agent Output
            for chunk in planner.budget_agent.analyze_budget_stream(
                destination=request.destination,
                departure_date=request.departure_date,
                return_date=request.return_date,
                travelers=request.travelers,
                flight_summary=flight_summary,
                hotel_summary=hotel_summary,
                user_budget=request.budget,
            ):
                budget_summary += chunk
                budget_stream_area.markdown(f"<div class='agent-content'>{budget_summary}</div>", unsafe_allow_html=True)
                
            # 4. NEGOTIATION SPECIALIST AGENT
            status_text.text("Invoking Negotiation Specialist Agent...")
            progress_bar.progress(80)
            
            neg_container = st.container()
            with neg_container:
                st.markdown(
                    "<div class='agent-header'><span class='agent-title'>🤝 Negotiation Specialist Agent</span><span class='agent-badge'>Active</span></div>", 
                    unsafe_allow_html=True
                )
                neg_stream_area = st.empty()
                
            negotiation_summary = ""
            # Stream Negotiation Agent Output
            for chunk in planner.negotiation_agent.resolve_conflicts_stream(
                flight_summary=flight_summary,
                hotel_summary=hotel_summary,
                budget_summary=budget_summary,
            ):
                negotiation_summary += chunk
                neg_stream_area.markdown(f"<div class='agent-content'>{negotiation_summary}</div>", unsafe_allow_html=True)
                
            # Compile final plan
            plan = {
                "destination": request.destination,
                "travel_window": f"{request.departure_date} to {request.return_date}",
                "flight_recommendation": flight_summary,
                "hotel_recommendation": hotel_summary,
                "budget_analysis": budget_summary,
                "negotiation_summary": negotiation_summary,
            }
            
            status_text.text("Building final itinerary...")
            progress_bar.progress(95)
            
            itinerary = planner.build_itinerary(request, plan)
            
            progress_bar.progress(100)
            status_text.text("Plan generated successfully!")
            
            # Display final itinerary in a beautiful text area
            st.markdown("### 📋 Final Compiled Itinerary")
            st.code(itinerary, language="markdown")
            
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
        
    st.components.v1.iframe(src="http://127.0.0.1:5000", height=800, scrolling=True)
