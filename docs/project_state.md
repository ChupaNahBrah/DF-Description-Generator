# Project State

## Current Focus
Build a robust testing and logging foundation before continuing deeper bug fixes.

The immediate goal is to make the program easier to diagnose and safer to refactor by:
- defining invariants
- expanding test coverage
- adding structured logging
- isolating known bugs through repeatable tests

## Current Priorities
1. Add structured logging to the project one module at a time
2. Expand loader invariants and tests
3. Add data integrity tests
4. Add selector/grammar tests for known failure cases

## Current Progress

### Logging
Implemented:
- loader.py: runtime reset, subject loading, and description loading
- logic.py: weighted choices, description mix, constraints, and subject pairing
- generator.py: loading and generation stage boundaries

Remaining:
- loader.py: weight loading
- selector.py
- filters.py
- grammar.py

Logging configuration currently lives in generator.py.
Move configuration to the application entry point when reviewing startup.

### Testing
tests/test_loader.py currently checks:
- Runtime containers populate after loading.
- Runtime containers are empty after resetting.

These are initial checks. They do not yet verify index correctness, complete
file loading, or repeated-load behavior.

## Known Issues and Verification Targets

### Subject Selection
`selector.py` XY path can fail with `required_tags` undefined
- choose_subject_ids() has inconsistent tag variables in its XY branch.
- required_tags_x is commented out while required_tags is still referenced.
- Depending on the preceding path, required_tags may be undefined or may
  contain values from a previous description.
- Review both X and Y filtering arguments and selected subject assignments.

### Index Compatibility
`selector.py` / `filters.py` recently changed from list-based tag lookup to dict-based tag lookup and may still contain downstream assumptions
- GlobalState.index["tags"] changed from defaultdict(list) to
  defaultdict(dict).
- Audit selector.py and filters.py for assumptions about the old structure.

### Grammar
`grammar.py` previously treated description dicts as strings; fixed locally, needs regression test
- A previous description-dictionary/string handling bug needs a regression test.
- Verify the current implementation before treating that issue as resolved.

### Edge Cases
subject/description planning path still needs deterministic tests for edge cases
Add deterministic coverage for:
- One subject with zero descriptions
- X and XY description combinations
- Requested subject counts and valid subject assignments
- Empty filtering results
- Repeated generation runs

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

## Testing Priorities
1. Strengthen loader tests with invariants
   - Expected source files are loaded.
   - Subject and description IDs are valid and unique.
   - Index entries refer to the correct loaded subjects.
   - Reset followed by reload produces consistent state.
2. Add data integrity tests for JSON inputs
3. Add selector tests for tag filtering and subject count guarantees
4. Add grammar tests for 0-desc / 1-desc / XY-desc combinations
5. Add generator integration tests for stable end-to-end runs

For bug fixes, prefer a test that reproduces the failure and then verifies
the corrected behavior.

## Logging Conventions

### Logger Setup
Each module uses a module-level logger:

    import logging
    logger = logging.getLogger(__name__)

Configure logging once in the application entry point.
Do not configure handlers or call basicConfig() in individual core/data modules.

### Levels
INFO:
- Major operations beginning
- Useful completion summaries
- High-level progress that remains useful during normal troubleshooting

Examples:
- "loading subject files"
- "loading description files"
- "loaded %s X descriptions and %s XY descriptions"
- "generation complete"

DEBUG:
- Individual files being processed
- Intermediate values, counts, choices, and plans
- Filtering inputs and candidate counts
- Internal state needed to explain a result or failure

Examples:
- "runtime data reset"
- "loading subject file %s"
- "loaded %s subject records from %s"

WARNING:
- Unexpected conditions where processing can continue and no exception
  traceback is needed
- Do not use for ordinary random outcomes or expected branches

ERROR:
- An operation failed, but there is no caught exception requiring a traceback

logger.exception():
- Use inside an exception handler when the traceback helps diagnose failure.
- Logs at ERROR level and includes the exception traceback.
- Example: "failed to read subject file %s"

Logging a failure does not determine whether execution should continue.
Choose whether to continue or raise based on the function's requirements.

### Message Style
- Start messages with lowercase.
- Use concise, direct wording.
- Omit ending periods.
- Use "loading..." for operations beginning and "loaded..." for completed work.
- Describe failures as "failed to..." followed by the operation.
- Include relevant filenames, IDs, tags, counts, or choices.
- Prefer counts and identifiers over dumping entire datasets.
- Do not manually prefix messages with module names or log levels.
- Avoid messages that merely narrate each line of code.
- Emit success messages only after the relevant operation succeeds.

### Formatting Values
Use logging placeholders with values passed as separate arguments:

    logger.debug("loaded %s subjects", subject_count)

Do not use f-strings or preformatted strings in logging calls.
Use f-strings for ordinary string construction outside logging.

Use %s for ordinary values, including numbers and collections.
Use %r when the exact representation helps reveal an ambiguous value.

Passing arguments separately defers message formatting.
It does not defer function calls used to calculate those arguments.

### Logging Ownership
- generator.py logs major pipeline boundaries and useful overall results.
- Individual modules log the details of their own operations.
- Avoid duplicate messages at multiple layers unless they add context.
- Keep core generation reusable: use logging for diagnostics instead of print().
- CLI output intended for the user remains separate from diagnostic logging.

## Current Rule of Thumb
Do not continue broad refactors until:
- logging exists in selector/filter failure paths
- tests can reproduce known bugs

## Working Approach
- Follow execution order when reviewing logging.
- Make small, focused changes.
- Verify each change before expanding scope.
- Update this document when a task is completed or priorities change.

## Architecture Decisions
- Keep file loading centralized in loader.py.
- Keep generator.py as the top-level orchestrator.
- Call choose_subject_ids() explicitly from generator.py.
- Keep CLI/UI behavior separate from generation logic.
- reset_runtime_state() replaces clear_indexes().
- The tag index maps tags to dictionaries keyed by subject ID.
- X and XY description indexes provide direct lookup by description ID.
- Flask/UI expansion remains deferred while the backend is stabilized.