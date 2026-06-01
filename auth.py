from google_auth_oauthlib.flow import Flow
from config import Config


def create_google_flow():
    return Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=Config.SCOPES,
        redirect_uri=Config.GOOGLE_REDIRECT_URI
    )
