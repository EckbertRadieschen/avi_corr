import os
from dotenv import load_dotenv

import pandas as pd
import streamlit as st
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import json
from pathlib import Path

from app.css import main_css
from app.markdown import apply_markdown   
from app.explorer_page import get_explorer_content
from app.lexicon_page import get_lexicon_content
from app.statistics_page import get_statistics_content


load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    database=MYSQL_DATABASE
)

ENGINE = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

BASE_DIR = Path(__file__).resolve().parent

PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
SPECIES_ZIP_PATH = PROCESSED_DATA_DIR / "species_csv_files.zip"

CONFIG_DIR = BASE_DIR / "src" / "config"
SPECIES_GRID_ZIP = CONFIG_DIR / "species_grid_configs.zip"

SPECIES_CONFIG_PATH = CONFIG_DIR / "species_config.json"
ROUTE_CONFIG_PATH = CONFIG_DIR / "route_config.json"
GRID_CONFIG_PATH = CONFIG_DIR / "grid_config.json"
BASE_GRID_CONFIG_PATH = CONFIG_DIR / "base_grid.json"

CLIMATE_CONFIG_PATH = CONFIG_DIR / "climate_config.json"
LANDCOVER_CONFIG_PATH = CONFIG_DIR / "landcover_config.json"

CLIMATE_STAT_CONFIG_PATH = CONFIG_DIR / "climate_stat_config.json"

# =====================================================

def print_value_list (column: pd.Series):
    meine_liste = column.sort_values().unique()
    print(*meine_liste, sep="\n")

# ============================================================================================================
# App
# ============================================================================================================

# =================================================================
# CSS

apply_markdown()
main_css()

st.set_page_config(layout="wide")

# ====================================================================
# State Management
# ====================================================================

if "page" not in st.session_state:
    st.session_state["page"] = "lexicon"

if "species_config" not in st.session_state:
    with open(SPECIES_CONFIG_PATH, "r") as file:
        st.session_state["species_config"] = json.load(file)

species_config = st.session_state["species_config"]

if "route_config" not in st.session_state:
    with open(ROUTE_CONFIG_PATH, "r") as file:
        st.session_state["route_config"] = json.load(file)

route_config = st.session_state["route_config"]

if "grid_config" not in st.session_state:
    with open(BASE_GRID_CONFIG_PATH, "r") as file:
        st.session_state["grid_config"] = json.load(file)

if "climate_config" not in st.session_state:
    with open(CLIMATE_CONFIG_PATH, "r") as file:
        st.session_state["climate_config"] = json.load(file)

if "landcover_config" not in st.session_state:
    with open(LANDCOVER_CONFIG_PATH, "r") as file:
        st.session_state["landcover_config"] = json.load(file)

if "climate_stat_config" not in st.session_state:
    with open(CLIMATE_STAT_CONFIG_PATH, "r") as file:
        st.session_state["climate_stat_config"] = json.load(file)

if "species_list" not in st.session_state:
    species_list = []

    for species_id, species_dict in species_config.items():
        audubon_info = species_dict["audubon_info"]
        meta_data = species_dict["meta_data"]
        common_name = audubon_info["common_name"]

        if meta_data["total_observations"] >= 250:
            species_list.append((species_id, common_name))

    # st.session_state["species_list"] = species_list
    st.session_state["species_list"] = sorted(species_list, key=lambda x: x[1])

species_list = st.session_state["species_list"]


if st.session_state["page"] == "explorer": 
    get_explorer_content()


elif st.session_state["page"] == "lexicon":
    get_lexicon_content()

elif st.session_state["page"] == "statistics":
    get_statistics_content()
    
    