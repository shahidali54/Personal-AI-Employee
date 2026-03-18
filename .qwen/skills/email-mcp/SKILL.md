---
name: email-mcp
description: |
  Email automation using Gmail API. Send emails, create drafts, search messages,
  and manage labels. Use when tasks require email communication, notifications,
  or email-based workflows. Requires Gmail API credentials setup.
---

# Email MCP (Model Context Protocol)

Send and manage emails via Gmail API.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Gmail API**: `APIs & Services > Library > Gmail API`
4. Create OAuth 2.0 credentials: `APIs & Services > Credentials`
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Authorize First Time

```bash
python scripts/email_mcp_auth.py
# Follow browser prompt to authorize
# token.json will be created automatically
```

## Server Lifecycle

### Start Server

```bash
# Start email MCP server
python scripts/email_mcp_server.py
```

### Stop Server

```bash
# Press Ctrl+C in the terminal running the server
```

## Quick Reference

### Send Email

```bash
python scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{"to": "recipient@example.com", "subject": "Hello", "body": "Message content"}'
```

### Create Draft

```bash
python scripts/mcp-client.py call -u http://localhost:8809 -t email_draft \
  -p '{"to": "recipient@example.com", "subject": "Hello", "body": "Message content"}'
```

### Search Emails

```bash
python scripts/mcp-client.py call -u http://localhost:8809 -t email_search \
  -p '{"query": "is:unread from:boss@company.com"}'
```

### Read Email

```bash
python scripts/mcp-client.py call -u http://localhost:8809 -t email_read \
  -p '{"message_id": "abc123"}'
```

### Add Label

```bash
python scripts/mcp-client.py call -u http://localhost:8809 -t email_label \
  -p '{"message_id": "abc123", "label": "Important"}'
```

## Workflow: Send Email with Attachment

1. Prepare email content
2. Call `email_send` with attachment path
3. Verify send confirmation
4. Log action in vault

```bash
python scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{
    "to": "client@example.com",
    "subject": "Invoice #123",
    "body": "Please find attached invoice.",
    "attachment": "AI_Employee_Vault/Files/invoice_123.pdf"
  }'
```

## Workflow: Email Response to Urgent Message

1. Gmail Watcher detects urgent email
2. Creates action file in `Needs_Action/`
3. Qwen reads action file
4. Calls `email_send` to reply
5. Marks original as read

## Human-in-the-Loop Pattern

For sensitive emails (payments, legal, new contacts):

1. Qwen creates `Pending_Approval/EMAIL_*.md`
2. User reviews and moves to `Approved/`
3. Orchestrator sends email via MCP
4. Moves to `Done/` after sending

## Configuration

### Environment Variables

Create `.env` file:

```env
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json
GMAIL_SENDER_EMAIL=your-email@gmail.com
DRY_RUN=false
```

### Server Config

Edit `scripts/email_mcp_server.py`:

```python
# Port for MCP server
PORT = 8809

# Auto-approve sending (set false for HITL)
AUTO_SEND = False

# Max emails per hour (rate limiting)
RATE_LIMIT = 10
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `credentials.json not found` | Download from Google Cloud Console |
| `token.json expired` | Re-run `email_mcp_auth.py` |
| `Rate limit exceeded` | Wait 1 hour or increase quota |
| `Attachment not found` | Use absolute path |
| `Server not responding` | Check port 8809 is free |

## Security Best Practices

1. **Never commit** `credentials.json` or `token.json` to git
2. Use **limited scope**: `gmail.send`, `gmail.readonly` only
3. Enable **2FA** on Google account
4. Review **sent emails** in Gmail regularly
5. Set **rate limits** to prevent abuse

## Testing

```bash
# Send test email to yourself
python scripts/mcp-client.py call -u http://localhost:8809 -t email_send \
  -p '{"to": "your-email@gmail.com", "subject": "Test", "body": "Email MCP working!"}'
```

Expected: Receive test email within 30 seconds.
