import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask import Flask, render_template, redirect, session, request, jsonify
from google.oauth2.credentials import Credentials

from config import Config
from auth import create_google_flow
from calendar_utils import (
    get_today_events,
    get_week_events,
    create_focus_block,
    create_calendar_event,
    update_calendar_event,
    delete_calendar_event,
    find_event_by_title
)
from analytics import build_dashboard_stats, build_weekly_analytics
from ollama_ai import (
    generate_ollama_recommendations,
    generate_copilot_response,
    detect_calendar_action
)


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY


def get_credentials_from_session():
    if "credentials" not in session:
        return None

    return Credentials(
        token=session["credentials"]["token"],
        refresh_token=session["credentials"].get("refresh_token"),
        token_uri=session["credentials"]["token_uri"],
        client_id=session["credentials"]["client_id"],
        client_secret=session["credentials"]["client_secret"],
        scopes=session["credentials"]["scopes"]
    )


def load_dashboard_context():
    credentials = get_credentials_from_session()

    events = []
    week_events = []
    connected = False
    stats = None
    weekly = None

    if credentials:
        connected = True

        try:
            events = get_today_events(credentials)
            week_events = get_week_events(credentials)

            stats = build_dashboard_stats(events)

            ollama_recommendations = generate_ollama_recommendations(
                events,
                stats
            )

            stats["recommendations"] = ollama_recommendations
            weekly = build_weekly_analytics(week_events)

        except Exception as e:
            print("Calendar Error:", e)

    return {
        "events": events,
        "week_events": week_events,
        "connected": connected,
        "stats": stats,
        "weekly": weekly,
        "message": request.args.get("message")
    }


@app.route("/")
def home():
    context = load_dashboard_context()
    return render_template("index.html", **context)


@app.route("/calendar")
def calendar_page():
    context = load_dashboard_context()
    return render_template("calendar.html", **context)


@app.route("/meetings")
def meetings_page():
    context = load_dashboard_context()
    return render_template("meetings.html", **context)


@app.route("/focus")
def focus_page():
    context = load_dashboard_context()
    return render_template("focus.html", **context)


@app.route("/ai-insights")
def ai_insights_page():
    context = load_dashboard_context()
    return render_template("ai_insights.html", **context)


@app.route("/tasks")
def tasks_page():
    context = load_dashboard_context()
    return render_template("tasks.html", **context)


@app.route("/analytics")
def analytics_page():
    context = load_dashboard_context()
    return render_template("analytics.html", **context)


@app.route("/copilot")
def copilot_page():
    context = load_dashboard_context()
    context["chat_history"] = []
    return render_template("copilot.html", **context)


@app.route("/copilot-chat", methods=["POST"])
def copilot_chat():
    context = load_dashboard_context()
    credentials = get_credentials_from_session()

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "success": False,
            "answer": "Please write a message first."
        })

    if not context["connected"] or not credentials:
        return jsonify({
            "success": True,
            "answer": (
                "Please connect your Google Calendar first so I can analyze "
                "and manage your meetings, focus time, and workload."
            )
        })

    try:
        action = detect_calendar_action(user_message)

        if action["type"] == "create_event":
            created_event = create_calendar_event(
                credentials=credentials,
                title=action["title"],
                event_date=action["event_date"],
                start_time=action["start_time"],
                duration_hours=action["duration_hours"],
                description=action.get("description", "Created by Smart Calendar Copilot.")
            )

            answer = (
                f"Done ✅\n\n"
                f"I created this event in your Google Calendar:\n\n"
                f"Title: {created_event.get('summary')}\n"
                f"Date: {action['event_date']}\n"
                f"Time: {action['start_time']}\n"
                f"Duration: {action['duration_hours']} hour(s)"
            )

            return jsonify({
                "success": True,
                "answer": answer
            })

        if action["type"] == "delete_event":
            event = find_event_by_title(
                credentials=credentials,
                title=action["title"]
            )

            if not event:
                return jsonify({
                    "success": True,
                    "answer": (
                        f"I could not find an event matching: {action['title']}.\n\n"
                        f"Try writing the event title more exactly."
                    )
                })

            delete_calendar_event(
                credentials=credentials,
                event_id=event["id"]
            )

            return jsonify({
                "success": True,
                "answer": (
                    f"Done ✅\n\n"
                    f"I deleted this event from your Google Calendar:\n\n"
                    f"{event.get('summary', 'No Title')}"
                )
            })

        if action["type"] == "move_event":
            event = find_event_by_title(
                credentials=credentials,
                title=action["title"]
            )

            if not event:
                return jsonify({
                    "success": True,
                    "answer": (
                        f"I could not find an event matching: {action['title']}.\n\n"
                        f"Try writing the event title more exactly."
                    )
                })

            current_title = event.get("summary", action["title"])
            current_description = event.get("description", "")

            update_calendar_event(
                credentials=credentials,
                event_id=event["id"],
                title=current_title,
                event_date=action["event_date"],
                start_time=action["start_time"],
                duration_hours=action["duration_hours"],
                description=current_description
            )

            return jsonify({
                "success": True,
                "answer": (
                    f"Done ✅\n\n"
                    f"I moved this event:\n\n"
                    f"{current_title}\n\n"
                    f"New date: {action['event_date']}\n"
                    f"New time: {action['start_time']}"
                )
            })

        ai_answer = generate_copilot_response(
            user_message=user_message,
            events=context["events"],
            week_events=context["week_events"],
            stats=context["stats"]
        )

        return jsonify({
            "success": True,
            "answer": ai_answer
        })

    except Exception as e:
        print("Copilot Action Error:", e)

        return jsonify({
            "success": False,
            "answer": (
                "Something went wrong while processing your calendar action.\n\n"
                f"Error: {str(e)}"
            )
        })


@app.route("/clear-copilot")
def clear_copilot():
    return redirect("/copilot")


@app.route("/create-event", methods=["POST"])
def create_event_route():
    credentials = get_credentials_from_session()

    if not credentials:
        return redirect("/login")

    try:
        title = request.form.get("title")
        event_date = request.form.get("event_date")
        start_time = request.form.get("start_time")
        duration_hours = request.form.get("duration_hours")
        description = request.form.get("description", "")

        if not title or not event_date or not start_time or not duration_hours:
            return redirect("/calendar?message=Please fill all event fields")

        create_calendar_event(
            credentials=credentials,
            title=title,
            event_date=event_date,
            start_time=start_time,
            duration_hours=duration_hours,
            description=description
        )

        return redirect("/calendar?message=Event created successfully")

    except Exception as e:
        return f"""
        <h1>Create Event Error</h1>
        <p>{str(e)}</p>
        <a href="/calendar">Back to Calendar</a>
        """


@app.route("/edit-event/<event_id>", methods=["POST"])
def edit_event_route(event_id):
    credentials = get_credentials_from_session()

    if not credentials:
        return redirect("/login")

    try:
        title = request.form.get("title")
        event_date = request.form.get("event_date")
        start_time = request.form.get("start_time")
        duration_hours = request.form.get("duration_hours")
        description = request.form.get("description", "")

        if not title or not event_date or not start_time or not duration_hours:
            return redirect("/calendar?message=Please fill all edit fields")

        update_calendar_event(
            credentials=credentials,
            event_id=event_id,
            title=title,
            event_date=event_date,
            start_time=start_time,
            duration_hours=duration_hours,
            description=description
        )

        return redirect("/calendar?message=Event updated successfully")

    except Exception as e:
        return f"""
        <h1>Edit Event Error</h1>
        <p>{str(e)}</p>
        <a href="/calendar">Back to Calendar</a>
        """


@app.route("/delete-event/<event_id>", methods=["POST"])
def delete_event_route(event_id):
    credentials = get_credentials_from_session()

    if not credentials:
        return redirect("/login")

    try:
        delete_calendar_event(
            credentials=credentials,
            event_id=event_id
        )

        return redirect("/calendar?message=Event deleted successfully")

    except Exception as e:
        return f"""
        <h1>Delete Event Error</h1>
        <p>{str(e)}</p>
        <a href="/calendar">Back to Calendar</a>
        """


@app.route("/login")
def login():
    print("REDIRECT URI:", Config.GOOGLE_REDIRECT_URI)

    flow = create_google_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    session["state"] = state

    if hasattr(flow, "code_verifier"):
        session["code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    try:
        flow = create_google_flow()

        if "code_verifier" in session:
            flow.code_verifier = session["code_verifier"]

        flow.fetch_token(
            authorization_response=request.url
        )

        credentials = flow.credentials

        session["credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

        return redirect("/?message=Google Calendar connected successfully")

    except Exception as e:
        return f"""
        <h1>OAuth Error</h1>
        <p>{str(e)}</p>
        <a href="/">Back to Dashboard</a>
        """


@app.route("/create-focus-block", methods=["POST"])
def create_focus_block_route():
    credentials = get_credentials_from_session()

    if not credentials:
        return redirect("/login")

    try:
        focus_date = request.form.get("focus_date")
        start_time = request.form.get("start_time")
        duration_hours = request.form.get("duration_hours")
        title = request.form.get("title")

        if not focus_date or not start_time or not duration_hours or not title:
            return redirect("/?message=Please fill all Focus Block fields")

        create_focus_block(
            credentials=credentials,
            focus_date=focus_date,
            start_time=start_time,
            duration_hours=duration_hours,
            title=title
        )

        return redirect("/?message=Focus Block created successfully")

    except Exception as e:
        return f"""
        <h1>Create Focus Block Error</h1>
        <p>{str(e)}</p>
        <a href="/">Back to Dashboard</a>
        """

@app.route("/settings")
def settings_page():
    context = load_dashboard_context()
    return render_template("settings.html", **context)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/?message=Disconnected successfully")


if __name__ == "__main__":
    app.run(debug=True, port=5001)