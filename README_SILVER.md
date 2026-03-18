# Personal AI Employee - Silver Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

Silver Tier implementation of the Personal AI Employee - a functional autonomous assistant with multiple watchers, MCP servers, and human-in-the-loop approvals.

## 🥈 Silver Tier Deliverables

This implementation completes all **Silver Tier** requirements:

- ✅ **All Bronze requirements** plus:
- ✅ **Two or more Watcher scripts** (Gmail + WhatsApp + File System)
- ✅ **Automatically Post on LinkedIn** for business promotion
- ✅ **Claude reasoning loop** that creates Plan.md files
- ✅ **One working MCP server** for external action (Email MCP)
- ✅ **Human-in-the-loop approval workflow** for sensitive actions
- ✅ **Basic scheduling** via cron or Task Scheduler
- ✅ **All AI functionality implemented as Agent Skills**

## 📁 Project Structure

```
Personal-AI-Employee/
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── In_Progress/
│   ├── Pending_Approval/       # HITL approval requests
│   ├── Approved/               # Approved actions ready to execute
│   ├── Rejected/               # Rejected actions with reason
│   ├── Done/
│   ├── Plans/                  # Task plans with checkboxes
│   ├── Briefings/              # Daily/Weekly/Monthly briefings
│   ├── Logs/
│   └── Files/
│
├── .qwen/skills/
│   ├── browsing-with-playwright/   # Browser automation
│   ├── email-mcp/                  # Email sending via Gmail
│   ├── gmail-watcher/              # Gmail monitoring
│   ├── whatsapp-watcher/           # WhatsApp Web monitoring
│   ├── linkedin-posting/           # LinkedIn automation
│   ├── plan-creator/               # Structured planning
│   ├── hitl-approval/              # Human-in-the-loop workflow
│   └── scheduler/                  # Time-based scheduling
│
├── scripts/
│   ├── base_watcher.py             # Base watcher class
│   ├── filesystem_watcher.py       # File system monitoring
│   ├── gmail_watcher.py            # Gmail API watcher
│   ├── whatsapp_watcher.py         # WhatsApp Web watcher
│   ├── orchestrator.py             # Master orchestration
│   ├── email_mcp_server.py         # Email MCP server
│   ├── email_mcp_auth.py           # Gmail OAuth setup
│   ├── linkedin_mcp_server.py      # LinkedIn MCP server
│   ├── daily_scheduler.py          # Daily briefing scheduler
│   └── weekly_scheduler.py         # Weekly audit scheduler
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.13+
- Node.js v24+ LTS
- Qwen Code subscription
- Obsidian (optional)

**For Email MCP:**
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials (`credentials.json`)

**For WhatsApp Watcher:**
- WhatsApp account with phone number
- Playwright installed

**For LinkedIn Posting:**
- LinkedIn account
- Playwright installed

### Installation

1. **Install Python dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install playwright
playwright install chromium
```

2. **Install Node.js dependencies:**
```bash
npm install -D @playwright/mcp
```

3. **Set up Gmail API (for Email MCP):**
```bash
# 1. Download credentials.json from Google Cloud Console
# 2. Run authorization
python scripts/email_mcp_auth.py
```

### Running the AI Employee

#### Start All Watchers

**Terminal 1 - File System Watcher:**
```bash
python scripts/filesystem_watcher.py ./AI_Employee_Vault
```

**Terminal 2 - Gmail Watcher:**
```bash
python scripts/gmail_watcher.py ./AI_Employee_Vault
```

**Terminal 3 - WhatsApp Watcher:**
```bash
python scripts/whatsapp_watcher.py ./AI_Employee_Vault
```

#### Start MCP Servers

**Terminal 4 - Email MCP:**
```bash
python scripts/email_mcp_server.py
# Runs on http://localhost:8809
```

**Terminal 5 - LinkedIn MCP:**
```bash
python scripts/linkedin_mcp_server.py
# Runs on http://localhost:8810
```

#### Start Orchestrator

**Terminal 6 - Orchestrator:**
```bash
python scripts/orchestrator.py ./AI_Employee_Vault
```

### Setting Up Scheduling

#### Linux/Mac (cron)

```bash
# Edit crontab
crontab -e

# Add daily briefing at 8 AM
0 8 * * * cd /path/to/Personal-AI-Employee && python scripts/daily_scheduler.py ./AI_Employee_Vault

# Add weekly audit every Monday 9 AM
0 9 * * 1 cd /path/to/Personal-AI-Employee && python scripts/weekly_scheduler.py ./AI_Employee_Vault
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task: "AI Employee Daily Briefing"
3. Trigger: Daily at 8:00 AM
4. Action: Start program
   - Program: `python.exe`
   - Args: `scripts\daily_scheduler.py ./AI_Employee_Vault`

## 📖 Core Concepts

### Architecture: Perception → Reasoning → Action → Approval

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Watchers      │────▶│   Qwen Code      │────▶│   MCP Servers   │
│ - Gmail         │     │  - Reads vault   │     │ - Email         │
│ - WhatsApp      │     │  - Creates plans │     │ - LinkedIn      │
│ - Filesystem    │     │  - Requests HITL │     │ - Browser       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │   Plans/         │     │  Pending_Approval│
                        │   Briefings/     │     │  → Approved/    │
                        └──────────────────┘     └─────────────────┘
```

### Human-in-the-Loop Workflow

For sensitive actions (payments, emails to new contacts, social posts):

```
1. Qwen detects need for approval
2. Creates: Pending_Approval/ACTION_description.md
3. User reviews file content
4. User moves file:
   - To Approved/ → Action executes
   - To Rejected/ → Action cancelled with reason
5. Orchestrator executes approved actions
6. File moved to Done/
```

### Plan Creation Workflow

For complex multi-step tasks:

```
1. Qwen receives complex task
2. Creates: Plans/PLAN_task_name.md
3. Plan contains checkboxes for each step
4. Qwen updates plan after each step
5. Some steps may require approval
6. Plan complete → moved to Done/Plans/
```

## 🔧 Available Skills

### browsing-with-playwright
Browser automation for web interactions.
- Navigate websites
- Fill forms
- Click elements
- Take screenshots
- Extract data

**Usage:** See `.qwen/skills/browsing-with-playwright/SKILL.md`

### email-mcp
Send and manage emails via Gmail API.
- Send emails
- Create drafts
- Search emails
- Read emails
- Add labels

**Usage:** See `.qwen/skills/email-mcp/SKILL.md`

### gmail-watcher
Monitor Gmail for new/important emails.
- Checks every 2 minutes
- Filters by keywords
- Creates action files
- Tracks processed emails

**Usage:** See `.qwen/skills/gmail-watcher/SKILL.md`

### whatsapp-watcher
Monitor WhatsApp Web for urgent messages.
- Checks every 30 seconds
- Keyword detection
- Session-based auth
- Creates action files

**Usage:** See `.qwen/skills/whatsapp-watcher/SKILL.md`

### linkedin-posting
Automate LinkedIn posts for business.
- Create posts
- Schedule posts
- Engage with content
- Get analytics

**Usage:** See `.qwen/skills/linkedin-posting/SKILL.md`

### plan-creator
Create structured plans for complex tasks.
- Step-by-step checkboxes
- Progress tracking
- Dependencies
- Time logging

**Usage:** See `.qwen/skills/plan-creator/SKILL.md`

### hitl-approval
Human-in-the-loop approval workflow.
- Approval request files
- Pending/Approved/Rejected folders
- Risk assessment
- Expiration handling

**Usage:** See `.qwen/skills/hitl-approval/SKILL.md`

### scheduler
Time-based task execution.
- Daily briefings
- Weekly audits
- Monthly reports
- Scheduled posts

**Usage:** See `.qwen/skills/scheduler/SKILL.md`

## 📝 Example Workflows

### Workflow 1: Email Invoice Request

```
1. Gmail Watcher detects: "Please send invoice"
2. Creates: Needs_Action/EMAIL_invoice_request.md
3. Orchestrator triggers Qwen
4. Qwen creates plan: Plans/PLAN_generate_invoice.md
5. Qwen executes plan steps:
   - [x] Identify client details
   - [x] Calculate amount
   - [x] Generate invoice PDF
   - [ ] Create approval request (HITL)
6. Creates: Pending_Approval/EMAIL_send_invoice.md
7. User reviews and moves to Approved/
8. Email MCP sends email
9. Plan complete → Done/
```

### Workflow 2: WhatsApp Lead Capture

```
1. WhatsApp Watcher detects: "What are your pricing options?"
2. Keyword "pricing" triggers action
3. Creates: Needs_Action/WHATSAPP_lead_*.md
4. Qwen reads and drafts response
5. Creates: Pending_Approval/WHATSAPP_response_*.md
6. User approves response
7. Response sent via WhatsApp
8. Lead logged in Business_Goals.md
```

### Workflow 3: LinkedIn Business Post

```
1. Scheduler triggers at scheduled time
2. Qwen reads Business_Goals.md for content ideas
3. Drafts LinkedIn post
4. Creates: Pending_Approval/LINKEDIN_post_*.md
5. User reviews content
6. Moves to Approved/
7. LinkedIn MCP posts content
8. Analytics logged
```

### Workflow 4: Daily Briefing

```
1. cron/Task Scheduler triggers at 8 AM
2. daily_scheduler.py runs
3. Counts pending tasks
4. Lists yesterday's completions
5. Identifies today's priorities
6. Creates: Briefings/2026-03-17_daily_briefing.md
7. Updates Dashboard.md
8. Qwen can read briefing and act on items
```

## 🔐 Security

### Credential Management

- Never commit `credentials.json`, `token.json`, or session files
- Use environment variables for paths
- Rotate credentials monthly
- Enable 2FA on all accounts

### Approval Thresholds

| Action | Auto-Approve | Requires HITL |
|--------|-------------|---------------|
| Payments | < $50 (existing) | ≥ $50 or new payee |
| Emails | Known contacts | New contacts, bulk |
| Social Posts | Pre-approved | All new content |
| File Operations | Create, read | Delete, export |

### Audit Logging

All actions logged to `Logs/YYYY-MM-DD.log`:
```json
{
  "timestamp": "2026-03-17T15:30:00Z",
  "action_type": "email_send",
  "target": "client@example.com",
  "approval_status": "approved",
  "result": "success"
}
```

## 🛠️ Troubleshooting

### Gmail Watcher Not Working

1. Check authorization: `python scripts/email_mcp_auth.py`
2. Verify `credentials.json` exists
3. Check Gmail API is enabled in Google Cloud Console
4. Review logs: `Logs/processed_emails.log`

### WhatsApp Watcher Needs QR Scan

1. Run watcher: `python scripts/whatsapp_watcher.py ./AI_Employee_Vault`
2. Wait for QR code prompt
3. Open WhatsApp on phone
4. Settings > Linked Devices > Link a Device
5. Scan QR code
6. Session saved for future use

### LinkedIn Post Not Publishing

1. Check session: Clear `linkedin_session/` and re-login
2. Verify LinkedIn is accessible
3. Check rate limits (max 3 posts/day)
4. Review MCP server logs

### Approval Not Executing

1. Verify file moved to `Approved/` folder
2. Check orchestrator is running
3. Review `Logs/approvals.log`
4. Check file hasn't expired

### Scheduler Not Triggering

1. Verify cron/Task Scheduler is configured
2. Check script permissions (chmod +x)
3. Review system scheduler logs
4. Test manual execution

## 📈 Upgrading to Gold Tier

To extend beyond Silver:

1. **Add Odoo Accounting Integration**
   - Self-hosted Odoo Community
   - MCP server for JSON-RPC API
   - Automated invoice posting

2. **Add Social Media Integrations**
   - Facebook/Instagram posting
   - Twitter (X) integration
   - Cross-platform scheduling

3. **Implement Ralph Wiggum Loop**
   - Autonomous multi-step completion
   - Stop hook pattern
   - File movement detection

4. **Add Error Recovery**
   - Exponential backoff
   - Graceful degradation
   - Watchdog process

## 📚 Resources

- [Full Architecture Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/QwenLM/qwen-code)
- [Obsidian Documentation](https://help.obsidian.md)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart)
- [Playwright Documentation](https://playwright.dev)

## 🤝 Contributing

This is a hackathon project. Feel free to:
- Fork and extend for your own use
- Add new watchers (Twitter, Facebook, etc.)
- Improve MCP servers
- Add more scheduling options
- Enhance HITL workflow

---

**Version:** 0.2 (Silver Tier)  
**Last Updated:** 2026-03-17  
**Hackathon:** Personal AI Employee Hackathon 0
