import typer
import csv
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from job_tracker.database import get_jobs
from job_tracker.utils import parse_filter_string, parse_sort_string, get_visible_columns, COLUMN_MAPPING

console = Console()


def view(
    query: Optional[str] = typer.Argument(None, help="Optional query string for filtering (e.g., 'company~google')"),
    filter: Optional[List[str]] = typer.Option(None, "--filter", "-f", help="Filter strings (e.g., 'rating>=4')"),
    sort: Optional[List[str]] = typer.Option(None, "--sort", "-s", help="Sort instructions (e.g., 'date:desc'). Default is 'date:desc, id:desc'."),
    show: Optional[str] = typer.Option(None, "--show", help="Comma-separated list of columns to show"),
    hide: Optional[str] = typer.Option(None, "--hide", help="Comma-separated list of columns to hide"),
    all: bool = typer.Option(False, "--all", help="Show all columns"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of results to display"),
    export: bool = typer.Option(False, "--export", "-e", help="Export results to a CSV file"),
    output: str = typer.Option("output.csv", "--output", "-o", help="Filename for the exported CSV"),
):
    """
    View and filter job applications.
    """
    # 1. Combine filters
    all_filters = []
    if query:
        all_filters.append(query)
    if filter:
        all_filters.extend(filter)

    combined_filter_str = " AND ".join(all_filters)
    where_clause, params = parse_filter_string(combined_filter_str)

    # 2. Parse sorting
    sort_clause = parse_sort_string(sort) if sort else None

    # 3. Fetch data
    try:
        jobs = get_jobs(where_clause=where_clause, params=params, sort_clause=sort_clause, limit=limit)
    except Exception as e:
        console.print(f"[bold red]Error fetching jobs:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not jobs:
        console.print("[yellow]No jobs found matching your criteria.[/yellow]")
        return

    # 4. Determine visible columns
    visible_col_keys = get_visible_columns(show=show, hide=hide, all_cols=all)

    # 5. Handle CSV Export
    if export:
        try:
            with open(output, mode="w", newline="", encoding="utf-8") as f:
                # Use all columns for CSV export if not specified otherwise
                fieldnames = [COLUMN_MAPPING[k] for k in visible_col_keys]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for job in jobs:
                    # Filter job dict to only include visible columns
                    row = {COLUMN_MAPPING[k]: job[COLUMN_MAPPING[k]] for k in visible_col_keys}
                    writer.writerow(row)
            console.print(f"[bold green]Success![/bold green] Exported {len(jobs)} jobs to [cyan]{output}[/cyan]")
        except Exception as e:
            console.print(f"[bold red]Error exporting to CSV:[/bold red] {e}")
            raise typer.Exit(code=1)

    # 6. Display Table
    table = Table(title="Job Applications", row_styles=["", "on grey7"], padding=(1, 1))

    for key in visible_col_keys:
        table.add_column(key.replace("_", " ").title(), style="cyan")

    for job in jobs:
        row_data = []
        for key in visible_col_keys:
            val = job.get(COLUMN_MAPPING[key])
            display_val = str(val) if val is not None else ""

            # Truncate long values (like transcripts) in the table
            if len(display_val) > 100:
                display_val = display_val[:97] + "..."

            # Add clickable links for company and role if URLs exist
            if key == "company":
                link_url = job.get("company_url") or job.get("company_linkedin")
                if link_url:
                    display_val = f"[link={link_url}]{display_val}[/link]"
            elif key == "role" and job.get("role_url"):
                display_val = f"[link={job['role_url']}]{display_val}[/link]"
            elif key == "company_linkedin" and job.get("company_linkedin"):
                display_val = f"[link={job['company_linkedin']}]{display_val}[/link]"
            elif key == "recruiter_linkedin" and job.get("recruiter_linkedin"):
                display_val = f"[link={job['recruiter_linkedin']}]{display_val}[/link]"
            elif key == "interview_link" and job.get("interview_link"):
                display_val = f"[link={job['interview_link']}]{display_val}[/link]"

            row_data.append(display_val)
        table.add_row(*row_data)

    console.print(table)
    console.print(f"\n[dim]Showing {len(jobs)} applications.[/dim]")
