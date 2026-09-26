USE bbs_analysis;

-- ===============================================================
-- ERA5_MONTHLY_DATA
-- ===============================================================

-- Bei der Aggregation auf Routenebene würden die Windrichtungen 
-- der Windkomponenten (u, v) den Mittelwert verfälschen
-- Deswegen wird auf dieser Ebene zunächst die Wind-Magnitude aus
-- beiden Komponenten errechnet, die wiederum vorzeichenfrei ist

SET SQL_SAFE_UPDATES = 0;
 
UPDATE era5_monthly_data
SET wind_magnitude = ROUND(SQRT(POWER(wind_u, 2) + POWER(wind_v, 2)), 4);

SET SQL_SAFE_UPDATES = 1;


-- ===============================================================
-- ERA5_ROUTE_MONTHLY
-- ===============================================================

-- Relative Luftfeuchtigkeit

ALTER TABLE era5_route_monthly 
	ADD COLUMN relative_humidity DECIMAL(6, 2);
    
SET SQL_SAFE_UPDATES = 0;
 
UPDATE era5_route_monthly
	SET relative_humidity = ROUND(
		100 *
		(6.112 * exp(17.62 * dewpoint_temperature / (243.12 + dewpoint_temperature)))
        /
        (6.112 * exp(17.62 * temperature / (243.12 + temperature)))
    , 2);

SET SQL_SAFE_UPDATES = 1;

-- =======================================================================================
-- Vegetationskoeffizient

ALTER TABLE era5_route_monthly 
	ADD COLUMN vegetation_coefficient DECIMAL(8, 6);
    
SET SQL_SAFE_UPDATES = 0;

WITH ranked_values AS (
    SELECT
        route_id,
        soil_moisture,
        solar_flux_density,
        relative_humidity,
        ROW_NUMBER() OVER (PARTITION BY route_id ORDER BY soil_moisture) AS sm_rank,
        ROW_NUMBER() OVER (PARTITION BY route_id ORDER BY solar_flux_density) AS sr_rank,
        ROW_NUMBER() OVER (PARTITION BY route_id ORDER BY relative_humidity) AS rh_rank,
        COUNT(*) OVER (PARTITION BY route_id) AS n
    FROM era5_route_monthly
    WHERE `year` NOT IN (2022, 2023)
),
route_quantiles AS (
    SELECT
        route_id,
        MAX(CASE WHEN sm_rank = CEIL(n * 0.05) THEN soil_moisture END) AS sm_q05,
        MAX(CASE WHEN sm_rank = CEIL(n * 0.95) THEN soil_moisture END) AS sm_q95,
        MAX(CASE WHEN sr_rank = CEIL(n * 0.05) THEN solar_flux_density END) AS sr_q05,
        MAX(CASE WHEN sr_rank = CEIL(n * 0.95) THEN solar_flux_density END) AS sr_q95,
        MAX(CASE WHEN rh_rank = CEIL(n * 0.05) THEN relative_humidity END) AS rh_q05,
        MAX(CASE WHEN rh_rank = CEIL(n * 0.95) THEN relative_humidity END) AS rh_q95
    FROM ranked_values
    GROUP BY route_id
),
normalized AS (
    SELECT
        e.route_id,
        e.`year`,
        e.`month`,
        (e.soil_moisture - q.sm_q05) / (q.sm_q95 - q.sm_q05) AS sm_norm,
        (e.solar_flux_density - q.sr_q05) / (q.sr_q95 - q.sr_q05) AS sr_norm,
        (e.relative_humidity - q.rh_q05) / (q.rh_q95 - q.rh_q05) AS rh_norm
    FROM era5_route_monthly AS e
    JOIN route_quantiles AS q
        ON e.route_id = q.route_id
    WHERE e.`year` NOT IN (2022, 2023)
),
factors AS (
    SELECT
        route_id,
        `year`,
        `month`,
		1 / (1 + EXP(-40 / 11 * LOG(6) * sm_norm + 2 * ln(3))) AS sm_factor,
		1 / (1 + EXP(-40 / 11 * LOG(6) * sr_norm + 2 * ln(3))) AS sr_factor,
		1 / (1 + EXP(-10 / 3 * LOG(6) * rh_norm + 2 * ln(3))) AS rh_factor
    FROM normalized
)
UPDATE era5_route_monthly AS e
	JOIN factors AS f
		ON e.route_id = f.route_id
		AND e.`year` = f.`year`
		AND e.`month` = f.`month`
	SET e.vegetation_coefficient = ROUND(POW(f.sm_factor * f.sr_factor * f.rh_factor, 1/3), 6);

SET SQL_SAFE_UPDATES = 1;


-- total_precipitation
-- total_snowfall

ALTER TABLE era5_route_monthly
ADD COLUMN total_precipitation DECIMAL(11, 4);

ALTER TABLE era5_route_monthly
ADD COLUMN total_snowfall DECIMAL(11, 4);

SET SQL_SAFE_UPDATES = 0;

UPDATE era5_route_monthly
SET total_precipitation = 
	ROUND(daily_precipitation * DAY(LAST_DAY(CONCAT(`year`, '-', `month`, '-01'))), 4);

UPDATE era5_route_monthly
SET total_snowfall = 
	ROUND(daily_snowfall * DAY(LAST_DAY(CONCAT(`year`, '-', `month`, '-01'))), 4);
    
SET SQL_SAFE_UPDATES = 1;


-- ===============================================================
-- BBS_SPECIES_LIST
-- ===============================================================

SET SQL_SAFE_UPDATES = 0;

UPDATE bbs_species_list
	SET species_name = CONCAT(genus, ' ', species)
    WHERE 
		(NOT genus LIKE '%/%')
        AND (NOT species REGEXP '(^|[[:space:]])x([[:space:]]|$)')
        AND (NOT species LIKE '%/%');
        
SET SQL_SAFE_UPDATES = 1;


SET SQL_SAFE_UPDATES = 0;

UPDATE bbs_species_list
SET scientific_name =
    CASE
        WHEN species_name REGEXP '^[A-Z][a-z-]+ [a-z-]+ [a-z-]+$'
            THEN SUBSTRING_INDEX(species_name, ' ', 2)
        ELSE species_name
    END
WHERE NOT species_name LIKE '%sp.%';
    
SET SQL_SAFE_UPDATES = 1;


-- ====================================================================
-- ebird_species_info
-- ====================================================================

-- Ergänzen der eindeutigen ID aou aus bbs_species_list

ALTER TABLE ebird_species_info
ADD COLUMN aou VARCHAR(5);

SET SQL_SAFE_UPDATES = 0;

UPDATE ebird_species_info AS e
JOIN bbs_species_list AS b
    ON e.scientific_name = b.scientific_name
SET e.aou = b.aou;

SET SQL_SAFE_UPDATES = 1;


-- Kontrolle:

SELECT DISTINCT
	eb.aou,
    sl.aou,
    sl.scientific_name
FROM bbs_species_list AS sl
JOIN analysis_observations AS ao
	ON sl.aou = ao.species_id
LEFT JOIN ebird_species_info AS eb
	ON sl.scientific_name = eb.scientific_name
ORDER BY eb.aou, sl.scientific_name;


-- ====================================================================
-- analysis_routes
-- ====================================================================

-- Erweiterung der Tabelle um die Spalte latitude_zone
-- Diese gibt an, in welcher der 7 definierten Breitenzonen des Projektbereiches
-- sich die Route befindet

ALTER TABLE analysis_routes
ADD COLUMN latitude_zone TINYINT;

SET SQL_SAFE_UPDATES = 0;

UPDATE analysis_routes AS ar
JOIN routes AS r
    ON r.state_num * 1000 + r.route = ar.route_id
CROSS JOIN (
    SELECT
        MIN(latitude) AS min_latitude,
        MAX(latitude) AS max_latitude
    FROM routes AS r
    JOIN analysis_routes AS ar
        ON r.state_num * 1000 + r.route = ar.route_id
) AS x
SET ar.latitude_zone =
    CASE
        WHEN r.latitude < x.min_latitude + (x.max_latitude - x.min_latitude) * 1 / 7
            THEN 1
        WHEN r.latitude < x.min_latitude + (x.max_latitude - x.min_latitude) * 2 / 7
            THEN 2
        WHEN r.latitude < x.min_latitude + (x.max_latitude - x.min_latitude) * 3 / 7
            THEN 3
        WHEN r.latitude < x.min_latitude + (x.max_latitude - x.min_latitude) * 4 / 7
            THEN 4
        WHEN r.latitude < x.min_latitude + (x.max_latitude - x.min_latitude) * 5 / 7
            THEN 5
        WHEN r.latitude < x.min_latitude + (x.max_latitude - x.min_latitude) * 6 / 7
            THEN 6
        ELSE 7
    END;
    
SET SQL_SAFE_UPDATES = 1;


-- ====================================================================
-- analysis_species_list
-- ====================================================================

/*
Für die Korrelationsanalyse werden zwei generelle Ansätze unterschieden
Dafür benötigt die Tabelle zwei Werte, die festhalten, wie viele Routen
mindestens 10 bzw. 20 Beobachtungen liefern.
*/

ALTER TABLE analysis_species_list
ADD COLUMN routes_over_10_obs INT;

ALTER TABLE analysis_species_list
ADD COLUMN routes_over_20_obs INT;

SET SQL_SAFE_UPDATES = 0;

WITH
relevant_observations AS (
	SELECT 
		species_id,
		route_id,
		COUNT(`year`) AS observation_count
	FROM analysis_relevant_observations
	GROUP BY species_id, route_id
	HAVING observation_count >= 10
),
route_counts AS (
	SELECT
		species_id,
        COUNT(route_id) AS route_count
	FROM relevant_observations
    GROUP BY species_id
)
UPDATE analysis_species_list AS sl
LEFT JOIN route_counts AS rc
	ON sl.species_id = rc.species_id
SET routes_over_10_obs = COALESCE(rc.route_count, 0);


WITH
relevant_observations AS (
	SELECT 
		species_id,
		route_id,
		COUNT(`year`) AS observation_count
	FROM analysis_relevant_observations
	GROUP BY species_id, route_id
	HAVING observation_count >= 20
),
route_counts AS (
	SELECT
		species_id,
        COUNT(route_id) AS route_count
	FROM relevant_observations
    GROUP BY species_id
)
UPDATE analysis_species_list AS sl
LEFT JOIN route_counts AS rc
	ON sl.species_id = rc.species_id
SET routes_over_20_obs = COALESCE(rc.route_count, 0);

SET SQL_SAFE_UPDATES = 1;


-- ====================================================================
-- analysis_relevant_observations
-- ====================================================================

/*
Für die Korrelationsanalyse erhält die Tabelle zwei bool'sche Marker
Marker 1: Eintrag bezieht sich auf eine Vogelart, die auf mindestens 20 Routen beobachtet wurde
Marker 2: Eintrag bezieht sich auf eine Route, die bzgl der Vogelart über ausreichend Beobachtungsjahre verfügt. Besonders:
	Für Marker 1 = True:  Route verfügt über mindestens 10 Beobachtungen
    Für Marker 1 = False: Route verfügt über mindestens 20 Beobachtungen
*/

ALTER TABLE analysis_relevant_observations
ADD COLUMN sufficient_routes BOOL;

ALTER TABLE analysis_relevant_observations
ADD COLUMN sufficient_observations BOOL;

SET SQL_SAFE_UPDATES = 0;

UPDATE analysis_relevant_observations AS o
JOIN analysis_species_list AS sl
	ON o.species_id = sl.species_id
SET sufficient_routes = CASE WHEN sl.routes_over_10_obs >= 20 THEN 1 ELSE 0 END;

UPDATE analysis_relevant_observations AS o
JOIN analysis_route_species_relevant AS rsr
	ON o.species_id = rsr.species_id AND o.route_id = rsr.route_id
SET sufficient_observations = CASE
		WHEN o.sufficient_routes = 1 THEN 
			CASE WHEN rsr.observation_count >= 10 THEN 1 ELSE 0 END
		ELSE CASE WHEN rsr.observation_count >= 20 THEN 1 ELSE 0 END
	END;

SET SQL_SAFE_UPDATES = 1;


SELECT 
	COUNT(DISTINCT species_id)
FROM analysis_relevant_observations
WHERE sufficient_routes = 0 AND sufficient_observations = 1;