#!/usr/bin/env python3
"""
Email MCP Server - Gmail API integration for sending emails.

This server provides email capabilities to Qwen Code via MCP protocol.
"""

import os
import sys
import json
import logging
import base64
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmailMCP')

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class GmailClient:
    """Gmail API client for sending and managing emails."""

    def __init__(self, credentials_path: str = None, token_path: str = None):
        """Initialize Gmail client."""
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path or os.getenv('GMAIL_TOKEN_PATH', 'token.json')
        self.service = None
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
                    logger.error(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                logger.info("Requesting new authorization...")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API authenticated successfully")
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False, attachment: str = None) -> dict:
        """Send an email."""
        try:
            message = self._create_message('me', to, subject, body, html, attachment)
            sent_message = self.service.users().messages().send(userId='me', body=message).execute()
            logger.info(f"Email sent to {to}, message ID: {sent_message['id']}")
            return {'success': True, 'message_id': sent_message['id']}
        except HttpError as e:
            logger.error(f"Failed to send email: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_draft(self, to: str, subject: str, body: str, html: bool = False, attachment: str = None) -> dict:
        """Create a draft email."""
        try:
            message = self._create_message('me', to, subject, body, html, attachment)
            draft = self.service.users().drafts().create(userId='me', body={'message': message}).execute()
            logger.info(f"Draft created, ID: {draft['id']}")
            return {'success': True, 'draft_id': draft['id']}
        except HttpError as e:
            logger.error(f"Failed to create draft: {e}")
            return {'success': False, 'error': str(e)}
    
    def search_emails(self, query: str, max_results: int = 10) -> list:
        """Search emails."""
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            
            email_list = []
            for msg in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                email_list.append({
                    'id': msg['id'],
                    'headers': {h['name']: h['value'] for h in msg_detail['payload']['headers']}
                })
            
            return email_list
        except HttpError as e:
            logger.error(f"Failed to search emails: {e}")
            return []
    
    def read_email(self, message_id: str) -> dict:
        """Read an email."""
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            body = self._get_email_body(message)
            
            return {
                'id': message['id'],
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'body': body,
                'snippet': message.get('snippet', '')
            }
        except HttpError as e:
            logger.error(f"Failed to read email: {e}")
            return {}
    
    def _create_message(self, sender: str, to: str, subject: str, body: str, html: bool, attachment: str):
        """Create email message."""
        if html:
            message = MIMEText(body, 'html')
        else:
            message = MIMEText(body, 'plain')
        
        message['to'] = to
        message['subject'] = subject
        
        if attachment:
            self._add_attachment(message, attachment)
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    def _add_attachment(self, message: MIMEText, file_path: str):
        """Add attachment to email."""
        if not os.path.exists(file_path):
            logger.warning(f"Attachment not found: {file_path}")
            return
        
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(file_path)}"'
            )
            message.attach(part)
    
    def _get_email_body(self, message: dict) -> str:
        """Extract email body."""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode()
        elif 'body' in message['payload']:
            data = message['payload']['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode()
        return ''


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP protocol."""
    
    gmail = None
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
            method = request.get('method', '')
            params = request.get('params', {})
            
            if method == 'tools/call':
                result = self.handle_tool_call(params)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'result': result}).encode())
            elif method == 'tools/list':
                tools = self.list_tools()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'tools': tools}).encode())
            else:
                self.send_error(404, 'Method not found')
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_error(500, str(e))
    
    def handle_tool_call(self, params: dict) -> dict:
        """Handle tool call."""
        tool_name = params.get('name', '')
        arguments = params.get('arguments', {})
        
        logger.info(f"Tool call: {tool_name}")
        
        if tool_name == 'email_send':
            return self.gmail.send_email(
                to=arguments.get('to'),
                subject=arguments.get('subject'),
                body=arguments.get('body'),
                html=arguments.get('html', False),
                attachment=arguments.get('attachment')
            )
        elif tool_name == 'email_draft':
            return self.gmail.create_draft(
                to=arguments.get('to'),
                subject=arguments.get('subject'),
                body=arguments.get('body'),
                html=arguments.get('html', False),
                attachment=arguments.get('attachment')
            )
        elif tool_name == 'email_search':
            return self.gmail.search_emails(
                query=arguments.get('query', ''),
                max_results=arguments.get('max_results', 10)
            )
        elif tool_name == 'email_read':
            return self.gmail.read_email(
                message_id=arguments.get('message_id', '')
            )
        else:
            return {'error': f'Unknown tool: {tool_name}'}
    
    def list_tools(self) -> list:
        """List available tools."""
        return [
            {
                'name': 'email_send',
                'description': 'Send an email via Gmail',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'to': {'type': 'string', 'description': 'Recipient email'},
                        'subject': {'type': 'string', 'description': 'Email subject'},
                        'body': {'type': 'string', 'description': 'Email body'},
                        'html': {'type': 'boolean', 'description': 'Is HTML content'},
                        'attachment': {'type': 'string', 'description': 'Attachment file path'}
                    },
                    'required': ['to', 'subject', 'body']
                }
            },
            {
                'name': 'email_draft',
                'description': 'Create a draft email',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'to': {'type': 'string', 'description': 'Recipient email'},
                        'subject': {'type': 'string', 'description': 'Email subject'},
                        'body': {'type': 'string', 'description': 'Email body'},
                        'html': {'type': 'boolean', 'description': 'Is HTML content'},
                        'attachment': {'type': 'string', 'description': 'Attachment file path'}
                    },
                    'required': ['to', 'subject', 'body']
                }
            },
            {
                'name': 'email_search',
                'description': 'Search emails',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string', 'description': 'Gmail search query'},
                        'max_results': {'type': 'integer', 'description': 'Max results'}
                    }
                }
            },
            {
                'name': 'email_read',
                'description': 'Read an email',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'message_id': {'type': 'string', 'description': 'Email message ID'}
                    },
                    'required': ['message_id']
                }
            }
        ]
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Start Email MCP Server."""
    port = int(os.getenv('EMAIL_MCP_PORT', 8809))

    # Initialize Gmail client
    logger.info("Initializing Gmail client...")
    try:
        gmail = GmailClient()
        MCPRequestHandler.gmail = gmail
        logger.info("Gmail client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Gmail: {e}")
        logger.info("Run 'python scripts/gmail_auth.py' first to authorize")
        sys.exit(1)

    # Start server
    server = HTTPServer(('localhost', port), MCPRequestHandler)
    logger.info(f"Email MCP Server running on http://localhost:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.shutdown()


if __name__ == '__main__':
    main()
