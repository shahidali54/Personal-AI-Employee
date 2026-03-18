---
name: scheduler
description: |
  Scheduler skill for time-based task execution. Integrates with cron (Linux/Mac)
  or Task Scheduler (Windows) to run daily briefings, weekly audits, scheduled posts,
  and recurring tasks. Enables proactive AI operations without manual triggers.
---

# Scheduler Skill

Time-based task execution using system schedulers.

## Overview

The Scheduler skill enables automated, time-based execution of AI Employee tasks:
- **Daily Briefings** - Morning summary of pending items
- **Weekly Audits** - Business review every Monday
- **Scheduled Posts** - Social media at optimal times
- **Recurring Tasks** - Monthly reports, invoices, etc.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  System Timer   │────▶│  Scheduler      │────▶│  Qwen Code      │
│  (cron/Task)    │     │  Script         │     │  Processing     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Obsidian Vault │
                        │  - Dashboard    │
                        │  - Briefings    │
                        └─────────────────┘
```

## Quick Start

### Linux/Mac (cron)

1. **Create scheduler script:**
```bash
#!/bin/bash
# /path/to/ai-employee/scripts/daily_scheduler.sh

cd /path/to/Personal-AI-Employee
python scripts/orchestrator.py ./AI_Employee_Vault --task daily_briefing
```

2. **Add cron job:**
```bash
crontab -e

# Daily briefing at 8 AM
0 8 * * * /path/to/ai-employee/scripts/daily_scheduler.sh

# Weekly audit every Monday 9 AM
0 9 * * 1 /path/to/ai-employee/scripts/weekly_scheduler.sh
```

### Windows (Task Scheduler)

1. **Create batch file:**
```batch
@echo off
cd C:\path\to\Personal-AI-Employee
python scripts\orchestrator.py ./AI_Employee_Vault --task daily_briefing
```

2. **Schedule task:**
   - Open Task Scheduler
   - Create Basic Task
   - Name: "AI Employee Daily Briefing"
   - Trigger: Daily at 8:00 AM
   - Action: Start program
   - Program: `daily_scheduler.bat`

## Scheduled Tasks

### Daily Briefing (8:00 AM)

Generates morning summary:
- Pending tasks count
- Yesterday's completions
- Today's priorities
- Urgent items

**Output:** `Briefings/YYYY-MM-DD_daily_briefing.md`

### Weekly Audit (Monday 9:00 AM)

Reviews past week:
- Revenue summary
- Task completion rate
- Bottlenecks identified
- Proactive suggestions

**Output:** `Briefings/YYYY-MM-DD_weekly_audit.md`

### Monthly Report (1st of month 10:00 AM)

Comprehensive monthly review:
- Financial summary
- Goal progress
- Subscription audit
- Next month planning

**Output:** `Briefings/YYYY-MM_monthly_report.md`

### Social Media Schedule

| Day | Time | Platform | Content Type |
|-----|------|----------|--------------|
| Tue | 10 AM | LinkedIn | Industry insight |
| Wed | 11 AM | LinkedIn | Product update |
| Thu | 10 AM | LinkedIn | Thought leadership |
| Fri | 2 PM | LinkedIn | Weekly roundup |

## Scheduler Scripts

### daily_scheduler.py

```python
#!/usr/bin/env python3
"""Daily Briefing Scheduler"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.orchestrator import Orchestrator

def generate_daily_briefing(vault_path: str):
    """Generate daily briefing document."""
    vault = Path(vault_path)
    briefings = vault / 'Briefings'
    briefings.mkdir(exist_ok=True)
    
    # Get counts
    needs_action = len(list((vault / 'Needs_Action').glob('*.md')))
    done_yesterday = count_done_yesterday(vault / 'Done')
    
    # Create briefing
    today = datetime.now().strftime('%Y-%m-%d')
    content = f"""---
created: {datetime.now().isoformat()}
type: daily_briefing
date: {today}
---

# Daily Briefing: {today}

## Quick Summary

| Metric | Value |
|--------|-------|
| Pending Tasks | {needs_action} |
| Completed Yesterday | {done_yesterday} |

## Pending Items

"""
    
    # List pending items
    for f in (vault / 'Needs_Action').glob('*.md'):
        content += f"- [ ] {f.name}\n"
    
    # Write file
    output = briefings / f'{today}_daily_briefing.md'
    output.write_text(content)
    
    print(f"Daily briefing created: {output}")
    return output

def count_done_yesterday(done_folder: Path) -> int:
    """Count files moved to Done yesterday."""
    # Implementation here
    return 0

if __name__ == '__main__':
    vault_path = sys.argv[1] if len(sys.argv) > 1 else './AI_Employee_Vault'
    generate_daily_briefing(vault_path)
```

### weekly_scheduler.py

```python
#!/usr/bin/env python3
"""Weekly Audit Scheduler"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

def generate_weekly_audit(vault_path: str):
    """Generate weekly audit document."""
    vault = Path(vault_path)
    briefings = vault / 'Briefings'
    briefings.mkdir(exist_ok=True)
    
    # Calculate date range
    today = datetime.now()
    last_week = today - timedelta(days=7)
    
    # Get week's completions
    done_files = list((vault / 'Done').glob('*.md'))
    
    content = f"""---
created: {datetime.now().isoformat()}
type: weekly_audit
period: {last_week.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}
---

# Weekly Audit

## Period
{last_week.strftime('%B %d')} - {today.strftime('%B %d, %Y')}

## Completed This Week

"""
    
    for f in done_files[:20]:  # Last 20 items
        content += f"- [x] {f.name}\n"
    
    content += f"""

## Revenue Summary

*Add revenue data from accounting system*

## Bottlenecks

*Identify tasks that took too long*

## Proactive Suggestions

*AI-generated improvement ideas*

"""
    
    output = briefings / f'{today.strftime("%Y-%m-%d")}_weekly_audit.md'
    output.write_text(content)
    
    print(f"Weekly audit created: {output}")

if __name__ == '__main__':
    vault_path = sys.argv[1] if len(sys.argv) > 1 else './AI_Employee_Vault'
    generate_weekly_audit(vault_path)
```

## Cron Templates

### Basic Templates

```bash
# Daily at 8 AM
0 8 * * * /path/to/daily_scheduler.sh

# Every hour
0 * * * * /path/to/hourly_check.sh

# Every Monday at 9 AM
0 9 * * 1 /path/to/weekly_scheduler.sh

# First of every month at 10 AM
0 10 1 * * /path/to/monthly_scheduler.sh

# Every weekday at 9 AM
0 9 * * 1-5 /path/to/weekday_scheduler.sh
```

### Advanced Templates

```bash
# Every 30 minutes during business hours
*/30 9-17 * * 1-5 /path/to/check_watcher.sh

# Daily with logging
0 8 * * * /path/to/daily_scheduler.sh >> /var/log/ai-employee.log 2>&1

# Weekly with error notification
0 9 * * 1 /path/to/weekly_scheduler.sh || mail -s "Scheduler Error" admin@example.com
```

## Windows Task Scheduler Templates

### PowerShell Script

```powershell
# daily_scheduler.ps1
$ vaultPath = "C:\path\to\AI_Employee_Vault"
$ scriptPath = "C:\path\to\scripts\orchestrator.py"

Start-Process python -ArgumentList $scriptPath, $vaultPath, "--task", "daily_briefing" -Wait
```

### Schedule via PowerShell

```powershell
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "scripts\orchestrator.py ./AI_Employee_Vault --task daily_briefing" `
  -WorkingDirectory "C:\path\to\Personal-AI-Employee"

$trigger = New-ScheduledTaskTrigger -Daily -At 8am

Register-ScheduledTask -TaskName "AI Employee Daily Briefing" `
  -Action $action -Trigger $trigger -User "username"
```

## Integration with Orchestrator

Add task parameter to orchestrator:

```python
# In orchestrator.py
def run_with_task(self, task_type: str):
    """Run specific scheduled task."""
    
    if task_type == 'daily_briefing':
        self.generate_daily_briefing()
    elif task_type == 'weekly_audit':
        self.generate_weekly_audit()
    elif task_type == 'monthly_report':
        self.generate_monthly_report()
    
    # Then continue with normal orchestration
    self.run()
```

## Scheduled Task Outputs

### Daily Briefing Template

```markdown
---
created: 2026-03-17T08:00:00Z
type: daily_briefing
date: 2026-03-17
---

# Daily Briefing: March 17, 2026

## Quick Summary

| Metric | Value |
|--------|-------|
| Pending Tasks | 5 |
| Completed Yesterday | 12 |

## Top Priorities Today

1. Client invoice follow-up
2. Social media post
3. Weekly report prep

## Urgent Items

- [ ] Payment approval required (expires today)
- [ ] Client email response needed

---
*Generated by AI Employee Scheduler*
```

### Weekly Audit Template

```markdown
---
created: 2026-03-17T09:00:00Z
type: weekly_audit
period: 2026-03-10 to 2026-03-17
---

# Weekly Audit

## Revenue

- This Week: $2,450
- MTD: $4,500 (45% of $10,000 target)
- Trend: On track

## Completed Tasks

- 25 tasks completed
- 100% on-time rate
- 0 bottlenecks

## Proactive Suggestions

1. **Cost Optimization**: Notion unused for 45 days - cancel?
2. **Process Improvement**: Automate invoice generation
3. **Growth Opportunity**: Follow up with 3 pending leads

---
*Generated by AI Employee Scheduler*
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check cron/Task Scheduler logs |
| Python not found | Use absolute path to python |
| Permission denied | Grant execute permission |
| Output not created | Check vault path is correct |

## Best Practices

1. **Log everything** - Capture stdout/stderr
2. **Handle errors** - Don't fail silently
3. **Test manually** - Run scripts before scheduling
4. **Monitor execution** - Check logs regularly
5. **Set notifications** - Email on failure
