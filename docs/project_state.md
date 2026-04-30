# Project State

## Current Focus
Build a robust testing and logging foundation before continuing deeper bug fixes.

The immediate goal is to make the program easier to diagnose and safer to refactor by:
- defining invariants
- expanding test coverage
- adding structured logging
- isolating known bugs through repeatable tests

## Current Priorities
1. Add structured logging to selector and filters
2. Expand loader invariants and tests
3. Expand logging to the rest of the modules
4. Add data integrity tests
5. Add selector/grammar tests for known failure cases

## Known Active Bugs
- `selector.py` XY path can fail with `required_tags` undefined
- `selector.py` / `filters.py` recently changed from list-based tag lookup to dict-based tag lookup and may still contain downstream assumptions
- `grammar.py` previously treated description dicts as strings; fixed locally, needs regression test
- subject/description planning path still needs deterministic tests for edge cases

## Recent Architecture Changes
- Replaced `clear_indexes()` with `reset_runtime_state()`
- `GlobalState.index["tags"]` changed from `defaultdict(list)` to `defaultdict(dict)`
- `GlobalState.index["x_descriptions"]` and `["xy_descriptions"]` now behave as direct lookup dictionaries
- `generator.py` should remain the top-level orchestration layer
- `choose_subject_ids()` should be called explicitly by `generator.py`, not hidden inside `select_subjects_for_descriptions()`

## Deferred Refactors
- Normalize tag fields when building `desc_plan` so all tag constraints are always lists
- Audit selector XY path for variable consistency (`required_tags_x`, `required_tags_y`, etc.)
- Reevaluate `GlobalState.index["subcategories"]` list vs set tradeoffs later
- Remove dead helper functions in `loader.py` if confirmed unused

## Testing Roadmap
- Strengthen loader tests with invariants
- Add data integrity tests for JSON inputs
- Add selector tests for tag filtering and subject count guarantees
- Add grammar tests for 0-desc / 1-desc / XY-desc combinations
- Add generator integration tests for stable end-to-end runs

## Logging Roadmap
- Add module-level loggers to:
  - selector.py
  - filters.py
  - grammar.py
  - loader.py
- Keep generator logging minimal:
  - stage boundaries
  - major outputs
- Prefer DEBUG for internal state
- Prefer INFO for high-level flow

## Current Rule of Thumb
Do not continue broad refactors until:
- logging exists in selector/filter failure paths
- tests can reproduce known bugs