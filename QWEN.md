# Personal AI Employee

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) - an autonomous AI agent that manages personal and business affairs 24/7. The architecture is **local-first**, using **Claude Code** as the reasoning engine and **Obsidian** (Markdown) as the dashboard/memory.

**Core Concept:** Transform AI from a chatbot into a proactive employee that:
- Monitors Gmail, WhatsApp, and filesystems via "Watcher" scripts
- Creates actionable tasks in an Obsidian vault
- Uses MCP (Model Context Protocol) servers to interact with external systems
- Implements human-in-the-loop approval for sensitive actions
- Runs autonomous multi-step tasks using the "Ralph Wiggum" persistence pattern

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Watchers      │────▶│   Claude Code    │────▶│   MCP Servers   │
│ (Python scripts)│     │  (Reasoning)     │     │  (Actions)      │
│ - Gmail         │     │  - Reads vault   │     │ - Email         │
│ - WhatsApp      │     │  - Creates plans │     │ - Browser       │
│ - Filesystem    │     │  - Writes tasks  │     │ - Calendar      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   Obsidian Vault │
                        │  (Memory/GUI)    │
                        │ - Dashboard.md   │
                        │ - Needs_Action/  │
                        │ - Done/          │
                        └──────────────────┘
```

## Key Components

### 1. Watchers (Perception Layer)
Lightweight Python scripts that monitor external inputs:
- **Gmail Watcher:** Monitors unread/important emails
- **WhatsApp Watcher:** Uses Playwright to monitor WhatsApp Web
- **Filesystem Watcher:** Watches drop folders for new files

### 2. MCP Servers (Action Layer)
Model Context Protocol servers provide "hands" for the AI:
- **Playwright MCP:** Browser automation (navigate, click, fill forms, screenshots)
- **Email MCP:** Send/draft emails
- **Custom MCPs:** For domain-specific actions (payments, social media, etc.)

### 3. Ralph Wiggum Loop (Persistence)
A Stop hook pattern that keeps Claude Code iterating until tasks are complete:
- Intercepts Claude's exit attempt
- Checks if task is marked complete
- Re-injects prompt if work remains

## Available Skills

### browsing-with-playwright
Browser automation skill for web interactions. See `.qwen/skills/browsing-with-playwright/` for:
- Server lifecycle scripts (start/stop)
- MCP client for tool invocation
- Tool reference documentation

## Project Structure

```
Personal-AI-Employee/
├── .qwen/
│   └── skills/
│       └── browsing-with-playwright/
│           ├── SKILL.md              # Skill documentation
│           ├── references/
│           │   └── playwright-tools.md  # Tool schemas
│           └── scripts/
│               ├── mcp-client.py     # Universal MCP client
│               ├── start-server.sh   # Start Playwright MCP
│               ├── stop-server.sh    # Stop Playwright MCP
│               └── verify.py         # Server health check
├── skills-lock.json                  # Skill versioning
└── Personal AI Employee Hackathon 0_...md  # Full architecture doc
```

## Building and Running

### Prerequisites
- **Claude Code:** Active subscription
- **Obsidian:** v1.10.6+ (for vault/dashboard)
- **Python:** 3.13+
- **Node.js:** v24+ LTS
- **Playwright:** `npm install -D @playwright/mcp`

### Playwright MCP Server

```bash
# Start server (keeps browser context alive)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server (closes browser + process)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python scripts/mcp-client.py list -u http://localhost:8808

# Call a tool
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Take a snapshot (accessibility tree)
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_snapshot -p '{}'

# Execute custom Playwright code
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_run_code -p '{"code": "async (page) => { ... }"}'
```

## Development Conventions

### File Naming
- Watcher scripts: `*_watcher.py`
- Approval requests: `APPROVAL_*_<description>.md`
- Action files: `<TYPE>_<id>.md` in `Needs_Action/`

### Human-in-the-Loop Pattern
For sensitive actions, Claude writes an approval file instead of acting:
1. Create `Pending_Annroval/<action>.md` with details
2. User moves file to `/Approved` or `/Rejected`
3. Orchestrator triggers actual action on approval

### Task States
```
/Inbox/          → New unprocessed items
/Needs_Action/   → Items requiring AI attention
/In_Progress/    → Currently being worked on
/Pending_Approval/ → Awaiting human decision
/Done/           → Completed tasks
```

## Hackathon Tiers

| Tier | Description | Time |
|------|-------------|------|
| **Bronze** | Foundation: Obsidian vault, one watcher, basic Claude integration | 8-12h |
| **Silver** | Functional: Multiple watchers, MCP server, HITL workflow | 20-30h |
| **Gold** | Autonomous: Full integration, Odoo accounting, Ralph loop | 40+h |
| **Platinum** | Production: Cloud deployment, 24/7 operation, A2A sync | 60+h |

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_...md` | Complete architecture blueprint (1200+ lines) |
| `skills-lock.json` | Tracks installed skill versions |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation skill docs |
| `scripts/mcp-client.py` | Universal MCP client (HTTP + stdio) |

## Common Workflows

### Form Submission
1. Navigate to page
2. Get snapshot to find element refs
3. Fill form fields using refs
4. Click submit
5. Wait for confirmation
6. Screenshot result

### Data Extraction
1. Navigate to page
2. Get snapshot (contains text content)
3. Use `browser_evaluate` for complex extraction
4. Process results

### Autonomous Task Loop
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task in `/Done`?
5. If no → Block exit, re-inject prompt (loop continues)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |

## Resources

- **Zoom Meetings:** Wednesdays 10:00 PM (starting Jan 7, 2026)
- **YouTube:** https://www.youtube.com/@panaversity
- **Ralph Wiggum Reference:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
