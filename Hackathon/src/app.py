"""A Streamlit front-end for our agentic AI assistant."""

import streamlit as st
import asyncio
from main import run_agent

# Configure the Streamlit page
st.set_page_config(page_title="Agentic AI Assistant", layout="wide")

st.title("🤖 Agentic AI Assistant")
st.caption("Your personal assistant for research and analysis, powered by Google Gemini.")

# Initialize chat history in session state if it doesn't exist
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Sidebar for future configuration ---
with st.sidebar:
    st.header("Configuration")
    st.info("Future agent settings will appear here.")

# --- Main Chat Interface ---

# Display past messages
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if goal := st.chat_input("What can I help you with today?"):
    # Add user message to history and display it
    st.session_state.history.append({"role": "user", "content": goal})
    with st.chat_message("user"):
        st.markdown(goal)

    # Process the goal and display the agent's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                plan, results, final_response = asyncio.run(run_agent(goal))

                # Create a formatted response with the plan, results, and final answer
                response_content = f"### My Plan:\n"
                plan_str = "\n".join(f"{i+1}. {task['task']}" for i, task in enumerate(plan))
                response_content += f"```\n{plan_str}\n```\n\n"
                response_content += "### Execution Results:\n"
                for i, result in enumerate(results):
                    response_content += f"**Task {i+1}: {plan[i]['task']}**\n> {result}\n\n"
                response_content += f"### Final Answer:\n{final_response}"

                st.markdown(response_content)
                st.session_state.history.append({"role": "assistant", "content": response_content})

            except Exception as e:
                error_message = f"An error occurred: {e}"
                st.error(error_message)
                st.session_state.history.append({"role": "assistant", "content": error_message})
