import plotly.graph_objects as go
from pathlib import Path
from zipfile import ZipFile
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MAP_VISUALS_FOLDER = BASE_DIR / "assets" / "map_visuals"

CONFIG_PATH = BASE_DIR / "src" / "config" 
SPECIES_GRID_ZIP = CONFIG_PATH / "species_grid_configs.zip"
SPECIES_CONFIG_PATH = CONFIG_PATH / "species_config.json"

def load_base_grid ():
    with ZipFile(SPECIES_GRID_ZIP, "r") as zip:
        with zip.open("base_grid.json", "r") as file:
            return json.load(file)

def load_species_grid(species_id, base_grid):
    with ZipFile(SPECIES_GRID_ZIP, "r") as zip:
        with zip.open(f"{species_id}_grid.json", "r") as file:
            species_grid_config = json.load(file)

    features = species_grid_config["features"]

    for feature in features:
        cell_id = feature["id"]
        geometry = base_grid[cell_id]
        feature["geometry"] = geometry

    return species_grid_config


def plot_species_usa_map(species_grid):
    features = species_grid["features"]
    locations = []
    values = []

    for feature in features:
        values.append(feature["properties"]["value"])
        locations.append(feature["id"])

    colorscale_map = [
        [0.00, "#FFFFFF"],
        [0.10, "#FFF0B3"],
        [0.25, "#FFB347"],
        [0.55, "#FF6B1A"],
        [0.75, "#D7191C"],
        [1.00, "#8B0000"]
    ]

    fig = go.Figure(
        go.Choroplethmap(
            geojson=species_grid,
            locations=locations,
            z=values,
            featureidkey="id",
            colorscale=colorscale_map,
            zmin=0,
            zmax=1,
            marker={"line": {"width": 0}},
            colorbar={
                "title": {"text": "High-count ratio"},
                "tickvals": [0, 0.25, 0.5, 0.75, 1],
                "ticktext": ["0", "0.25", "0.5", "0.75", "1"]
            },
            hoverinfo="skip"
        )
    )

    fig.update_traces(
        showscale=False
    )

    fig.update_layout(
        map={
            "style": "carto-positron",
            "center": {"lat": 38.0, "lon": -98.5},
            "zoom": 2.8
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=270
    )

    return fig


def create_map_visual_files ():
    base_grid = load_base_grid()
    
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    species_count = len(species_config)

    for counter, species_id in enumerate(species_config, start=1):
        print(f"{counter}/{species_count} - Working on {species_id}")

        species_grid = load_species_grid(species_id, base_grid)
        species_map_figure = plot_species_usa_map(species_grid)

        species_map_file_path = MAP_VISUALS_FOLDER / f"map_{species_id}.png"

        species_map_figure.write_image(
            species_map_file_path,
            width=800,
            height=540,
            scale=2
        )


if __name__ == "__main__":
    create_map_visual_files()