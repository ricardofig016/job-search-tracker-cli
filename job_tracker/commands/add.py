import typer
import click
from datetime import date, timedelta
from rich.console import Console
from job_tracker.database import add_job, update_job
from job_tracker.models import Arrangement, JobType, ExperienceLevel, Source, Status
from job_tracker.utils import validate_date, validate_datetime
from job_tracker.calendar_utils import sync_event

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
    job_data["arrangement"] = typer.prompt("Arrangement", default=Arrangement.REMOTE.value, type=click.Choice([e.value for e in Arrangement]))
    job_data["type"] = typer.prompt("Job Type", default=JobType.FULLTIME.value, type=click.Choice([e.value for e in JobType]))
    job_data["level"] = typer.prompt("Experience Level", default=ExperienceLevel.MID_LEVEL.value, type=click.Choice([e.value for e in ExperienceLevel]))
    job_data["source"] = typer.prompt("Source", default=Source.LINKEDIN.value, type=click.Choice([e.value for e in Source]))
    job_data["location"] = typer.prompt("Location (e.g., City, Country)", default="", show_default=False)

    # Recruiter
    job_data["recruiter_name"] = typer.prompt("Recruiter Name", default="", show_default=False)
    job_data["recruiter_email"] = typer.prompt("Recruiter Email", default="", show_default=False)
    job_data["recruiter_linkedin"] = typer.prompt("Recruiter LinkedIn URL", default="", show_default=False)

    # Compensation & Notes
    job_data["expected_salary"] = typer.prompt("Expected Salary", default="", show_default=False)
    job_data["notes"] = typer.prompt("Notes", default="", show_default=False)

    # Status & Dates
    job_data["status"] = typer.prompt("Status", default=Status.APPLIED.value, type=click.Choice([e.value for e in Status]))

    while True:
        date_posted = typer.prompt("Date Posted (YYYY-MM-DD)", default="", show_default=False)
        if validate_date(date_posted):
            job_data["date_posted"] = date_posted
            break
        console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")

    while True:
        date_applied_str = typer.prompt("Date Applied (YYYY-MM-DD)", default=date.today().isoformat())
        if validate_date(date_applied_str):
            job_data["date_applied"] = date_applied_str
            break
        console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")

    # Calculate default follow-up date (10 days after applied date)
    try:
        applied_dt = date.fromisoformat(job_data["date_applied"])
        default_followup = (applied_dt + timedelta(days=10)).isoformat()
    except (ValueError, TypeError):
        default_followup = ""

    while True:
        followup_date = typer.prompt("Follow-up Date (YYYY-MM-DD)", default=default_followup)
        if validate_date(followup_date):
            job_data["followup_date"] = followup_date
            break
        console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")

    while True:
        response_date = typer.prompt("Response Date (YYYY-MM-DD)", default="", show_default=False)
        if validate_date(response_date):
            job_data["response_date"] = response_date
            break
        console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")

    # Interview
    while True:
        interview_time = typer.prompt("Interview Time (YYYY-MM-DD HH:MM)", default="", show_default=False)
        if validate_datetime(interview_time):
            job_data["interview_time"] = interview_time
            break
        console.print("[bold red]Error:[/bold red] Invalid format. Please use YYYY-MM-DD HH:MM.")

    job_data["interview_type"] = typer.prompt("Interview Type", default="", show_default=False)
    job_data["interview_link"] = typer.prompt("Interview Link (Meeting URL)", default="", show_default=False)
    job_data["offer"] = typer.prompt("Offer Details", default="", show_default=False)

    # Ratings
    while True:
        rating = typer.prompt("Job Rating (1-5)", default=0, type=int)
        if 0 <= rating <= 5:
            job_data["rating"] = rating
            break
        console.print("[bold red]Error:[/bold red] Rating must be between 1 and 5 (or 0 to skip).")

    while True:
        fit = typer.prompt("Job Fit (1-5)", default=0, type=int)
        if 0 <= fit <= 5:
            job_data["fit"] = fit
            break
        console.print("[bold red]Error:[/bold red] Fit must be between 1 and 5 (or 0 to skip).")

    job_data["feedback"] = typer.prompt("Feedback", default="", show_default=False)
    job_data["application_method"] = typer.prompt("Application Method", default="", show_default=False)

    # Clean up empty strings for optional fields (convert to None for DB)
    final_data = {k: (v if v != "" else None) for k, v in job_data.items()}
    # Handle 0 for rating/fit as None if not provided
    if final_data.get("rating") == 0:
        final_data["rating"] = None
    if final_data.get("fit") == 0:
        final_data["fit"] = None

    try:
        job_id = add_job(final_data)
        console.print(f"\n[bold green]Success![/bold green] Job application added with ID: [cyan]{job_id}[/cyan]")

        # Sync with Google Calendar
        calendar_updates = {}
        if final_data.get("followup_date"):
            console.print("[dim]Syncing follow-up with Google Calendar...[/dim]")
            f_id = sync_event(final_data, "followup")
            if f_id:
                calendar_updates["followup_event_id"] = f_id

        if final_data.get("interview_time"):
            console.print("[dim]Syncing interview with Google Calendar...[/dim]")
            i_id = sync_event(final_data, "interview")
            if i_id:
                calendar_updates["interview_event_id"] = i_id

        if calendar_updates:
            update_job(job_id, calendar_updates)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] Could not add job. {e}")
