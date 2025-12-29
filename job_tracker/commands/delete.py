import typer
from rich.console import Console
from job_tracker.database import get_job_by_id, delete_job_by_id

console = Console()


def delete(job_id: int = typer.Argument(..., help="The ID of the job application to delete")):
    """
    Delete a job application by its ID.
    """
    # 1. Check if job exists
    job = get_job_by_id(job_id)
    if not job:
        console.print(f"[bold red]Error:[/bold red] Job with ID [cyan]{job_id}[/cyan] not found.")
        raise typer.Exit(code=1)

    # 2. Confirm deletion
    confirm = typer.confirm(f"Are you sure you want to delete the application for {job['company_name']} ({job['role_name']})?")

    if not confirm:
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return

    # 3. Perform deletion
    try:
        delete_job_by_id(job_id)
        console.print(f"[bold green]Success![/bold green] Job application [cyan]{job_id}[/cyan] has been deleted.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not delete job. {e}")
        raise typer.Exit(code=1)
