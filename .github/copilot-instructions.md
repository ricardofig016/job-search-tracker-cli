# Job Search Tracker CLI - AI Coding Instructions

## Architecture & Data Flow

- **CLI Framework**: [Typer](https://typer.tiangolo.com/) powered commands in `job_tracker/commands/`. Subcommands (like `config`) use `app.add_typer`.
- **Database**: SQLite (raw `sqlite3`). Use the `get_db()` context manager in [job_tracker/database.py](job_tracker/database.py) for all connections.
- **Maintenance**: `main.py` triggers `initialize_db()` and `update_ghosted_jobs()` (which marks applications >30 days old as ghosted) on every run.
- **Mapping Layer**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI aliases (e.g., `company`) and SQL columns (e.g., `company_name`).

## UI & Interactivity Patterns

- **Rich Terminal UI**:
  - Use `[link=URL]Text[/link]` for clickable links in tables ([view.py](job_tracker/commands/view.py)).
  - Truncate long strings (like `notes` or `transcript`) to ~100 chars in table views.
  - Use `on grey7` row styles and colored status panels in `stats`.
- **Interactivity**:
  - Intensive use of `typer.prompt()` for interactive workflows.
  - **Nullable Support**: Use `NULL_STRINGS` ("-", "none", "null") and `is_null_string()` to allow users to intentionally clear database fields.
  - **Lazy Imports**: Import expensive modules (`scraper`, `llm`, `calendar_utils`) inside command functions to keep CLI startup fast.

## Data & Logic Conventions

- **Filtering/Sorting**: Logic for `view` and `stats` is in `parse_filter_string` and `parse_sort_string` ([utils.py](job_tracker/utils.py)). Supports `col~val` (LIKE), `col:[min-max]` (Range), and `AND/OR` logic.
- **Date/Time Management**:
  - Date Format: `YYYY-MM-DD`.
  - DateTime Format: `YYYY-MM-DD HH:MM`.
  - Always use `_parse_dt` helper in [stats.py](job_tracker/commands/stats.py) for ISO/manual format conversion.
- **State Triggers**:
  - Moving to `interviewing` status automatically triggers followup date generation (Interview + 7 days).
  - Updating "trigger fields" (e.g., `interview_time`, `status`) in [edit.py](job_tracker/commands/edit.py) automatically initiates a Google Calendar sync.

## External Integrations

- **Scraper**: [scraper.py](job_tracker/scraper.py) uses `BeautifulSoup` with multiple fallback selectors (e.g., checking both `top-card-layout__title` and `sub-nav-cta__header` for job titles).
- **LLM**: [llm.py](job_tracker/llm.py) uses `gpt-5-nano` with `strict: True` JSON schema.
- **Google Calendar**:
  - Linked via `interview_event_id` and `followup_event_id`.
  - `sync_event()` handles both creation and updates (via `.update()` or `.insert()` fallback).

## Metrics Definitions

- **Settled Applications**: For conversion rates, "settled" means terminal states (Ghosted, Rejected, Offered) or defined outcomes, excluding "Awaiting" or "Currently Interviewing" states.
- **Calculated Funnel**: Analytics distinguish between `rejections_pre_interview` and `rejections_post_interview`.
