import streamlit as st
import os
from dotenv import load_dotenv
from agentic_ai import Orchestrator

st.set_page_config(
    page_title="Agentic AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stTitle {
            font-size: 3rem !important;
            padding-bottom: 1rem;
        }
        .stMarkdown {
            font-size: 1.1rem;
        }
        .stButton button {
            width: 100%;
        }
        .stChatMessage {
            background-color: rgba(240, 242, 246, 0.4);
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stTextInput input {
            font-size: 1.1rem;
        }
        .sidebar .stButton button {
            background-color: #ff4b4b;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Main title with animation effect
st.markdown("""
    <h1 style='text-align: center; color: #0066cc; animation: fadeIn 2s;'>
        🤖 Agentic AI Assistant
    </h1>
    <p style='text-align: center; font-size: 1.2rem; color: #666;'>
        Your intelligent research companion, powered by Google Gemini
    </p>
""", unsafe_allow_html=True)

# Info box for key features
st.info("""
    **Key Features:**
    * 🔍 Advanced research and analysis
    * 💡 Intelligent task planning
    * 🧠 Context-aware responses
    * 📊 Data visualization support
    * 🛠️ Customizable behavior
""")

# Keep chat history across interactions
if 'history' not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model Settings
    st.subheader("🤖 Model Settings")
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = 1000
        
    st.session_state.temperature = st.slider(
        "Temperature (Creativity)", 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state.temperature,
        help="Higher values make the output more creative but less focused"
    )
    
    st.session_state.max_tokens = st.number_input(
        "Max Response Length",
        min_value=100,
        max_value=2000,
        value=st.session_state.max_tokens,
        help="Maximum number of tokens in the response"
    )
    
    # Agent Behavior
    st.subheader("🎯 Agent Behavior")
    st.session_state.style = st.selectbox(
        "Response Style",
        ["Balanced", "Concise", "Detailed"],
        help="Choose how detailed the agent's responses should be"
    )
    
    st.session_state.tools = st.multiselect(
        "Enabled Tools",
        ["Web Search", "Code Analysis", "Data Analysis", "Memory"],
        default=["Web Search", "Code Analysis"],
        help="Select which tools the agent can use"
    )
    
    # Memory Settings
    st.subheader("🧠 Memory Settings")
    st.session_state.memory_enabled = st.toggle(
        "Enable Long-term Memory",
        value=True,
        help="Allow the agent to remember context from previous conversations"
    )
    if st.session_state.memory_enabled:
        st.session_state.memory_length = st.slider(
            "Memory Length",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of previous conversations to remember"
        )
    
    # Advanced Settings
    with st.expander("🔧 Advanced Settings"):
        st.session_state.safety_level = st.select_slider(
            "Safety Level",
            options=["Low", "Medium", "High"],
            value="Medium",
            help="Control the level of content filtering"
        )
        
    # Add a clear button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.history = []
        st.rerun()

for m in st.session_state.history:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if 'orchestrator' not in st.session_state:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in .env file.")
        st.stop()
    st.session_state.orchestrator = Orchestrator(api_key)

st.markdown("---")

# Chat interface
st.markdown("""
    <h3 style='text-align: center; color: #666;'>
        💬 Chat Interface
    </h3>
""", unsafe_allow_html=True)

if goal := st.chat_input("What can I help you with today? (Type your question here)"):
    st.session_state.history.append({"role": "user", "content": goal})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"**You:** {goal}")
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 Thinking..."):
            try:
                result = st.session_state.orchestrator.process_request(goal)
                if result["status"] == "error":
                    raise Exception(result["error"])
                    
                data = result["data"]
                if "rate limit" in str(data).lower():
                    st.warning(data)
                    st.session_state.history.append({"role": "assistant", "content": data})
                else:
                    plan_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(data["plan"]))
                    response = f"### My Plan:\n```\n{plan_str}\n```\n\n### Execution Results:\n"
                    
                    for i, (step, result) in enumerate(zip(data["plan"], data["results"])):
                        response += f"**Task {i+1}: {step}**\n> {result}\n\n"
                    
                    response += f"### Final Answer:\n{data['response']}"
                    st.markdown(response)
                    st.session_state.history.append({"role": "assistant", "content": response})
            except Exception as e:
                err = f"An error occurred: {str(e)}"
                if "429" in str(e):
                    st.warning("Rate limit exceeded. Please wait a minute and try again. The free tier is limited to 50 requests per day.")
                else:
                    st.error(err)
                st.session_state.history.append({"role": "assistant", "content": err})
