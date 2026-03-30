import streamlit as st

st.set_page_config(page_title="Math Quiz Game", page_icon="🧮", layout="wide")

st.title("🧮 Math Quiz Game")
st.write(
    """
Welcome!

Use the sidebar to navigate:
- **📊 Dashboard**: Tracks every session from `sessions.json`
- **✖ Multiplication**: Multiplication table quiz
- **➕ Addition**: Addition practice quiz

Later we can add Subtraction and Division as separate pages.
"""
)
