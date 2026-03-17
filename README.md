# Personal AI Employee - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A hackathon project for building a "Digital FTE" (Full-Time Equivalent) - an autonomous AI agent that manages personal and business affairs 24/7 using **Qwen Code** as the reasoning engine and **Obsidian** as the dashboard/memory.

## 🥉 Bronze Tier Deliverables

This implementation completes all **Bronze Tier** requirements:

- ✅ **Obsidian vault** with `Dashboard.md` and `Company_Handbook.md`
- ✅ **One working Watcher script** (File System monitoring)
- ✅ **Qwen Code integration** - reads from and writes to the vault
- ✅ **Basic folder structure**: `/Inbox`, `/Needs_Action`, `/Done`
- ✅ **Agent Skills ready** - all AI functionality can be converted to Agent Skills

## 📁 Project Structure

```
Personal-AI-Employee/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and targets
│   ├── Inbox/                  # Drop files here for processing
│   ├── Needs_Action/           # Items requiring AI attention
│   ├── In_Progress/            # Currently being processed
│   ├── Pending_Approval/       # Awaiting human decision
│   ├── Approved/               # Ready for execution
│   ├── Rejected/               # Declined actions
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Activity logs
│   ├── Files/                  # Processed files storage
│   └── Accounting/             # Financial records
│
├── scripts/
│   ├── base_watcher.py         # Abstract base class for watchers
│   ├── filesystem_watcher.py   # File system monitoring script
│   ├── orchestrator.py         # Master orchestration process
│   └── test_watcher.py         # Test script for watcher
│
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **Qwen Code** - Active subscription
- **Obsidian** (optional) - [Download](https://obsidian.md/download)

### Installation

1. **Clone or download this repository**

2. **Verify Python version**
   ```bash
   python --version
   ```

3. **No additional dependencies required** - Bronze Tier uses only Python standard library

### Running the AI Employee

#### Option 1: Run Watcher and Orchestrator Separately

**Terminal 1 - Start the File System Watcher:**
```bash
cd Personal-AI-Employee
python scripts/filesystem_watcher.py ./AI_Employee_Vault
```

**Terminal 2 - Start the Orchestrator:**
```bash
cd Personal-AI-Employee
python scripts/orchestrator.py ./AI_Employee_Vault
```

#### Option 2: Run Watcher Only (Manual Qwen Processing)

```bash
python scripts/filesystem_watcher.py ./AI_Employee_Vault
```

Then manually trigger Qwen Code when files appear in `Needs_Action/`.

### Using the System

1. **Drop a file into `AI_Employee_Vault/Inbox/`**
   - Any file (document, image, etc.)
   - The watcher will detect it within 30 seconds

2. **Watcher creates action file**
   - File is copied to `Files/` folder
   - Action file created in `Needs_Action/`

3. **Orchestrator triggers Qwen**
   - Creates a prompt file in `In_Progress/`
   - Qwen Code processes the task

4. **Qwen processes the task**
   - Reads files from `Needs_Action/`
   - Creates plans in `Plans/`
   - Executes or requests approval
   - Moves completed items to `Done/`

## 📖 Core Concepts

### Architecture: Perception → Reasoning → Action

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Watchers      │────▶│   Qwen Code      │────▶│   MCP Servers   │
│ (Python scripts)│     │  (Reasoning)     │     │  (Actions)      │
│ - Filesystem    │     │  - Reads vault   │     │ - File ops      │
│ - Gmail (Silver)│     │  - Creates plans │     │ - Email (Silver)│
│ - WhatsApp (Silver)│   │  - Writes tasks  │     │ - Browser (Gold)│
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

### Task States

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Drop files here for processing |
| `/Needs_Action` | Items requiring AI attention |
| `/In_Progress` | Currently being processed |
| `/Pending_Approval` | Awaiting human decision |
| `/Approved` | Ready for execution |
| `/Rejected` | Declined actions |
| `/Done` | Completed tasks |

### Human-in-the-Loop Pattern

For sensitive actions, Qwen writes an approval file instead of acting directly:

1. Qwen creates `Pending_Approval/ACTION_description.md` with details
2. User reviews and moves file to `Approved/` or `Rejected/`
3. Orchestrator triggers actual action on approval

## 🔧 Configuration

### Watcher Settings

Edit `scripts/filesystem_watcher.py`:

```python
# Check interval (default: 30 seconds)
check_interval = 30

# Vault path (default: ./AI_Employee_Vault)
vault_path = './AI_Employee_Vault'
```

### Orchestrator Settings

Edit `scripts/orchestrator.py`:

```python
# Check interval (default: 30 seconds)
check_interval = 30

# Auto-start Qwen (uncomment in code)
# subprocess.run(['qwen', '--prompt', prompt_content], ...)
```

## 📝 Example Workflow

### Processing a Document

1. **User drops file**: `report.pdf` into `Inbox/`

2. **Watcher detects and creates**:
   - Copies `report.pdf` to `Files/`
   - Creates `Needs_Action/FILE_report_20260317_120000.md`

3. **Action file content**:
   ```markdown
   ---
   type: file_drop
   original_name: "report.pdf"
   file_path: "Files/report.pdf"
   file_size: "1.25 MB"
   status: pending
   ---

   ## File Dropped for Processing

   **Original Name:** report.pdf
   **Size:** 1.25 MB
   **Location:** `/Files/report.pdf`

   ## Suggested Actions

   - [ ] Review file contents
   - [ ] Categorize file type
   - [ ] Take appropriate action
   - [ ] Move to Done when complete
   ```

4. **Qwen Code processes**:
   - Reads the action file
   - Analyzes the PDF
   - Creates summary in `Briefings/`
   - Moves to `Done/`

## 🧪 Testing

Run the test script to verify the watcher works:

```bash
python scripts/test_watcher.py
```

Expected output:
```
✓ Created action file: FILE_test_document_*.md
✓ Action file verified
✓ File was copied to Files folder
=== Test Complete ===
```

## 📊 Dashboard

The `Dashboard.md` provides real-time status:

- **Pending Tasks**: Items in `Needs_Action/`
- **In Progress**: Items being processed
- **Awaiting Approval**: Items in `Pending_Approval/`
- **Completed Today**: Items moved to `Done/` today

## 🔐 Security

### Credential Handling

- No credentials stored in vault
- Environment variables for API keys (for Silver/Gold tier)
- All actions logged in `Logs/`

### Data Boundaries

- All data stays local in the vault
- No external sync required for Bronze tier
- Files processed remain on your machine

## 🛠️ Troubleshooting

### Watcher not detecting files

1. Check watcher is running: Look for heartbeat logs
2. Verify file is not a `.md` file (excluded by design)
3. Check file wasn't processed before (hash-based dedup)

### Orchestrator not triggering Qwen

1. Check `In_Progress/` for prompt files
2. Verify Qwen Code is installed: `qwen --version`
3. Check logs in `Logs/YYYY-MM-DD.log`

### Dashboard not updating

1. Ensure orchestrator is running
2. Check file permissions on `Dashboard.md`
3. Review orchestrator logs

## 📈 Upgrading to Silver Tier

To extend beyond Bronze:

1. **Add Gmail Watcher** - Monitor Gmail for new emails
2. **Add WhatsApp Watcher** - Monitor WhatsApp Web via Playwright
3. **Add Email MCP** - Send emails autonomously
4. **Add scheduling** - cron/Task Scheduler for daily briefings

## 🎯 Next Steps (Gold Tier)

- [ ] Integrate Odoo accounting via MCP
- [ ] Add Ralph Wiggum loop for autonomous multi-step tasks
- [ ] Implement social media posting
- [ ] Add weekly CEO Briefing generation

## 📚 Resources

- [Full Architecture Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/QwenLM/qwen-code)
- [Obsidian Documentation](https://help.obsidian.md)
- [Model Context Protocol](https://modelcontextprotocol.io)

## 🤝 Contributing

This is a hackathon project. Feel free to:
- Fork and extend for your own use
- Add new watchers (Gmail, WhatsApp, etc.)
- Improve the orchestrator logic
- Add MCP server integrations

## 📄 License

This project is for educational and hackathon purposes. Use at your own risk.

---

**Version:** 0.1 (Bronze Tier)  
**Last Updated:** 2026-03-17  
**Hackathon:** Personal AI Employee Hackathon 0
