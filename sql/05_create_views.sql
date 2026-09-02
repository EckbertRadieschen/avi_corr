USE bbs_analysis;

CREATE OR REPLACE VIEW bbs_relevant_routes_view AS 
	SELECT
		s.rteno,
		bo.country_num,
		bo.state_num,
		bo.route,
		COUNT(*) AS observation_count,
		MIN(bo.year) AS first_year,
		MAX(bo.year) AS last_year
	FROM (
		SELECT DISTINCT rteno
		FROM stops_nearest_autogen_point
	) AS s
	JOIN bird_observations AS bo
		ON s.rteno =
		   bo.state_num * 1000 + CAST(bo.route AS UNSIGNED)
	GROUP BY
		s.rteno,
		bo.country_num,
		bo.state_num,
		bo.route;