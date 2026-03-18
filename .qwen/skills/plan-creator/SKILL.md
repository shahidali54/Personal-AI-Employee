---
name: plan-creator
description: |
  Plan creation skill for structured task execution. Creates detailed Plan.md files
  in the Plans folder with checkboxes, dependencies, and progress tracking. Use for
  complex multi-step tasks that require organized execution and progress monitoring.
---

# Plan Creator Skill

Create structured plans for complex tasks with progress tracking.

## Overview

The Plan Creator skill helps Qwen Code break down complex tasks into manageable steps with clear checkboxes and progress tracking.

## When to Use

Use Plan Creator when:
- Task has 3+ steps
- Task spans multiple sessions
- Task requires approval at certain stages
- Task has dependencies between steps
- Progress tracking is needed

## Plan File Structure

```markdown
---
created: 2026-03-17T15:00:00Z
type: plan
status: in_progress
priority: high
estimated_duration: 2 hours
actual_duration: -
---

# Plan: [Task Name]

## Objective

Clear statement of what this plan aims to achieve.

## Context

Background information and why this task is needed.

## Steps

- [ ] Step 1: First action
- [ ] Step 2: Second action (depends on Step 1)
- [ ] Step 3: Third action
- [ ] Step 4: Approval required
- [ ] Step 5: Final action

## Dependencies

| Step | Depends On | Status |
|------|------------|--------|
| 2 | 1 | Waiting |
| 3 | 2 | Waiting |
| 4 | 3 | Waiting |

## Resources

- [[Related Document 1]]
- [[Related Document 2]]
- [External Link](https://example.com)

## Risks & Blockers

| Risk | Impact | Mitigation |
|------|--------|------------|
| Risk description | High/Medium/Low | How to mitigate |

## Progress Log

| Time | Update |
|------|--------|
| 15:00 | Plan created, starting Step 1 |
| 15:30 | Step 1 complete, starting Step 2 |

## Completion Criteria

- [ ] All steps completed
- [ ] Approval obtained (if required)
- [ ] Results documented
- [ ] Files moved to Done

---
*Created by Plan Creator Skill*
```

## Usage Pattern

### 1. Qwen Receives Complex Task

```
Task: Process client invoice request
- Generate invoice
- Send via email
- Follow up if not paid in 7 days
```

### 2. Qwen Creates Plan

```markdown
---
created: 2026-03-17T15:00:00Z
type: plan
status: in_progress
---

# Plan: Process Client Invoice Request

## Objective
Generate and send invoice to client, track payment.

## Steps
- [ ] Identify client details from request
- [ ] Calculate invoice amount
- [ ] Generate invoice PDF
- [ ] Create approval request for sending
- [ ] Send invoice via email
- [ ] Log in accounting system
- [ ] Schedule follow-up in 7 days

## Approval Required
- Step 4: Email sending requires human approval
```

### 3. Execute Plan Step by Step

```
Qwen updates plan after each step:
- [x] Step 1: Identified client (ACME Corp)
- [x] Step 2: Calculated amount ($1,500)
- [ ] Step 3: Generating invoice...
```

### 4. Request Approval When Needed

```
Qwen creates: Pending_Approval/EMAIL_invoice_acme.md
User moves to: Approved/
Qwen continues with Step 5
```

### 5. Mark Plan Complete

```
Update plan status: complete
Move to: Done/Plans/
```

## Templates

### Simple Task Plan

```markdown
---
created: {{timestamp}}
type: plan
status: in_progress
---

# Plan: {{task_name}}

## Objective
{{objective}}

## Steps
- [ ] {{step_1}}
- [ ] {{step_2}}
- [ ] {{step_3}}

## Notes
{{additional_context}}
```

### Complex Project Plan

```markdown
---
created: {{timestamp}}
type: plan
status: in_progress
priority: high
estimated_duration: {{duration}}
---

# Plan: {{project_name}}

## Objective
{{objective}}

## Stakeholders
- Owner: {{owner}}
- Reviewer: {{reviewer}}
- Approver: {{approver}}

## Phases

### Phase 1: Discovery
- [ ] Research requirements
- [ ] Gather resources
- [ ] Identify constraints

### Phase 2: Execution
- [ ] Complete task A
- [ ] Complete task B
- [ ] Quality check

### Phase 3: Review
- [ ] Self-review
- [ ] Peer review
- [ ] Incorporate feedback

### Phase 4: Delivery
- [ ] Final approval
- [ ] Deliver to client
- [ ] Document lessons learned

## Timeline

| Phase | Start | End | Status |
|-------|-------|-----|--------|
| Discovery | Date | Date | Done |
| Execution | Date | Date | In Progress |
| Review | Date | Date | Pending |
| Delivery | Date | Date | Pending |
```

## Integration with Orchestrator

Plans are stored in `Plans/` folder:

```
AI_Employee_Vault/
├── Plans/
│   ├── PLAN_invoice_client_a.md
│   ├── PLAN_social_media_campaign.md
│   └── PLAN_quarterly_review.md
├── In_Progress/    # Active plans
└── Done/Plans/     # Completed plans
```

## Progress Tracking

Update plan progress in real-time:

```python
# In Qwen Code, after completing each step:
# 1. Read plan file
# 2. Update checkbox: - [ ] → - [x]
# 3. Add progress log entry
# 4. Write updated plan
```

## Status Values

| Status | Meaning |
|--------|---------|
| `draft` | Plan being created |
| `in_progress` | Actively working |
| `blocked` | Waiting on external factor |
| `pending_approval` | Awaiting human decision |
| `complete` | All steps done |
| `cancelled` | Plan abandoned |

## Best Practices

1. **Create plan before starting** complex tasks
2. **Update after each step** - keep progress current
3. **Link related files** - invoices, emails, documents
4. **Log time spent** - for future estimation
5. **Document blockers** - helps identify patterns
6. **Review completed plans** - continuous improvement

## Example: Email Campaign Plan

```markdown
---
created: 2026-03-17T10:00:00Z
type: plan
status: complete
priority: normal
---

# Plan: Weekly Newsletter Campaign

## Objective
Send weekly newsletter to 500 subscribers.

## Steps
- [x] Draft newsletter content
- [x] Review for errors
- [x] Create approval request
- [x] Incorporate feedback
- [x] Schedule in email platform
- [x] Verify links work
- [x] Send test email
- [x] Confirm send

## Metrics
- Sent: 500 emails
- Open rate: 25% (pending 24h)
- Click rate: 5% (pending 24h)

## Completed
2026-03-17T11:30:00Z - Newsletter sent successfully
```
