# Job Search Tracker CLI - AI Coding Instructions

## Architecture & Data Flow

- **CLI Framework**: [Typer](https://typer.tiangolo.com/) powered commands in `job_tracker/commands/`. Subcommands (like `config`) use `app.add_typer`.
- **Database**: SQLite (raw `sqlite3`). Use `get_db()` context manager in [job_tracker/database.py](job_tracker/database.py) for connections. It uses `sqlite3.Row` for dict-like access.
- **Maintenance**: `main.py` triggers `initialize_db()` and `update_ghosted_jobs()` (marks apps >30 days old as ghosted) on every run via `@app.callback()`.
- **Mapping Layer**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI aliases (e.g., `company`) and SQL columns (e.g., `company_name`).
- **Schema Management**: New columns **must** be added to `COLUMN_MAPPING` and `EDIT_COLUMN_ORDER` in `utils.py`, and handled via `run_migrations()` in `database.py`.

## UI & Interactivity

- **Rich Terminal UI**: Use `rich` for tables and formatting. Use `[link=URL]Text[/link]` for clickable links in views. Truncate long notes/transcripts to ~100 chars in table views.
- **Interactivity**: Intensive use of `typer.prompt()` for interactive workflows in `add.py` and `edit.py`.
- **Nullable Support**: Use `NULL_STRINGS` ("-", "none", "null") and `is_null_string()` to allow users to clear DB fields. Use `NullableChoice` for Enum prompts.

## State Triggers & Sync

- **Calendar Sync**: Updating "trigger fields" (e.g., `interview_time`, `status`, `followup_date`) in `edit.py` or entering them in `add.py` initiates a Google Calendar sync via `sync_event()`.
- **Event IDs**: Events are linked via `interview_event_id` and `followup_event_id` columns. Clearing a trigger field (like `interview_time`) should trigger `delete_event()`.
- **LLM Enrichment**: `llm.enrich_job_data()` enriches scraped data using `gpt-5-nano`. It requires `user_profile.md` for context.

## Filtering & Logic

- **DSL**: `view` and `stats` use `parse_filter_string` ([utils.py](job_tracker/utils.py)). Supports `col~val` (LIKE), `col:[min-max]` (Range), and `AND/OR` logic.
- **Conventions**: Date format `YYYY-MM-DD`, DateTime `YYYY-MM-DD HH:MM`. Use `validate_date()` and `validate_datetime()`.
- **Lazy Imports**: Import heavy modules (`scraper`, `llm`, `calendar_utils`) inside command functions to keep CLI startup fast.
