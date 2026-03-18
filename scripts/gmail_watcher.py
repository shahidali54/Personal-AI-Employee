#!/usr/bin/env python3
"""
Gmail Watcher - Monitors Gmail for new/important emails.

This watcher extends the base watcher to check Gmail for:
- Unread emails
- Important emails
- Emails matching specific keywords

When new emails are found, action files are created in Needs_Action folder.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Missing dependencies. Install with:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

from base_watcher import BaseWatcher

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new and important emails.
    
    Creates action files in Needs_Action folder for:
    - Unread emails from important contacts
    - Emails with urgent keywords
    - Emails with attachments
    """
    
    def __init__(self, vault_path: str = None, credentials_path: str = None, check_interval: int = None):
        """
        Initialize Gmail watcher.

        Args:
            vault_path: Path to Obsidian vault (default: from env VAULT_PATH)
            credentials_path: Path to Gmail credentials JSON (default: from env GMAIL_CREDENTIALS_PATH)
            check_interval: Seconds between checks (default: from env GMAIL_CHECK_INTERVAL or 120)
        """
        # Use environment variables if not provided
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        if check_interval is None:
            check_interval = int(os.getenv('GMAIL_CHECK_INTERVAL', '120'))
        
        super().__init__(vault_path, check_interval)

        # Look for credentials.json in project root by default
        if credentials_path is None:
            credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
        
        # Try multiple locations if not in env
        if not Path(credentials_path).exists():
            possible_paths = [
                Path(__file__).parent.parent / 'credentials.json',  # Project root
                Path.cwd() / 'credentials.json',  # Current directory
            ]
            for path in possible_paths:
                if path.exists():
                    credentials_path = str(path)
                    break

        self.credentials_path = credentials_path
        self.token_path = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
        self.service = None
        self.processed_ids: set = set()

        # Keywords that indicate urgency
        self.urgent_keywords = ['urgent', 'asap', 'important', 'deadline', 'emergency', 'invoice', 'payment']

        # Important sender domains (customize for your use case)
        self.important_domains = ['@company.com', '@client.com', '@boss.com']

        # Load processed email IDs from log
        self._load_processed_log()

        # Authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                self.logger.info("Requesting new authorization...")
                self.logger.info("Run 'python scripts/email_mcp_auth.py' first")
                raise Exception("Gmail authorization required")
            
            # Save token
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API authenticated")
    
    def _load_processed_log(self):
        """Load list of processed email IDs."""
        log_file = self.vault_path / 'Logs' / 'processed_emails.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                self.processed_ids = set(line.strip() for line in f if line.strip())
    
    def _save_to_log(self, email_id: str):
        """Save processed email ID to log."""
        log_file = self.vault_path / 'Logs' / 'processed_emails.log'
        with open(log_file, 'a') as f:
            f.write(f"{email_id}\n")
    
    def _is_important(self, headers: Dict) -> bool:
        """Check if email is important."""
        subject = headers.get('Subject', '').lower()
        from_email = headers.get('From', '').lower()
        
        # Check for urgent keywords
        for keyword in self.urgent_keywords:
            if keyword in subject:
                return True
        
        # Check important domains
        for domain in self.important_domains:
            if domain in from_email:
                return True
        
        return False
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for new emails.
        
        Returns:
            List of email data dictionaries
        """
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            new_emails = []
            
            for msg in messages:
                if msg['id'] in self.processed_ids:
                    continue
                
                # Get full message details
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                
                # Only process important emails
                if self._is_important(headers):
                    new_emails.append({
                        'id': msg['id'],
                        'headers': headers,
                        'snippet': message.get('snippet', '')
                    })
            
            return new_emails
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return []
    
    def create_action_file(self, email: Dict) -> Optional[Path]:
        """
        Create action file for email.
        
        Args:
            email: Email data dictionary
            
        Returns:
            Path to created file
        """
        headers = email['headers']
        filename = self.generate_filename('EMAIL', email['id'][:8])
        filepath = self.needs_action / filename
        
        # Determine priority
        priority = 'high' if any(k in headers.get('Subject', '').lower() for k in ['urgent', 'asap', 'emergency']) else 'normal'
        
        content = f"""{self.create_frontmatter(
            item_type='email',
            from_email=f'"{headers.get("From", "Unknown")}"',
            subject=f'"{headers.get("Subject", "No Subject")}"',
            received=f'"{headers.get("Date", datetime.now().isoformat())}"',
            priority=priority,
            status='pending'
        )}

## Email Content

**From:** {headers.get('From', 'Unknown')}
**To:** {headers.get('To', 'Unknown')}
**Subject:** {headers.get('Subject', 'No Subject')}
**Date:** {headers.get('Date', 'Unknown')}

---

{email.get('snippet', 'No content preview available')}

## Suggested Actions

- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes

```
Add notes about this email here
```

---
*Detected by GmailWatcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*View in Gmail: https://mail.google.com/mail/u/0/#inbox/{email['id']}*
"""
        
        filepath.write_text(content)
        
        # Log as processed
        self.processed_ids.add(email['id'])
        self._save_to_log(email['id'])
        
        return filepath


def main():
    """Run the Gmail watcher."""
    # Use environment variable or command line argument
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Check interval from environment or default (2 minutes = 120 seconds)
    check_interval = int(os.getenv('GMAIL_CHECK_INTERVAL', '120'))

    watcher = GmailWatcher(vault_path, check_interval=check_interval)
    watcher.run()


if __name__ == '__main__':
    main()
