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


SELECT 
	MIN(temperature) AS min_temperature,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    
    MIN(precipitation) AS min_precipitation,
    AVG(precipitation) AS avg_precipitation,
    MAX(precipitation) AS max_precipitation,
    
    MIN(snowfall) AS min_snowfall,
    AVG(snowfall) AS avg_snowfall,
    MAX(snowfall) AS max_snowfall,
    
    MIN(wind_speed) AS min_wind_speed,
    AVG(wind_speed) AS avg_wind_speed,
    MAX(wind_speed) AS max_wind_speed,
    
    MIN(vpd) AS min_vpd,
    AVG(vpd) AS avg_vpd,
    MAX(vpd) AS max_vpd,
    
    MIN(soil_moisture) AS min_soil_moisture,
    AVG(soil_moisture) AS avg_soil_moisture,
    MAX(soil_moisture) AS max_soil_moisture,
    
    MIN(solar_radiation) AS min_solar_radiation,
    AVG(solar_radiation) AS avg_solar_radiation,
    MAX(solar_radiation) AS max_solar_radiation
FROM era5_route_monthly;
