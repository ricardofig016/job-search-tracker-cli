import typer
from typing import List, Optional
from datetime import datetime
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from job_tracker.database import get_jobs
from job_tracker.utils import parse_filter_string

console = Console()


def stats(
    query: Optional[str] = typer.Argument(None, help="Optional query string for filtering (e.g., 'company~google')"),
    filter: Optional[List[str]] = typer.Option(None, "--filter", "-f", help="Filter strings (e.g., 'rating>=4')"),
):
    """
    View insightful job application statistics.
    """
    # 1. Combine filters
    all_filters = []
    if query:
        all_filters.append(query)
    if filter:
        all_filters.extend(filter)

    combined_filter_str = " AND ".join(all_filters)
    where_clause, params = parse_filter_string(combined_filter_str)

    # 2. Fetch data
    try:
        jobs = get_jobs(where_clause=where_clause, params=params)
    except Exception as e:
        console.print(f"[bold red]Error fetching jobs:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not jobs:
        console.print("[yellow]No jobs found matching your criteria to generate statistics.[/yellow]")
        return

    total_count = len(jobs)

    # 3. Calculate Metrics
    status_counts = Counter(j["status"] for j in jobs)
    arrangement_counts = Counter(j["arrangement"] for j in jobs if j["arrangement"])
    source_counts = Counter(j["source"] for j in jobs if j["source"])
    level_counts = Counter(j["level"] for j in jobs if j["level"])

    # Funnel Metrics
    interviews = sum(1 for j in jobs if j["status"] in ("interviewing", "offered", "accepted"))
    offers = sum(1 for j in jobs if j["status"] in ("offered", "accepted"))
    accepted = status_counts.get("accepted", 0)

    interview_rate = (interviews / total_count * 100) if total_count > 0 else 0
    offer_rate = (offers / interviews * 100) if interviews > 0 else 0
    success_rate = (accepted / total_count * 100) if total_count > 0 else 0

    # Performance Metrics
    ratings = [j["rating"] for j in jobs if j["rating"] is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    fits = [j["fit"] for j in jobs if j["fit"] is not None]
    avg_fit = sum(fits) / len(fits) if fits else 0

    # Response Time
    response_times = []
    for j in jobs:
        if j["date_applied"] and j["response_date"]:
            try:
                d1 = datetime.fromisoformat(j["date_applied"])
                d2 = datetime.fromisoformat(j["response_date"])
                delta = (d2 - d1).days
                if delta >= 0:
                    response_times.append(delta)
            except ValueError:
                continue
    avg_response_time = sum(response_times) / len(response_times) if response_times else None

    # 4. Display Dashboard
    console.print(f"\n[bold blue]Job Search Statistics[/bold blue] ({total_count} Applications)\n")

    # Funnel Panel
    funnel_text = f"Total Applications: [bold]{total_count}[/bold]\n" f"Interviews:         [bold cyan]{interviews}[/bold cyan] ({interview_rate:.1f}%)\n" f"Offers:             [bold green]{offers}[/bold green] ({offer_rate:.1f}% of interviews)\n" f"Accepted:           [bold gold1]{accepted}[/bold gold1] ({success_rate:.1f}% total success)"
    console.print(Panel(funnel_text, title="Application Funnel", expand=False))

    # Performance Panel
    perf_text = f"Avg Job Rating:     [bold]{avg_rating:.1f}/5.0[/bold]\n" f"Avg Job Fit:        [bold]{avg_fit:.1f}/5.0[/bold]\n" f"Avg Response Time:  [bold]{f'{avg_response_time:.1f} days' if avg_response_time is not None else 'N/A'}[/bold]"
    console.print(Panel(perf_text, title="Performance Metrics", expand=False))

    # Breakdowns
    cols = []

    # Status Table
    status_table = Table(title="Status Breakdown", show_header=True, header_style="bold magenta")
    status_table.add_column("Status")
    status_table.add_column("Count", justify="right")
    status_table.add_column("%", justify="right")
    for status, count in status_counts.most_common():
        status_table.add_row(status.title(), str(count), f"{(count/total_count*100):.1f}%")
    cols.append(status_table)

    # Arrangement Table
    if arrangement_counts:
        arr_table = Table(title="Arrangement", show_header=True, header_style="bold yellow")
        arr_table.add_column("Type")
        arr_table.add_column("Count", justify="right")
        for arr, count in arrangement_counts.most_common():
            arr_table.add_row(arr.title(), str(count))
        cols.append(arr_table)

    # Source Table
    if source_counts:
        src_table = Table(title="Top Sources", show_header=True, header_style="bold green")
        src_table.add_column("Source")
        src_table.add_column("Count", justify="right")
        for src, count in source_counts.most_common(5):
            src_table.add_row(src.title(), str(count))
        cols.append(src_table)

    console.print(Columns(cols))
