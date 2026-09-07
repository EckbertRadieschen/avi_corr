import os
from dotenv import load_dotenv

import time
import tempfile
import xarray as xr
import pandas as pd

import cdsapi
import mysql.connector


# ============================================================
# API/MYSQL - KONFIGURATION
# ============================================================

load_dotenv()

CDS_API_URL = os.getenv("CDS_API_URL")
CDS_API_KEY = os.getenv("CDS_API_KEY")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_BATCH_SIZE = 100_000

# ============================================================
# SEKTOR - KONFIGURATION
# ============================================================

SECTOR_ROWS = 6
SECTOR_COLUMNS = 10
FAILED_SECTORS_FILE = "failed_sectors.txt"
SECTORS_TO_PROCESS = None


# ============================================================
# REQUEST - KONFIGURATION
# ============================================================

START_YEAR = 1966
END_YEAR = 2025

YEARS = [
    str(year)
    for year in range(START_YEAR, END_YEAR + 1)
]
MONTHS = [
    str(month).zfill(2)
    for month in range(1, 13)
]

VARIABLES = {
    "temperature": {
        "request_key": "2m_temperature",
        "dataset_key": "t2m",
        "output_column": "temperature",
    },

    "dewpoint_temperature": {
        "request_key": "2m_dewpoint_temperature",
        "dataset_key": "d2m",
        "output_column": "dewpoint_temperature",
    },

    "precipitation": {
        "request_key": "total_precipitation",
        "dataset_key": "tp",
        "output_column": "precipitation",
    },

    "snowfall": {
        "request_key": "snowfall",
        "dataset_key": "sf",
        "output_column": "snowfall",
    },

    "wind_u": {
        "request_key": "10m_u_component_of_wind",
        "dataset_key": "u10",
        "output_column": "wind_u",
    },

    "wind_v": {
        "request_key": "10m_v_component_of_wind",
        "dataset_key": "v10",
        "output_column": "wind_v",
    },

    "soil_moisture": {
        "request_key": "volumetric_soil_water_layer_1",
        "dataset_key": "swvl1",
        "output_column": "soil_moisture",
    },

    "solar_radiation": {
        "request_key": "surface_net_solar_radiation",
        "dataset_key": "ssr",
        "output_column": "solar_radiation",
    },
}


# ============================================================
# MYSQL
# ============================================================

def get_mysql_connection():
    """
    Erstellt eine Verbindung zur MySQL-Datenbank.
    """

    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

def get_stops():
    """Lädt alle Stops aus analysis_stops."""

    connection = get_mysql_connection()

    query = """
        SELECT
            stop_id,
            route_id,
            latitude,
            longitude
        FROM analysis_stops
        ORDER BY route_id
    """

    try:
        return pd.read_sql(query, connection)
    finally:
        connection.close()


# ============================================================
# FEHLERHAFTE SEKTOREN
# ============================================================

def save_failed_sectors(failed_sectors):
    """Speichert die IDs der fehlgeschlagenen Sektoren."""

    with open(FAILED_SECTORS_FILE, "w", encoding="utf-8") as file:
        for sector_id in sorted(failed_sectors):
            file.write(f"{sector_id}\n")


def load_failed_sectors():
    """Liest fehlgeschlagene Sektoren aus der Datei."""

    if not os.path.exists(FAILED_SECTORS_FILE):
        return []

    failed_sectors = []

    with open(FAILED_SECTORS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            failed_sectors.append(int(line))

    return failed_sectors


# ============================================================
# ERA5 AREA
# ============================================================

def create_sectors(stops_df, rows=SECTOR_ROWS, columns=SECTOR_COLUMNS):
    """
    Teilt die gesamte räumliche Ausdehnung der Stops
    in ein regelmäßiges Raster auf.
    """

    lat_min = stops_df["latitude"].min()
    lat_max = stops_df["latitude"].max()
    lon_min = stops_df["longitude"].min()
    lon_max = stops_df["longitude"].max()

    lat_edges = pd.Series(
        [
            lat_min + i * (lat_max - lat_min) / rows
            for i in range(rows + 1)
        ]
    )

    lon_edges = pd.Series(
        [
            lon_min + i * (lon_max - lon_min) / columns
            for i in range(columns + 1)
        ]
    )

    sectors = []
    sector_id = 1

    for row in range(rows):
        for column in range(columns):
            sectors.append(
                {
                    "sector_id": sector_id,
                    "lat_min": lat_edges.iloc[row],
                    "lat_max": lat_edges.iloc[row + 1],
                    "lon_min": lon_edges.iloc[column],
                    "lon_max": lon_edges.iloc[column + 1]
                }
            )
            sector_id += 1

    return pd.DataFrame(sectors)


def assign_stops_to_sectors(stops_df, sectors, rows=SECTOR_ROWS, columns=SECTOR_COLUMNS):
    """Ordnet jedem Stop einen Sektor zu."""

    lat_min = sectors["lat_min"].min()
    lat_max = sectors["lat_max"].max()
    lon_min = sectors["lon_min"].min()
    lon_max = sectors["lon_max"].max()

    lat_edges = [
        lat_min + i * (lat_max - lat_min) / rows
        for i in range(rows + 1)
    ]

    lon_edges = [
        lon_min + i * (lon_max - lon_min) / columns
        for i in range(columns + 1)
    ]

    df = stops_df.copy()

    df["sector_row"] = pd.cut(
        df["latitude"],
        bins=lat_edges,
        labels=False,
        include_lowest=True
    )

    df["sector_column"] = pd.cut(
        df["longitude"],
        bins=lon_edges,
        labels=False,
        include_lowest=True
    )

    df["sector_id"] = df["sector_row"] * columns + df["sector_column"] + 1

    return df


def get_combined_area(sectors, sector_ids):
    selected_sectors = [
        sectors[sector_id]
        for sector_id in sector_ids
    ]

    return [
        max(sector["lat_max"] for sector in selected_sectors),
        min(sector["lon_min"] for sector in selected_sectors),
        min(sector["lat_min"] for sector in selected_sectors),
        max(sector["lon_max"] for sector in selected_sectors),
    ]


def download_sector_data(client, sector_id, area):
    """Lädt die ERA5-Daten einer Route."""

    filename = os.path.join(tempfile.gettempdir(), f"era5_route_{sector_id}.nc")

    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": [
            variable["request_key"]
            for variable in VARIABLES.values()
        ],
        "year": YEARS,
        "month": MONTHS,
        "time": "00:00",
        "area": area,
        "data_format": "netcdf",
        "download_format": "unarchived"
    }

    client.retrieve("reanalysis-era5-land-monthly-means", request, filename)

    return filename


def extract_sector_data(nc_file, sector_stops) -> pd.DataFrame:
    """Extrahiert für alle Stops eines Sektors die nächstgelegenen ERA5-Gitterwerte."""

    ds = xr.open_dataset(nc_file)

    try:
        era5_lat = sector_stops["latitude"].round(1)
        era5_lon = sector_stops["longitude"].round(1)
        stop_ids = sector_stops["stop_id"].values

        stop_lats = xr.DataArray(
            era5_lat.values,
            dims="stop",
            coords={
                "stop": stop_ids
            }
        )

        stop_lons = xr.DataArray(
            era5_lon.values,
            dims="stop",
            coords={
                "stop": stop_ids
            }
        )

        ds_stops = ds.sel(latitude=stop_lats, longitude=stop_lons, method="nearest")

        dataset_keys = [
            variable["dataset_key"]
            for variable in VARIABLES.values()
        ]

        ds_stops = ds_stops[dataset_keys]

        # ==================================================================
        # Erzeugen der DataFrame Struktur
        # ==================================================================

        result_df = ds_stops.to_dataframe().reset_index()

        result_df = result_df.rename(
            columns={
                variable["dataset_key"]:
                    variable["output_column"]
                for variable in VARIABLES.values()
            }
        )

        result_df["stop_id"] = result_df["stop"].astype(int)

        result_df = result_df.drop(columns=["stop", "latitude", "longitude"], errors="ignore")
     
        result_df["valid_time"] = pd.to_datetime(result_df["valid_time"])
        result_df["year"] = result_df["valid_time"].dt.year
        result_df["month"] = result_df["valid_time"].dt.month
        result_df = result_df.drop(columns=["valid_time"])

        result_df = result_df[
            [
                "stop_id",
                "year",
                "month",
                "temperature",
                "dewpoint_temperature",
                "precipitation",
                "snowfall",
                "wind_u",
                "wind_v",
                "soil_moisture",
                "solar_radiation",
            ]
        ]

        return result_df

    finally:
        ds.close()


# ============================================================
# MYSQL INSERT
# ============================================================

def insert_sector_data(data_df):
    connection = get_mysql_connection()
    cursor = connection.cursor()

    columns = [
        "stop_id",
        "year",
        "month",
        "temperature",
        "dewpoint_temperature",
        "precipitation",
        "snowfall",
        "wind_u",
        "wind_v",
        "soil_moisture",
        "solar_radiation"
    ]

    placeholders = ["%s"] * len(columns)

    query = f"""
        INSERT INTO era5_monthly_data 
        VALUES ({", ".join(placeholders)})
    """

    try:
        data = list(data_df[columns].itertuples(index=False, name=None))

        total_rows = len(data)

        for start in range(0, total_rows, MYSQL_BATCH_SIZE):
            end = min(start + MYSQL_BATCH_SIZE, total_rows)

            batch = data[start:end]

            print(f"MySQL Batch {start:,}–{end:,} von {total_rows:,}")
            
            cursor.executemany(query, batch)

            connection.commit()

        print(f"{total_rows:,} Datensätze exportiert")

    finally:
        cursor.close()
        connection.close()


def process_combined_sectors(client, sector_ids, sector_stops, sectors):
    nc_file = None

    try:
        print(f"Sektoren: {sector_ids}")
        print(f"Stops: {len(sector_stops):,}")

        area = get_combined_area(sectors, sector_ids)
        nc_file = download_sector_data(client, "combined", area)
        data = extract_sector_data(nc_file, sector_stops)
        insert_sector_data(data)

    finally:
        if nc_file and os.path.exists(nc_file):
            os.remove(nc_file)


def process_sector(client, sector_id, sector_stops, sector):
    """Lädt und verarbeitet einen einzelnen Sektor."""

    nc_file = None

    try:
        area = [sector["lat_max"], sector["lon_min"], sector["lat_min"], sector["lon_max"]]

        print(f"Stops: {len(sector_stops):,}")
        print(f"Area: {area}")

        nc_file = download_sector_data(client, sector_id, area)
        sector_data = extract_sector_data(nc_file, sector_stops)
        insert_sector_data(sector_data)

        print("Sektor erfolgreich verarbeitet")

    finally:
        if nc_file and os.path.exists(nc_file):
            os.remove(nc_file)


# ============================================================
# HAUPTPROGRAMM
# ============================================================

def get_era5_data(bunch=False):
    """
    Durchführung des Datenimports aus dem Climate Data Store
    
    bunch=True: sendet eine gebündelte Sektoren-Request an den Server.
    Empfehlenswert bei langen Request-Queues serverseitig.
    """

    client = cdsapi.Client(url=CDS_API_URL, key=CDS_API_KEY)   

    print("=" * 60)
    print("ERA5-LAND IMPORT")
    print("=" * 60)

    stops_df = get_stops()
    sectors_df = create_sectors(stops_df)
    stops_df = assign_stops_to_sectors(stops_df, sectors_df)
    sector_groups = stops_df.groupby("sector_id")
    active_sector_ids = set(sector_groups.groups.keys())

    if SECTORS_TO_PROCESS is None:
        failed_sectors = load_failed_sectors()

        if len(failed_sectors) == 0:
            sectors_to_process = active_sector_ids

        else:
            sectors_to_process = [
                sector_id
                for sector_id in failed_sectors
                if sector_id in active_sector_ids
            ]
       
    else:
        sectors_to_process = [
            sector_id
            for sector_id in SECTORS_TO_PROCESS
            if sector_id in active_sector_ids
        ]


    if bunch == True:
        sectors = sectors_df.set_index("sector_id").to_dict("index")

        if not sectors_to_process:
            raise ValueError("Keiner der konfigurierten Sektoren enthält Stops")

        sector_ids = sectors_to_process

        combined_stops = stops_df[stops_df["sector_id"].isin(sector_ids)].copy()

        process_combined_sectors(client, sector_ids, combined_stops, sectors)   

    else:
        loop_start = time.perf_counter()
        sector_durations = []

        successful_sectors = []
        failed_sectors = []

        total_sectors = len(sectors_to_process)

        for sector_number, sector_id in enumerate(sorted(sectors_to_process), start=1):
            sector_start = time.perf_counter()

            print("-" * 60)
            print(f"[{sector_number}/{total_sectors}]: Sektor {sector_id}")

            try:
                sector_stops = sector_groups.get_group(sector_id)

                sector_filter = sectors_df["sector_id"] == sector_id
                sector = sectors_df[sector_filter].iloc[0]
                
                process_sector(client, sector_id, sector_stops, sector)
                successful_sectors.append(sector_id)

            except Exception as error:
                print("\n!!! FEHLER bei Sektor {sector_id}:")
                print(f"{type(error).__name__}: {error}")

                failed_sectors.append(sector_id)

            finally:
                sector_duration = time.perf_counter() - sector_start
                sector_durations.append(sector_duration)
                elapsed_time = time.perf_counter() - loop_start
                average_duration = sum(sector_durations) / len(sector_durations)
                remaining_sectors = total_sectors - sector_number
                estimated_remaining = remaining_sectors * average_duration
        
                print(f"\nSektordauer: {sector_duration / 60:.2f} min")
                print(f"Gesamtlaufzeit: {elapsed_time / 60:.2f} min")
                print(f"Durchschnitt/Sektor: {average_duration / 60:.2f} min")
                print(f"Verbleibende Sektoren: {remaining_sectors}")
                print(f"Geschätzte Restlaufzeit: {estimated_remaining / 60:.2f} min")

        save_failed_sectors(failed_sectors)

        print()
        print("=" * 60)
        print("IMPORT ABGESCHLOSSEN")
        print("=" * 60)
        print(f"Erfolgreiche Sektoren: {len(successful_sectors):,}")
        print(f"Fehlerhafte Sektoren: {len(failed_sectors):,}")

        if failed_sectors:
            print("\nFehlerhafte Sektor-IDs:")

            for sector_id in sorted(failed_sectors):
                print(f"{sector_id}")

            print(f"Die Fehlerliste wurde in '{FAILED_SECTORS_FILE}' gespeichert")

        else:
            if os.path.exists(FAILED_SECTORS_FILE):
                os.remove(FAILED_SECTORS_FILE)

            print("\nKeine Fehler.")

# =======================================================================================
# =======================================================================================

if __name__ == "__main__":
    get_era5_data(bunch=True)