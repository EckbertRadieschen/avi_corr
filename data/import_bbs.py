from pathlib import Path
from zipfile import ZipFile
import shutil
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
RAW_DIR = DATA_DIR / "raw"

STATES_ZIP = RAW_DIR / "states.zip"

MYSQL_UPLOAD_DIR = Path(
    r"C:\ProgramData\MySQL\MySQL Server 9.6\Uploads"
)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Ps50689k!!!",
    "database": "bbs_analysis"
}

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()

with ZipFile(STATES_ZIP, "r") as zip_file:

    csv_files = [
        file
        for file in zip_file.namelist()
        if file.lower().endswith(".csv")
    ]

    for file in csv_files:
        print(file)

    for number, csv_file in enumerate(csv_files, start=1):

        file_name = Path(csv_file).name

        print()
        print("=" * 60)
        print(f"[{number}/{len(csv_files)}] {file_name}")
        print("=" * 60)

        extracted_file = Path(
            zip_file.extract(csv_file, DATA_DIR / "_temp_states")
        )

        upload_file = MYSQL_UPLOAD_DIR / file_name

        shutil.copy2(
            extracted_file,
            upload_file
        )

        sql = f"""
        LOAD DATA INFILE '{upload_file.as_posix()}'
        INTO TABLE bird_observations
        CHARACTER SET utf8mb4
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS
        (
            route_data_id,
            country_num,
            state_num,
            route,
            rpid,
            year,
            aou,
            @count10,
            @count20,
            @count30,
            @count40,
            @count50,
            @stop_total,
            @species_total
        )
        SET
            count10 = NULLIF(TRIM(@count10), ''),
            count20 = NULLIF(TRIM(@count20), ''),
            count30 = NULLIF(TRIM(@count30), ''),
            count40 = NULLIF(TRIM(@count40), ''),
            count50 = NULLIF(TRIM(@count50), ''),
            stop_total = NULLIF(TRIM(@stop_total), ''),
            species_total = NULLIF(TRIM(@species_total), '');
        """

        cursor.execute(sql)
        connection.commit()

        upload_file.unlink()
        extracted_file.unlink()

temp_directory = DATA_DIR / "_temp_states"

if temp_directory.exists():
    shutil.rmtree(temp_directory)

cursor.close()
connection.close()


