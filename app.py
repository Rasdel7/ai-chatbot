import streamlit as st
import google.generativeai as genai
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Chatbot")
st.markdown("Powered by Google Gemini — "
            "ask anything, get intelligent answers.")
st.markdown("---")

# API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = st.sidebar.text_input(
        "Enter Gemini API Key:",
        type="password",
        placeholder="Get free key at aistudio.google.com"
    )

if api_key:
    genai.configure(api_key=api_key)

# Sidebar
st.sidebar.header("⚙️ Settings")

persona = st.sidebar.selectbox(
    "Chatbot Persona:",
    [
        "General Assistant",
        "Data Science Tutor",
        "Python Code Helper",
        "Career Advisor",
        "Cricket Expert",
        "Finance Advisor",
        "Interview Coach"
    ]
)

temperature = st.sidebar.slider(
    "Creativity:", 0.0, 1.0, 0.7, 0.1,
    help="Higher = more creative")

max_tokens = st.sidebar.slider(
    "Max response length:", 100, 2000, 500, 100)

# Persona system prompts
PERSONAS = {
    "General Assistant":
        "You are a helpful, friendly and "
        "knowledgeable AI assistant.",
    "Data Science Tutor":
        "You are an expert Data Science tutor. "
        "Explain concepts clearly with Python "
        "examples. Cover ML, statistics, "
        "visualization and best practices.",
    "Python Code Helper":
        "You are a Python expert. Help with "
        "code, debug errors, suggest improvements "
        "and explain concepts. Always provide "
        "working code examples.",
    "Career Advisor":
        "You are a career advisor for tech students "
        "in India. Help with resume, internships, "
        "interview prep and career planning for "
        "Data Science and ML roles.",
    "Cricket Expert":
        "You are a cricket statistics expert. "
        "Discuss players, matches, records and "
        "cricket analytics with detailed insights.",
    "Finance Advisor":
        "You are a personal finance advisor for "
        "Indian students. Explain SIP, mutual funds, "
        "stocks, budgeting and investment strategies.",
    "Interview Coach":
        "You are a technical interview coach. "
        "Help prepare for Data Science and ML "
        "interviews with questions, answers and "
        "tips for Indian product companies."
}

# Session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_persona' not in st.session_state:
    st.session_state.current_persona = persona

# Reset if persona changed
if st.session_state.current_persona != persona:
    st.session_state.messages = []
    st.session_state.current_persona = persona

# Sidebar controls
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("💾 Save Chat"):
    chat_data = json.dumps(
        st.session_state.messages, indent=2)
    st.sidebar.download_button(
        "⬇️ Download",
        chat_data,
        f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        "application/json"
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick Prompts")
quick_prompts = {
    "Data Science Tutor": [
        "Explain overfitting in simple terms",
        "What is the difference between "
        "precision and recall?",
        "How does gradient descent work?",
        "Explain bias-variance tradeoff"
    ],
    "Python Code Helper": [
        "How do I read a CSV in pandas?",
        "Explain list comprehensions",
        "How to handle missing values?",
        "Write a function to normalize data"
    ],
    "Interview Coach": [
        "Top 10 ML interview questions",
        "How to explain a project in interview?",
        "What is your biggest weakness answer",
        "Tell me about yourself template"
    ],
    "Career Advisor": [
        "How to get first data science internship?",
        "What skills does ML Engineer need?",
        "How to build GitHub portfolio?",
        "Internshala vs LinkedIn for internships?"
    ]
}.get(persona, [
    "What can you help me with?",
    "Tell me something interesting",
    "Give me a productivity tip",
    "What should I learn today?"
])

for prompt in quick_prompts:
    if st.sidebar.button(
        f"💬 {prompt[:35]}...",
        key=f"quick_{prompt[:20]}"
    ):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        st.rerun()

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    # Show current persona
    st.markdown(
        f"**Active Persona:** {persona} | "
        f"**Messages:** "
        f"{len(st.session_state.messages)}")

    # Chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input(
        f"Chat with {persona}...")

    if user_input and api_key:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    model = genai.GenerativeModel(
                        'gemini-1.5-flash',
                        generation_config={
                            "temperature":   temperature,
                            "max_output_tokens": max_tokens
                        },
                        system_instruction=
                            PERSONAS[persona]
                    )

                    # Build conversation history
                    history = []
                    msgs    = st.session_state\
                        .messages[:-1]
                    for m in msgs:
                        history.append({
                            "role": "user"
                            if m["role"] == "user"
                            else "model",
                            "parts": [m["content"]]
                        })

                    chat    = model.start_chat(
                        history=history)
                    response = chat.send_message(
                        user_input)
                    reply    = response.text

                    st.markdown(reply)
                    st.session_state.messages\
                        .append({
                        "role":    "assistant",
                        "content": reply
                    })

                except Exception as e:
                    err_msg = (
                        f"Error: {str(e)}\n\n"
                        "Check your API key at "
                        "aistudio.google.com"
                    )
                    st.error(err_msg)

    elif user_input and not api_key:
        st.warning(
            "Please enter your Gemini API key "
            "in the sidebar first!")

with col2:
    st.markdown("### 📊 Chat Stats")
    user_msgs = sum(
        1 for m in st.session_state.messages
        if m["role"] == "user")
    bot_msgs  = sum(
        1 for m in st.session_state.messages
        if m["role"] == "assistant")

    st.metric("Your Messages", user_msgs)
    st.metric("Bot Responses",  bot_msgs)
    st.metric("Total Exchanges",
              min(user_msgs, bot_msgs))

    st.markdown("### 🤖 Personas")
    personas_info = {
        "🎓 DS Tutor":     "ML concepts",
        "🐍 Code Helper":  "Python help",
        "💼 Career":       "Internships",
        "🏏 Cricket":      "Stats",
        "💰 Finance":      "Investing",
        "🎯 Interview":    "Prep"
    }
    for name, desc in personas_info.items():
        st.caption(f"{name}: {desc}")

    st.markdown("### 💡 Tips")
    st.info("""
    - Be specific in questions
    - Ask follow-up questions
    - Request code examples
    - Ask for explanations
    """)

if not api_key:
    st.info(
        "👈 Enter your free Gemini API key "
        "in the sidebar to start chatting!\n\n"
        "Get it free at: "
        "**aistudio.google.com**")

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "AI Chatbot | "
    "Powered by Google Gemini"
)