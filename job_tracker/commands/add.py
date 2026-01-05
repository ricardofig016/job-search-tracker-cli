import typer
import click
from datetime import date, timedelta
from rich.console import Console
from job_tracker.database import add_job, update_job, get_job_by_url
from job_tracker.models import Arrangement, JobType, ExperienceLevel, Source, Status
from job_tracker.utils import validate_date, validate_datetime
from pathlib import Path

console = Console()


def add(url: str = typer.Option(None, "--url", help="LinkedIn job post URL")):
    """Add a new job application by answering a series of prompts."""

    console.print("[bold blue]Add New Job Application[/bold blue]")

    if url:
        # Check if job already exists
        existing_job = get_job_by_url(url)
        if existing_job:
            console.print(f"[bold yellow]Warning:[/bold yellow] A job with this URL already exists in the database.")
            console.print(f"ID: [cyan]{existing_job['id']}[/cyan] | Company: [bold]{existing_job['company_name']}[/bold] | Role: [bold]{existing_job['role_name']}[/bold]")
            raise typer.Exit()

    # Lazy import to improve startup time
    from job_tracker import scraper, llm

    scraped_data = {}
    if url:
        try:
            with console.status("[bold green]Fetching job details from LinkedIn...[/bold green]"):
                html = scraper.fetch_job_page(url)
                html_data = scraper.extract_html_data(html)

                # Load user profile
                profile_path = Path("user_profile.md")
                if profile_path.exists():
                    user_profile = profile_path.read_text(encoding="utf-8")
                else:
                    console.print("[yellow]Warning: user_profile.md not found. Fit and Rating might be inaccurate.[/yellow]")
                    user_profile = ""

                llm_data = llm.enrich_job_data(html_data, user_profile)

                # Merge data (LLM overrides HTML if needed, but usually fills gaps)
                scraped_data = {**html_data, **llm_data}
                scraped_data["role_url"] = url
                scraped_data["source"] = Source.LINKEDIN.value

                console.print("[green]Successfully extracted data![/green]")

        except Exception as e:
            console.print(f"[bold red]Error scraping URL:[/bold red] {e}")
            console.print("Proceeding with manual entry...")

    console.print("Please provide the following details (press Enter to skip optional fields):\n")

    job_data = {}

    # Essential Fields
    job_data["company_name"] = typer.prompt("Company Name", default=scraped_data.get("company_name") or "")
    job_data["role_name"] = typer.prompt("Role Name", default=scraped_data.get("role_name") or "")

    # URLs
    job_data["company_url"] = typer.prompt("Company Website URL", default=scraped_data.get("company_url") or "")
    job_data["company_linkedin"] = typer.prompt("Company LinkedIn URL", default=scraped_data.get("company_linkedin") or "")
    job_data["role_url"] = typer.prompt("Job Posting URL", default=scraped_data.get("role_url") or "")

    # Details
    # Helper to safely get enum default
    def get_enum_default(field, enum_cls):
        val = scraped_data.get(field)
        if val and val in [e.value for e in enum_cls]:
            return val
        return enum_cls(list(enum_cls)[0]).value  # Default to first item if not found/invalid

    job_data["arrangement"] = typer.prompt("Arrangement", default=scraped_data.get("arrangement") or Arrangement.REMOTE.value, type=click.Choice([e.value for e in Arrangement]))
    job_data["type"] = typer.prompt("Job Type", default=scraped_data.get("type") or JobType.FULLTIME.value, type=click.Choice([e.value for e in JobType]))
    job_data["level"] = typer.prompt("Experience Level", default=scraped_data.get("level") or ExperienceLevel.MID_LEVEL.value, type=click.Choice([e.value for e in ExperienceLevel]))
    job_data["source"] = typer.prompt("Source", default=scraped_data.get("source") or Source.LINKEDIN.value, type=click.Choice([e.value for e in Source]))
    job_data["location"] = typer.prompt("Location (e.g., City, Country)", default=scraped_data.get("location") or "")

    # Recruiter
    job_data["recruiter_name"] = typer.prompt("Recruiter Name", default=scraped_data.get("recruiter_name") or "")
    job_data["recruiter_email"] = typer.prompt("Recruiter Email", default=scraped_data.get("recruiter_email") or "")
    job_data["recruiter_linkedin"] = typer.prompt("Recruiter LinkedIn URL", default=scraped_data.get("recruiter_linkedin") or "")

    # Compensation & Notes
    job_data["expected_salary"] = typer.prompt("Expected Salary", default=scraped_data.get("expected_salary") or "")
    job_data["notes"] = typer.prompt("Notes", default=scraped_data.get("notes") or "")

    # Status & Dates
    job_data["status"] = typer.prompt("Status", default=Status.APPLIED.value, type=click.Choice([e.value for e in Status]))

    while True:
        date_posted = typer.prompt("Date Posted (YYYY-MM-DD)", default=scraped_data.get("date_posted") or "")
        if not date_posted:  # Allow empty
            break
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

    while True:
        response_date = typer.prompt("Response Date (YYYY-MM-DD)", default="")
        if validate_date(response_date):
            job_data["response_date"] = response_date
            break
        console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")

    # Interview
    while True:
        interview_time = typer.prompt("Interview Time (YYYY-MM-DD HH:MM)", default="")
        if validate_datetime(interview_time):
            job_data["interview_time"] = interview_time
            break
        console.print("[bold red]Error:[/bold red] Invalid format. Please use YYYY-MM-DD HH:MM.")

    job_data["interview_type"] = typer.prompt("Interview Type", default="")
    job_data["interview_link"] = typer.prompt("Interview Link (Meeting URL)", default="")
    job_data["offer"] = typer.prompt("Offer Details", default="")

    # Ratings
    while True:
        rating = typer.prompt("Job Rating (1-5)", default=scraped_data.get("rating") or 0, type=int)
        if 0 <= rating <= 5:
            job_data["rating"] = rating
            break
        console.print("[bold red]Error:[/bold red] Rating must be between 1 and 5 (or 0 to skip).")

    while True:
        fit = typer.prompt("Job Fit (1-5)", default=scraped_data.get("fit") or 0, type=int)
        if 0 <= fit <= 5:
            job_data["fit"] = fit
            break
        console.print("[bold red]Error:[/bold red] Fit must be between 1 and 5 (or 0 to skip).")

    job_data["feedback"] = typer.prompt("Feedback", default="")
    job_data["application_method"] = typer.prompt("Application Method", default="easy apply")

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
        from job_tracker.calendar_utils import sync_event

        calendar_updates = {}
        if final_data.get("interview_time"):
            console.print("[dim]Syncing interview with Google Calendar...[/dim]")
            i_id = sync_event(final_data, "interview")
            if i_id:
                calendar_updates["interview_event_id"] = i_id

        if calendar_updates:
            update_job(job_id, calendar_updates)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] Could not add job. {e}")
