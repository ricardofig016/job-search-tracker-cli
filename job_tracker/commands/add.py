import typer
from datetime import date, timedelta
from rich.console import Console
from job_tracker.database import add_job

console = Console()


def add():
    """Add a new job application by answering a series of prompts."""
    console.print("[bold blue]Add New Job Application[/bold blue]")
    console.print("Please provide the following details (press Enter to skip optional fields):\n")

    job_data = {}

    # Essential Fields
    job_data["company_name"] = typer.prompt("Company Name")
    job_data["role_name"] = typer.prompt("Role Name")

    # URLs
    job_data["company_url"] = typer.prompt("Company Website URL", default="", show_default=False)
    job_data["company_linkedin"] = typer.prompt("Company LinkedIn URL", default="", show_default=False)
    job_data["role_url"] = typer.prompt("Job Posting URL", default="", show_default=False)

    # Details
    job_data["location"] = typer.prompt("Location (e.g., City, Country)", default="", show_default=False)
    job_data["arrangement"] = typer.prompt("Arrangement (onsite, hybrid, remote)", default="remote")
    job_data["type"] = typer.prompt("Job Type (fulltime, contract, part-time, freelance)", default="fulltime")
    job_data["level"] = typer.prompt("Experience Level (internship, junior, mid level, senior, lead, manager)", default="mid level")
    job_data["source"] = typer.prompt("Source (linkedin, company website, indeed, glassdoor, referral, other)", default="linkedin")

    # Recruiter
    job_data["recruiter_name"] = typer.prompt("Recruiter Name", default="", show_default=False)
    job_data["recruiter_email"] = typer.prompt("Recruiter Email", default="", show_default=False)
    job_data["recruiter_linkedin"] = typer.prompt("Recruiter LinkedIn URL", default="", show_default=False)

    # Compensation & Notes
    job_data["expected_salary"] = typer.prompt("Expected Salary", default="", show_default=False)
    job_data["notes"] = typer.prompt("Notes", default="", show_default=False)

    # Status & Dates
    job_data["status"] = typer.prompt("Status (applied, rejected, accepted, interviewing, offered)", default="applied")
    job_data["date_posted"] = typer.prompt("Date Posted (YYYY-MM-DD)", default="", show_default=False)

    date_applied_str = typer.prompt("Date Applied (YYYY-MM-DD)", default=date.today().isoformat())
    job_data["date_applied"] = date_applied_str

    # Calculate default follow-up date (10 days after applied date)
    try:
        applied_dt = date.fromisoformat(date_applied_str)
        default_followup = (applied_dt + timedelta(days=10)).isoformat()
    except ValueError:
        default_followup = ""

    job_data["followup_date"] = typer.prompt("Follow-up Date (YYYY-MM-DD)", default=default_followup)
    job_data["response_date"] = typer.prompt("Response Date (YYYY-MM-DD)", default="", show_default=False)

    # Interview
    job_data["interview_date"] = typer.prompt("Interview Date (YYYY-MM-DD)", default="", show_default=False)
    job_data["interview_type"] = typer.prompt("Interview Type", default="", show_default=False)
    job_data["offer"] = typer.prompt("Offer Details", default="", show_default=False)

    # Ratings
    job_data["rating"] = typer.prompt("Job Rating (1-5)", default=0, type=int)
    job_data["fit"] = typer.prompt("Job Fit (1-5)", default=0, type=int)
    job_data["feedback"] = typer.prompt("Feedback", default="", show_default=False)
    job_data["application_method"] = typer.prompt("Application Method", default="", show_default=False)

    # Clean up empty strings for optional fields (convert to None for DB)
    final_data = {k: (v if v != "" else None) for k, v in job_data.items()}
    # Handle 0 for rating/fit as None if not provided
    if final_data["rating"] == 0:
        final_data["rating"] = None
    if final_data["fit"] == 0:
        final_data["fit"] = None

    try:
        job_id = add_job(final_data)
        console.print(f"\n[bold green]Success![/bold green] Job application added with ID: [cyan]{job_id}[/cyan]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] Could not add job. {e}")
