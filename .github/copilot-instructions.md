# Job Search Tracker CLI - AI Coding Instructions

## Architecture Overview

- **CLI Framework**: Built with [Typer](https://typer.tiangolo.com/). Subcommands are modularized in [job_tracker/commands/](job_tracker/commands/) and registered in [job_tracker/main.py](job_tracker/main.py).
- **Database**: SQLite ([jobs.db](jobs.db) in root). Managed via [job_tracker/database.py](job_tracker/database.py) using raw SQL and `sqlite3`. No ORM is used.
- **UI/Formatting**: [Rich](https://rich.readthedocs.io/) is used for all console output, including tables, panels, and columns.
- **Calendar Integration**: Google Calendar sync for follow-ups and interviews via [job_tracker/calendar_utils.py](job_tracker/calendar_utils.py).

## Key Patterns & Conventions

- **Field Mapping**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI-friendly names (e.g., `company`) and database column names (e.g., `company_name`).
- **Enums & Validation**: Use the `Enum` classes in [job_tracker/models.py](job_tracker/models.py) for validating fields like `status`, `arrangement`, and `level`. Use `validate_date` and `validate_datetime` from [job_tracker/utils.py](job_tracker/utils.py).
- **Database Operations**: All SQL logic should reside in [job_tracker/database.py](job_tracker/database.py). Use the `get_db()` context manager for connections. Results are returned as `sqlite3.Row` objects.
- **Schema Management**: Use `initialize_db()` for setup and `run_migrations()` for updates. Dynamic columns can be added via `add_new_column()`.
- **Filtering & Sorting**: Use `parse_filter_string` and `parse_sort_string` from [job_tracker/utils.py](job_tracker/utils.py).
  - **Operators**: `==`, `!=`, `>=`, `<=`, `>`, `<`, `~` (substring), `:` (substring), `AND`, `OR`, and `col:[min-max]` ranges.
  - **Example**: `rating>=4 AND company~google OR status==offered`.

## Developer Workflows

- **Running the App**: Use `python -m job_tracker.main [COMMAND]`.
- **Adding Commands**: Create a new file in [job_tracker/commands/](job_tracker/commands/) and register it in [job_tracker/main.py](job_tracker/main.py).
- **Calendar Sync**: Requires `credentials.json` and `token.json` in the root. Syncing is triggered during `add` and `edit` commands if relevant dates are provided.

## Integration Points

- **Google Calendar**: Uses `google-api-python-client`. Events are identified by `followup_event_id` and `interview_event_id` in the DB.
- **CSV Export**: The `view` command supports exporting to CSV via the `--export` flag.
- **Interactive Prompts**: Use `typer.prompt` for user input in commands like `add` and `edit`.
