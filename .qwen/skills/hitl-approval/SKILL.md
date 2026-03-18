---
name: hitl-approval
description: |
  Human-in-the-Loop approval workflow for sensitive actions. Creates approval
  request files in Pending_Approval folder, waits for human decision (Approved/Rejected),
  and executes approved actions. Essential for payments, sensitive emails, and
  irreversible operations.
---

# HITL Approval Skill

Human-in-the-Loop (HITL) approval workflow for sensitive actions.

## Overview

The HITL Approval skill ensures sensitive actions require human approval before execution. This protects against:
- Unauthorized payments
- Inappropriate communications
- Irreversible actions
- Compliance violations

## How It Works

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Qwen      │────▶│  Create Approval │────▶│   Human      │────▶│  Execute    │
│  Detects    │     │  Request File    │     │  Reviews     │     │  Action     │
│  Need for   │     │  Pending_Approval│     │  Move file   │     │  Approved   │
│  Approval   │     │                  │     │  Approved/   │     │  Rejected/  │
└─────────────┘     └─────────────────┘     └──────────────┘     └─────────────┘
```

## Approval File Structure

```markdown
---
type: approval_request
action: email_send
created: 2026-03-17T15:00:00Z
expires: 2026-03-18T15:00:00Z
status: pending
priority: normal
---

# Approval Request: Send Email

## Action Details

**Action:** Send email via Gmail
**To:** client@example.com
**Subject:** Invoice #123 - $1,500
**From:** your-email@gmail.com

## Context

Client requested invoice for January services. Invoice generated and ready to send.

## Email Content

```
Dear Client,

Please find attached invoice #123 for January 2026 services.
Amount due: $1,500
Due date: February 15, 2026

Thank you for your business!

Best regards,
Your Company
```

## Attachments

- Files/invoice_123_january_2026.pdf

## Risk Assessment

| Factor | Level | Notes |
|--------|-------|-------|
| Financial impact | Low | Standard invoice |
| Reversibility | High | Can send follow-up |
| Relationship | Low | Routine communication |

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder with reason.

---
*Created by HITL Approval Skill*
```

## When Approval is Required

### Always Require Approval

| Action Type | Threshold | Reason |
|-------------|-----------|--------|
| Payments | Any amount | Financial risk |
| New payees | First payment | Fraud prevention |
| Emails | New contacts | Relationship risk |
| Social posts | All posts | Brand reputation |
| File deletions | Any file | Data loss risk |
| Contract changes | Any change | Legal risk |

### Auto-Approved (No HITL)

| Action Type | Conditions |
|-------------|------------|
| Invoice generation | Any amount |
| Email replies | Known contacts, no attachments |
| File creation | Within vault |
| Data read operations | Any |
| Scheduled posts | Pre-approved content |

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/
│   ├── PAYMENT_vendor_abc.md
│   ├── EMAIL_invoice_client.md
│   └── SOCIAL_linkedin_post.md
├── Approved/
│   └── (files moved here for execution)
├── Rejected/
│   └── (files moved here with reason)
└── Logs/
    └── approvals.log
```

## Workflow Example: Payment Approval

### Step 1: Qwen Creates Approval

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Vendor ABC
created: 2026-03-17T15:00:00Z
status: pending
---

# Approval Request: Payment

## Payment Details
- **Amount:** $500.00
- **Recipient:** Vendor ABC
- **Bank:** XXXX1234
- **Reference:** Invoice #789
- **Due Date:** 2026-03-20

## Context
Monthly software subscription. Same vendor paid previously.

## To Approve
Move to /Approved folder
```

### Step 2: Human Reviews

1. Open `Pending_Approval/PAYMENT_vendor_abc.md`
2. Review amount, recipient, purpose
3. Verify against bank statement
4. Decision: Approve or Reject

### Step 3: Human Acts

**To Approve:**
```
Move file: Pending_Approval/ → Approved/
```

**To Reject:**
```
Move file: Pending_Approval/ → Rejected/
Add note: "Duplicate invoice, already paid"
```

### Step 4: Orchestrator Executes

```
Orchestrator detects file in Approved/
Executes payment via MCP server
Logs action
Moves file to Done/
```

## Configuration

### Approval Thresholds

Edit in Company Handbook:

```markdown
## Payment Approval Rules

| Amount | Approval Required |
|--------|-------------------|
| < $50 | Auto-approve (existing vendor) |
| $50-$500 | HITL required |
| > $500 | HITL + 24h cooling period |
```

### Expiration Settings

```markdown
## Approval Expiration

- Standard approvals: 24 hours
- Urgent approvals: 4 hours
- Payment approvals: 48 hours

Expired approvals require re-creation.
```

## Orchestrator Integration

The Orchestrator monitors Approved/ folder:

```python
# In orchestrator.py
def process_approved_tasks():
    approved = get_approved_tasks()
    for task in approved:
        execute_action(task)
        log_action(task)
        move_to_done(task)
```

## Logging

All approvals are logged:

```json
{
  "timestamp": "2026-03-17T15:30:00Z",
  "action_type": "payment",
  "amount": 500.00,
  "recipient": "Vendor ABC",
  "approval_status": "approved",
  "approved_by": "human",
  "execution_status": "success"
}
```

## Templates

### Email Approval

```markdown
---
type: approval_request
action: email_send
created: {{timestamp}}
status: pending
---

# Approval Request: Send Email

## Details
- **To:** {{recipient}}
- **Subject:** {{subject}}
- **Priority:** {{priority}}

## Content
{{email_body}}

## Attachments
{{attachments}}

## Risk Level
{{risk_assessment}}
```

### Payment Approval

```markdown
---
type: approval_request
action: payment
amount: {{amount}}
created: {{timestamp}}
status: pending
---

# Approval Request: Payment

## Details
- **Amount:** ${{amount}}
- **Recipient:** {{recipient}}
- **Bank:** {{bank_details}}
- **Reference:** {{reference}}

## Justification
{{reason}}

## Supporting Documents
{{attachments}}
```

### Social Media Approval

```markdown
---
type: approval_request
action: social_post
platform: {{platform}}
created: {{timestamp}}
status: pending
---

# Approval Request: Social Media Post

## Details
- **Platform:** {{platform}}
- **Content:** {{post_text}}
- **Scheduled:** {{publish_time}}

## Hashtags
{{hashtags}}

## Image/Media
{{media_path}}
```

## Best Practices

1. **Clear context** - Explain why action is needed
2. **Complete details** - Include all relevant information
3. **Risk assessment** - Help human understand implications
4. **Reasonable deadlines** - Set appropriate expiration
5. **Track patterns** - Review approval history for improvements

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not executed | Check file moved to Approved/ |
| Wrong action executed | Review approval file details |
| Approval expired | Re-create approval request |
| File stuck in Pending | Human review required |
