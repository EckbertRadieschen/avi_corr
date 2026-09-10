USE bbs_analysis;

-- =============================================
-- NLCD_YEAR_DATA
-- =============================================

SELECT COUNT(*) 
FROM nlcd_year_data;

SELECT COUNT(*)
FROM analysis_stops;

-- Importiert wurden für jeden der 25.535 Stopps Daten für 41 Jahre
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
