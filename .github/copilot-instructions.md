# Job Search Tracker CLI - AI Coding Instructions

## Architecture Overview

- **CLI Framework**: Built with [Typer](https://typer.tiangolo.com/). Subcommands are modularized in [job_tracker/commands/](job_tracker/commands/).
- **Database**: SQLite ([jobs.db](jobs.db) in root). Managed via [job_tracker/database.py](job_tracker/database.py) using raw SQL and `sqlite3`. No ORM is used.
- **UI/Formatting**: [Rich](https://rich.readthedocs.io/) is used for all console output, including tables and status messages.
- **Entry Point**: [job_tracker/main.py](job_tracker/main.py) initializes the DB and registers subcommands.

## Key Patterns & Conventions

- **Field Mapping**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI-friendly names (e.g., `company`) and database column names (e.g., `company_name`).
- **Subcommand Registration**: New commands must be added to [job_tracker/commands/](job_tracker/commands/) and registered in [job_tracker/main.py](job_tracker/main.py) using `app.command()`.
- **Database Operations**: All SQL logic should reside in [job_tracker/database.py](job_tracker/database.py). Use the `get_db()` context manager for connections.
- **Interactive Prompts**: Use `typer.prompt` for user input in commands like `add` and `edit`.
- **Filtering & Sorting**: Use `parse_filter_string` and `parse_sort_string` from [job_tracker/utils.py](job_tracker/utils.py) to handle complex CLI queries.

## Developer Workflows

- **Running the App**: Use `python -m job_tracker.main [COMMAND]`.
- **Database Schema**: Defined in `initialize_db()` within [job_tracker/database.py](job_tracker/database.py).
- **Adding Columns**: Use `add_new_column()` in [job_tracker/database.py](job_tracker/database.py) for migrations.

## Integration Points

- **CSV Export**: The `view` command supports exporting to CSV via the `--export` flag, handled in [job_tracker/commands/view.py](job_tracker/commands/view.py).
- **Clickable Links**: The `view` command uses Rich's `[link=URL]text[/link]` syntax for clickable URLs in the terminal.
