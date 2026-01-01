# Job Search Tracker CLI - AI Coding Instructions

## Architecture Overview

- **CLI Framework**: Built with [Typer](https://typer.tiangolo.com/). Subcommands are modularized in [job_tracker/commands/](job_tracker/commands/).
- **Database**: SQLite ([jobs.db](jobs.db) in root). Managed via [job_tracker/database.py](job_tracker/database.py) using raw SQL and `sqlite3`. No ORM is used.
- **UI/Formatting**: [Rich](https://rich.readthedocs.io/) is used for all console output, including tables, panels, and columns.
- **Entry Point**: [job_tracker/main.py](job_tracker/main.py) initializes the DB and registers subcommands.

## Key Patterns & Conventions

- **Field Mapping**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI-friendly names (e.g., `company`) and database column names (e.g., `company_name`).
- **Subcommand Registration**: New commands must be added to [job_tracker/commands/](job_tracker/commands/) and registered in [job_tracker/main.py](job_tracker/main.py) using `app.command()` or `app.add_typer()` for command groups.
- **Database Operations**: All SQL logic should reside in [job_tracker/database.py](job_tracker/database.py). Use the `get_db()` context manager for connections. Results are returned as `sqlite3.Row` objects for dictionary-like access.
- **Interactive Prompts**: Use `typer.prompt` for user input in commands like `add` and `edit`.
- **Filtering & Sorting**: Use `parse_filter_string` and `parse_sort_string` from [job_tracker/utils.py](job_tracker/utils.py).
  - **Supported Operators**: `==`, `!=`, `>=`, `<=`, `>`, `<`, `~` (substring), `:` (substring), `AND`, `OR`, and `col:[min-max]` ranges.
  - **Example**: `rating>=4 AND company~google OR status==offered`.

## Developer Workflows

- **Running the App**: Use `python -m job_tracker.main [COMMAND]`.
- **Database Schema**: Defined in `initialize_db()` within [job_tracker/database.py](job_tracker/database.py).
- **Adding Columns**: Use `add_new_column()` in [job_tracker/database.py](job_tracker/database.py) for migrations.

## Integration Points

- **CSV Export**: The `view` command supports exporting to CSV via the `--export` flag. Note that the `stats` command does **not** support CSV export.
- **Clickable Links**: The `view` command uses Rich's `[link=URL]text[/link]` syntax for clickable URLs in the terminal.
- **Dashboards**: The `stats` command uses `rich.panel.Panel` and `rich.columns.Columns` to create a visual dashboard of application metrics.
