# Implementation Plan: Job Search Tracker CLI

This document outlines the step-by-step implementation plan for the Job Search Tracker CLI tool. The tool will be built using Python and SQLite.

## Phase 1: Project Setup and Architecture

### 1.1. Environment Setup

- [x] Create a `requirements.txt` file.
  - **Dependencies**:
    - `typer`: For building the CLI interface (modern, easy to use).
    - `rich`: For beautiful console output (tables, colors).
    - `sqlite3`: Built-in Python library for database interactions.
- [x] Create the project structure:
  ```
  job-search-tracker/
  ├── job_tracker/
  │   ├── __init__.py
  │   ├── main.py          # CLI Entry point
  │   ├── database.py      # DB connection and schema management
  │   ├── models.py        # Data classes/types
  │   ├── commands/        # Command implementations
  │   │   ├── __init__.py
  │   │   ├── add.py
  │   │   ├── edit.py
  │   │   ├── view.py
  │   │   └── stats.py
  │   └── utils.py         # Helper functions (CSV export, formatting)
  ├── tests/
  ├── requirements.txt
  └── README.md
  ```

### 1.2. Database Design

- [x] Define the SQLite schema in `job_tracker/database.py`.
- [x] Implement a `initialize_db()` function to create the `jobs` table if it doesn't exist.
- **Table Schema (`jobs`)**:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `company_name`: TEXT
  - `company_url`: TEXT
  - `company_linkedin`: TEXT
  - `role_name`: TEXT
  - `role_url`: TEXT
  - `location`: TEXT
  - `arrangement`: TEXT (Enum: onsite, hybrid, remote)
  - `type`: TEXT (Enum: fulltime, contract, etc)
  - `level`: TEXT (Enum: internship, junior, mid level, senior)
  - `source`: TEXT (Enum: linkedin, company website)
  - `recruiter_name`: TEXT
  - `recruiter_email`: TEXT
  - `recruiter_linkedin`: TEXT
  - `expected_salary`: TEXT
  - `notes`: TEXT
  - `status`: TEXT (Enum: applied, rejected, accepted)
  - `date_posted`: DATE
  - `date_applied`: DATE
  - `followup_date`: DATE
  - `response_date`: DATE
  - `interview_date`: DATE
  - `interview_type`: TEXT
  - `offer`: TEXT
  - `rating`: INTEGER (1-5)
  - `fit`: INTEGER (1-5)
  - `feedback`: TEXT
  - `application_method`: TEXT

## Phase 2: Core Database Operations

### 2.1. Database Connection

- [x] Implement context manager for SQLite connection in `database.py`.

### 2.2. Schema Migration Support

- [ ] Implement a function `add_new_column(column_name, column_type, default_value)` in `database.py`.
  - This allows adding columns dynamically as requested.
  - Logic: Execute `ALTER TABLE jobs ADD COLUMN {column_name} {column_type} DEFAULT {default_value}`.

### 2.3. CRUD Operations

- [ ] Implement `add_job(job_data)`: Insert a new record.
- [ ] Implement `update_job(job_id, updates)`: Update specific fields of a job.
- [ ] Implement `get_jobs(filters, sort_by)`: Retrieve jobs with dynamic `WHERE` and `ORDER BY` clauses.
- [ ] Implement `get_job_by_id(job_id)`: Retrieve a single job.

## Phase 3: CLI Implementation - Core Functionalities

### 3.1. Main Entry Point

- [ ] Setup `job_tracker/main.py` using `typer.Typer`.
- [ ] Define the main callback to handle global flags if any.

### 3.2. Feature 1: Add New Jobs

- [ ] Implement `add` command in `commands/add.py`.
- [ ] Use `typer.prompt` to interactively ask for essential fields (Company, Role, Status).
- [ ] Allow optional fields to be passed via flags or skipped.
- [ ] Auto-fill `date_applied` with today's date if not provided.

### 3.3. Feature 2: Edit Existing Jobs

- [ ] Implement `edit` command in `commands/edit.py`.
- [ ] Arguments: `job_id`.
- [ ] Logic:
  1. Fetch job by ID.
  2. Display current values.
  3. Prompt user for which field to update or accept flags for updates (e.g., `--status rejected`).
  4. Commit changes to DB.

### 3.4. Feature 3: Visualize Applications

- [ ] Implement `list` (or `view`) command in `commands/view.py`.
- [ ] **Filtering**: Add flags like `--status`, `--company`, `--date-applied`.
- [ ] **Sorting**: Add `--sort` flag (e.g., `date_applied`, `rating`).
- [ ] **Output Modes**:
  - **Console**: Use `rich.table.Table` to display data nicely. Truncate long text.
  - **CSV**: Add `--export-csv [filename]` flag. Use Python's `csv` module to write the query results to a file.

### 3.5. Feature 4: Statistics

- [ ] Implement `stats` command in `commands/stats.py`.
- [ ] **Filtering**: Allow same filters as `view` (e.g., stats for "remote" jobs only).
- [ ] **Metrics to calculate**:
  - Total applications.
  - Breakdown by Status (Applied vs Rejected vs Accepted).
  - Breakdown by Arrangement (Remote/Hybrid/Onsite).
  - Average Rating/Fit.
  - Applications per week/month.
- [ ] Display results using `rich` panels or simple text.

## Phase 4: Advanced Features & Polish

### 4.1. Dynamic Column Management (CLI)

- [ ] Add a `config` command group.
- [ ] Implement `config add-column --name [name] --type [type] --default [value]`.
  - Connects to the schema migration function defined in Phase 2.2.

### 4.2. Refinement

- [ ] Add error handling (e.g., invalid dates, ID not found).
- [ ] Ensure Enums are validated (e.g., Status must be one of applied/rejected/accepted).
- [ ] Add `--help` documentation for all commands.

## Phase 5: Testing and Verification

- [ ] Manual testing of the workflow:
  1. Initialize DB.
  2. Add a job.
  3. View the job list.
  4. Edit the job status.
  5. View stats.
  6. Add a new column (e.g., `referral_bonus`).
  7. Export to CSV.
