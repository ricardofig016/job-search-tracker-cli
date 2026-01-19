# Job Search Tracker CLI - AI Coding Instructions

## Architecture & Data Flow

- **CLI Framework**: [Typer](https://typer.tiangolo.com/) powered commands in `job_tracker/commands/`. Subcommands (like `config`) use `app.add_typer`.
- **Entry Point**: The application is installed as a package with `job-tracker` as the console script (defined in `pyproject.toml`).
- **Database**: SQLite (raw `sqlite3`). Use the `get_db()` context manager in [job_tracker/database.py](job_tracker/database.py) for all connections. It uses `sqlite3.Row` for dict-like access.
- **Data Access**: Use `get_jobs()`, `get_job_by_id()`, and `update_job()` in `database.py` instead of raw SQL in commands when possible.
- **Maintenance**: `main.py` triggers `initialize_db()` and `update_ghosted_jobs()` (which marks applications >30 days old as ghosted) on every run.
- **Mapping Layer**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI aliases (e.g., `company`) and SQL columns (e.g., `company_name`).
- **Schema Management**: Dynamic column addition is handled via `add_new_column` in `database.py`. New columns **MUST** be added to `COLUMN_MAPPING` and `EDIT_COLUMN_ORDER` in [job_tracker/utils.py](job_tracker/utils.py).
- **Core Models**: Use Enums in [models.py](job_tracker/models.py) (`Status`, `Arrangement`, `JobType`, etc.) for field validation and CLI choices.

## UI & Interactivity Patterns

- **Rich Terminal UI**:
  - Use `[link=URL]Text[/link]` for clickable links in tables ([view.py](job_tracker/commands/view.py)).
  - Truncate long strings (like `notes` or `interview_transcript`) to ~100 chars in table views.
  - Use `on grey7` row styles for readability.
- **Interactivity**:
  - Intensive use of `typer.prompt()` for interactive workflows in [add.py](job_tracker/commands/add.py) and [edit.py](job_tracker/commands/edit.py).
  - Use `NullableChoice` for Enum-based prompts to support clearing fields.
  - **Nullable Support**: Use `NULL_STRINGS` ("-", "none", "null") and `is_null_string()` to allow users to intentionally clear database fields.
  - **Lazy Imports**: Import expensive modules (`scraper`, `llm`, `calendar_utils`) inside command functions to keep CLI startup fast.

## Data & Logic Conventions

- **Filtering/Sorting**: Logic for `view` and `stats` is in `parse_filter_string` and `parse_sort_string` ([utils.py](job_tracker/utils.py)). Supports `col~val` (LIKE), `col:[min-max]` (Range), and `AND/OR` logic.
- **Date/Time Management**:
  - Date Format: `YYYY-MM-DD`. Validated by `validate_date()`.
  - DateTime Format: `YYYY-MM-DD HH:MM`. Validated by `validate_datetime()`.
- **State Triggers**:
  - Updating "trigger fields" (e.g., `interview_time`, `status`, `followup_date`) in [edit.py](job_tracker/commands/edit.py) or entering them in [add.py](job_tracker/commands/add.py) automatically initiates a Google Calendar sync via `sync_event()`.
  - Setting status to `interviewing` defaults a followup date to (Today/Interview + 7 days).
  - Clearing a trigger field (like `interview_time`) should trigger `delete_event()` for the associated `event_id`.

## External Integrations

- **Scraper**: [scraper.py](job_tracker/scraper.py) uses `BeautifulSoup` with multiple fallback selectors for extracting job details.
- **LLM**: [llm.py](job_tracker/llm.py) enriches data using `gpt-5-nano`. It requires `user_profile.md` for context.
- **Google Calendar**:
  - Events are linked via `interview_event_id` and `followup_event_id` columns.
  - `sync_event()` handles creation/updates; `delete_event()` handles removal if fields are cleared.

## Metrics & Analytics

- **Stats Logic**: Funnel calculation and response time analysis reside in `job_tracker/commands/stats.py`.
- **Settled States**: Conversion rates often exclude "Awaiting" or "Currently Interviewing" to focus on terminal outcomes (Ghosted, Rejected, Offered).
