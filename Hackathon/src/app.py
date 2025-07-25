st.caption("Your personal assistant for research and analysis, powered by Google Gemini.")
import streamlit as st
import asyncio
from main import run_agent

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

if goal := st.chat_input("What can I help you with today?"):
    st.session_state.history.append({"role": "user", "content": goal})
    with st.chat_message("user"): st.markdown(goal)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                plan, results, final_response = asyncio.run(run_agent(goal))
                plan_str = "\n".join(f"{i+1}. {t['task']}" for i, t in enumerate(plan))
                response = f"### My Plan:\n```\n{plan_str}\n```\n\n### Execution Results:\n"
                for i, r in enumerate(results):
                    response += f"**Task {i+1}: {plan[i]['task']}**\n> {r}\n\n"
                response += f"### Final Answer:\n{final_response}"
                st.markdown(response)
                st.session_state.history.append({"role": "assistant", "content": response})
            except Exception as e:
                err = f"An error occurred: {e}"
                st.error(err)
                st.session_state.history.append({"role": "assistant", "content": err})
