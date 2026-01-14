import typer
from rich.console import Console
from job_tracker.database import get_job_by_id, update_job
from job_tracker.utils import is_null_string
from pathlib import Path

console = Console()


def transcript(job_id: int = typer.Argument(..., help="The ID of the job to associate the transcript with."), file: Path = typer.Option(None, "--file", "-f", help="Path to the transcript text file."), view: bool = typer.Option(False, "--view", "-v", help="View the current transcript."), clear: bool = typer.Option(False, "--clear", help="Clear the transcript.")):
    """Store or view interview transcripts for a job."""
    job = get_job_by_id(job_id)

    if not job:
        console.print(f"[bold red]Error:[/bold red] Job with ID {job_id} not found.")
        raise typer.Exit(1)

    if clear:
        if typer.confirm(f"Are you sure you want to clear the transcript for job {job_id}?"):
            update_job(job_id, {"interview_transcript": None})
            console.print(f"[bold green]Success![/bold green] Transcript cleared for job {job_id}.")
        return

    if view:
        current_transcript = job.get("interview_transcript")
        if not current_transcript:
            console.print(f"[yellow]No transcript found for job {job_id}.[/yellow]")
        else:
            console.print(f"[bold blue]Transcript for Job {job_id} ({job['company_name']} - {job['role_name']})[/bold blue]")
            console.print("-" * 40)
            console.print(current_transcript)
            console.print("-" * 40)
        return

    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File {file} not found.")
            raise typer.Exit(1)

        try:
            content = file.read_text(encoding="utf-8")
            update_job(job_id, {"interview_transcript": content})
            console.print(f"[bold green]Success![/bold green] Transcript from {file.name} saved for job {job_id}.")
        except Exception as e:
            console.print(f"[bold red]Error reading file:[/bold red] {e}")
            raise typer.Exit(1)
        return

    # If no options provided, prompt for input or file path
    console.print(f"[bold blue]Managing Transcript for Job {job_id}[/bold blue]")
    choice = typer.prompt("How would you like to enter the transcript? (file/text/cancel)", default="file").lower()

    if choice == "file":
        file_path_str = typer.prompt("Enter the path to the transcript file")
        file_path = Path(file_path_str)
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File {file_path} not found.")
        else:
            try:
                content = file_path.read_text(encoding="utf-8")
                update_job(job_id, {"interview_transcript": content})
                console.print(f"[bold green]Success![/bold green] Transcript saved.")
            except Exception as e:
                console.print(f"[bold red]Error reading file:[/bold red] {e}")
    elif choice == "text":
        console.print("Paste your transcript below (Ctrl-Z/Ctrl-D on a new line and Enter to save):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        content = "\n".join(lines).strip()
        if content:
            update_job(job_id, {"interview_transcript": content})
            console.print(f"[bold green]Success![/bold green] Transcript saved.")
        else:
            console.print("[yellow]Empty transcript. Nothing saved.[/yellow]")
    else:
        console.print("Cancelled.")
