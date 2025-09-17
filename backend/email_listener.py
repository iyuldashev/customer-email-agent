import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import time
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailListener:
    def __init__(self, account_name='default'):
        self.account_name = account_name
        self.token_file = f'token_{account_name}.pickle' if account_name != 'default' else 'token.pickle'
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        creds = None
        
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print(f"Token refreshed for account: {self.account_name}")
                except Exception as e:
                    print(f"Token refresh failed for {self.account_name}: {e}")
                    creds = None
            
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                print(f"New authentication completed for account: {self.account_name}")
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def get_unread_emails(self):
        """Get unread emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread label:INBOX'
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id']
                ).execute()
                
                # Parse email
                email_data = self.parse_email(msg)
                emails.append(email_data)
                
                # Mark as read
                self.service.users().messages().modify(
                    userId='me',
                    id=message['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            
            return emails
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []
    
    def parse_email(self, msg):
        """Extract email data"""
        payload = msg['payload']
        headers = payload.get('headers', [])
        
        email_data = {
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'from': 'unknown@unknown.com',
            'subject': 'No Subject'
        }
        
        for header in headers:
            if header['name'] == 'From':
                # Clean email address for reply safety
                from_email = header['value']
                # Extract email from "Name <email@domain.com>" format
                import re
                match = re.search(r'<([^>]+)>', from_email)
                if match:
                    email_data['from'] = match.group(1)
                elif '@' in from_email:
                    email_data['from'] = from_email.strip()
                else:
                    email_data['from'] = 'noreply@unknown.com'
            elif header['name'] == 'Subject':
                email_data['subject'] = header['value'] or 'No Subject'
        
        # Get body
        body = self.get_message_body(payload)
        email_data['body'] = body or 'No content'
        
        return email_data
    
    def get_message_body(self, payload):
        """Extract email body"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8')
        
        return body
    
    def send_reply(self, to_email, subject, body, thread_id=None):
        """Send reply email"""
        # Don't reply to noreply addresses or invalid emails
        if ('noreply' in to_email.lower() or 
            'no-reply' in to_email.lower() or
            'unknown' in to_email.lower() or
            not '@' in to_email):
            print(f"Skipping reply to: {to_email} (noreply/invalid address)")
            return False
            
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}"
        
        raw = base64.urlsafe_b64encode(
            message.as_bytes()).decode('utf-8')
        
        send_message = {'raw': raw}
        if thread_id:
            send_message['threadId'] = thread_id
        
        try:
            self.service.users().messages().send(
                userId='me', 
                body=send_message
            ).execute()
            print(f"Reply sent to: {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False