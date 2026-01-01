import typer
from job_tracker.database import initialize_db
from job_tracker.commands import add, edit, view, delete, stats, config

app = typer.Typer(
    help="Job Search Tracker CLI Application",
    add_completion=False,
)

# Add subcommands
app.command(name="add")(add.add)
app.command(name="edit")(edit.edit)
app.command(name="view")(view.view)
app.command(name="delete")(delete.delete)
app.command(name="stats")(stats.stats)

# Add command groups
app.add_typer(config.app, name="config")


@app.callback()
def main():
    """
    Initialize the application.
    """
    initialize_db()


if __name__ == "__main__":
    app()
