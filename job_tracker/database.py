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
        company_name TEXT NOT NULL,
        company_url TEXT,
        company_linkedin TEXT,
        role_name TEXT NOT NULL,
        role_url TEXT,
        location TEXT,
        arrangement TEXT CHECK(arrangement IN ('onsite', 'hybrid', 'remote')),
        type TEXT CHECK(type IN ('fulltime', 'contract', 'part-time', 'freelance')),
        level TEXT CHECK(level IN ('internship', 'junior', 'mid level', 'senior', 'lead', 'manager')),
        source TEXT CHECK(source IN ('linkedin', 'company website', 'indeed', 'glassdoor', 'referral', 'other')),
        recruiter_name TEXT,
        recruiter_email TEXT,
        recruiter_linkedin TEXT,
        expected_salary TEXT,
        notes TEXT,
        status TEXT DEFAULT 'applied' CHECK(status IN ('applied', 'rejected', 'accepted', 'interviewing', 'offered')),
        date_posted DATE,
        date_applied DATE,
        followup_date DATE,
        response_date DATE,
        interview_date DATE,
        interview_type TEXT,
        offer TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        fit INTEGER CHECK(fit >= 1 AND fit <= 5),
        feedback TEXT,
        application_method TEXT
    );
    """
    with get_db() as conn:
        conn.execute(query)
        conn.commit()


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


if __name__ == "__main__":
    initialize_db()
    print(f"Database initialized at {DB_PATH}")
