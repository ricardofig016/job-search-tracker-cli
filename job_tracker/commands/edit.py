import typer
from rich.console import Console
from rich.table import Table
from job_tracker.database import get_job_by_id, update_job

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

        # Prompt for new value
        new_value = typer.prompt(f"Enter new value for {field_to_edit}", default=str(job[field_to_edit]) if job[field_to_edit] is not None else "")

        # Handle numeric fields
        if field_to_edit in ["rating", "fit"]:
            try:
                updates[field_to_edit] = int(new_value) if new_value != "" else None
            except ValueError:
                console.print("[bold red]Error:[/bold red] Rating and Fit must be integers.")
        else:
            updates[field_to_edit] = new_value if new_value != "" else None

    if updates:
        try:
            update_job(job_id, updates)
            console.print(f"[bold green]Success![/bold green] Job {job_id} updated.")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Could not update job. {e}")
    else:
        console.print("No changes made.")
