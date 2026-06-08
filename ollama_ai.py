import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
TIMEZONE = "Europe/Berlin"


GREETING_WORDS = [
    "hi", "hello", "hey", "salam", "salaam",
    "good morning", "good afternoon", "good evening", "good night",
    "سلام", "سلام علیکم", "صبح بخیر", "شب بخیر"
]


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}


def get_current_greeting():
    now = datetime.now(ZoneInfo(TIMEZONE))
    hour = now.hour

    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 18:
        return "Good afternoon"
    return "Good evening"


def is_short_greeting(message):
    cleaned = message.lower().strip()
    cleaned = cleaned.replace("!", "").replace(".", "").replace("?", "")
    return cleaned in GREETING_WORDS


def clean_recommendation_line(line):
    line = line.strip()
    line = re.sub(r"^[-•\*\d\.\)\s]+", "", line)
    line = line.replace("**", "")

    unwanted_starts = [
        "based on",
        "here are",
        "recommendations",
        "sure",
        "to prevent burnout",
        "analysis"
    ]

    if any(line.lower().startswith(item) for item in unwanted_starts):
        return ""

    return line.strip()


def format_events_for_prompt(events):
    schedule_text = []

    for event in events:
        title = event.get("summary", "No Title")
        start = event.get("start", {}).get("dateTime", "")
        end = event.get("end", {}).get("dateTime", "")

        schedule_text.append(
            f"- {title} | Start: {start} | End: {end}"
        )

    if not schedule_text:
        return "No calendar events found."

    return "\n".join(schedule_text)


def parse_natural_date(text):
    text = text.lower()
    now = datetime.now(ZoneInfo(TIMEZONE))

    if "today" in text:
        return now.date().isoformat()

    if "tomorrow" in text:
        return (now + timedelta(days=1)).date().isoformat()

    for day_name, day_index in WEEKDAYS.items():
        if day_name in text:
            days_ahead = day_index - now.weekday()

            if "next" in text or days_ahead <= 0:
                days_ahead += 7

            return (now + timedelta(days=days_ahead)).date().isoformat()

    iso_match = re.search(r"\d{4}-\d{2}-\d{2}", text)

    if iso_match:
        return iso_match.group(0)

    return now.date().isoformat()


def parse_natural_time(text):
    text = text.lower()

    time_match = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
        text
    )

    if not time_match:
        return "10:00"

    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or 0)
    meridiem = time_match.group(3)

    if meridiem == "pm" and hour < 12:
        hour += 12

    if meridiem == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"


def parse_duration_hours(text):
    text = text.lower()

    from_to_match = re.search(
        r"from\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s+to\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
        text
    )

    if from_to_match:
        start_hour = int(from_to_match.group(1))
        start_minute = int(from_to_match.group(2) or 0)
        start_meridiem = from_to_match.group(3)

        end_hour = int(from_to_match.group(4))
        end_minute = int(from_to_match.group(5) or 0)
        end_meridiem = from_to_match.group(6)

        if start_meridiem == "pm" and start_hour < 12:
            start_hour += 12

        if end_meridiem == "pm" and end_hour < 12:
            end_hour += 12

        start_total = start_hour + start_minute / 60
        end_total = end_hour + end_minute / 60

        duration = end_total - start_total

        if duration > 0:
            return str(duration)

    duration_match = re.search(
        r"for\s+(\d+(?:\.\d+)?)\s*(hour|hours|hr|hrs)",
        text
    )

    if duration_match:
        return duration_match.group(1)

    minute_match = re.search(
        r"for\s+(\d+)\s*(minute|minutes|min|mins)",
        text
    )

    if minute_match:
        minutes = int(minute_match.group(1))
        return str(minutes / 60)

    return "1"


def extract_title_for_create(message):
    patterns = [
        r"called\s+(.+)",
        r"named\s+(.+)",
        r"title\s+(.+)",
        r"about\s+(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            title = match.group(1).strip()
            title = re.sub(r"\s+at\s+\d{1,2}.*", "", title, flags=re.IGNORECASE)
            title = re.sub(r"\s+tomorrow.*", "", title, flags=re.IGNORECASE)
            title = re.sub(r"\s+today.*", "", title, flags=re.IGNORECASE)
            return title.strip().title()

    if "focus" in message.lower():
        return "Focus Time Block"

    return "AI Created Event"


def extract_title_for_delete(message):
    cleaned = message.strip()

    cleaned = re.sub(
        r"^(delete|remove|cancel)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"^(my\s+)?(meeting|event|calendar event)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    return cleaned.strip()


def extract_title_for_move(message):
    match = re.search(
        r"(move|reschedule)\s+(.+?)\s+to\s+(.+)",
        message,
        re.IGNORECASE
    )

    if match:
        return match.group(2).strip(), match.group(3).strip()

    return "", ""


def detect_calendar_action(message):
    text = message.lower().strip()

    create_words = ["create", "add", "schedule", "book"]
    delete_words = ["delete", "remove", "cancel"]
    move_words = ["move", "reschedule"]

    if any(text.startswith(word) for word in create_words):
        title = extract_title_for_create(message)
        event_date = parse_natural_date(message)
        start_time = parse_natural_time(message)
        duration_hours = parse_duration_hours(message)

        return {
            "type": "create_event",
            "title": title,
            "event_date": event_date,
            "start_time": start_time,
            "duration_hours": duration_hours,
            "description": "Created by Smart Calendar Copilot."
        }

    if any(text.startswith(word) for word in delete_words):
        title = extract_title_for_delete(message)

        return {
            "type": "delete_event",
            "title": title
        }

    if any(text.startswith(word) for word in move_words):
        title, target_text = extract_title_for_move(message)

        if title and target_text:
            event_date = parse_natural_date(target_text)
            start_time = parse_natural_time(target_text)

            return {
                "type": "move_event",
                "title": title,
                "event_date": event_date,
                "start_time": start_time,
                "duration_hours": "1"
            }

    return {
        "type": "chat"
    }


def generate_ollama_recommendations(events, stats):
    schedule_text = format_events_for_prompt(events)

    prompt = f"""
You are a smart calendar productivity assistant.

Give exactly 3 short practical recommendations based on the user's calendar.

Stats:
- Meetings count: {stats.get("meetings_count")}
- Meeting hours: {stats.get("meeting_hours")}
- Focus hours: {stats.get("focus_hours")}
- Burnout score: {stats.get("burnout_score")}
- Burnout level: {stats.get("burnout_level")}

Today's schedule:
{schedule_text}

Rules:
- Return only 3 bullet points.
- No introduction.
- No markdown bold.
- Each point must be short and useful.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()
        text = response.json().get("response", "")

        recommendations = []

        for line in text.splitlines():
            clean = clean_recommendation_line(line)
            if clean:
                recommendations.append(clean)

        recommendations = recommendations[:3]

        if len(recommendations) < 3:
            fallback = [
                "Add a short break between meetings.",
                "Protect at least two hours of focus time.",
                "Avoid adding more meetings late in the day."
            ]

            for item in fallback:
                if len(recommendations) >= 3:
                    break
                if item not in recommendations:
                    recommendations.append(item)

        return recommendations

    except Exception as e:
        print("Ollama Error:", e)

        return [
            "Ollama AI is not available, so rule-based recommendations are being used.",
            "Try blocking two hours of focus time today.",
            "Add short breaks between meetings to reduce burnout risk."
        ]


def generate_copilot_response(user_message, events, week_events, stats):
    if is_short_greeting(user_message):
        greeting = get_current_greeting()

        return f"""{greeting} Basit 👋

How can I help you today?

You can ask me about:
• Your calendar
• Meetings
• Focus time
• Burnout risk
• Productivity
• Or any general question"""

    today_schedule = format_events_for_prompt(events)
    week_schedule = format_events_for_prompt(week_events)

    prompt = f"""
You are Smart Calendar Copilot.

You must behave like ChatGPT plus a calendar assistant.

Important behavior:
- If the user asks a general question, answer it normally like ChatGPT.
- If the user asks about calendar, meetings, focus time, productivity, schedule, workload, burnout, or planning, use the calendar data.
- Do not force calendar analysis when the question is general.
- Do not over-explain.
- Be natural, intelligent, and helpful.
- Use simple, clear language.
- If the answer needs steps, give short steps.
- Do not use markdown bold.
- Do not say you are an AI model.

User message:
{user_message}

Calendar data available:

Today's stats:
- Meetings count: {stats.get("meetings_count") if stats else 0}
- Meeting hours: {stats.get("meeting_hours") if stats else 0}
- Focus hours: {stats.get("focus_hours") if stats else 0}
- Burnout score: {stats.get("burnout_score") if stats else 0}
- Burnout level: {stats.get("burnout_level") if stats else "Unknown"}

Today's schedule:
{today_schedule}

This week's schedule:
{week_schedule}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=90
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        if not answer:
            return "I could not generate a response. Please try again."

        answer = answer.replace("**", "")
        return answer

    except Exception as e:
        print("Ollama Copilot Error:", e)

        return (
            "Ollama is not available right now. "
            "Please make sure Ollama is running with: ollama serve"
        )
