#!/usr/bin/env python3
"""
Simple Email Sender - Direct email sending without MCP server.

This script sends emails directly using Gmail API without needing a separate server.

Usage:
    python scripts/simple_email_sender.py "recipient@example.com" "Subject" "Message body"

Example:
    python scripts/simple_email_sender.py "test@gmail.com" "Hello" "This is a test"
"""

import sys
import os
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("\n❌ Missing dependencies!")
    print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client\n")
    sys.exit(1)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    """Authenticate and get Gmail service."""
    credentials_path = Path(os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json'))
    token_path = Path(os.getenv('GMAIL_TOKEN_PATH', 'token.json'))

    # Check credentials
    if not credentials_path.exists():
        print("❌ credentials.json not found!")
        print("\nDownload from Google Cloud Console and place in project root.")
        return None
    
    creds = None
    
    # Load existing token
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except:
            pass
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None
        
        if not creds:
            print("\n📱 Need to authenticate...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save token
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
            print("✓ Authentication successful!")
    
    # Build service
    service = build('gmail', 'v1', credentials=creds)
    return service


def send_email(to: str, subject: str, body: str, html: bool = False):
    """Send email via Gmail API."""
    service = get_gmail_service()
    if not service:
        return False
    
    try:
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message.attach(MIMEText(body, 'html' if html else 'plain'))
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send
        sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        
        print(f"\n✅ Email sent successfully!")
        print(f"   Message ID: {sent_message['id']}")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to send email: {e}")
        return False


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("📧 Simple Email Sender")
    print("=" * 60)
    
    if len(sys.argv) >= 4:
        to = sys.argv[1]
        subject = sys.argv[2]
        body = ' '.join(sys.argv[3:])
    else:
        print("\nEnter email details:")
        to = input("To: ").strip()
        subject = input("Subject: ").strip()
        print("Body (press Enter twice to send):")
        body_lines = []
        while True:
            line = input()
            if line == '':
                break
            body_lines.append(line)
        body = '\n'.join(body_lines)
    
    if not to or not subject:
        print("\n❌ Email and subject are required!")
        sys.exit(1)
    
    # Send email
    success = send_email(to, subject, body)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\nCheck inbox: {to}")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Check credentials.json exists")
        print("2. Run: python scripts/gmail_auth.py")
        print("3. Check internet connection")
    
    print()


if __name__ == '__main__':
    main()
