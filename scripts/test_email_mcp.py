#!/usr/bin/env python3
"""
TEST SCRIPT - Test Email MCP Server

This is a test script for verifying Email MCP server functionality.
Not required for production use.

Usage:
    python scripts/test_email_mcp.py "recipient@example.com" "Subject" "Message body"

Example:
    python scripts/test_email_mcp.py "test@gmail.com" "Hello" "This is a test email"
"""

import os
import sys
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_mcp_server(tool_name: str, arguments: dict):
    """Call MCP server tool."""
    port = os.getenv('EMAIL_MCP_PORT', '8809')
    url = f'http://localhost:{port}'
    
    request_data = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments
        }
    }
    
    try:
        data = json.dumps(request_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('result', {})
            
    except urllib.error.URLError as e:
        print(f"❌ Connection failed: {e}")
        print("\nMake sure Email MCP Server is running:")
        print("   python scripts/email_mcp_server.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def list_tools():
    """List available email tools."""
    port = os.getenv('EMAIL_MCP_PORT', '8809')
    url = f'http://localhost:{port}'
    
    request_data = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/list'
    }
    
    try:
        data = json.dumps(request_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            tools = result.get('result', {}).get('tools', [])
            
            print("\n📧 Available Email Tools:")
            print("-" * 50)
            for tool in tools:
                print(f"  • {tool['name']}: {tool.get('description', 'No description')}")
            print()
            
    except:
        print("❌ Could not connect to Email MCP Server")
        return False
    
    return True


def send_email(to: str, subject: str, body: str, html: bool = False):
    """Send an email via MCP server."""
    print(f"\n📧 Sending email...")
    print(f"   To: {to}")
    print(f"   Subject: {subject}")
    print(f"   Body: {body[:50]}...")
    
    result = call_mcp_server('email_send', {
        'to': to,
        'subject': subject,
        'body': body,
        'html': html
    })
    
    if result is None:
        return False
    
    if result.get('success'):
        print(f"\n✅ Email sent successfully!")
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
        return True
    else:
        print(f"\n❌ Failed to send email")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("📧 Email MCP Server Test")
    print("=" * 60)
    
    # First, check if server is running
    print("\n🔍 Checking Email MCP Server...")
    if not list_tools():
        print("\n❌ Email MCP Server is not running!")
        print("\nStart the server first:")
        print("   python scripts/email_mcp_server.py")
        sys.exit(1)
    
    print("✓ Email MCP Server is running")
    
    # Get email details
    if len(sys.argv) >= 4:
        to = sys.argv[1]
        subject = sys.argv[2]
        body = ' '.join(sys.argv[3:])
    else:
        # Default test email
        to = input("\nEnter recipient email (or press Enter for default): ").strip()
        if not to:
            to = input("No email provided. Enter recipient email: ").strip()
        
        subject = "Test Email from AI Employee"
        body = """Hello!

This is a test email sent from the AI Employee Silver Tier system.

If you're reading this, the Email MCP integration is working correctly! 🎉

Best regards,
AI Employee"""
    
    # Send email
    success = send_email(to, subject, body)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\nCheck your inbox: {to}")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Make sure Gmail authentication is complete")
        print("   Run: python scripts/gmail_auth.py")
        print("2. Check token.json exists")
        print("3. Verify credentials.json is valid")
    
    print()


if __name__ == '__main__':
    main()
