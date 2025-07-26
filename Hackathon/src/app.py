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
            color: #333; /* Darker text for chat messages */
        }
        .stTextInput input {
            font-size: 1.1rem;
        }
        .sidebar .stButton button {
            background-color: #ff4b4b;
            color: white;
        }
        .result-box, .result-box *, .final-answer-box, .final-answer-box * {
            color: #333 !important; /* Darker text for results, force override */
        }
        .result-box {
            background-color: rgba(240, 242, 246, 0.7);
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #0066cc;
            margin-bottom: 1rem;
        }
        .final-answer-box {
            background-color: rgba(220, 235, 255, 0.9);
            padding: 1.5rem;
            border-radius: 0.7rem;
            border: 2px solid #0066cc;
            margin-top: 1rem;
        }
        /* Style for code blocks for better readability (Light Theme) */
        .result-box pre, .final-answer-box pre {
            background-color: #f5f5f5; /* Light grey background */
            color: #333; /* Dark text for code */
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #ddd;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .result-box code, .final-answer-box code {
            background-color: #e7e7e7; /* Slightly different grey for inline code */
            color: #d63369; /* A nice pink/red for inline code */
            padding: 0.2rem 0.4rem;
            border-radius: 0.3rem;
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
                if isinstance(data, str) and "rate limit" in data.lower():
                    st.warning(data)
                    st.session_state.history.append({"role": "assistant", "content": data})
                else:
                    # Ensure data is properly structured
                    if isinstance(data, dict) and all(k in data for k in ["plan", "results", "response"]):
                        # Create plan string and display it
                        plan_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(data["plan"]))
                        
                        # Display the plan in a nice format
                        st.markdown("### 📋 Analysis & Plan")
                        with st.expander("View Detailed Plan", expanded=True):
                            for i, step in enumerate(data["plan"]):
                                st.markdown(f"**Step {i+1}:** {step}")
                        
                        # Display execution results
                        st.markdown("### 🔄 Execution Results")
                        for i, (step, result) in enumerate(zip(data["plan"], data["results"])):
                            with st.expander(f"Task {i+1}: {step[:100]}...", expanded=True):
                                st.markdown(
                                    f'<div class="result-box">{result}</div>',
                                    unsafe_allow_html=True
                                )
                    
                        # Display final answer if it exists
                        if "response" in data and data["response"]:
                            st.markdown("### 💡 Final Answer")
                            st.markdown(
                                f'<div class="final-answer-box">{data["response"]}</div>',
                                unsafe_allow_html=True
                            )
                        
                        # Store the formatted response in history
                        formatted_response = (
                            "### 📋 Analysis & Plan\n" +
                            plan_str + "\n\n" +
                            "### 🔄 Execution Results\n" +
                            "\n".join(f"**Task {i+1}:** {step}\n> {result}" 
                                    for i, (step, result) in enumerate(zip(data["plan"], data["results"]))) +
                            "\n\n### 💡 Final Answer\n" +
                            data.get('response', 'No final answer provided.')
                        )
                        st.session_state.history.append({"role": "assistant", "content": formatted_response})
                    else:
                        # Handle unstructured response
                        st.markdown("### Response")
                        st.markdown(
                            f'<div class="final-answer-box">{str(data)}</div>',
                            unsafe_allow_html=True
                        )
                        st.session_state.history.append({"role": "assistant", "content": str(data)})
            except Exception as e:
                err = f"An error occurred: {str(e)}"
                if "429" in str(e):
                    st.warning("Rate limit exceeded. Please wait a minute and try again. The free tier is limited to 50 requests per day.")
                else:
                    st.error(err)
                st.session_state.history.append({"role": "assistant", "content": err})
