---
name: linkedin-posting
description: |
  LinkedIn automation using Playwright. Create and schedule posts, engage with
  content, and grow your professional network. Use for business promotion,
  lead generation, and professional branding. Requires LinkedIn authentication.
---

# LinkedIn Posting Skill

Automate LinkedIn posts for business promotion and lead generation.

## Prerequisites

### 1. Install Playwright

```bash
npm install -D @playwright/mcp
pip install playwright
playwright install chromium
```

### 2. LinkedIn Account

- Active LinkedIn account
- Company page (optional, for business posts)
- Session stored in `linkedin_session/` folder

## Quick Start

### Start LinkedIn MCP Server

```bash
python scripts/linkedin_mcp_server.py
```

### First-Time Authentication

1. Server opens browser window
2. Log in to LinkedIn
3. Session saved automatically
4. Ready to post

## Tools Available

### `linkedin_post`

Create a new post on LinkedIn.

**Parameters:**
- `content` (string, required): Post text content
- `image_path` (string, optional): Path to image to attach
- `schedule_time` (string, optional): ISO format time for scheduled posting

**Example:**
```bash
python scripts/mcp-client.py call -u http://localhost:8810 -t linkedin_post \
  -p '{"content": "Excited to announce our new AI Employee product! #AI #Automation"}'
```

### `linkedin_schedule_post`

Schedule a post for future publishing.

**Parameters:**
- `content` (string, required): Post text
- `publish_time` (string, required): ISO format datetime
- `image_path` (string, optional): Image path

**Example:**
```bash
python scripts/mcp-client.py call -u http://localhost:8810 -t linkedin_schedule_post \
  -p '{
    "content": "Monday motivation: Automate your workflow with AI!",
    "publish_time": "2026-03-20T09:00:00Z"
  }'
```

### `linkedin_engage`

Engage with posts in your feed (like, comment).

**Parameters:**
- `action` (string): "like" or "comment"
- `comment_text` (string, optional): Comment to post

**Example:**
```bash
python scripts/mcp-client.py call -u http://localhost:8810 -t linkedin_engage \
  -p '{"action": "like"}'
```

### `linkedin_post_analytics`

Get analytics for recent posts.

**Parameters:**
- `days` (integer, optional): Number of days to analyze (default: 7)

**Example:**
```bash
python scripts/mcp-client.py call -u http://localhost:8810 -t linkedin_post_analytics \
  -p '{"days": 7}'
```

## Workflow: Business Promotion Post

1. **Qwen creates draft** based on business goals
2. **Creates approval file**: `Pending_Approval/LINKEDIN_post_*.md`
3. **User reviews** content and timing
4. **Moves to Approved**
5. **Orchestrator posts** via MCP server
6. **Logs result** in vault

## Content Templates

### Product Launch

```
🚀 Exciting News!

We're thrilled to announce [Product Name] - a revolutionary solution that
[brief benefit description].

After [time period] of development, we're ready to help businesses like yours
[key benefit/outcome].

👉 Learn more: [link]

#Innovation #ProductLaunch #[YourIndustry]
```

### Thought Leadership

```
💡 Industry Insight:

[Observation about industry trend]

What we're seeing in [industry]:
• Point 1
• Point 2
• Point 3

The future is [trend prediction]. Is your business ready?

#ThoughtLeadership #[Industry] #FutureOfWork
```

### Customer Success

```
🎉 Customer Success Story!

Helped [Client Type] achieve [impressive result] using our solution.

"The results exceeded our expectations..." - [Client Name]

Ready for similar results? Let's talk!

#CustomerSuccess #Results #Testimonial
```

## Scheduling Best Practices

| Day | Best Time | Content Type |
|-----|-----------|--------------|
| Tuesday | 9-11 AM | Industry insights |
| Wednesday | 10 AM-12 PM | Product updates |
| Thursday | 9-11 AM | Thought leadership |
| Friday | 10 AM | Weekly roundup |

## Human-in-the-Loop Pattern

For all LinkedIn posts:

1. **Qwen drafts** post content
2. **Creates file**: `Pending_Approval/LINKEDIN_post_*.md`
3. **User reviews** for:
   - Brand voice alignment
   - Accuracy of claims
   - Appropriate timing
4. **Approves or rejects**
5. **Posted on approval**

## Configuration

### Environment Variables

```env
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
LINKEDIN_SESSION_PATH=./linkedin_session
DRY_RUN=false
```

### Server Config

```python
# Port for MCP server
PORT = 8810

# Auto-post (set false for HITL)
AUTO_POST = False

# Rate limiting (posts per day)
DAILY_LIMIT = 3
```

## Integration with Orchestrator

```bash
# Orchestrator creates prompt
In_Progress/qwen_prompt_linkedin_*.md

# Qwen processes and creates approval
Pending_Approval/LINKEDIN_post_*.md

# User approves (moves to Approved/)

# Orchestrator executes post
python scripts/linkedin_mcp_server.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Clear session, re-authenticate |
| Post not publishing | Check LinkedIn accessibility |
| Rate limited | Reduce posting frequency |
| Image upload fails | Use absolute path, check file size |
| Session expired | Re-login via browser |

## Security

⚠️ **Important:**
- Never commit session files to git
- Use app-specific passwords if available
- Enable 2FA on LinkedIn account
- Monitor account activity regularly
- Respect LinkedIn Terms of Service

## Testing

```bash
# Test connection
python scripts/mcp-client.py call -u http://localhost:8810 -t linkedin_engage \
  -p '{"action": "like"}'
```

## Compliance

- Follow LinkedIn [User Agreement](https://www.linkedin.com/legal/user-agreement)
- No spam or excessive automation
- Disclose AI assistance where appropriate
- Respect copyright and intellectual property
