# 0.8 Modernization Tasks

## Plan
- [x] Add transport abstraction shared by sync/async clients
- [ ] Introduce `AsyncAPI` with httpx
- [ ] Add Pydantic response models (opt-in)
- [ ] Add GeoJSON helpers on models (`to_geojson`, `__geo_interface__`)
- [x] Expand test coverage for all response formats and error handling
- [ ] Update docs for async usage and model opt-in

## Tracking
- [ ] Close #181 GeoJSON hardening (relations/multipolygons/routes/boundaries)
- [ ] Address open bugs: #172, #176
