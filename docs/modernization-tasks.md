# 0.8 Modernization Tasks

## Completed (Previous Work)
- [x] Add transport abstraction shared by sync/async clients
- [x] Introduce `AsyncAPI` with httpx
- [x] Add Pydantic response models (opt-in)
- [x] Add GeoJSON helpers on models (`to_geojson`, `__geo_interface__`)
- [x] Expand test coverage for all response formats and error handling
- [x] Update docs for async usage and model opt-in
- [x] Merge security updates (requests 2.32.4, deepdiff 8.6.1)
- [x] Configure Dependabot for uv

## Phase 1: Code Deduplication (High Priority)

### 1.1 Extract shared base module
- [ ] Create `overpass/_base.py` with shared constants and utilities
- [ ] Move class constants: `SUPPORTED_FORMATS`, `_timeout`, `_endpoint`, `_default_endpoints`, `_headers`, `_QUERY_TEMPLATE`, `_GEOJSON_QUERY_TEMPLATE`
- [ ] Move static/pure methods: `_construct_ql_query()`, `_select_endpoint()`, `_guard_bbox()`, `_bbox_area_km2()`
- [ ] Move response parsing logic to shared functions

### 1.2 Refactor API classes to use shared base
- [ ] Update `API` class to import from `_base`
- [ ] Update `AsyncAPI` class to import from `_base`
- [ ] Ensure tests still pass after refactor

## Phase 2: Exception Handling Fixes

### 2.1 Fix exception classes
- [ ] Add `super().__init__()` calls to all exception classes
- [ ] Implement `__str__` methods for meaningful error messages
- [ ] Add `__repr__` for debugging
- [ ] Update tests to verify exception messages

## Phase 3: Transport Layer Improvements

### 3.1 Define Transport Protocol
- [ ] Create `Transport` Protocol in `transport.py` for type safety
- [ ] Create `AsyncTransport` Protocol
- [ ] Add runtime_checkable decorator for duck typing validation

### 3.2 Fix async transport bugs
- [ ] Fix unused `proxies` parameter in `HttpxAsyncTransport`
- [ ] Ensure proxy configuration works for async client

### 3.3 Status endpoint fix
- [ ] Make `_api_status()` respect custom endpoint configuration
- [ ] Extract status URL from configured endpoint base

## Phase 4: API Consistency

### 4.1 Sync/Async interface alignment
- [ ] Document the property vs method difference for slots (sync: property, async: method)
- [ ] Consider deprecation path for sync properties in favor of methods (optional, breaking)

### 4.2 Type hint improvements
- [ ] Add type hints to `query` parameter in `get()` methods
- [ ] Add `@overload` decorators for precise return types based on `model` parameter
- [ ] Add return type annotations to all public methods

## Phase 5: Configuration & Logging

### 5.1 Environment variable support
- [ ] Support `OVERPASS_ENDPOINT` environment variable
- [ ] Support `OVERPASS_TIMEOUT` environment variable
- [ ] Document environment variable configuration

### 5.2 Structured logging
- [ ] Replace `print()` statements with `logging` module
- [ ] Add configurable log levels
- [ ] Add request/response logging at DEBUG level

## Phase 6: Testing & Documentation

### 6.1 Test coverage expansion
- [ ] Add tests for custom transport implementations
- [ ] Add tests for endpoint rotation behavior
- [ ] Add tests for proxy configuration

### 6.2 Documentation updates
- [ ] Update README with new features
- [ ] Add docstrings to private methods
- [ ] Document breaking changes for 0.8

## Open Issues to Address
- [ ] #181 GeoJSON hardening (relations/multipolygons/routes/boundaries)
- [ ] #172 (investigate)
- [ ] #176 (investigate)

## Implementation Order

Execute phases in order. Each phase should be a separate commit or PR:

1. **Phase 1** - Deduplication (largest impact, reduces maintenance burden)
2. **Phase 2** - Exception fixes (quick win, improves debugging)
3. **Phase 3** - Transport fixes (bug fixes, protocol safety)
4. **Phase 4** - API consistency (type safety improvements)
5. **Phase 5** - Configuration (feature additions)
6. **Phase 6** - Testing & docs (polish)
