import streamlit as st

def explorer_button ():
    st.session_state["page"] = "explorer"

def lexicon_button ():
    st.session_state["page"] = "lexicon"

def statistics_button ():
    st.session_state["page"] = "statistics"

def top_button_main ():
    st.session_state["top_bottom_main"] = "top"

def bottom_button_main ():
    st.session_state["top_bottom_main"] = "bottom"

def top_button_width ():
    st.session_state["top_bottom_width"] = "top"

def bottom_button_width ():
    st.session_state["top_bottom_width"] = "bottom"

def male_button ():
    st.session_state["bird_gender"] = "male"

def female_button ():
    st.session_state["bird_gender"] = "female"    