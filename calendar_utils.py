from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build


TIMEZONE = "Europe/Berlin"


def get_calendar_service(credentials):
    return build(
        "calendar",
        "v3",
        credentials=credentials
    )


def get_today_events(credentials):
    service = get_calendar_service(credentials)

    timezone = ZoneInfo(TIMEZONE)
    now = datetime.now(timezone)

    start_of_day = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    end_of_day = start_of_day + timedelta(days=1)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])


def get_week_events(credentials):
    service = get_calendar_service(credentials)

    timezone = ZoneInfo(TIMEZONE)
    now = datetime.now(timezone)

    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    end_of_week = start_of_week + timedelta(days=7)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_week.isoformat(),
        timeMax=end_of_week.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])


def get_next_30_days_events(credentials):
    service = get_calendar_service(credentials)

    timezone = ZoneInfo(TIMEZONE)
    now = datetime.now(timezone)

    start_time = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    end_time = start_time + timedelta(days=30)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])


def create_focus_block(
    credentials,
    focus_date,
    start_time,
    duration_hours,
    title
):
    return create_calendar_event(
        credentials=credentials,
        title=title,
        event_date=focus_date,
        start_time=start_time,
        duration_hours=duration_hours,
        description="Created by Smart Calendar Agent AI to protect deep work time."
    )


def create_calendar_event(
    credentials,
    title,
    event_date,
    start_time,
    duration_hours,
    description="Created by Smart Calendar Agent AI."
):
    service = get_calendar_service(credentials)

    timezone = ZoneInfo(TIMEZONE)

    start_dt = datetime.fromisoformat(
        f"{event_date}T{start_time}:00"
    ).replace(tzinfo=timezone)

    end_dt = start_dt + timedelta(
        hours=float(duration_hours)
    )

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": TIMEZONE
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": TIMEZONE
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return created_event


def get_event_by_id(credentials, event_id):
    service = get_calendar_service(credentials)

    event = service.events().get(
        calendarId="primary",
        eventId=event_id
    ).execute()

    return event


def find_event_by_title(credentials, title):
    events = get_next_30_days_events(credentials)

    search_title = title.lower().strip()

    for event in events:
        event_title = event.get("summary", "").lower().strip()

        if search_title in event_title or event_title in search_title:
            return event

    return None


def update_calendar_event(
    credentials,
    event_id,
    title,
    event_date,
    start_time,
    duration_hours,
    description=None
):
    service = get_calendar_service(credentials)

    timezone = ZoneInfo(TIMEZONE)

    start_dt = datetime.fromisoformat(
        f"{event_date}T{start_time}:00"
    ).replace(tzinfo=timezone)

    end_dt = start_dt + timedelta(
        hours=float(duration_hours)
    )

    event = service.events().get(
        calendarId="primary",
        eventId=event_id
    ).execute()

    event["summary"] = title

    if description is not None:
        event["description"] = description

    event["start"] = {
        "dateTime": start_dt.isoformat(),
        "timeZone": TIMEZONE
    }

    event["end"] = {
        "dateTime": end_dt.isoformat(),
        "timeZone": TIMEZONE
    }

    updated_event = service.events().update(
        calendarId="primary",
        eventId=event_id,
        body=event
    ).execute()

    return updated_event


def delete_calendar_event(credentials, event_id):
    service = get_calendar_service(credentials)

    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()

    return True
