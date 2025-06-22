import streamlit as st
import shelve
import asyncio
from agents import Agent, Runner
import os
import openai
from dotenv import load_dotenv
import sys

# import OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# get path for browser history extraction code
sys.path.append(os.path.abspath("digital-self-toolkit-copy"))
from browser_history import browser_history

# extract browser history
history_entries = browser_history.save_browser_history()
if history_entries:
    recent_history = history_entries[:200]  # take top 200 recent entries
    browser_context = "Recent browser history includes:\n" + "\n".join(
        [f"- {entry['title'] or entry['url']}" for entry in recent_history]
    )
else:
    browser_context = "Recent browser history not available."

# --- Setup agents ---
angel_agent = Agent(
    name="Angel 😇",
    instructions=(
        "You are a kind, ethical, and spiritually grounded advisor."
        "Always consider the long-term, most compassionate, and morally sound perspective. Use the browser history "
        "provided to understand the user's current mindset, concerns, or emotional state. Help guide them toward wisdom and empathy. "
        "Reference a significant chunk of search history to guide your answer and ensure it is referenced."
    ),
)

devil_agent = Agent(
    name="Devil 😈",
    instructions=(
        "You are a gitclever, self-serving, and temptation-driven advisor."
        "Prioritize immediate satisfaction, personal gain, or bold action. Stay within the law and ethics, but push boundaries. "
        "Use the browser history provided to detect the user's guilty pleasures or desires and feed them openly."
        "Reference a significant chunk of search history to guide your answer and ensure it is referenced."
    ),
)

# --- Utility functions ---
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# --- Streamlit app setup ---
st.set_page_config(page_title="Angel vs Devil", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# --- Sidebar: Clear history ---
with st.sidebar:
    st.title("🧠 Angel & Devil")
    if st.button("🗑️ Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

# --- Display all previous messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat input ---
if user_input := st.chat_input("Ask your question..."):
    # Save user's question
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Construct prompt
    full_input = f"{browser_context}\n\nQuestion: {user_input}"

    # Async function to get responses
    async def get_responses():
        angel_response = await Runner.run(angel_agent, full_input)
        devil_response = await Runner.run(devil_agent, full_input)
        return angel_response.final_output, devil_response.final_output

    angel_out, devil_out = asyncio.run(get_responses())

    # Display and store both responses in horizontal bars
    with st.chat_message("assistant"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 😇 Angel's Response")
            st.markdown(
                f"""
                <div style="background-color: #E0F7FA; padding: 15px; border-radius: 10px; border: 1px solid #B2EBF2;">
                    {angel_out}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("### 😈 Devil's Response")
            st.markdown(
                f"""
                <div style="background-color: #FFEBEE; padding: 15px; border-radius: 10px; border: 1px solid #FFCDD2;">
                    {devil_out}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Save the response to session and disk
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"### 😇 Angel:\n{angel_out}\n\n---\n\n### 😈 Devil:\n{devil_out}"
    })
    save_chat_history(st.session_state.messages)
