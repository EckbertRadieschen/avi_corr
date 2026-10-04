import streamlit as st

def explorer_button ():
    st.session_state["page"] = "explorer"

def lexicon_button ():
    st.session_state["page"] = "lexicon"