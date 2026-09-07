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

DESCRIBE era5_monthly_data;

