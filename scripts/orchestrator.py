#!/usr/bin/env python3
"""
Orchestrator - Master process for the AI Employee.

The Orchestrator:
1. Monitors the Needs_Action folder for new tasks
2. Triggers Qwen Code to process pending items
3. Updates the Dashboard with current status
4. Manages the flow of tasks through the system

For Bronze Tier: Triggers Qwen Code processing when files appear in Needs_Action.
"""

import os
import sys
import time
import logging
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code, and the vault.
    """
    
    def __init__(self, vault_path: str = None, check_interval: int = None):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault root (default: from env VAULT_PATH)
            check_interval: Seconds between checks (default: from env ORCHESTRATOR_CHECK_INTERVAL or 30)
        """
        # Use environment variables if not provided
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        if check_interval is None:
            check_interval = int(os.getenv('ORCHESTRATOR_CHECK_INTERVAL', '30'))
        
        self.vault_path = Path(vault_path).absolute()
        self.check_interval = check_interval
        self.logger = logging.getLogger('Orchestrator')
        
        # Vault folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure all folders exist
        for folder in [self.inbox, self.needs_action, self.in_progress, 
                       self.done, self.pending_approval, self.approved, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Dashboard file
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Track processed files to avoid reprocessing
        self.processed_files: set = set()
        
        self.logger.info(f"Orchestrator initialized")
        self.logger.info(f"Vault path: {self.vault_path}")
    
    def count_files(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md'])
    
    def get_pending_tasks(self) -> List[Path]:
        """Get list of pending task files in Needs_Action."""
        if not self.needs_action.exists():
            return []
        
        pending = []
        for f in self.needs_action.iterdir():
            if f.suffix == '.md' and f not in self.processed_files:
                pending.append(f)
        
        return sorted(pending, key=lambda x: x.stat().st_mtime)
    
    def get_approved_tasks(self) -> List[Path]:
        """Get list of approved tasks ready for execution."""
        if not self.approved.exists():
            return []
        
        return [f for f in self.approved.iterdir() if f.suffix == '.md']
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning("Dashboard.md not found")
            return

        # Count items in each folder
        pending_count = self.count_files(self.needs_action)
        in_progress_count = self.count_files(self.in_progress)
        approval_count = self.count_files(self.pending_approval)
        done_today = self.count_done_today()

        # Read current dashboard (UTF-8 encoding for emoji support)
        lines = self.dashboard.read_text(encoding='utf-8').split('\n')

        # Build new dashboard by replacing specific sections
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Update timestamp
            if line.startswith('last_updated:'):
                new_lines.append(f'last_updated: {datetime.now().isoformat()}Z')
                i += 1
                continue
            
            # Replace Quick Status table
            if '| Metric | Value |' in line:
                # Add the new status table
                new_lines.append('| Metric | Value |')
                new_lines.append('|--------|-------|')
                new_lines.append(f'| **Pending Tasks** | {pending_count} |')
                new_lines.append(f'| **In Progress** | {in_progress_count} |')
                new_lines.append(f'| **Awaiting Approval** | {approval_count} |')
                new_lines.append(f'| **Completed Today** | {done_today} |')
                new_lines.append('')  # Add blank line after table
                # Skip old table rows until we hit next section
                i += 1
                while i < len(lines) and (lines[i].startswith('|') or lines[i].strip() == ''):
                    i += 1
                continue
            
            # Replace Inbox list
            if '## 📥 Inbox' in line or '## Inbox' in line:
                new_lines.append(line)
                i += 1
                # Add description line
                while i < len(lines) and not lines[i].startswith('- [ ]'):
                    new_lines.append(lines[i])
                    i += 1
                # Replace list items
                new_lines.append(self._generate_inbox_list())
                new_lines.append('')  # Add blank line after list
                # Skip old list items until next section
                while i < len(lines) and lines[i].startswith('- [ ]'):
                    i += 1
                continue
            
            # Replace Needs Action list
            if '## 🔄 Needs Action' in line or '## Needs Action' in line:
                new_lines.append(line)
                i += 1
                # Add description line
                while i < len(lines) and not lines[i].startswith('- [ ]'):
                    new_lines.append(lines[i])
                    i += 1
                # Replace list items
                new_lines.append(self._generate_needs_action_list())
                new_lines.append('')  # Add blank line after list
                # Skip old list items until next section
                while i < len(lines) and lines[i].startswith('- [ ]'):
                    i += 1
                continue
            
            # Replace Pending Approval list
            if '## ⏳ Pending Approval' in line or '## Pending Approval' in line:
                new_lines.append(line)
                i += 1
                # Add description line
                while i < len(lines) and not lines[i].startswith('- [ ]'):
                    new_lines.append(lines[i])
                    i += 1
                # Replace list items
                new_lines.append(self._generate_approval_list())
                new_lines.append('')  # Add blank line after list
                # Skip old list items until next section
                while i < len(lines) and lines[i].startswith('- [ ]'):
                    i += 1
                continue
            
            new_lines.append(line)
            i += 1

        content = '\n'.join(new_lines)

        # Write updated dashboard (UTF-8 encoding for emoji support)
        self.dashboard.write_text(content, encoding='utf-8')
        self.logger.debug("Dashboard updated")
    
    def _update_section(self, content: str, section_name: str, items: str) -> str:
        """Update a section in the dashboard content."""
        lines = content.split('\n')
        new_lines = []
        in_section = False
        in_list = False
        section_found = False
        
        # Section headers to detect
        section_headers = [
            f'## 📥 {section_name}',
            f'## 🔄 {section_name}',
            f'## ⏳ {section_name}',
            f'## {section_name}'
        ]
        
        for line in lines:
            # Detect section start
            is_section_start = any(header in line for header in section_headers)
            
            if is_section_start and not section_found:
                in_section = True
                section_found = True
                new_lines.append(line)
            elif in_section and line.startswith('- [ ]'):
                if not in_list:
                    in_list = True
                    new_lines.extend(items.split('\n'))
                # Skip old list items
            elif in_section and (line.startswith('---') or (line.startswith('## ') and not any(section_name in line for header in section_headers))):
                in_section = False
                in_list = False
                new_lines.append(line)
            elif not in_list or not in_section:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _generate_inbox_list(self) -> str:
        """Generate inbox items list for dashboard."""
        inbox_files = list(self.inbox.glob('*')) if self.inbox.exists() else []
        if not inbox_files:
            return "- [ ] No items pending"
        
        items = []
        for f in inbox_files[:5]:  # Show max 5 items
            items.append(f"- [ ] {f.name}")
        return '\n'.join(items)
    
    def _generate_needs_action_list(self) -> str:
        """Generate needs action items list for dashboard."""
        pending = self.get_pending_tasks()
        if not pending:
            return "- [ ] No items"
        
        items = []
        for f in pending[:5]:  # Show max 5 items
            items.append(f"- [ ] {f.name}")
        return '\n'.join(items)
    
    def _generate_approval_list(self) -> str:
        """Generate pending approval items list for dashboard."""
        approval_files = list(self.pending_approval.glob('*.md')) if self.pending_approval.exists() else []
        if not approval_files:
            return "- [ ] No approvals pending"
        
        items = []
        for f in approval_files[:5]:
            items.append(f"- [ ] {f.name}")
        return '\n'.join(items)
    
    def count_done_today(self) -> int:
        """Count files moved to Done today."""
        if not self.done.exists():
            return 0
        
        today = datetime.now().strftime('%Y-%m-%d')
        count = 0
        for f in self.done.iterdir():
            if f.suffix == '.md':
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime.strftime('%Y-%m-%d') == today:
                        count += 1
                except:
                    pass
        return count
    
    def log_action(self, action_type: str, details: str, status: str = 'info'):
        """Log an action to the logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.log'
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{status.upper()}] {action_type}: {details}\n"
        
        with open(log_file, 'a') as f:
            f.write(log_entry)
    
    def trigger_qwen_processing(self) -> bool:
        """
        Trigger Qwen Code to process pending items.

        For Bronze Tier: This creates a prompt file that the user can
        give to Qwen Code for processing.

        Returns:
            True if processing was triggered, False otherwise
        """
        pending = self.get_pending_tasks()

        if not pending:
            self.logger.debug("No pending tasks to process")
            return False

        # Create a processing prompt for Qwen Code
        prompt_file = self.vault_path / 'In_Progress' / f'qwen_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        prompt_content = f"""---
created: {datetime.now().isoformat()}
type: qwen_prompt
status: ready
---

# Qwen Code Processing Request

## Instructions

Process all files in `/Needs_Action` folder according to the Company Handbook rules.

## Files to Process

"""

        for f in pending:
            prompt_content += f"- {f.name}\n"

        prompt_content += f"""

## Expected Workflow

1. Read each file in /Needs_Action
2. Understand the task/request
3. Create a plan in /Plans if needed
4. Execute the task or create approval request in /Pending_Approval
5. Move completed items to /Done

## Company Handbook

Refer to [[Company_Handbook]] for rules and guidelines.

---
*Generated by Orchestrator at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        prompt_file.write_text(prompt_content)
        self.logger.info(f"Created Qwen prompt: {prompt_file.name}")

        # Log the action
        self.log_action(
            'qwen_trigger',
            f'Created prompt for {len(pending)} pending tasks',
            'info'
        )

        # Optionally: Auto-start Qwen Code if available
        # Uncomment the following lines to auto-start Qwen
        """
        try:
            subprocess.run(
                ['qwen', '--prompt', prompt_content],
                cwd=str(self.vault_path),
                capture_output=True
            )
            self.logger.info("Qwen Code processing started")
        except Exception as e:
            self.logger.warning(f"Qwen Code not available: {e}")
        """

        return True
    
    def process_approved_tasks(self):
        """Process tasks that have been approved."""
        approved = self.get_approved_tasks()

        for task_file in approved:
            self.logger.info(f"Processing approved task: {task_file.name}")
            
            # Read the approved task (UTF-8 encoding)
            content = task_file.read_text(encoding='utf-8')
            
            # Execute the approved action (for Bronze Tier, just log it)
            self.log_action(
                'approved_task',
                f'Executing: {task_file.name}',
                'success'
            )
            
            # Move to Done
            dest = self.done / task_file.name
            task_file.rename(dest)
            self.logger.info(f"Moved to Done: {dest.name}")
    
    def run(self):
        """Main run loop for the orchestrator."""
        self.logger.info("Starting Orchestrator")
        self.logger.info(f"Monitoring vault: {self.vault_path}")

        try:
            while True:
                try:
                    # Update dashboard
                    self.update_dashboard()

                    # Trigger Qwen processing if there are pending tasks
                    if self.get_pending_tasks():
                        self.trigger_qwen_processing()

                    # Process approved tasks
                    if self.get_approved_tasks():
                        self.process_approved_tasks()

                    # Log heartbeat
                    self.logger.debug(f"Heartbeat - Pending: {self.count_files(self.needs_action)}, Done today: {self.count_done_today()}")

                except Exception as e:
                    self.logger.error(f"Error in orchestration cycle: {e}", exc_info=True)

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            raise


def main():
    """Run the orchestrator."""
    # Use environment variable or command line argument
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Allow override from command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Check interval from environment or default (30 seconds)
    check_interval = int(os.getenv('ORCHESTRATOR_CHECK_INTERVAL', '30'))

    orchestrator = Orchestrator(vault_path, check_interval)
    orchestrator.run()


if __name__ == '__main__':
    main()
