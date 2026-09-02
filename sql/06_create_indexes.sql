USE bbs_analysis;

-- =====================================================
-- analysis_observations
-- =====================================================

CREATE INDEX idx_analysis_observations_route_id
	ON analysis_observations (route_id);
    
CREATE INDEX idx_analysis_observations_species_id
	ON analysis_observations (species_id);

CREATE INDEX idx_analysis_observations_species_year
	ON analysis_observations (species_id, `year`);
    
CREATE INDEX idx_analysis_observations_route_year
	ON analysis_observations (route_id, `year`);
    
CREATE INDEX idx_analysis_observations_state_num
	ON analysis_observations (state_num);
