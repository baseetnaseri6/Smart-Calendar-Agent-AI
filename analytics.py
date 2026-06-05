from datetime import datetime
from zoneinfo import ZoneInfo


def calculate_event_duration_hours(event):
    start = event.get("start", {}).get("dateTime")
    end = event.get("end", {}).get("dateTime")

    if not start or not end:
        return 0

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        duration = end_dt - start_dt
        return round(duration.total_seconds() / 3600, 2)

    except Exception:
        return 0


def is_focus_event(title):
    title = title.lower()

    focus_keywords = [
        "focus",
        "deep work",
        "study",
        "coding",
        "learning",
        "work block",
        "focus time"
    ]

    return any(keyword in title for keyword in focus_keywords)


def build_dashboard_stats(events):
    meetings_count = len(events)
    meeting_hours = 0
    focus_hours = 0

    for event in events:
        title = event.get("summary", "")
        duration = calculate_event_duration_hours(event)

        if is_focus_event(title):
            focus_hours += duration
        else:
            meeting_hours += duration

    meeting_hours = round(meeting_hours, 1)
    focus_hours = round(focus_hours, 1)

    if meetings_count == 0:
        burnout_score = 0
        burnout_level = "Low"

    else:
        burnout_score = 20

        if meeting_hours >= 2:
            burnout_score += 20

        if meeting_hours >= 4:
            burnout_score += 25

        if meetings_count >= 4:
            burnout_score += 20

        if focus_hours < 1:
            burnout_score += 15

        if focus_hours >= 2:
            burnout_score -= 20

        burnout_score = max(0, min(100, burnout_score))

        if burnout_score >= 70:
            burnout_level = "High"
        elif burnout_score >= 40:
            burnout_level = "Medium"
        else:
            burnout_level = "Low"

    recommendations = []

    if meetings_count == 0:
        recommendations.append("Your calendar is free today. Use this time for deep work or planning.")

    if focus_hours < 2:
        recommendations.append("Schedule at least 2 hours of focus time today.")

    if meeting_hours >= 4:
        recommendations.append("Your meeting load is high. Add short breaks between meetings.")

    if meetings_count >= 4:
        recommendations.append("Review your meetings and reschedule low-priority events if possible.")

    if not recommendations:
        recommendations.append("Your schedule looks balanced today.")

    productivity_score = 100
    productivity_score -= min(meeting_hours * 8, 40)
    productivity_score -= min(burnout_score * 0.4, 40)
    productivity_score += min(focus_hours * 10, 30)

    productivity_score = max(0, min(100, round(productivity_score)))

    if meetings_count == 0:
        productivity_score = 100

    if productivity_score >= 80:
        productivity_label = "Excellent"
    elif productivity_score >= 60:
        productivity_label = "Good"
    elif productivity_score >= 40:
        productivity_label = "Average"
    else:
        productivity_label = "Poor"

    return {
        "meetings_count": meetings_count,
        "meeting_hours": meeting_hours,
        "focus_hours": focus_hours,
        "burnout_score": burnout_score,
        "burnout_level": burnout_level,
        "recommendations": recommendations,
        "productivity_score": productivity_score,
        "productivity_label": productivity_label
    }


def build_weekly_analytics(week_events):
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    focus_hours = [0, 0, 0, 0, 0, 0, 0]
    meeting_hours = [0, 0, 0, 0, 0, 0, 0]
    burnout_scores = [0, 0, 0, 0, 0, 0, 0]

    timezone = ZoneInfo("Europe/Berlin")

    for event in week_events:
        title = event.get("summary", "")
        start = event.get("start", {}).get("dateTime")

        if not start:
            continue

        try:
            start_dt = datetime.fromisoformat(start).astimezone(timezone)
            weekday = start_dt.weekday()
            duration = calculate_event_duration_hours(event)

            if is_focus_event(title):
                focus_hours[weekday] += duration
            else:
                meeting_hours[weekday] += duration

        except Exception:
            continue

    for index in range(7):
        score = 20

        if meeting_hours[index] >= 2:
            score += 20

        if meeting_hours[index] >= 4:
            score += 25

        if focus_hours[index] < 1 and meeting_hours[index] > 0:
            score += 15

        if focus_hours[index] >= 2:
            score -= 20

        if meeting_hours[index] == 0 and focus_hours[index] == 0:
            score = 0

        burnout_scores[index] = max(0, min(100, round(score)))

    return {
        "labels": labels,
        "focus_hours": [round(item, 1) for item in focus_hours],
        "meeting_hours": [round(item, 1) for item in meeting_hours],
        "burnout_scores": burnout_scores
    }
