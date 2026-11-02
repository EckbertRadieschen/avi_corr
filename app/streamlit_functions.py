import streamlit as st

def explorer_button ():
    st.session_state["page"] = "explorer"
    species_index = st.session_state["species_options"].index(st.session_state.get(
        "selected_species", 
        ('04650', 'Acadian Flycatcher', 'Empidonax virescens', 'Passeriformes', 'Tyrannidae')
    ))
    
    st.session_state["selected_species"] = st.session_state["species_options"][species_index]

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

def top_button_water ():
    st.session_state["top_bottom_water"] = "top"

def bottom_button_water ():
    st.session_state["top_bottom_water"] = "bottom"

def top_button_urban ():
    st.session_state["top_bottom_urban"] = "top"

def bottom_button_urban ():
    st.session_state["top_bottom_urban"] = "bottom"

def male_button ():
    st.session_state["bird_gender"] = "male"

def female_button ():
    st.session_state["bird_gender"] = "female"