#!/usr/bin/env python3
"""
Gmail Authentication - Quick setup for Gmail API.

This script will:
1. Check if credentials.json exists
2. Open browser for OAuth authorization
3. Save token.json for future use

Usage:
    python scripts/gmail_auth.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError:
    print("\n❌ Missing dependencies!")
    print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client\n")
    sys.exit(1)

# Gmail API scopes for Silver Tier
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.send',      # Send emails
    'https://www.googleapis.com/auth/gmail.labels',    # Manage labels
]

def main():
    """Run Gmail OAuth2 authorization."""

    # Find credentials.json - use environment variable or default
    credentials_path = Path(os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json'))
    token_path = Path(os.getenv('GMAIL_TOKEN_PATH', 'token.json'))

    print("\n📧 Gmail API Authorization")
    print("=" * 50)

    # Check credentials file
    if not credentials_path.exists():
        print(f"\n❌ Error: credentials.json not found!")
        print(f"\nExpected location: {credentials_path.absolute()}")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print(f"6. Place it at: {credentials_path.absolute()}")
        sys.exit(1)

    print(f"\n✓ Found credentials: {credentials_path.absolute()}")
    print(f"✓ Token will be saved to: {token_path.absolute()}")
    
    # Check for existing token
    creds = None
    if token_path.exists():
        print("\n✓ Existing token found")
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds.valid:
                print("✓ Token is valid - already authorized!")
                print("\n✅ Gmail API is ready to use!")
                print("\nTo re-authorize, delete token.json and run again.")
                return
            elif creds.expired and creds.refresh_token:
                print("⚠ Token expired, refreshing...")
                try:
                    creds.refresh(Request())
                    print("✓ Token refreshed successfully!")
                    with open(token_path, 'w') as f:
                        f.write(creds.to_json())
                    print("\n✅ Gmail API is ready to use!")
                    return
                except Exception as e:
                    print(f"⚠ Refresh failed: {e}")
                    creds = None
            else:
                print("⚠ Token invalid, re-authorizing...")
                creds = None
        except Exception as e:
            print(f"⚠ Error reading token: {e}")
            creds = None
    
    # Need new authorization
    print("\n📱 Opening browser for authorization...")
    print("\nSteps:")
    print("1. Browser will open automatically")
    print("2. Sign in with your Google account")
    print("3. Grant permissions when prompted")
    print("4. Browser will redirect to success page")
    print("5. This script will save the token automatically")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        
        # Save token
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        
        print("\n" + "=" * 50)
        print("✅ Authorization successful!")
        print(f"📁 Token saved to: {token_path.absolute()}")
        print("\n🚀 You can now run the Gmail Watcher:")
        print("   python scripts/gmail_watcher.py ./AI_Employee_Vault")
        print("\n🚀 Or run the Email MCP Server:")
        print("   python scripts/email_mcp_server.py")
        
    except Exception as e:
        print(f"\n❌ Authorization failed: {e}")
        print("\nTroubleshooting:")
        print("- Make sure Gmail API is enabled in Google Cloud Console")
        print("- Check that OAuth consent screen is configured")
        print("- Try deleting token.json and running again")
        sys.exit(1)


if __name__ == '__main__':
    main()
