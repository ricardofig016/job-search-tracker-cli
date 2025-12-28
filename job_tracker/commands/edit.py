import typer

def edit(job_id: int = typer.Argument(..., help="The ID of the job to edit.")):
    """Edit an existing job application."""
    typer.echo(f"Editing job {job_id}...")
