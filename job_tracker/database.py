import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

DB_NAME = "jobs.db"
# Database lives in the project root
DB_PATH = Path(__file__).parent.parent / DB_NAME


@contextmanager
def get_db():
    """Context manager for database connection. Ensures connection is closed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def initialize_db():
    """Creates the jobs table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        company_url TEXT,
        company_linkedin TEXT,
        role_name TEXT,
        role_url TEXT,
        location TEXT,
        arrangement TEXT,
        type TEXT,
        level TEXT,
        source TEXT,
        recruiter_name TEXT,
        recruiter_email TEXT,
        recruiter_linkedin TEXT,
        expected_salary TEXT,
        notes TEXT,
        status TEXT DEFAULT 'applied',
        date_posted DATE,
        date_applied DATE,
        application_response_date DATE,
        interview_response_date DATE,
        interview_time DATETIME,
        interview_type TEXT,
        interview_link TEXT,
        interview_event_id TEXT,
        offer TEXT,
        rating INTEGER,
        fit INTEGER,
        feedback TEXT,
        application_method TEXT,
        followup_date DATE,
        calendar_event_id TEXT,
        followup_event_id TEXT
    );
    """
    with get_db() as conn:
        conn.execute(query)
        conn.commit()

    # Run migrations for existing databases
    run_migrations()


def run_migrations():
    """Handles schema updates for existing databases."""
    with get_db() as conn:
        # Check if interview_date exists and rename it to interview_time
        cursor = conn.execute("PRAGMA table_info(jobs)")
        columns = [row["name"] for row in cursor.fetchall()]

        if "interview_date" in columns and "interview_time" not in columns:
            try:
                conn.execute("ALTER TABLE jobs RENAME COLUMN interview_date TO interview_time")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add interview_link if it doesn't exist
        if "interview_link" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN interview_link TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add interview_event_id if it doesn't exist
        if "interview_event_id" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN interview_event_id TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add recruiter_linkedin if it doesn't exist
        if "recruiter_linkedin" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN recruiter_linkedin TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add expected_salary if it doesn't exist
        if "expected_salary" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN expected_salary TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add notes if it doesn't exist
        if "notes" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN notes TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add rating if it doesn't exist
        if "rating" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN rating INTEGER")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        # Add fit if it doesn't exist
        if "fit" not in columns:
            try:
                conn.execute("ALTER TABLE jobs ADD COLUMN fit INTEGER")
                conn.commit()
            except sqlite3.OperationalError:
                pass


def add_new_column(column_name: str, column_type: str, default_value: str = None):
    """Adds a new column to the jobs table dynamically."""
    # Basic validation to ensure column_name is alphanumeric/underscore
    if not column_name.replace("_", "").isalnum():
        raise ValueError("Invalid column name. Use only alphanumeric characters and underscores.")

    query = f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}"
    if default_value is not None:
        query += f" DEFAULT '{default_value}'"

    with get_db() as conn:
        try:
            conn.execute(query)
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column '{column_name}' already exists.")
            else:
                raise e


def add_job(job_data: dict) -> int:
    """Inserts a new job record and returns the new job ID."""
    columns = ", ".join(job_data.keys())
    placeholders = ", ".join(["?" for _ in job_data])
    query = f"INSERT INTO jobs ({columns}) VALUES ({placeholders})"

    with get_db() as conn:
        cursor = conn.execute(query, list(job_data.values()))
        conn.commit()
        return cursor.lastrowid


def update_job(job_id: int, updates: dict):
    """Updates specific fields of a job record."""
    if not updates:
        return

    set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
    query = f"UPDATE jobs SET {set_clause} WHERE id = ?"
    params = list(updates.values()) + [job_id]

    with get_db() as conn:
        conn.execute(query, params)
        conn.commit()


def update_ghosted_jobs():
    """Updates status to 'ghosted' for jobs applied > 30 days ago with status 'applied' and no responses."""
    query = """
    UPDATE jobs 
    SET status = 'ghosted' 
    WHERE status = 'applied' 
    AND date_applied <= date('now', '-30 days')
    AND application_response_date IS NULL
    AND interview_response_date IS NULL
    """
    with get_db() as conn:
        conn.execute(query)
        conn.commit()


def get_jobs(where_clause: str = None, params: list = None, sort_clause: str = None):
    """Retrieves jobs with dynamic filtering and sorting."""
    query = "SELECT * FROM jobs"

    if where_clause:
        query += f" WHERE {where_clause}"

    if sort_clause:
        query += f" ORDER BY {sort_clause}, id DESC"
    else:
        # Default sort by date applied descending, then id descending
        query += " ORDER BY date_applied DESC, id DESC"

    with get_db() as conn:
        return [dict(row) for row in conn.execute(query, params or []).fetchall()]


def get_job_by_id(job_id: int):
    """Retrieves a single job by its ID."""
    query = "SELECT * FROM jobs WHERE id = ?"
    with get_db() as conn:
        row = conn.execute(query, (job_id,)).fetchone()
        return dict(row) if row else None


def get_job_by_url(url: str):
    """Retrieves a single job by its role URL."""
    query = "SELECT * FROM jobs WHERE role_url = ?"
    with get_db() as conn:
        row = conn.execute(query, (url,)).fetchone()
        return dict(row) if row else None


def delete_job_by_id(job_id: int):
    """Deletes a single job by its ID."""
    query = "DELETE FROM jobs WHERE id = ?"
    with get_db() as conn:
        conn.execute(query, (job_id,))
        conn.commit()


if __name__ == "__main__":
    initialize_db()
    print(f"Database initialized at {DB_PATH}")
