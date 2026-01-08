import typer
from typing import List, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.layout import Layout
from rich import box
from job_tracker.database import get_jobs
from job_tracker.utils import parse_filter_string

console = Console()


def _parse_dt(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        # Try ISO format first
        return datetime.fromisoformat(dt_str.replace(" ", "T") if " " in dt_str and "T" not in dt_str else dt_str)
    except ValueError:
        try:
            # Try the format used in validate_datetime
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return None


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
    type_counts = Counter(j["type"] for j in jobs if j["type"])
    location_counts = Counter(j["location"] for j in jobs if j["location"])
    company_counts = Counter(j["company_name"] for j in jobs if j["company_name"])

    # Funnel Metrics
    interviews = sum(1 for j in jobs if j["status"] in ("interviewing", "offered", "accepted"))
    offers = sum(1 for j in jobs if j["status"] in ("offered", "accepted"))
    rejections = status_counts.get("rejected", 0)
    accepted = status_counts.get("accepted", 0)
    no_reply = sum(1 for j in jobs if j["status"] == "applied" and not j["application_response_date"])

    interview_rate = (interviews / total_count * 100) if total_count > 0 else 0
    offer_rate = (offers / interviews * 100) if interviews > 0 else 0
    rejection_rate = (rejections / total_count * 100) if total_count > 0 else 0
    success_rate = (accepted / total_count * 100) if total_count > 0 else 0
    no_reply_rate = (no_reply / total_count * 100) if total_count > 0 else 0

    # Performance Metrics
    ratings = [j["rating"] for j in jobs if j["rating"] is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    fits = [j["fit"] for j in jobs if j["fit"] is not None]
    avg_fit = sum(fits) / len(fits) if fits else 0

    # Response & Interview Time
    response_times = []
    interview_lead_times = []
    for j in jobs:
        d_applied = _parse_dt(j["date_applied"])
        if d_applied:
            d_resp = _parse_dt(j["application_response_date"])
            if d_resp:
                delta = (d_resp - d_applied).days
                if delta >= 0:
                    response_times.append(delta)

            d_int = _parse_dt(j["interview_time"])
            if d_int:
                delta = (d_int - d_applied).days
                if delta >= 0:
                    interview_lead_times.append(delta)

    avg_response_time = sum(response_times) / len(response_times) if response_times else None
    avg_interview_time = sum(interview_lead_times) / len(interview_lead_times) if interview_lead_times else None

    # Trends
    weekly_apps = defaultdict(int)
    monthly_apps = defaultdict(int)
    for j in jobs:
        dt = _parse_dt(j["date_applied"])
        if dt:
            # Week start (Monday)
            week_start = dt - timedelta(days=dt.weekday())
            weekly_apps[week_start.strftime("%Y-%W")] += 1
            monthly_apps[dt.strftime("%Y-%m")] += 1

    # 4. Display Dashboard
    console.print(f"\n[bold blue]Job Search Analytics Dashboard[/bold blue] ({total_count} Applications)\n")

    # Funnel Panel
    funnel_text = f"Total Applications: [bold]{total_count}[/bold]\n" f"No Reply:           [bold yellow]{no_reply}[/bold yellow] ({no_reply_rate:.1f}%)\n" f"Rejections:         [bold red]{rejections}[/bold red] ({rejection_rate:.1f}%)\n" f"Interviews:         [bold cyan]{interviews}[/bold cyan] ({interview_rate:.1f}%)\n" f"Offers:             [bold green]{offers}[/bold green] ({offer_rate:.1f}% of interviews)\n" f"Accepted:           [bold gold1]{accepted}[/bold gold1] ({success_rate:.1f}% total success)"

    # Performance Panel
    perf_text = f"Avg Job Rating:     [bold]{avg_rating:.1f}/5.0[/bold]\n" f"Avg Job Fit:        [bold]{avg_fit:.1f}/5.0[/bold]\n" f"Avg Response Time:  [bold]{f'{avg_response_time:.1f} days' if avg_response_time is not None else 'N/A'}[/bold]\n" f"Avg Time to Int:    [bold]{f'{avg_interview_time:.1f} days' if avg_interview_time is not None else 'N/A'}[/bold]"

    console.print(Columns([Panel(funnel_text, title="Application Funnel", expand=True), Panel(perf_text, title="Performance Metrics", expand=True)]))

    # Breakdowns
    breakdown_cols = []

    # Status Table
    status_table = Table(title="Status Breakdown", show_header=True, header_style="bold magenta", box=box.ROUNDED)
    status_table.add_column("Status")
    status_table.add_column("Count", justify="right")
    status_table.add_column("%", justify="right")
    for status, count in status_counts.most_common():
        status_table.add_row(status.title(), str(count), f"{(count/total_count*100):.1f}%")
    breakdown_cols.append(status_table)

    # Company Table
    company_table = Table(title="Top Companies", show_header=True, header_style="bold blue", box=box.ROUNDED)
    company_table.add_column("Company")
    company_table.add_column("Apps", justify="right")
    for company, count in company_counts.most_common(5):
        company_table.add_row(company, str(count))
    breakdown_cols.append(company_table)

    # Source Table
    src_table = Table(title="Top Sources", show_header=True, header_style="bold green", box=box.ROUNDED)
    src_table.add_column("Source")
    src_table.add_column("Count", justify="right")
    for src, count in source_counts.most_common(5):
        src_table.add_row(src.title(), str(count))
    breakdown_cols.append(src_table)

    console.print(Columns(breakdown_cols, equal=True))
    console.print()

    # More Breakdowns
    more_breakdown_cols = []

    # Level Table
    if level_counts:
        lvl_table = Table(title="Experience Level", show_header=True, header_style="bold cyan", box=box.ROUNDED)
        lvl_table.add_column("Level")
        lvl_table.add_column("Count", justify="right")
        for lvl, count in level_counts.most_common():
            lvl_table.add_row(lvl.title(), str(count))
        more_breakdown_cols.append(lvl_table)

    # Arrangement Table
    if arrangement_counts:
        arr_table = Table(title="Arrangement", show_header=True, header_style="bold yellow", box=box.ROUNDED)
        arr_table.add_column("Type")
        arr_table.add_column("Count", justify="right")
        for arr, count in arrangement_counts.most_common():
            arr_table.add_row(arr.title(), str(count))
        more_breakdown_cols.append(arr_table)

    # Location Table
    if location_counts:
        loc_table = Table(title="Top Locations", show_header=True, header_style="bold white", box=box.ROUNDED)
        loc_table.add_column("Location")
        loc_table.add_column("Count", justify="right")
        for loc, count in location_counts.most_common(5):
            loc_table.add_row(loc.title(), str(count))
        more_breakdown_cols.append(loc_table)

    if more_breakdown_cols:
        console.print(Columns(more_breakdown_cols, equal=True))
        console.print()

    # Trends Table
    trends_cols = []

    if monthly_apps:
        month_table = Table(title="Monthly Trends", show_header=True, header_style="bold magenta", box=box.ROUNDED)
        month_table.add_column("Month")
        month_table.add_column("Apps", justify="right")
        # Sort by month key
        for month in sorted(monthly_apps.keys(), reverse=True)[:6]:
            month_table.add_row(month, str(monthly_apps[month]))
        trends_cols.append(month_table)

    if weekly_apps:
        week_table = Table(title="Weekly Trends", show_header=True, header_style="bold yellow", box=box.ROUNDED)
        week_table.add_column("Week")
        week_table.add_column("Apps", justify="right")
        # Sort by week key
        for week in sorted(weekly_apps.keys(), reverse=True)[:8]:
            week_table.add_row(week, str(weekly_apps[week]))
        trends_cols.append(week_table)

    if trends_cols:
        console.print(Columns(trends_cols, equal=True))
        console.print()

    # 5. Quality Analysis
    # Compare avg rating/fit of interviewed vs non-interviewed
    interviewed_jobs = [j for j in jobs if j["status"] in ("interviewing", "offered", "accepted")]
    non_interviewed_jobs = [j for j in jobs if j["status"] not in ("interviewing", "offered", "accepted")]

    def get_avg(job_list, key):
        vals = [j[key] for j in job_list if j[key] is not None]
        return sum(vals) / len(vals) if vals else 0

    avg_rating_int = get_avg(interviewed_jobs, "rating")
    avg_fit_int = get_avg(interviewed_jobs, "fit")
    avg_rating_non = get_avg(non_interviewed_jobs, "rating")
    avg_fit_non = get_avg(non_interviewed_jobs, "fit")

    quality_table = Table(title="Quality Analysis (Interviewed vs. Others)", show_header=True, header_style="bold green", box=box.ROUNDED)
    quality_table.add_row("Avg Fit", f"{avg_fit_int:.1f}", f"{avg_fit_non:.1f}")

    console.print(quality_table)
