import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import shelve
from src.main import run_full_turn, triage_agent

load_dotenv()

st.title("Chatbot Test")

user_emj = "👤"
bot_emj = "🤖"

def load_chat_history():
    with shelve.open("chat_hisory") as db:
        return db.get("messages",[])
    
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

def extract_role_content(message):
    """Return (role, content) regardless of message object type."""
    if hasattr(message, 'role'):
        return message.role, message.content
    else:
        return message.get("role"), message.get("content")

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "current_agent" not in st.session_state:
    st.session_state.current_agent = triage_agent

with st.sidebar:
    if st.button("Delete chat history"):
        st.session_state.messages = []
        save_chat_history([])

for message in st.session_state.messages:
    role, content = extract_role_content(message)
    avatar = user_emj if role == "user" else bot_emj
    if role != "tool":
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role":"user", "content": prompt})
    with st.chat_message("user", avatar=user_emj):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar = bot_emj):
        response = run_full_turn(
            st.session_state.current_agent,
            st.session_state.messages
        )
        for msg in response.messages:
            role, content = extract_role_content(msg)
            if role == "assistant":
                st.markdown(content)
            # Store as plain dict for consistency
            st.session_state.messages.append({"role": role, "content": content})

        st.session_state.current_agent = response.agent

    save_chat_history(st.session_state.messages)