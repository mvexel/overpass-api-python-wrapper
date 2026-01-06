# 0.8 Modernization Plan

## Goals
- Keep sync `overpass.API` stable while adding a parallel async client.
- Introduce opt-in Pydantic models (v2) for responses and helpers for GeoJSON output.
- Improve test coverage to avoid regressions across all response formats and errors.

## Non-goals (for 0.8 alpha)
- Breaking changes to default return types.
- Full rewrite of the API surface.

## Design overview
- Split transport from parsing to make sync/async share code.
- Add a typed response layer:
  - Pydantic models for Overpass JSON and GeoJSON.
  - Dataclasses for configuration and small internal structures.
- Provide helpers on models (`to_geojson()`, `__geo_interface__`) while keeping
  existing dict return behavior by default.

## Implemented (current branch)

### Foundation (previous work)
- Shared transport abstraction for sync/async HTTP.
- `AsyncAPI` alongside `API` (httpx-based).
- Opt-in Pydantic models for Overpass JSON + GeoJSON, plus CSV/XML wrappers.
- `to_geojson()` and `__geo_interface__` on GeoJSON models (Shapely round-trip test).
- Extended tests for response formats, error mapping, and async parity.
- Hardened JSON parsing with clearer errors when content is invalid.
- `Utils.to_overpass_id` now requires a source type (`way` or `relation`).

### Phase 1: Code Deduplication (commit b2cef17)
- Created `overpass/_base.py` with 207 lines of shared code
- Extracted shared constants: `SUPPORTED_FORMATS`, `DEFAULT_TIMEOUT`, `DEFAULT_ENDPOINT`, etc.
- Extracted pure functions: `construct_ql_query()`, `select_endpoint()`, `guard_bbox()`, `bbox_area_km2()`
- Extracted response parsing: `parse_csv_response()`, `parse_xml_response()`, `parse_json_response()`
- Reduced `api.py` by 169 lines, `async_api.py` by 166 lines
- Single source of truth for shared logic

### Phase 2: Exception Handling (commit ca88f3f)
- All exception classes now call `super().__init__()` properly
- Implemented `__str__` methods for meaningful error messages
- Added `__repr__` methods for debugging
- `str(exception)` now returns useful messages instead of empty strings

### Phase 3: Transport Layer (commit ca88f3f)
- Added `Transport` Protocol for sync transport type safety
- Added `AsyncTransport` Protocol for async transport type safety
- Fixed `HttpxAsyncTransport` to actually use the `proxies` parameter
- Fixed hardcoded status endpoint to derive from configured endpoint
- Custom Overpass instances now have working status checks

## Testing strategy
- Unit tests for:
  - Query construction (`MapQuery`, `WayQuery`, `build`, `verbosity`, `date`).
  - Response parsing for CSV/XML/JSON/GeoJSON.
  - Error mapping for HTTP status codes (400/429/504/other).
  - Overpass status endpoint parsing.
- Async parity tests for the same responses using mocked HTTP.
- Integration tests remain opt-in (`RUN_NETWORK_TESTS=1`).
- **Current status:** 39 tests passing, 2 skipped (live API tests).

## Next steps

### Phase 4: API Consistency
- Add type hints to `query` parameter in `get()` methods
- Add `@overload` decorators for precise return types
- Document sync property vs async method difference for slot status

### Phase 5: Configuration & Logging
- Environment variable support (`OVERPASS_ENDPOINT`, `OVERPASS_TIMEOUT`)
- Replace `print()` statements with `logging` module
- Add configurable log levels

### Phase 6: Testing & Documentation
- Add tests for custom transport implementations
- Add tests for endpoint rotation behavior
- Update README with new features
- Document breaking changes for 0.8

## Open questions
- GeoJSON hardening for relations/multipolygons/routes/boundaries (#181).
- Investigate #172 and #176.
