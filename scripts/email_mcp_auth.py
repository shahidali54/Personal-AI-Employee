#!/usr/bin/env python3
"""
Gmail MCP Authentication - One-time authorization for Gmail API.

Run this script first to authorize the Email MCP server.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    import pickle
except ImportError:
    print("Missing dependencies. Install with:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.draft',
    'https://www.googleapis.com/auth/gmail.labels'
]

def main():
    """Run OAuth2 flow to authorize Gmail API."""
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    token_path = os.getenv('GMAIL_TOKEN_PATH', 'token.json')

    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        print(f"\n❌ Error: credentials.json not found at: {credentials_path}")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print(f"6. Place it at: {credentials_path}")
        sys.exit(1)

    print("\n📧 Gmail API Authorization")
    print("=" * 40)
    print(f"\nCredentials: {credentials_path}")
    print(f"Token will be saved to: {token_path}")
    print("\nOpening browser for authorization...")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        
        print(f"\n✅ Authorization successful!")
        print(f"📁 Token saved to: {token_path}")
        print("\nYou can now run the Email MCP server:")
        print("   python scripts/email_mcp_server.py")
        
    except Exception as e:
        print(f"\n❌ Authorization failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
