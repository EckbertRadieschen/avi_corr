USE bbs_analysis;

-- =============================================
-- NLCD_YEAR_DATA
-- =============================================

SELECT COUNT(*) 
FROM nlcd_year_data;

SELECT COUNT(*)
FROM analysis_stops;

-- Importiert wurde für jeden der 25.535 Stopps Daten für 41 Jahre
-- nlcd_year_data ist also mit 1.046.935 Einträgen vollständig importiert worden.

SELECT 
	COUNT(water) AS water_count,
    COUNT(snow_ice) AS snow_count,
    COUNT(developed) AS urban_count,
    COUNT(barren) AS barren_count,
    COUNT(forest) AS forest_count,
    COUNT(shrubland) AS shrubland_count,
    COUNT(grassland) AS grassland_count,
    COUNT(pasture) AS pasture_count,
    COUNT(cropland) AS cropland_count,
    COUNT(wetland) AS wetland_count
FROM nlcd_year_data;

-- Keine Null-Values

SELECT
	(water + snow_ice + developed + barren + forest 
    + shrubland + grassland + pasture + cropland + wetland) AS area_total,
	COUNT(stop_id) AS count
FROM nlcd_year_data
GROUP BY area_total
ORDER BY count;

-- Alle räumlichen Anteile ergänzen sich sauber zu 100%

SELECT 
	AVG(water) AS avg_water,
    AVG(developed) AS avg_developed,
    AVG(barren) AS avg_barren,
    AVG(forest) AS avg_forest,
    AVG(shrubland) AS avg_shrubland,
    AVG(grassland) AS avg_grassland,
    AVG(pasture) AS avg_pasture,
    AVG(cropland) AS avg_cropland,
    AVG(wetland) AS avg_wetland
FROM nlcd_year_data;

-- Verteilung ist schlüssig


-- =============================================
-- NLCD_ROUTE_ANALYSIS
-- =============================================

SELECT COUNT(*)
FROM analysis_routes;

SELECT COUNT(*)
FROM nlcd_route_analysis;

-- Vorhanden sind 568 Analyse-Routen und NLCD Daten über 41 Jahre.
-- nlcd_route_analysis ist mit 23.288 Einträgen vollständig.


-- =============================================
-- ERA5_MONTHLY_DATA
-- =============================================

SELECT 
	COUNT(*)
FROM analysis_stops;

SELECT
	COUNT(*) 
FROM era5_monthly_data;

-- 25.535 Stopps in analysis_stops x 60 Jahre x 12 Monate
-- 18.385.200 Einträge in era5_monthly_data
-- era5_monthly_data ist vollständig
    
SELECT
	COUNT(temperature) AS temperature_count,
    COUNT(dewpoint_temperature) AS dewpoint_temperature_count,
    COUNT(precipitation) AS precipitation_count,
    COUNT(snowfall) AS snowfall_count,
    COUNT(wind_u) AS wind_u_count,
    COUNT(wind_v) AS wind_v_count,
    COUNT(soil_moisture) AS soil_moisture_count,
    COUNT(solar_radiation) AS solar_radiation_count
FROM era5_monthly_data;

-- keine Null-Values
-- Restliche Qualitäts-Analyse auf era5_route_monthly
-- dort gefundene Qualitätsprobleme haben ihre Ursache zwingend in era5_monthly_data

-- =============================================
-- ERA5_ROUTE_MONTHLY
-- =============================================

-- Generelle Plausibilität 
SELECT 
	MIN(temperature) AS min_temperature,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    
    MIN(dewpoint_temperature) AS min_dewpoint_temperature,
    AVG(dewpoint_temperature) AS avg_dewpoint_temperature,
    MAX(dewpoint_temperature) AS max_dewpoint_temperature,
    
    MIN(daily_precipitation) AS min_daily_precipitation,
    AVG(daily_precipitation) AS avg_daily_precipitation,
    MAX(daily_precipitation) AS max_daily_precipitation,
    
    MIN(daily_snowfall) AS min_daily_snowfall,
    AVG(daily_snowfall) AS avg_daily_snowfall,
    MAX(daily_snowfall) AS max_daily_snowfall,
    
    MIN(wind_magnitude) AS min_wind_magnitude,
    AVG(wind_magnitude) AS avg_wind_magnitude,
    MAX(wind_magnitude) AS max_wind_magnitude,

    MIN(soil_moisture) AS min_soil_moisture,
    AVG(soil_moisture) AS avg_soil_moisture,
    MAX(soil_moisture) AS max_soil_moisture,
    
    MIN(solar_flux_density) AS min_solar_flux_density,
    AVG(solar_flux_density) AS avg_solar_flux_density,
    MAX(solar_flux_density) AS max_solar_flux_density
FROM era5_route_monthly;

-- Alle Werte liegen in einem plausiblen Bereich
-- Keine absurden Ausreißer oder unrealistische Werte


-- Routenebene
SELECT 
	route_id,
    AVG(temperature) AS avg_temperature,
    AVG(dewpoint_temperature) AS avg_dewpoint_temperature,
    AVG(daily_precipitation) AS avg_daily_precipitation_mm,
    AVG(daily_snowfall) AS avg_daily_snowfall_mm,
    AVG(wind_magnitude) AS wind_magnitude,
    AVG(soil_moisture) AS avg_soil_moisture,
    AVG(solar_flux_density) AS avg_solar_flux_density
FROM era5_route_monthly
GROUP BY route_id;

/* Schwankungen
Temperature: 				0.9-18.5 °C
Dewpoint-Temperature: 		-6.5-12.4 °C
Precipitation:				0.99-3.62 mm/day
Snowfall:					0.01-1.48 mm/day 
Wind-Magnitude:				1.7-10.3 m/s
Soil-Moisture:				0.11-0.44 m³/m³
Solar-Flux-Density:			115-173 W/m²

Wie erwartet gibt es in allen Bereichen extreme Routen,
aber alle Durchschnittswerte bewegen sich in einem realistischen Bereich
Ausreißer in Temperatur und Taupunkt-Temperatur nach unten in Route 92041
*/

SELECT
    `month`,
    AVG(temperature) AS avg_temperature,
    AVG(dewpoint_temperature) AS avg_dewpoint
FROM era5_route_monthly
WHERE route_id = 92041
GROUP BY `month`
ORDER BY `month`;

-- Route liegt in Wyoming ziemlich hochgelegen. 
-- Ist oben als Ausreißer nach unten aufgefallen,
-- erscheint aber insgesamt plausibel


-- Routenebene
SELECT 
	`year`,
    AVG(temperature) AS avg_temperature,
    AVG(dewpoint_temperature) AS avg_dewpoint_temperature,
    AVG(daily_precipitation) AS avg_daily_precipitation_mm,
    AVG(daily_snowfall) AS avg_daily_snowfall_mm,
    AVG(wind_magnitude) AS avg_wind_magnitude,
    AVG(soil_moisture) AS avg_soil_moisture,
    AVG(solar_flux_density) AS avg_solar_flux_density
FROM era5_route_monthly
GROUP BY `year`;


/* Schwankungen
Temperature: 				8.7-12.3 °C
Dewpoint-Temperature: 		1.8-5.0 °C
Precipitation:				1.67-2.89 mm/day
Snowfall:					0.17-0.42 mm/day 
Wind-Magnitude:				3.3-4.6 m/s
Soil-Moisture:				0.27-0.34 m³/m³
Solar-Flux-Density:			122-155 W/m²

- 2022/23 liefern unrealistisch niedrige Werte in solar_flux_density, sowie daily_precipitation
- Entscheidung: Ausschluss der beiden Jahre aus der Analyse. 
- Alle weiteren Jahre verhalten sich unauffällig.
- In den Schwankungen oben sind die Ausreißer ausgenommen.
*/

SELECT 
	`month`,
    AVG(temperature) AS avg_temperature,
    AVG(dewpoint_temperature) AS avg_dewpoint_temperature,
    AVG(daily_precipitation) AS avg_daily_precipitation_mm,
    AVG(daily_snowfall) AS avg_daily_snowfall_mm,
    AVG(wind_magnitude) AS avg_wind_magnitude,
    AVG(soil_moisture) AS avg_soil_moisture,
    AVG(solar_flux_density) AS avg_solar_flux_density
FROM era5_route_monthly
WHERE `year` NOT IN (2022, 2023)
GROUP BY `month`;

-- Jahresverlauf wie erwartet, ohne große Auffälligkeiten
-- Auffällig ist das raue Klima im Projektgebiet


-- Räumliche Plausibilität


WITH 
	route_lat_min_max AS (
		SELECT 
			ar.route_id,
            MIN(r.latitude) OVER() AS min_latitude,
            MAX(r.latitude) OVER() AS max_latitude 
		FROM routes r
        JOIN analysis_routes AS ar
			ON r.state_num * 1000 + r.route = ar.route_id
	),
    route_lat AS (
		SELECT
			r.state_num * 1000 + r.route AS route_id,
            CASE 
				WHEN r.latitude < mm.min_latitude + (mm.max_latitude - mm.min_latitude) * 1/7
					THEN '1_far_south'
				WHEN r.latitude < mm.min_latitude + (mm.max_latitude - mm.min_latitude) * 2/7
					THEN '2_south'
				WHEN r.latitude < mm.min_latitude + (mm.max_latitude - mm.min_latitude) * 3/7
					THEN '3_south_central'
				WHEN r.latitude < mm.min_latitude + (mm.max_latitude - mm.min_latitude) * 4/7
					THEN '4_central'
				WHEN r.latitude < mm.min_latitude + (mm.max_latitude - mm.min_latitude) * 5/7
					THEN '5_north_central'
				WHEN r.latitude < mm.min_latitude + (mm.max_latitude - mm.min_latitude) * 6/7
					THEN '6_north'
				ELSE 
					'7_far_north'
			END AS latitude_bin
        FROM routes AS r
        JOIN route_lat_min_max AS mm
			ON r.state_num * 1000 + r.route = mm.route_id
    )
SELECT
    l.latitude_bin,
    e.`month`,
    COUNT(*) AS route_count,
    ROUND(AVG(e.temperature), 2)         	AS mean_temperature,
    ROUND(AVG(e.relative_humidity), 2)   	AS mean_relative_humidity,
    ROUND(AVG(e.daily_precipitation), 3)  AS mean_daily_precipitation,
    ROUND(AVG(e.daily_snowfall), 3)       AS mean_daily_snowfall,
    ROUND(AVG(e.soil_moisture), 4)       	AS mean_soil_moisture,
    ROUND(AVG(e.solar_flux_density), 2)   AS mean_solar_flux_density,
    ROUND(AVG(e.wind_magnitude), 2)      	AS mean_wind_magnitude
FROM era5_route_monthly AS e
JOIN route_lat AS l
	ON e.route_id = l.route_id
WHERE e.`year` NOT IN (2022, 2023) AND e.`month` IN (1, 7)
GROUP BY l.latitude_bin, e.`month`
ORDER BY e.`month`, l.latitude_bin;

-- ========================================
-- Modellkontrolle Vegetationskoeffizient

SELECT
    COUNT(*) AS n,
    ROUND(MIN(vegetation_coefficient), 6) AS min_vc,
    ROUND(MAX(vegetation_coefficient), 6) AS max_vc,
    ROUND(AVG(vegetation_coefficient), 6) AS mean_vc,
    ROUND(STDDEV_SAMP(vegetation_coefficient), 6) AS std_vc
FROM era5_route_monthly
WHERE vegetation_coefficient IS NOT NULL;

SELECT
    CASE
        WHEN vegetation_coefficient = 0 THEN '0'
        WHEN vegetation_coefficient < 0.1 THEN '0.00–0.09'
        WHEN vegetation_coefficient < 0.2 THEN '0.10–0.19'
        WHEN vegetation_coefficient < 0.3 THEN '0.20–0.29'
        WHEN vegetation_coefficient < 0.4 THEN '0.30–0.39'
        WHEN vegetation_coefficient < 0.5 THEN '0.40–0.49'
        WHEN vegetation_coefficient < 0.6 THEN '0.50–0.59'
        WHEN vegetation_coefficient < 0.7 THEN '0.60–0.69'
        WHEN vegetation_coefficient < 0.8 THEN '0.70–0.79'
        WHEN vegetation_coefficient < 0.9 THEN '0.80–0.89'
        ELSE '0.90–1.00'
    END AS vc_class,
    COUNT(*) AS n,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS anteil_prozent
FROM era5_route_monthly
WHERE vegetation_coefficient IS NOT NULL
GROUP BY vc_class
ORDER BY vc_class;


-- =============================================
-- BBS_SPECIES_LIST
-- =============================================

/*
BBS listet beobachtete Vögel AOU-konform
seit 1998 vergibt die AOU keine neuen Nummern mehr, 
sodass BBS zwecks Konsistenz die Nummerierung eigenständig weiterführt
*/

SELECT 
	COUNT(DISTINCT species_id),
    COUNT(DISTINCT route_id)
FROM analysis_observations;

SELECT DISTINCT
	sl.common_name
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON ao.species_id = sl.aou
WHERE 
	(NOT sl.common_name LIKE '%unid.%')
    AND (sl.common_name LIKE '%(%')
ORDER BY sl.common_name;

SELECT DISTINCT
	sl.common_name
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON ao.species_id = sl.aou
ORDER BY sl.common_name;

-- Einige unidentifizierte Arten oder Hybride oder Zusatzinformationen (13)


SELECT DISTINCT
	species
FROM bbs_species_list
ORDER BY species;

/* Es wird nach mehreren Kritierien unterschieden
- Vollständig bestimmbare Art
- Hybride
- Unidentiziert, aber ungefähr einzuordnen
*/

SELECT DISTINCT
	genus
FROM bbs_species_list
ORDER BY genus;

-- Auch einzelne Geni sind nicht eindeutig zugeordnet

SELECT 
	common_name,
	species_name
FROM bbs_species_list
ORDER BY species_name;

-- Kleinere Änderungen nötig, die nicht der gängigen Nomenklatur entsprechen
-- Diese werden später in Abstimmung mit den eBird-Daten vorgenommen


-- ======================================================================
-- Reduziert auf die Analyse-relevanten Arten:

SELECT DISTINCT
	sl.common_name,
	sl.species_name,
    sl.scientific_name
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON sl.aou = ao.species_id
WHERE sl.scientific_name IS NOT NULL
ORDER BY sl.scientific_name, sl.species_name;

SELECT
    COUNT(DISTINCT sl.scientific_name)
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON sl.aou = ao.species_id;

-- 384 Einträge mit einem wissenschaftlichen Namen
-- Es existieren 374 eindeutige wissenschaftliche Namen
-- Diese bilden die Grundlage für die finale Auswertung



/*
Überprüfung Vorhandensein aller BBS-Arten in ebird_species_info
Später Import der einheitlichen Species_ID
*/

SELECT DISTINCT
	eb.species_code,
    sl.scientific_name
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON sl.aou = ao.species_id
LEFT JOIN ebird_species_info AS eb
	ON sl.scientific_name = eb.scientific_name
ORDER BY eb.species_code, sl.scientific_name;

/*
Fehlende Verknüpfung für:

Accipiter atricapillus
Accipiter cooperii
Bubulcus ibis
Carduelis carduelis
Larus argentatus
Porphyrio martinicus
Troglodytes aedon
*/

-- =====================================================
-- ebird_species_info
-- =====================================================

SELECT 
	* 
    FROM bbs_species_list
    WHERE 
		scientific_name IN (
			'Accipiter atricapillus',
			'Accipiter cooperii',
			'Bubulcus ibis',
			'Carduelis carduelis',
			'Larus argentatus',
			'Troglodytes aedon',
            'Porphyrio martinicus'
		);

SELECT 
	* 
    FROM ebird_species_info
    WHERE 
		common_name LIKE '%Herring Gull%' 
        OR common_name LIKE "%Cooper's Hawk%"
        OR common_name LIKE '%Western Cattle-Egret%'
        OR common_name LIKE '%American Goshawk%'
        OR common_name LIKE '%Goldfinch%'
        OR common_name LIKE '%House Wren%'
        OR common_name LIKE '%Purple Gallinule%';

/*
Gefunden als:
'Herring Gull' = 'American Herring Gull' = Larus smithsonianus  
-> Änderung in BBS auf Larus smithsonianus
'Western Cattle-Egret' = Ardea ibis (categr1)
-> Änderung in BBS auf Bubulcus ibis
'Cooper's Hawk' = Astur cooperii (coohaw)
'American Goshawk' = Astur atricapillus (norgos)
-> Übernahme des aktualisierten Genus Astur in BBS
'Purple Gallinule' = Porphyrio martinica (purgal2)
-> Änderung in BBS auf Porphyrio martinica
'European Goldfinch' = Carduelis carduelis/caniceps 
-> 
	'y01288'/'y01288a', 'Carduelis carduelis'/'Carduelis caniceps', 'European Goldfinch'/'Gray-crowned Goldfinch', 
    '0', '2', '2023-04-05', '2023-07-26', '2', '2023-08-02', '2023-03-29', '0', 
    NULL, NULL, 
    '0', 
    NULL, NULL, NULL, NULL, NULL, 
    '2023', '0', 
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL

'Northern House Wren' = Troglodytes aedon/musculus
->
    'y01309'/'y01309a', 'Troglodytes aedon'/'Troglodytes musculus', 'Northern House Wren'/'Southern House Wren', 
    '0', '3', '2023-05-31', '2023-08-02', '3', '2023-11-29', '2023-02-22', 
    '3', '2023-08-09', '2023-11-22', '3', '2023-03-01', '2023-05-24', 
    NULL, NULL, NULL, 
    '2023', '0', 
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL

Anlegen einer separaten Zeile für jede der beiden Arten in eBird
*/

SET SQL_SAFE_UPDATES = 0;

UPDATE bbs_species_list
SET scientific_name = 'Larus smithsonianus'
WHERE common_name = 'Herring Gull';

UPDATE bbs_species_list
SET scientific_name = 'Bubulcus ibis'
WHERE common_name = 'Western Cattle-Egret'; 

UPDATE ebird_species_info
SET scientific_name = 'Bubulcus ibis'
WHERE species_code = 'categr1'; 

UPDATE bbs_species_list
SET scientific_name = 'Astur atricapillus'
WHERE common_name = "Cooper's Hawk"; 

UPDATE bbs_species_list
SET scientific_name = 'Astur cooperii'
WHERE common_name = 'American Goshawk'; 

UPDATE bbs_species_list
SET scientific_name = 'Porphyrio martinica'
WHERE common_name = 'Purple Gallinule'; 

-- ========================================
UPDATE ebird_species_info
SET scientific_name = 'Carduelis carduelis'
WHERE species_code = 'y01288'; 

UPDATE ebird_species_info
SET common_name = 'European Goldfinch'
WHERE species_code = 'y01288'; 

-- ==========================================
UPDATE ebird_species_info
SET scientific_name = 'Troglodytes aedon'
WHERE species_code = 'y01309'; 

UPDATE ebird_species_info
SET common_name = 'Northern House Wren'
WHERE species_code = 'y01309'; 

SET SQL_SAFE_UPDATES = 1;

INSERT INTO ebird_species_info
VALUES (
	'y01288a', 'Carduelis caniceps', 'Gray-crowned Goldfinch', 
    '0', '2', '2023-04-05', '2023-07-26', '2', '2023-08-02', '2023-03-29', '0', 
    NULL, NULL, 
    '0', 
    NULL, NULL, NULL, NULL, NULL, 
    '2023', '0', 
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
);

INSERT INTO ebird_species_info
VALUES (
	'y01309a', 'Troglodytes musculus', 'Southern House Wren', 
    '0', '3', '2023-05-31', '2023-08-02', '3', '2023-11-29', '2023-02-22', 
    '3', '2023-08-09', '2023-11-22', '3', '2023-03-01', '2023-05-24', 
    NULL, NULL, NULL, 
    '2023', '0', 
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
);

-- Finaler Check

SELECT DISTINCT
	eb.species_code,
    sl.scientific_name
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON sl.aou = ao.species_id
LEFT JOIN ebird_species_info AS eb
	ON sl.scientific_name = eb.scientific_name
ORDER BY eb.species_code, sl.scientific_name;


SELECT
	COUNT(DISTINCT sl.aou) AS species_with_breeding_start
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON sl.aou = ao.species_id
JOIN ebird_species_info AS eb
	ON sl.aou = eb.aou
WHERE (eb.breeding_start IS NOT NULL) AND (eb.breeding_end IS NOT NULL);

-- Für 309 Analyse-relevante Vogelarten sind Informationen in breeding_start und breeding_end verfügbar
-- Die restlichen 67 Arten gehen nicht in die Brutzeitraum-Analysen ein 
-- Diese erhalten später einen Marker, der diese fehlende Information kennzeichnet


SELECT 
	species_code
FROM ebird_species_info AS eb
WHERE LENGTH(species_code) > 8;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM ebird_species_info
WHERE LENGTH(species_code) > 8;

SET SQL_SAFE_UPDATES = 1;

-- Daten enthielten einen Beispieldatensatz
-- Dadurch liefen zwei wissenschaftliche Namen unter verschiedenem species_code.
-- Der Beispieldatensatz wurde entfernt


-- =====================================================
-- latitude_day_length
-- =====================================================

SELECT * FROM latitude_day_length;

SELECT
    latitude,
    `date`,
    day_length
FROM latitude_day_length
WHERE latitude IN (-55.7, -30.0, 0.0, 30.0, 55.0, 80.0)
  AND `date` IN (
      '2023-03-21',
      '2023-06-21',
      '2023-12-21'
  )
ORDER BY latitude, `date`;

-- Nullwerte für einige Tage


SELECT
    COUNT(*) AS null_count,
    COUNT(DISTINCT latitude) AS affected_latitudes
FROM latitude_day_length
WHERE day_length IS NULL;

SELECT
    latitude,
    MIN(`date`) AS first_null_date,
    MAX(`date`) AS last_null_date,
    COUNT(*) AS null_days
FROM latitude_day_length
WHERE day_length IS NULL
GROUP BY latitude
ORDER BY latitude;



SELECT
    zone,
    ROUND(latitude, 5) AS latitude,
    ROUND(MIN(relative_day_length), 5) AS min_relative,
    ROUND(MAX(relative_day_length), 5) AS max_relative,
    COUNT(*) AS days
FROM latitude_day_length
GROUP BY zone, latitude
ORDER BY latitude;


