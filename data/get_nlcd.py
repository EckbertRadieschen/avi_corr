import os
import re
import shutil
from collections import Counter, OrderedDict
from pathlib import Path

import boto3
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

from dotenv import load_dotenv
from rasterio.features import geometry_mask, geometry_window
from rasterio.errors import WindowError
from shapely.geometry import mapping
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


load_dotenv()

TILE_GRID = Path("data/CONUS_C2_ARD_grid/CONUS_C2_ARD_grid.shp")
REQUIRED_TILES_FILE = Path("required_nlcd_tiles.csv")

NLCD_DIR = Path("data/nlcd")

BUFFER_RADIUS_M = 1500