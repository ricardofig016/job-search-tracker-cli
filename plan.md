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

- [x] Implement a function `add_new_column(column_name, column_type, default_value)` in `database.py`.
  - This allows adding columns dynamically as requested.
  - Logic: Execute `ALTER TABLE jobs ADD COLUMN {column_name} {column_type} DEFAULT {default_value}`.

### 2.3. CRUD Operations

- [x] Implement `add_job(job_data)`: Insert a new record.
- [x] Implement `update_job(job_id, updates)`: Update specific fields of a job.
- [x] Implement `get_jobs(filters, sort_by)`: Retrieve jobs with dynamic `WHERE` and `ORDER BY` clauses.
- [x] Implement `get_job_by_id(job_id)`: Retrieve a single job.
- [x] Implement `delete_job_by_id(job_id)`: Delete a single job.

## Phase 3: CLI Implementation - Core Functionalities

### 3.1. Main Entry Point

- [x] Setup `job_tracker/main.py` using `typer.Typer`.
- [x] Define the main callback to handle global flags if any.

### 3.2. Feature 1: Add New Jobs

- [x] Implement `add` command in `commands/add.py`.
- [x] Use `typer.prompt` to interactively ask for essential fields (Company, Role, Status).
- [x] Allow optional fields to be passed via flags or skipped.
- [x] Auto-fill `date_applied` with today's date if not provided.

### 3.3. Feature 2: Edit Existing Jobs

- [x] Implement `edit` command in `commands/edit.py`.
- [x] Arguments: `job_id`.
- [x] Logic:
  1. Fetch job by ID.
  2. Display current values.
  3. Prompt user for which field to update in a loop until users selects "done".
  4. Commit changes to DB.

### 3.4. Advanced Query and Filtering Engine

Implementing complex filtering via simple CLI flags can become unwieldy. We will implement a **Hybrid Query Approach**:

- **A "Query String" parser** for complex logic (e.g., `--filter "rating>=4 AND company~google"`).
- **Interactive Mode** (optional) if no arguments are provided to `view`.

#### Logic Implementation in `utils.py` & `database.py`:

- [x] **Filter Parser**: Create a utility to parse filter strings into SQL `WHERE` clauses.
  - **Operators**: `==`, `!=`, `>=`, `<=`, `>`, `<`.
  - **Substring**: Use `~` or `:` for `LIKE %value%`.
  - **Logic**: Support `AND` / `OR` keywords.
  - **Ranges**: Support `col:[min-max]` syntax.
- [x] **Multilevel Sort Parser**: Handle a list of sort instructions (e.g., `['date_applied:desc', 'rating:asc']`).
- [x] **Column Selector**: Implement a mapping of "short names" to DB columns to allow `--show company,role,status`.

### 3.5. Feature 3: Visualize Applications (`view`)

- [x] **Command Signature**: `view [QUERY] --filter TEXT --sort TEXT --show TEXT --hide TEXT --export --output FILENAME`.
- [x] **Filtering Logic**:
  - Combine positional `QUERY` and multiple `--filter` flags.
  - Default logic is `AND`, but allow `OR` within the query string.
- [x] **Sorting**: Support multiple `--sort` flags for multilevel sorting (e.g., `--sort date:desc --sort rating:desc`).
- [x] **Column Management**:
  - **Sensible Defaults**: ID, Company, Role, Status, Date Applied.
  - Use `--show` to add columns and `--hide` to remove them.
  - Use `--all` to show every column (useful for CSV export).
- [x] **Output**:
  - **Rich Table**: Use `rich.table` with dynamic columns based on selection.
  - **CSV Export**: Use `--export` (or `-e`) to enable export, and `--output` (or `-o`) to specify the filename (defaults to `output.csv`).

### 3.6. Feature 4: Statistics (`stats`)

- [ ] **Consistency**: Use the exact same `Filter Parser` as the `view` command.
- [ ] **Metrics**:
  - Calculate stats based on the _filtered_ subset of data.
  - Total count, success rate (Accepted/Total), average rating.
  - Grouped stats: Count by status, count by arrangement.
- [ ] **Visualization**: Use `rich.panel` or `rich.columns` for a clean dashboard view.

### 3.7. Feature 5: Delete Job (`delete`)

- [x] Implement `delete` command in `commands/delete.py`.
- [x] Arguments: `job_id`.
- [x] Logic:
  1. Fetch job by ID to verify existence.
  2. Prompt for confirmation.
  3. Delete from DB.

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
