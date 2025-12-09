from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import base64
import datetime
from src.state import Email

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify'
    ]

def get_gmail_service(token_path='token.json', credentials_path='credentials.json'):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def parse_email_address(message) -> Email:
    """
    Extracts email data from a Gmail API message resource.
    Returns a dict with id, subject, sender, date, and body.
    """
    headers_list = message.get('payload', {}).get('headers', [])
    headers = {header['name']: header['value'] for header in headers_list}
    subject = headers.get('Subject', 'No Subject')
    sender = headers.get('From', 'No Sender')
    date = headers.get('Date', 'No Date')
    body = ''
    payload = message.get('payload', {})
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                body = part.get('body', {}).get('data', '') #part['body'].get('data', '')
                break
    else:
        body = payload.get('body', {}).get('data', '')
    if body:
        try:
            body = base64.urlsafe_b64decode(body).decode('utf-8')
        except UnicodeDecodeError:
            body = ''
    return Email(id= message['id'], subject= subject, sender= sender, date= date, body= body)


def get_most_recent_email() -> Email:
    service = get_gmail_service()
    today = datetime.datetime.now().date()
    query = f'after:{today.strftime("%Y/%m/%d")}'
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
        messages = results.get('messages', [])
        if not messages:
            return None
        msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
        email_data = parse_email_address(msg)
        return email_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
