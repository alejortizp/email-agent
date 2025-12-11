from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import os
import base64
import datetime
from src.state import Email
import uuid 

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify'
    ]

def _get_gmail_service(token_path='token.json', credentials_path='credentials.json'):
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

def _parse_email_address(message) -> Email:
    """
    Extracts email data from a Gmail API message resource.
    Returns a dict with id, subject, sender, date, and body.
    """
    headers_list = message.get('payload', {}).get('headers', [])
    headers = {header['name']: header['value'] for header in headers_list}
    subject = headers.get('Subject', 'No Subject')
    sender = headers.get('From', 'No Sender')
    date = headers.get('Date', 'No Date')
    message_id = headers.get('message-id', '')
    references = headers.get('references', '')
    thread_id = headers.get('thread-id', '')
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
    return Email(
        id= message['id'],
        subject= subject,
        sender= sender,
        date= date,
        message_id= message_id,
        references= references,
        thread_id= thread_id,
        body= body
        )


def get_most_recent_email() -> Email:
    service = _get_gmail_service()
    today = datetime.datetime.now().date()
    query = f'after:{today.strftime("%Y/%m/%d")}'
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()  # pylint: disable=no-member
        messages = results.get('messages', [])
        if not messages:
            return None
        msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()  # pylint: disable=no-member
        email_data = _parse_email_address(msg)
        return email_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def send_reply_email(original_email: Email | str, reply_email: Email | str) -> bool:
    """
    Send a reply email to the original sender that will appear as a threaded reply.
    """
    try:
        service = _get_gmail_service()

        sender_email = original_email.sender # Micorreo <micorreo@gmail.com>
        if '<' in sender_email and '>' in sender_email:
            sender_email = sender_email.split('<')[1].split('>')[0]

        print(f"Reply will be sent to: {sender_email}")

        reply_subject = reply_email.subject
        original_subject = original_email.subject
        if original_subject.startswith('Re:'):
            reply_subject = original_subject
        else:
            reply_subject = f"Re: {original_subject}" # Re: no me gustan tus productos

        message_id = original_email.message_id
        references = original_email.references
        thread_id = original_email.thread_id

        if not message_id:
            message_id = f"<{original_email.id}@gmail.com>"

        message = _create_reply_message_with_thread(
            to=sender_email,
            subject=reply_subject,
            message_text=reply_email.body,
            original_message_id=message_id,
            original_references=references,
            thread_id=thread_id
        )

        sent_message = service.users().messages().send(userId='me', body=message).execute()

        print(f"Threaded reply email sent successfully. Message ID: {sent_message['id']}")
        return True

    except Exception as error:
        print(f'An error occurred while sending reply email: {error}')
        return False

def _create_reply_message_with_thread(to: str, subject: str, message_text: str, original_message_id: str, original_references: str, thread_id: str) -> dict:
    """
    Create a reply message that will appear as a threaded reply with proper thread ID.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    if original_message_id:
        message['In-Reply-To'] = original_message_id
        if original_references:
            references = f"{original_references} {original_message_id}".strip()
        else:
            references = original_message_id
        message['References'] = references

        message['Message-ID'] = f"<{uuid.uuid4()}@gmail.com>"

    body = {
        'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    }

    if thread_id:
        body['threadId'] = thread_id
    return body