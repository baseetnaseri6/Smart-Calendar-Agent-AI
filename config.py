import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv(
        "FLASK_SECRET_KEY",
        "dev-secret-key"
    )

    GOOGLE_CLIENT_SECRETS_FILE = os.getenv(
        "GOOGLE_CLIENT_SECRETS_FILE",
        "client_secret.json"
    )

    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5001/oauth2callback"
    )

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        ""
    )

    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ]