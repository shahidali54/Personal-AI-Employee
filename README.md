# Personal AI Employee - Bronze Tier

This is a Bronze Tier implementation of the Personal AI Employee as described in the hackathon document. This implementation includes the foundational components required for the Bronze Tier.

## Components Included

1. **Obsidian Vault Structure**
   - Dashboard.md - Main dashboard for monitoring the AI Employee
   - Company_Handbook.md - Rules of engagement for the AI
   - Folder structure: /Inbox, /Needs_Action, /Done

2. **File System Watcher**
   - Monitors the Inbox folder for new files
   - Moves files to Needs_Action for processing
   - Creates metadata files for each detected file

3. **Basic Claude Code Integration**
   - Files that demonstrate Claude Code's ability to read from and write to the vault
   - Sample action files that Claude can process

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the File System Watcher**
   ```bash
   python filesystem_watcher.py ./AI_Employee_Vault
   ```

3. **Test Claude Code Integration**
   - Place this vault directory in Claude Code's workspace
   - Claude should be able to read and process files in the vault
   - Test files are provided in the Needs_Action folder

## Bronze Tier Requirements Met

✅ Obsidian vault with Dashboard.md and Company_Handbook.md
✅ One working Watcher script (File system monitoring)
✅ Claude Code successfully reading from and writing to the vault
✅ Basic folder structure: /Inbox, /Needs_Action, /Done
✅ All AI functionality documented for implementation as Agent Skills

## Next Steps

For Silver or Gold Tier implementations, consider adding:
- Gmail watcher
- WhatsApp watcher
- MCP servers for external actions
- Human-in-the-loop approval workflows
