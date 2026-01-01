import typer
from rich.console import Console
from job_tracker.database import add_new_column

console = Console()
app = typer.Typer(help="Manage configuration and database schema.")


@app.command(name="add-column")
def add_column(
    name: str = typer.Option(..., "--name", "-n", help="The name of the new column."),
    type: str = typer.Option("TEXT", "--type", "-t", help="The SQLite data type (e.g., TEXT, INTEGER, DATE)."),
    default: str = typer.Option(None, "--default", "-d", help="The default value for the new column."),
):
    """
    Add a new column to the jobs table dynamically.
    """
    try:
        add_new_column(name, type, default)
        console.print(f"[bold green]Success![/bold green] Column '[cyan]{name}[/cyan]' added to the database.")
        console.print("[yellow]Note:[/yellow] You may need to update 'job_tracker/utils.py' to make this column visible in the 'view' command.")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Could not add column. {e}")
        raise typer.Exit(1)
