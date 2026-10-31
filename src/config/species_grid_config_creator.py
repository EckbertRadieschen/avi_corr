import json
import math
import numpy as np
import geopandas as gpd
from pathlib import Path
import zipfile

from shapely.geometry import Polygon, mapping


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
CONFIG_DIR = SRC_DIR / "config"

ROUTE_CONFIG_PATH = CONFIG_DIR / "route_config.json"
SPECIES_CONFIG_PATH = CONFIG_DIR / "species_config.json"

SPECIES_GRIDS_ZIP_PATH = CONFIG_DIR / "species_grid_configs.zip"

DATA_DIR = BASE_DIR / "data"
BOUNDARY_DIR = DATA_DIR / "boundaries"
USA_BOUNDARY_PATH = BOUNDARY_DIR / "cb_2025_us_nation_5m.zip"

MIN_LAT = 24
MAX_LAT = 50

MIN_LON = -125
MAX_LON = -66

LAT_STEP_BASE = 1
LON_STEP_BASE = 1

LAT_STEP_ANALYSIS = 0.2
LON_STEP_ANALYSIS = 0.2


def create_grid(
    min_lat,
    max_lat,
    min_lon,
    max_lon,
    lat_step,
    lon_step
):
    grid = {}

    rows = math.ceil((max_lat - min_lat) / lat_step)
    columns = math.ceil((max_lon - min_lon) / lon_step)

    for row in range(rows):
        for column in range(columns):

            lat = min_lat + row * lat_step
            lon = min_lon + column * lon_step

            cell_id = f"cell_{row:03d}_{column:03d}"

            grid[cell_id] = {
                "meta_data": {
                    "lat": lat + lat_step / 2,
                    "lon": lon + lon_step / 2,
                    "route_count": 0
                },
                "high_count_ratios": {}
            }

    return grid


def get_cell_id(
    lat,
    lon,
    min_lat,
    min_lon,
    max_lat,
    max_lon,
    lat_step,
    lon_step
):
    if not (
        min_lat <= lat < max_lat
        and min_lon <= lon < max_lon
    ):
        return None

    row = math.floor((lat - min_lat) / lat_step)
    column = math.floor((lon - min_lon) / lon_step)

    return f"cell_{row:03d}_{column:03d}"


def get_base_grid_config():
    with open(ROUTE_CONFIG_PATH, "r", encoding="utf-8") as file:
        route_config = json.load(file)

    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_config = json.load(file)

    grid_config = create_grid(
        min_lat=MIN_LAT,
        max_lat=MAX_LAT,
        min_lon=MIN_LON,
        max_lon=MAX_LON,
        lat_step=LAT_STEP_BASE,
        lon_step=LON_STEP_BASE
    )

    route_to_cell = {}

    for route_id, route_dict in route_config.items():
        if route_dict["country"] == "Canada" or route_dict["state"] == "Alaska":
            continue

        lat = route_dict["latitude"]
        lon = route_dict["longitude"]

        cell_id = get_cell_id(
            lat=lat,
            lon=lon,
            min_lat=MIN_LAT,
            min_lon=MIN_LON,
            max_lat=MAX_LAT,
            max_lon=MAX_LON,
            lat_step=LAT_STEP_BASE,
            lon_step=LON_STEP_BASE
        )

        if cell_id is not None:
            route_to_cell[route_id] = cell_id

            grid_config[cell_id]["meta_data"]["route_count"] += 1

    for species_id, species_dict in species_config.items():
        route_list = species_dict["meta_data"]["route_list"]

        for route_id in route_list:
            if route_id not in route_to_cell:
                continue

            route_dict = route_config[route_id]
            ratio_dict = route_dict["high_count_ratios"]
            ratio = ratio_dict[species_id]

            cell_id = route_to_cell[route_id]
            cell = grid_config[cell_id]

            if species_id not in cell["high_count_ratios"]:
                cell["high_count_ratios"][species_id] = []

            cell["high_count_ratios"][species_id].append(ratio)

    for cell in grid_config.values():

        for species_id, ratios in cell["high_count_ratios"].items():
            cell["high_count_ratios"][species_id] = (
                sum(ratios) / len(ratios)
            )

    base_grid_config = {
        cell_id: cell
        for cell_id, cell in grid_config.items()
        if cell["high_count_ratios"]
    }

    return base_grid_config


# =====================================================================
# Analysis Grid
# =====================================================================

def get_sorted_neighbors(target_cells, grid_config):
    source_cells = list(grid_config.values())

    source_coords = np.array([
        [
            cell["meta_data"]["lat"],
            cell["meta_data"]["lon"]
        ]
        for cell in source_cells
    ])

    total_cells = len(target_cells)
    neighbors_by_cell = []

    for target_count, target in enumerate(target_cells, start=1):
        if target_count % 1000 == 0:
            print(f"    Cell: {target_count}/{total_cells}")

        meta = target["meta_data"]
        lat = meta["lat"]
        lon = meta["lon"]

        distances = np.array([
            get_distance(lat, lon, source_lat, source_lon)
            for source_lat, source_lon in source_coords
        ])

        sorted_indices = np.argsort(distances)

        neighbors = [
            (index, distances[index])
            for index in sorted_indices
        ]

        neighbors_by_cell.append(neighbors)

    return source_cells, neighbors_by_cell


def get_sorted_analysis_neighbors(target_cells):
    coords = np.array([
        [cell["meta_data"]["lat"], cell["meta_data"]["lon"]]
        for cell in target_cells
    ])

    total_cells = len(target_cells)

    neighbors_by_cell = []

    for target_index, target in enumerate(target_cells):
        if (target_index + 1) % 100 == 0:
            print(f"    Cell: {target_index + 1}/{total_cells}")

        target_lat = target["meta_data"]["lat"]
        target_lon = target["meta_data"]["lon"]

        distances = np.array([
            get_distance(target_lat, target_lon, lat, lon)
            for lat, lon in coords
        ])

        sorted_indices = np.argsort(distances)
        neighbors_by_cell.append(sorted_indices)

    return neighbors_by_cell


def get_distance(lat1, lon1, lat2, lon2):
    radius = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2 
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(math.sqrt(a))


def interpolate_cell_value(
    species_id,
    target_cells,
    source_cells,
    neighbors_by_cell,
    max_neighbors=8,
    power=2,
    max_distance=200
):
    relevant_indices = {
        i
        for i, cell in enumerate(source_cells)
        if species_id in cell["high_count_ratios"]
    }

    results = np.zeros(len(target_cells), dtype=float)

    if not relevant_indices:
        return results

    total_cells = len(neighbors_by_cell)

    for cell_index, sorted_neighbors in enumerate(neighbors_by_cell):
        if (cell_index + 1) % 1000 == 0:
            print(f"    Cell {cell_index + 1}/{total_cells}")

        relevant_neighbors = [
            (i, distance)
            for i, distance in sorted_neighbors
            if distance <= max_distance
            and i in relevant_indices
        ][:max_neighbors]

        if not relevant_neighbors:
            continue

        weighted_sum = 0.0
        weight_total = 0.0

        for i, distance in relevant_neighbors:
            value = source_cells[i]["high_count_ratios"][species_id]

            if distance == 0:
                weighted_sum = value
                weight_total = 1.0
                break

            weight = 1 / (distance ** power)

            weighted_sum += weight * value
            weight_total += weight

        results[cell_index] = weighted_sum / weight_total

    return results


def create_grid_config():
    print("Loading base config...")
    base_grid_config = get_base_grid_config()

    with open(SPECIES_CONFIG_PATH, "r", encoding="utf-8") as file:
        species_config = json.load(file)

    usa = gpd.read_file(USA_BOUNDARY_PATH)
    usa_geometry = usa.union_all()

    grid_config = create_grid(
        min_lat=MIN_LAT,
        max_lat=MAX_LAT,
        min_lon=MIN_LON,
        max_lon=MAX_LON,
        lat_step=LAT_STEP_ANALYSIS,
        lon_step=LON_STEP_ANALYSIS
    )

    print("Clipping analysis grid to USA boundary ...")

    clipped_grid_config = {}

    half_lat = LAT_STEP_ANALYSIS / 2
    half_lon = LON_STEP_ANALYSIS / 2

    total_cells = len(grid_config)

    for counter, (cell_id, cell) in enumerate(grid_config.items(), start=1):
        if counter % 1000 == 0:
            print(f"Cell {counter}/{total_cells}")

        meta = cell["meta_data"]

        lat = meta["lat"]
        lon = meta["lon"]

        lat_min = lat - half_lat
        lat_max = lat + half_lat
        lon_min = lon - half_lon
        lon_max = lon + half_lon

        polygon = Polygon([
            (lon_min, lat_min),
            (lon_max, lat_min),
            (lon_max, lat_max),
            (lon_min, lat_max),
            (lon_min, lat_min)
        ])

        clipped = polygon.intersection(usa_geometry)

        if clipped.is_empty:
            continue

        cell["geometry"] = mapping(clipped)

        clipped_grid_config[cell_id] = cell

    grid_config = clipped_grid_config

    target_cells = list(grid_config.values())

    print("Working on calculation of neighbor cells ...")

    source_cells, neighbors_by_cell = get_sorted_neighbors(target_cells, base_grid_config)

    total_species = len(species_config)

    for species_counter, species_id in enumerate(species_config, start=1):
        print(f"Species-Count: {species_counter}/{total_species}")
        
        values = interpolate_cell_value(species_id, target_cells, source_cells, neighbors_by_cell)

        for cell, value in zip(target_cells, values):
            cell["high_count_ratios"][species_id] = float(value)

    return grid_config


def create_display_grid_config(self_weight=0.6, iterations=1, max_neighbors=8):
    
    grid_config = create_grid_config()

    cell_ids = list(grid_config.keys())
    target_cells = list(grid_config.values())

    print("Working on calculation of neighbor cells ...")
    neighbors_by_cell = get_sorted_analysis_neighbors(target_cells)

    display_grid_config = {}

    for cell_id, cell in grid_config.items():
        display_grid_config[cell_id] = {
            "meta_data": cell["meta_data"],
            "geometry": cell["geometry"],
            "display_ratios": {}
        }

    species_ids = set()

    for cell in grid_config.values():
        species_ids.update(cell["high_count_ratios"].keys())

    species_ids = sorted(species_ids)
    total_species = len(species_ids)

    for species_counter, species_id in enumerate(species_ids, start=1):
        print(f"Species-Count: {species_counter}/{total_species}")

        current_values = {}

        for cell_id, cell in grid_config.items():
            value = cell["high_count_ratios"].get(species_id)

            if value is not None:
                current_values[cell_id] = float(value)

        for _ in range(iterations):
            smoothed_values = {}

            for target_index, cell_id in enumerate(cell_ids):
                if cell_id not in current_values:
                    continue

                own_value = current_values[cell_id]
                sorted_indices = neighbors_by_cell[target_index]

                neighbor_values = []

                for neighbor_index in sorted_indices:
                    if neighbor_index == target_index:
                        continue

                    neighbor_id = cell_ids[neighbor_index]
                    neighbor_value = current_values.get(neighbor_id)

                    if neighbor_value is not None:
                        neighbor_values.append(neighbor_value)

                    if len(neighbor_values) >= max_neighbors:
                        break

                if not neighbor_values:
                    smoothed_values[cell_id] = own_value
                    continue

                neighbor_mean = sum(neighbor_values) / len(neighbor_values)

                display_value = self_weight * own_value + (1 - self_weight) * neighbor_mean
                display_value = max(0.0, min(1.0, display_value))

                smoothed_values[cell_id] = display_value

            current_values = smoothed_values

        for cell_id, value in current_values.items():
            display_grid_config[cell_id]["display_ratios"][species_id] = float(value)

    return display_grid_config


def create_species_grids():
    with open(SPECIES_CONFIG_PATH, "r") as file:
        species_config = json.load(file)

    display_grid_config = create_display_grid_config()

    base_grid = {}

    cell_count = len(display_grid_config)

    for counter, (cell, cell_dict) in enumerate(display_grid_config.items(), start=1):
        if counter % 100 == 0:
            print(f"{counter}/{cell_count} cells done")

        base_grid[cell] = cell_dict["geometry"]

    with zipfile.ZipFile(
        SPECIES_GRIDS_ZIP_PATH,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:

        zip_file.writestr(
            "base_grid.json",
            json.dumps(base_grid, ensure_ascii=False, indent=4)
        )

        species_ids = list(species_config.keys())

        for species_id in species_ids:
            features = []

            print(f"Working on ID {species_id}")

            for cell_id, cell in display_grid_config.items():
                value = cell["display_ratios"].get(species_id)

                if value is None:
                    continue

                features.append({
                    "type": "Feature",
                    "id": cell_id,
                    "properties": {
                        "value": float(value)
                    }
                })

            geojson = {
                "type": "FeatureCollection",
                "features": features
            }

            zip_file.writestr(
                f"{species_id}_grid.json",
                json.dumps(geojson, ensure_ascii=False, indent=4)
            )


if __name__ == "__main__":
    create_species_grids()