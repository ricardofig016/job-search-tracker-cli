import typer
from job_tracker.database import initialize_db, update_ghosted_jobs
from job_tracker.commands import add, edit, view, delete, stats, config, transcript

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
app.command(name="transcript")(transcript.transcript)

# Add command groups
app.add_typer(config.app, name="config")


@app.callback()
def main():
    """
    Initialize the application.
    """
    initialize_db()
    update_ghosted_jobs()


if __name__ == "__main__":
    app()
