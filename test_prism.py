import io
import zipfile

import requests
import rasterio


LATITUDE = 33.31265397
LONGITUDE = -91.89068613

YEAR = 1967
MONTH = 1

URL = (
    f"https://services.nacse.org/prism/data/get/"
    f"us/800m/tmean/{YEAR}{MONTH:02d}"
)


print("Lade PRISM-Daten...")
print(URL)

response = requests.get(URL, timeout=120)
response.raise_for_status()

print(f"Downloadgröße: {len(response.content) / 1024**2:.1f} MB")


# PRISM liefert standardmäßig ein ZIP-Archiv
with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
    print("\nDateien im ZIP:")
    for name in zip.namelist():
        print("  ", name)

    # GeoTIFF suchen
    tif_files = [
        name
        for name in zip.namelist()
        if name.lower().endswith(".tif")
    ]

    if not tif_files:
        raise RuntimeError("Kein GeoTIFF im PRISM-Archiv gefunden.")

    tif_name = tif_files[0]

    print(f"\nVerwende Raster: {tif_name}")

    # GeoTIFF direkt aus dem ZIP öffnen
    with zip.open(tif_name) as tif_file:
        raster_bytes = tif_file.read()

    with rasterio.MemoryFile(raster_bytes) as memfile:
        with memfile.open() as raster:

            print("\n--- Rasterinformationen ---")
            print("CRS:", raster.crs)
            print("Breite:", raster.width)
            print("Höhe:", raster.height)
            print("Anzahl Bänder:", raster.count)
            print("Auflösung:", raster.res)
            print("Bounds:", raster.bounds)
            print("NoData:", raster.nodata)

            # Koordinate → Rasterzelle
            row, col = raster.index(LONGITUDE, LATITUDE)

            print("\n--- Testpunkt ---")
            print("Latitude:", LATITUDE)
            print("Longitude:", LONGITUDE)

            print("\n--- Rasterzelle ---")
            print("Zeile:", row)
            print("Spalte:", col)

            # Wert dieser Rasterzelle auslesen
            value = raster.read(1)[row, col]

            print("\n--- PRISM-Wert ---")
            print("tmean:", value)