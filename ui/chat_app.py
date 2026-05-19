import streamlit as st
import redis
import json
import time
from datetime import datetime
import os

st.set_page_config(page_title="ACR - Cognitive Chat", layout="wide")

st.title("🧠 Autobiographical Cognitive Runtime (ACR)")
st.subheader("Chat Interface - Multi-Agent Interaction")

# Redis Connection
redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Inserisci un obiettivo o un messaggio per l'ACR..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Publish to Redis
    event = {
        "event_type": "goal.update",
        "source": "chat_ui",
        "payload": {"goal": prompt},
        "timestamp": datetime.now().isoformat()
    }
    r.publish("goal.update", json.dumps(event))

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*(L'ACR sta elaborando l'obiettivo... controlla i log del runtime)*")
        
        # Listen for updates (simplified polling for demo)
        # In a real app, use a background thread or websocket
        st.info("Obiettivo inviato al bus. Gli agenti (Planner, Critic, Executor) sono al lavoro.")

# Sidebar for status
st.sidebar.header("System Status")
try:
    # Try to get self-model from redis if we had a dedicated key, 
    # but here we just show if redis is up
    if r.ping():
        st.sidebar.success("Redis Bus: Connected")
except:
    st.sidebar.error("Redis Bus: Disconnected")

st.sidebar.markdown("---")
st.sidebar.info("L'interfaccia pubblica eventi sul bus Redis. Gli agenti ACR reagiscono in background in modo asincrono.")
