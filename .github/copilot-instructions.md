# Job Search Tracker CLI - AI Coding Instructions

## Architecture Overview

- **CLI Framework**: Built with [Typer](https://typer.tiangolo.com/). Subcommands are modularized in [job_tracker/commands/](job_tracker/commands/) and registered in [job_tracker/main.py](job_tracker/main.py).
- **Database**: SQLite ([jobs.db](jobs.db) in root). Managed via [job_tracker/database.py](job_tracker/database.py) using raw SQL and `sqlite3`. No ORM is used.
- **UI/Formatting**: [Rich](https://rich.readthedocs.io/) is used for all console output. Use `Table`, `Panel`, and `Console` for structured output.
- **Prompts**: Use `typer.prompt` for interactive input. For bulk operations, scripts like `bulk_add.py` pipe newlines to accept defaults.
- **Data Enrichment**:
  - **Scraper**: [job_tracker/scraper.py](job_tracker/scraper.py) fetches LinkedIn job pages using `requests` and `BeautifulSoup`.
  - **LLM**: [job_tracker/llm.py](job_tracker/llm.py) uses OpenAI to extract structured data and generate insights (rating, fit, notes) based on [user_profile.md](user_profile.md).
- **Calendar Integration**: Google Calendar sync for interviews via [job_tracker/calendar_utils.py](job_tracker/calendar_utils.py).

## Key Patterns & Conventions

- **Field Mapping**: Always use `COLUMN_MAPPING` in [job_tracker/utils.py](job_tracker/utils.py) to translate between CLI-friendly names (e.g., `company`) and database column names (e.g., `company_name`).
- **Enums & Validation**: Use `Enum` classes in [job_tracker/models.py](job_tracker/models.py) for fields like `status`, `arrangement`, and `level`. Use `validate_date` and `validate_datetime` from [job_tracker/utils.py](job_tracker/utils.py).
- **Database Operations**: All SQL logic resides in [job_tracker/database.py](job_tracker/database.py). Use `get_db()` context manager. Results are `sqlite3.Row` objects.
- **Schema Management**: `initialize_db()` creates tables. `run_migrations()` handles updates. Use `add_new_column()` for dynamic schema changes.
- **Filtering & Sorting**: Use `parse_filter_string` and `parse_sort_string` from [job_tracker/utils.py](job_tracker/utils.py).
  - **Operators**: `==`, `!=`, `>=`, `<=`, `>`, `<`, `~` (substring), `:` (substring), `AND`, `OR`, and `col:[min-max]`.
- **LLM Integration**: `enrich_job_data` in [job_tracker/llm.py](job_tracker/llm.py) expects a specific JSON schema. `OPENAI_API_KEY` must be set in `.env`.

## Developer Workflows

- **Running the App**: `python -m job_tracker.main [COMMAND]`.
- **Adding Commands**: Create new file in [job_tracker/commands/](job_tracker/commands/), register in [job_tracker/main.py](job_tracker/main.py).
- **Adding Jobs**: The `add` command ([job_tracker/commands/add.py](job_tracker/commands/add.py)) supports a `--url` flag to trigger scraping and LLM enrichment.
- **Bulk Operations**: Use scripts in [scripts/](scripts/) (e.g., `bulk_add.py`) for processing multiple URLs from `bulk_urls.txt`.

## Integration Points

- **Google Calendar**: Events identified by `interview_event_id` in DB. Requires `credentials.json` and `token.json`.
- **OpenAI API**: Used for job data extraction and analysis.
- **LinkedIn**: Scraped for job details.
- **CSV Export**: `view` command supports `--export`.
- **User Profile**: [user_profile.md](user_profile.md) is read to personalize LLM analysis (fit/rating).
