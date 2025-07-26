import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from agentic_ai import Orchestrator

st.set_page_config(page_title="Agentic AI Assistant", layout="wide")
st.title("🤖 Agentic AI Assistant")
st.caption("Your personal assistant for research and analysis, powered by Google Gemini.")

# Keep chat history across interactions
if 'history' not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.header("Configuration")
    st.info("(Future agent settings)")

for m in st.session_state.history:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if 'orchestrator' not in st.session_state:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found in .env file.")
        st.stop()
    st.session_state.orchestrator = Orchestrator(api_key)

if goal := st.chat_input("What can I help you with today?"):
    st.session_state.history.append({"role": "user", "content": goal})
    with st.chat_message("user"): st.markdown(goal)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = asyncio.run(st.session_state.orchestrator.process_request(goal))
                if result["status"] == "error":
                    raise Exception(result["error"])
                    
                data = result["data"]
                plan_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(data["plan"]))
                response = f"### My Plan:\n```\n{plan_str}\n```\n\n### Execution Results:\n"
                
                for i, (step, result) in enumerate(zip(data["plan"], data["results"])):
                    response += f"**Task {i+1}: {step}**\n> {result}\n\n"
                
                response += f"### Final Answer:\n{data['response']}"
                st.markdown(response)
                st.session_state.history.append({"role": "assistant", "content": response})
            except Exception as e:
                err = f"An error occurred: {e}"
                st.error(err)
                st.session_state.history.append({"role": "assistant", "content": err})
