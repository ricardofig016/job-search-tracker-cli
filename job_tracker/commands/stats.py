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
    # Improved interview detection: includes anyone who reached interview stage even if later rejected
    interviewed_jobs = [j for j in jobs if j["status"] in ("interviewing", "offered", "accepted") or j["interview_time"] or j["interview_response_date"]]
    interviews = len(interviewed_jobs)
    offers = sum(1 for j in jobs if j["status"] in ("offered", "accepted"))
    rejections = status_counts.get("rejected", 0)
    rejections_post_interview = sum(1 for j in interviewed_jobs if j["status"] == "rejected")
    rejections_pre_interview = rejections - rejections_post_interview

    accepted = status_counts.get("accepted", 0)
    ghosted = status_counts.get("ghosted", 0)
    awaiting = sum(1 for j in jobs if j["status"] == "applied" and not j["application_response_date"] and not j["interview_response_date"])
    # Consider a job "currently interviewing" if it's in the interview stage but hasn't reached an offer or rejection.
    currently_interviewing = sum(1 for j in interviewed_jobs if j["status"] in ("applied", "interviewing"))
    pending_offers = sum(1 for j in jobs if j["status"] == "offered")

    # Conversion Rates (Calculated using "settled" applications only)
    # A job is settled for a specific stage if it has a definitive outcome for that stage.

    # 1. App -> Interview: Settled if they responded (Total minus those still waiting for first word).
    settled_apps_count = total_count - awaiting

    # 2. Int -> Offer: Settled if interview process finished (Interviewed minus those still interviewing).
    settled_interviews_count = interviews - currently_interviewing

    # 3. Offer -> Accepted: Settled if offer decision made (Offered minus those still pending).
    settled_offers_count = offers - pending_offers

    # 4. Overall: Settled if the whole process reached a terminal status.
    terminal_settled_count = sum(1 for j in jobs if j["status"] in ("ghosted", "rejected", "offered", "accepted"))

    app_to_interview_rate = (interviews / settled_apps_count * 100) if settled_apps_count > 0 else 0
    interview_to_offer_rate = (offers / settled_interviews_count * 100) if settled_interviews_count > 0 else 0
    offer_to_acceptance_rate = (accepted / settled_offers_count * 100) if settled_offers_count > 0 else 0

    # Overall rates based on terminal settled applications
    overall_success_rate = (accepted / terminal_settled_count * 100) if terminal_settled_count > 0 else 0
    overall_offer_rate = (offers / terminal_settled_count * 100) if terminal_settled_count > 0 else 0

    # Total-based rates (for Funnel)
    total_interview_rate = (interviews / total_count * 100) if total_count > 0 else 0
    total_offer_rate = (offers / total_count * 100) if total_count > 0 else 0
    total_success_rate = (accepted / total_count * 100) if total_count > 0 else 0

    rejection_rate = (rejections / total_count * 100) if total_count > 0 else 0
    ghosted_rate = (ghosted / total_count * 100) if total_count > 0 else 0
    awaiting_rate = (awaiting / total_count * 100) if total_count > 0 else 0

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
    funnel_text = f"Total Applications: [bold]{total_count}[/bold]\n" f"Awaiting:           [bold yellow]{awaiting}[/bold yellow] ({awaiting_rate:.1f}%)\n" f"Ghosted:            [bold grey53]{ghosted}[/bold grey53] ({ghosted_rate:.1f}%)\n" f"Rejections:         [bold red]{rejections}[/bold red] ({rejection_rate:.1f}%)\n" f"  [dim]- Pre-int:[/dim]      [dim red]{rejections_pre_interview}[/dim red]\n" f"  [dim]- Post-int:[/dim]     [dim red]{rejections_post_interview}[/dim red]\n" f"Interviews:         [bold cyan]{interviews}[/bold cyan] ({total_interview_rate:.1f}%)\n" f"Offers:             [bold green]{offers}[/bold green] ({total_offer_rate:.1f}%)\n" f"Accepted:           [bold gold1]{accepted}[/bold gold1] ({total_success_rate:.1f}% total success)"

    # Conversion Rates Panel
    conv_text = f"App -> Interview:   [bold cyan]{app_to_interview_rate:.1f}%[/bold cyan]\n" f"Int -> Offer:       [bold green]{interview_to_offer_rate:.1f}%[/bold green]\n" f"Offer -> Accepted:  [bold gold1]{offer_to_acceptance_rate:.1f}%[/bold gold1]\n" f"Overall Success:    [bold]{overall_success_rate:.1f}%[/bold]"

    # Performance Panel
    perf_text = f"Avg Job Rating:     [bold]{avg_rating:.1f}/5.0[/bold]\n" f"Avg Job Fit:        [bold]{avg_fit:.1f}/5.0[/bold]\n" f"Avg Response Time:  [bold]{f'{avg_response_time:.1f} days' if avg_response_time is not None else 'N/A'}[/bold]\n" f"Avg Time to Int:    [bold]{f'{avg_interview_time:.1f} days' if avg_interview_time is not None else 'N/A'}[/bold]"

    console.print(Columns([Panel(funnel_text, title="Application Funnel", expand=True), Panel(conv_text, title="Conversion Rates", expand=True), Panel(perf_text, title="Performance Metrics", expand=True)]))

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
    # interviewed_jobs already defined above
    interviewed_ids = {j["id"] for j in interviewed_jobs}
    non_interviewed_jobs = [j for j in jobs if j["id"] not in interviewed_ids]

    def get_avg(job_list, key):
        vals = [j[key] for j in job_list if j[key] is not None]
        return sum(vals) / len(vals) if vals else 0

    avg_rating_int = get_avg(interviewed_jobs, "rating")
    avg_fit_int = get_avg(interviewed_jobs, "fit")
    avg_rating_non = get_avg(non_interviewed_jobs, "rating")
    avg_fit_non = get_avg(non_interviewed_jobs, "fit")

    quality_table = Table(title="Quality Analysis (Interviewed vs. Others)", show_header=True, header_style="bold green", box=box.ROUNDED)
    quality_table.add_column("Metric")
    quality_table.add_column("Interviewed", justify="right")
    quality_table.add_column("Others", justify="right")

    quality_table.add_row("Avg Fit", f"{avg_fit_int:.1f}", f"{avg_fit_non:.1f}")
    quality_table.add_row("Avg Rating", f"{avg_rating_int:.1f}", f"{avg_rating_non:.1f}")

    console.print(quality_table)
