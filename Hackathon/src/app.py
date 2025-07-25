"""
Streamlit Frontend for the Agentic AI App
"""

import streamlit as st
import asyncio
from main import run_agent

st.set_page_config(page_title="Agentic AI Assistant", layout="wide")

st.title("🤖 Agentic AI Assistant")
st.caption("Your personal assistant for research and analysis, powered by Google Gemini.")

if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    st.info("This is where you would put any configuration options for your agent.")
    # Add any configuration options here, e.g.:
    # model_name = st.selectbox("Select a model", ["gemini-pro", "other-model"])

# Main chat interface
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

goal = st.chat_input("What can I help you with today?")

if goal:
    st.session_state.history.append({"role": "user", "content": goal})
    with st.chat_message("user"):
        st.markdown(goal)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                plan, results, final_response = asyncio.run(run_agent(goal))
                
                # Display the plan
                st.subheader("My Plan:")
                plan_str = ""
                for i, task in enumerate(plan):
                    plan_str += f"{i+1}. {task['task']}\n"
                st.markdown(plan_str)

                # Display the execution results
                st.subheader("Execution Results:")
                for i, result in enumerate(results):
                    st.text(f"Task {i+1}: {plan[i]['task']}")
                    st.info(result)

                # Display the final response
                st.subheader("Final Answer:")
                st.markdown(final_response)

                st.session_state.history.append({"role": "assistant", "content": final_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.history.append({"role": "assistant", "content": f"Sorry, an error occurred: {e}"})
