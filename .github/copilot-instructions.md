# Job Search Tracker CLI - AI Coding Instructions

## Architecture Overview

- **CLI Framework**: Built with [Typer](https://typer.tiangolo.com/). Commands are modularized in [job_tracker/commands/](job_tracker/commands/) and registered in [job_tracker/main.py](job_tracker/main.py).
- **Database**: SQLite (raw SQL via `sqlite3`, no ORM). Connection managed by `get_db()` context manager in [job_tracker/database.py](job_tracker/database.py).
- **UI/Formatting**: [Rich](https://rich.readthedocs.io/) for tables, panels, and colored output.
- **Interactivity**: Intensive use of `typer.prompt`. [scripts/bulk_add.py](scripts/bulk_add.py) pipes newlines to bypass prompts by accepting defaults.
- **Enrichment**:
  - [job_tracker/scraper.py](job_tracker/scraper.py) parses LinkedIn HTML using `BeautifulSoup`.
  - [job_tracker/llm.py](job_tracker/llm.py) uses OpenAI to extract metadata and analyze fit based on [user_profile.md](user_profile.md).

## Key Patterns & Conventions

- **CLI-to-DB Field Mapping**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to bridge CLI aliases (e.g., `company`) to SQL columns (e.g., `company_name`).
- **Database Schema**:
  - Manage schema changes in `initialize_db()` and `run_migrations()` in [job_tracker/database.py](job_tracker/database.py).
  - Use `add_new_column()` for dynamic updates.
- **Nullable Inputs**: Use `NULL_STRINGS` ("-", "none", "null") and `is_null_string()` from [job_tracker/utils.py](job_tracker/utils.py) to permit clearing fields during prompts.
- **Data Integrity**:
  - Use Enums from [job_tracker/models.py](job_tracker/models.py) with `NullableChoice` for validated CLI inputs.
  - Custom logic for `view` filters (e.g., `col~val`, `col:[min-max]`, `AND/OR`) is in `parse_filter_string` in [job_tracker/utils.py](job_tracker/utils.py).

## Developer Workflows

- **Running local dev**: `python -m job_tracker.main [COMMAND]`.
- **Adding a Command**: Create a new module in `job_tracker/commands/` and register it in [job_tracker/main.py](job_tracker/main.py).
- **Extending Schema**:
  1. Add column to `CREATE TABLE` in `initialize_db()`.
  2. Add migration check in `run_migrations()`.
  3. Update `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py).
- **Modifying Scraper**: Sensitive to LinkedIn HTML structure changes (e.g., `topcard__org-name-link`).

## Integration Details

- **OpenAI**: Requires `OPENAI_API_KEY` in `.env`. The LLM returns structured JSON via `enrich_job_data`.
- **Google Calendar**: Events identified by `interview_event_id` in DB. Requires `credentials.json` and `token.json`. Sync logic in [job_tracker/calendar_utils.py](job_tracker/calendar_utils.py).
- **User Personalization**: [user_profile.md](user_profile.md) is the source of truth for "fit" and "rating" analysis.
