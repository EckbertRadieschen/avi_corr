USE bbs_analysis;

SELECT
    COUNT(DISTINCT s.rteno) AS routes_with_spatial_data,
    COUNT(DISTINCT
        CASE
            WHEN bo.route_data_id IS NOT NULL
            THEN s.rteno
        END
    ) AS routes_with_observations
FROM (
    SELECT DISTINCT rteno
    FROM stops_nearest_autogen_point
) AS s
LEFT JOIN bird_observations AS bo
    ON s.rteno =
       bo.state_num * 1000 + CAST(bo.route AS UNSIGNED);
       
       
SELECT
    s.rteno,
    bo.state_num,
    bo.route,
    bo.state_num * 1000 + CAST(bo.route AS UNSIGNED) AS calculated_rteno
FROM (
    SELECT DISTINCT rteno
    FROM stops_nearest_autogen_point
) AS s
JOIN bird_observations AS bo
    ON s.rteno = bo.state_num * 1000 + CAST(bo.route AS UNSIGNED)
GROUP BY
    s.rteno,
    bo.state_num,
    bo.route
ORDER BY s.rteno
LIMIT 20;

SELECT
    COUNT(DISTINCT s.rteno) AS spatial_routes,
    COUNT(DISTINCT bo.state_num * 1000 + CAST(bo.route AS UNSIGNED))
        AS routes_with_observations
FROM (
    SELECT DISTINCT rteno
    FROM stops_nearest_autogen_point
) AS s
LEFT JOIN bird_observations AS bo
    ON s.rteno =
       bo.state_num * 1000 + CAST(bo.route AS UNSIGNED);
       
SELECT *
FROM bbs_relevant_routes_view
WHERE last_year > 2024
ORDER BY rteno;

SELECT 
	year,
    COUNT(*) AS observation_count,
    COUNT(DISTINCT route) AS routes_count
FROM bird_observations
WHERE year > 2010
GROUP BY year
ORDER BY year DESC;

WITH bird_observation_agg AS (
	SELECT
		state_num,
        route,
		COUNT(DISTINCT year) AS year_count,
		MIN(year) AS first_year,
		MAX(year) AS last_year
	FROM bird_observations
    GROUP BY state_num, route
)
SELECT
	s.rteno,
	bo.year_count,
	bo.first_year,
	bo.last_year,
    bo.year_count / (bo.last_year - bo.first_year + 1) AS year_count_quote
FROM (
	SELECT DISTINCT rteno
	FROM stops_nearest_autogen_point
) AS s
JOIN bird_observation_agg AS bo
	ON s.rteno = bo.state_num * 1000 + CAST(bo.route AS UNSIGNED);
    
SELECT *
FROM route_evaluation
WHERE year_count_quote < 0.5
ORDER BY year_count_quote DESC;

SELECT *
FROM bbs_states
WHERE state_num = 81;


WITH evaluation AS (
	SELECT
		s.state_num,
		AVG(st.state_area) as state_area,
		COUNT(*) AS spatial_routes,
		ROUND(
			AVG(s.observation_years),
			1
		) AS avg_observation_years,
		ROUND(
			AVG(s.coverage_percent),
			1
		) AS avg_coverage_percent,
		SUM(
			CASE
				WHEN s.coverage_percent < 50
				THEN 1
				ELSE 0
			END
		) AS routes_below_50_percent
	FROM (
		SELECT
			s.rteno,
			bo.state_num,
			COUNT(DISTINCT bo.year) AS observation_years,
			MIN(bo.year) AS first_year,
			MAX(bo.year) AS last_year,
			COUNT(DISTINCT bo.year) /
			(MAX(bo.year) - MIN(bo.year) + 1) * 100
				AS coverage_percent
		FROM (
			SELECT DISTINCT rteno
			FROM stops_nearest_autogen_point
		) AS s
		JOIN bird_observations AS bo
			ON s.rteno =
			   bo.state_num * 1000
			   + CAST(bo.route AS UNSIGNED)
		WHERE bo.year <> 2020
		GROUP BY
			s.rteno,
			bo.state_num
	) AS s
	JOIN bbs_states as st
		ON s.state_num = st.state_num
	GROUP BY
		s.state_num
	ORDER BY
		s.state_num
) 
SELECT 
	state_num,
	ROUND(state_area) AS state_area,
	spatial_routes,
    ROUND(spatial_routes * 100000 / state_area, 1) AS routes_per_100000,
	avg_observation_years,
	avg_coverage_percent,
	routes_below_50_percent
FROM evaluation;

SELECT * 
FROM analysis_routes;


SELECT COUNT(*)
FROM bird_observations AS bo
JOIN analysis_routes AS r
    ON r.route_id = bo.state_num * 1000 + CAST(bo.route AS UNSIGNED);
    
SELECT COUNT(DISTINCT bo.route_data_id)
FROM bird_observations AS bo
JOIN analysis_routes AS r
    ON r.route_id = bo.state_num * 1000 + CAST(bo.route AS UNSIGNED);
    

SELECT
    COUNT(*) AS anzahl_stops,
    MIN(distance_from_nearest_autogen_m) AS min_distance,
    AVG(distance_from_nearest_autogen_m) AS avg_distance,
    MAX(distance_from_nearest_autogen_m) AS max_distance
FROM stops_nearest_autogen_point;

SELECT
    rteno,
    COUNT(*) AS anzahl_stops,
    MIN(distance_from_nearest_autogen_m) AS min_distance,
    AVG(distance_from_nearest_autogen_m) AS avg_distance,
    MAX(distance_from_nearest_autogen_m) AS max_distance,
    MAX(distance_from_nearest_autogen_m)
        - MIN(distance_from_nearest_autogen_m) AS distance_range
FROM stops_nearest_autogen_point
GROUP BY rteno
ORDER BY distance_range;
    

SELECT *
FROM analysis_stops
LIMIT 10;

SELECT 
	MIN(year) AS min_year,
    MAX(year) AS max_year
FROM analysis_route_years;


SELECT DISTINCT
	st.state_name
FROM analysis_routes as r
JOIN bbs_states AS st
	ON r.state_num = st.state_num 
ORDER BY st.state_name;


SELECT
	COUNT(*) 
FROM era5_monthly_data;


SELECT
    COUNT(*) AS rows_total,
    MIN(vegetation_coefficient) AS vc_min,
    MAX(vegetation_coefficient) AS vc_max,
    AVG(vegetation_coefficient) AS vc_mean
FROM era5_route_monthly;

SELECT *
FROM era5_route_monthly
ORDER BY route_id, year, month
LIMIT 20;

SELECT
    month,
    COUNT(*) AS n,
    ROUND(AVG(vegetation_coefficient), 4) AS vc_mean,
    ROUND(MIN(vegetation_coefficient), 4) AS vc_min,
    ROUND(MAX(vegetation_coefficient), 4) AS vc_max,
    ROUND(STDDEV(vegetation_coefficient), 4) AS vc_sd,
    ROUND(AVG(soil_moisture_factor), 4) AS sm_factor_mean,
    ROUND(AVG(solar_radiation_factor), 4) AS sr_factor_mean
FROM era5_route_monthly
GROUP BY month
ORDER BY month;


SELECT
    year,
    ROUND(AVG(vegetation_coefficient), 4) AS vc_mean,
    ROUND(AVG(soil_moisture_factor), 4) AS sm_factor_mean,
    ROUND(AVG(solar_radiation_factor), 4) AS sr_factor_mean
FROM era5_route_monthly
GROUP BY year
ORDER BY year;


WITH ranked AS (
    SELECT
        relative_humidity,
        ROW_NUMBER() OVER (ORDER BY relative_humidity) AS rn,
        COUNT(*) OVER () AS n
    FROM era5_route_monthly
    WHERE `year` NOT IN (2022, 2023)
      AND relative_humidity IS NOT NULL
),
quantiles AS (
    SELECT
        MAX(CASE WHEN rn = CEIL(n * 0.05) THEN relative_humidity END) AS q05,
        MAX(CASE WHEN rn = CEIL(n * 0.50) THEN relative_humidity END) AS median,
        MAX(CASE WHEN rn = CEIL(n * 0.95) THEN relative_humidity END) AS q95
    FROM ranked
)
SELECT
    ROUND(q05, 4) AS q05,
    ROUND(median, 4) AS median,
    ROUND(q95, 4) AS q95,
    ROUND((median - q05) / (q95 - q05), 4) AS median_norm
FROM quantiles;

SELECT
	MIN(latitude) AS min_latitude,
    MAX(latitude) AS max_latitude,
    MIN(longitude) AS min_longitude,
    MAX(longitude) AS max_longitude
FROM analysis_stops;

SELECT
	COUNT(DISTINCT species_id)
FROM analysis_observations;

SELECT 
	COUNT(*)
FROM ebird_species_info;

SELECT
	DISTINCT species_id
FROM analysis_observations;

-- 417 AOU in analysis_observations


SELECT
    species_id,
    ebird_species_code,
    scientific_name,
    common_name
FROM analysis_species_list
WHERE ebird_species_code IS NOT NULL
ORDER BY ebird_species_code;

SELECT
    COUNT(*) AS total_species,
    COUNT(ebird_species_code) AS species_with_ebird_code,
    COUNT(*) - COUNT(ebird_species_code) AS species_without_ebird_code
FROM analysis_species_list;

SELECT * FROM ebird_breeding_ranges;



