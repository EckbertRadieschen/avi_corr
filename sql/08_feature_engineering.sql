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
	ADD COLUMN norm_soil_moisture DECIMAL(8, 6);




