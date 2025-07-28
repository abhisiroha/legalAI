from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
 
def get_google_credentials():
    """Obtain Google API credentials."""
    creds = None
    token_path = 'token.json'
    creds_path = 'credentials.json'

    # Try to load existing credentials from token.json
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except Exception:
        pass

    # If there are no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds