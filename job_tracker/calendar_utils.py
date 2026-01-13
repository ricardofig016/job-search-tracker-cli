from datetime import datetime, timedelta
from job_tracker.calendar_auth import get_calendar_service


def format_event_body(job_data: dict, action_type: str):
    """
    Formats the Google Calendar event body based on job data and action type.
    action_type: 'interview' or 'followup'
    """
    company = (job_data.get("company_name") or "Unknown Company").upper()
    role = (job_data.get("role_name") or "Unknown Role").upper()

    title = f"{action_type.capitalize()} with {company} for {role} - Job Tracker"

    description_parts = []
    if job_data.get("id"):
        description_parts.append(f"Job ID: {job_data['id']}")

    if job_data.get("role_url"):
        description_parts.append(f"Job Posting: {job_data['role_url']}")

    recruiter_info = []
    if job_data.get("recruiter_name"):
        recruiter_info.append(job_data["recruiter_name"])
    if job_data.get("recruiter_email"):
        recruiter_info.append(job_data["recruiter_email"])
    if job_data.get("recruiter_linkedin"):
        recruiter_info.append(job_data["recruiter_linkedin"])

    if recruiter_info:
        description_parts.append(f"Recruiter: {', '.join(recruiter_info)}")

    if job_data.get("interview_link"):
        description_parts.append(f"Interview Link: {job_data['interview_link']}")

    if job_data.get("interview_type"):
        description_parts.append(f"Interview Type: {job_data['interview_type']}")

    if job_data.get("notes"):
        description_parts.append(f"Notes: {job_data['notes']}")

    description = "\n".join(description_parts)

    # Time handling
    if action_type == "interview":
        # Interview time (YYYY-MM-DD HH:MM)
        dt_str = job_data.get("interview_time")
        if not dt_str:
            return None
        # Convert YYYY-MM-DD HH:MM to ISO format YYYY-MM-DDTHH:MM:SSZ
        # Assuming input is already in WET/UTC
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        start_time = dt.strftime("%Y-%m-%dT%H:%M:00Z")
        end_time = (dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:00Z")
    else:  # followup
        # Followup date (YYYY-MM-DD)
        date_str = job_data.get("followup_date")
        if not date_str:
            return None
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Set followup to 9 AM
        start_time = dt.replace(hour=9).strftime("%Y-%m-%dT%H:%M:00Z")
        end_time = dt.replace(hour=10).strftime("%Y-%m-%dT%H:%M:00Z")

    return {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
    }


def sync_event(job_data: dict, action_type: str):
    """
    Creates or updates a Google Calendar event.
    Returns the event ID if successful, else None.
    """
    try:
        service = get_calendar_service()
        event_body = format_event_body(job_data, action_type)

        if not event_body:
            return None

        # Determine which event ID to use
        event_id_key = "interview_event_id" if action_type == "interview" else "followup_event_id"
        event_id = job_data.get(event_id_key)

        if event_id:
            try:
                # Try to update existing event
                event = service.events().update(calendarId="primary", eventId=event_id, body=event_body).execute()
                return event["id"]
            except Exception:
                # If update fails (e.g. event deleted manually), create a new one
                event = service.events().insert(calendarId="primary", body=event_body).execute()
                return event["id"]
        else:
            # Create new event
            event = service.events().insert(calendarId="primary", body=event_body).execute()
            return event["id"]

    except Exception as e:
        print(f"Error syncing {action_type} with Google Calendar: {e}")
        return None


def delete_event(event_id: str):
    """
    Deletes an event from Google Calendar.
    """
    if not event_id:
        return
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
    except Exception as e:
        print(f"Error deleting Google Calendar event: {e}")
