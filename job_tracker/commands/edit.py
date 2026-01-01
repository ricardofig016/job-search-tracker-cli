import typer
from rich.console import Console
from rich.table import Table
from job_tracker.database import get_job_by_id, update_job
from job_tracker.models import Arrangement, JobType, ExperienceLevel, Source, Status
from job_tracker.utils import validate_date, validate_datetime

console = Console()


def edit(job_id: int = typer.Argument(..., help="The ID of the job to edit.")):
    """Edit an existing job application interactively."""
    job = get_job_by_id(job_id)

    if not job:
        console.print(f"[bold red]Error:[/bold red] Job with ID {job_id} not found.")
        raise typer.Exit(1)

    console.print(f"[bold blue]Editing Job ID: {job_id}[/bold blue]")

    updates = {}

    # List of editable fields (excluding ID)
    fields = [k for k in job.keys() if k != "id"]

    # Map fields to their respective Enum classes for validation
    enum_fields = {"arrangement": Arrangement, "type": JobType, "level": ExperienceLevel, "source": Source, "status": Status}

    date_fields = ["date_posted", "date_applied", "followup_date", "response_date"]
    datetime_fields = ["interview_time"]

    while True:
        # Display current state of the job (including pending updates)
        table = Table(title=f"Current Values for Job {job_id}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        for field in fields:
            is_updated = field in updates
            current_val = updates.get(field, job[field])
            val_str = str(current_val) if current_val is not None else ""

            if is_updated:
                table.add_row(field, f"[bold green]{val_str}[/bold green]")
            else:
                table.add_row(field, val_str)

        console.print(table)

        # Prompt for field to edit
        field_to_edit = typer.prompt("\nEnter the field name to edit (or type 'done' to save, 'cancel' to exit)", default="done").lower()

        if field_to_edit == "done":
            break
        if field_to_edit == "cancel":
            console.print("[yellow]Edit cancelled.[/yellow]")
            raise typer.Exit()

        if field_to_edit not in fields:
            console.print(f"[bold red]Error:[/bold red] '{field_to_edit}' is not a valid field.")
            continue

        # Prompt for new value with validation
        if field_to_edit in enum_fields:
            enum_cls = enum_fields[field_to_edit]
            new_value = typer.prompt(f"Enter new value for {field_to_edit}", default=str(job[field_to_edit]) if job[field_to_edit] is not None else "", type=typer.Choice([e.value for e in enum_cls]))
            updates[field_to_edit] = new_value
        elif field_to_edit in date_fields:
            while True:
                new_value = typer.prompt(f"Enter new value for {field_to_edit} (YYYY-MM-DD)", default=str(job[field_to_edit]) if job[field_to_edit] is not None else "")
                if validate_date(new_value):
                    updates[field_to_edit] = new_value if new_value != "" else None
                    break
                console.print("[bold red]Error:[/bold red] Invalid date format. Please use YYYY-MM-DD.")
        elif field_to_edit in datetime_fields:
            while True:
                new_value = typer.prompt(f"Enter new value for {field_to_edit} (YYYY-MM-DD HH:MM)", default=str(job[field_to_edit]) if job[field_to_edit] is not None else "")
                if validate_datetime(new_value):
                    updates[field_to_edit] = new_value if new_value != "" else None
                    break
                console.print("[bold red]Error:[/bold red] Invalid format. Please use YYYY-MM-DD HH:MM.")
        elif field_to_edit in ["rating", "fit"]:
            while True:
                new_value = typer.prompt(f"Enter new value for {field_to_edit} (1-5)", default=str(job[field_to_edit]) if job[field_to_edit] is not None else "")
                if new_value == "":
                    updates[field_to_edit] = None
                    break
                try:
                    val = int(new_value)
                    if 1 <= val <= 5:
                        updates[field_to_edit] = val
                        break
                    console.print("[bold red]Error:[/bold red] Value must be between 1 and 5.")
                except ValueError:
                    console.print("[bold red]Error:[/bold red] Value must be an integer.")
        else:
            new_value = typer.prompt(f"Enter new value for {field_to_edit}", default=str(job[field_to_edit]) if job[field_to_edit] is not None else "")
            updates[field_to_edit] = new_value if new_value != "" else None

    if updates:
        try:
            update_job(job_id, updates)
            console.print(f"[bold green]Success![/bold green] Job {job_id} updated.")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Could not update job. {e}")
    else:
        console.print("No changes made.")
