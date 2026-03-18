---
name: whatsapp-watcher
description: |
  WhatsApp Web monitoring using Playwright. Monitors WhatsApp Web for new messages
  containing urgent keywords. Creates action files in Needs_Action folder for Qwen Code
  to process. Requires WhatsApp Web session authentication.
---

# WhatsApp Watcher

Monitor WhatsApp Web for urgent messages using Playwright automation.

## Prerequisites

### 1. Install Playwright

```bash
npm install -D @playwright/mcp
pip install playwright
playwright install chromium
```

### 2. WhatsApp Web Setup

- WhatsApp account with active phone number
- First-time: Scan QR code to authenticate session
- Session stored in `whatsapp_session/` folder

## How It Works

1. **Runs continuously** in background (checks every 30 seconds)
2. **Monitors WhatsApp Web** for unread messages
3. **Filters by keywords**: urgent, asap, invoice, payment, help
4. **Creates action files** in `Needs_Action/` folder
5. **Logs processed messages** to avoid duplicates

## Quick Start

### Run WhatsApp Watcher

```bash
python scripts/whatsapp_watcher.py ./AI_Employee_Vault
```

### First-Time Authentication

1. Script opens browser window
2. Scan QR code with your phone (WhatsApp > Linked Devices)
3. Session saved automatically
4. Monitoring starts immediately

## Configuration

### Edit Keywords

In `scripts/whatsapp_watcher.py`:

```python
# Keywords that trigger action file creation
self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'quote']
```

### Change Check Interval

```python
# Check every 30 seconds (default)
check_interval = 30

# Check every minute
check_interval = 60
```

### Session Path

```python
# Default session storage
session_path = './whatsapp_session'

# Custom path
session_path = '/secure/path/whatsapp_session'
```

## Action File Format

When urgent message detected:

```markdown
---
type: whatsapp_message
from: "+1234567890"
received: 2026-03-17T15:00:00
priority: high
status: pending
---

## WhatsApp Message

**From:** +1234567890
**Message:** Urgent: Need invoice for January

## Suggested Actions

- [ ] Reply to message
- [ ] Create invoice
- [ ] Mark as read

---
*Detected by WhatsAppWatcher*
```

## Workflow: Lead Capture

1. **Customer messages**: "Hi, what are your pricing options?"
2. **Watcher detects**: Keyword "pricing" triggers action
3. **Creates file**: `Needs_Action/WHATSAPP_lead_*.md`
4. **Qwen processes**: Reads message, drafts response
5. **Human approves**: Via HITL workflow
6. **Response sent**: Via WhatsApp MCP or manually

## Workflow: Invoice Request

1. **Client messages**: "Can you send me the invoice ASAP?"
2. **Watcher detects**: Keywords "invoice" + "ASAP"
3. **Creates file**: `Needs_Action/WHATSAPP_invoice_*.md`
4. **Qwen processes**: Identifies client, generates invoice
5. **Email sent**: Via Email MCP
6. **WhatsApp reply**: "Invoice sent to your email"

## Session Management

### View Session Status

```bash
ls -la whatsapp_session/
# Should contain:
# - session.json (authentication)
# - Local Storage (browser data)
```

### Clear Session (Re-authenticate)

```bash
rm -rf whatsapp_session/
# Run watcher again to re-authenticate
```

### Backup Session

```bash
cp -r whatsapp_session/ backup_whatsapp_session/
# Restore by copying back
```

## Security Considerations

⚠️ **Important:**

- Session tokens provide full WhatsApp access
- Never commit `whatsapp_session/` to git
- Store session in secure location
- Log out of unused linked devices regularly
- Monitor for suspicious activity

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not showing | Clear session, restart watcher |
| "Session expired" | Re-scan QR code |
| No messages detected | Check WhatsApp Web is accessible |
| Browser crashes | Update Playwright: `npm update @playwright/mcp` |
| Rate limited | Increase check_interval to 60+ seconds |

## Running in Background

### Linux/Mac (systemd)

```ini
# /etc/systemd/system/whatsapp-watcher.service
[Unit]
Description=WhatsApp Watcher
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Personal-AI-Employee
ExecStart=/usr/bin/python3 scripts/whatsapp_watcher.py ./AI_Employee_Vault
Restart=always

[Install]
WantedBy=multi-user.target
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At log on
4. Action: Start program
   - Program: `python.exe`
   - Args: `scripts/whatsapp_watcher.py ./AI_Employee_Vault`

## Integration with Orchestrator

WhatsApp Watcher works with Orchestrator:

```
WhatsApp Watcher → Creates action file → Orchestrator detects → Qwen processes
```

No additional configuration needed - files created in `Needs_Action/` are auto-detected.

## Testing

Send yourself a WhatsApp message with keyword:

```
Test urgent message
```

Expected: Action file created within 30 seconds in `Needs_Action/`

## Limitations

- WhatsApp Web must be accessible (no corporate firewall blocking)
- Session expires periodically (re-authenticate every few weeks)
- Not suitable for high-volume monitoring (rate limits apply)
- WhatsApp Terms of Service apply - use responsibly

## Alternative: WhatsApp Business API

For production use, consider official WhatsApp Business API:
- More reliable than web automation
- Official support
- Higher rate limits
- Requires business verification
