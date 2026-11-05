# TenderForge Deadline and Notification Intelligence

## 1. Overview & Architecture

Missing a procurement deadline results in immediate disqualification with zero recourse. Tenders typically specify multiple intermediate milestone dates:
1. **Pre-Bid Conference Date**
2. **Clarification / Query Submission Cutoff**
3. **Corrigendum / Addendum Issuance Date**
4. **Technical Bid Submission Deadline**
5. **Commercial Bid Submission Deadline**
6. **Bid Validity Horizon** (e.g., 90 or 180 days).

The **Deadline and Notification Intelligence Service** maintains an auditable milestone register, handles timezone-aware countdowns, and broadcasts proactive alerts to Switch war rooms.

---

## 2. Milestone Data Model & Timezone Handling

Deadlines are stored in UTC with explicit original timezone tagging:
- `deadline_date`: Normalized UTC datetime.
- `timezone_name`: Origin timezone (e.g., `America/New_York`, `Asia/Kolkata`, `Europe/London`).
- `is_mandatory`: Boolean indicating whether missing the date causes disqualification.
- `reminder_intervals_hours`: List of notification trigger hours (e.g., `[168, 72, 24, 2]`).
- `status`: `Upcoming`, `Approaching` ($\le 48$ hours), `Completed`, `Missed`.

---

## 3. Switch Room Proactive Reminders

The background notification scanner periodically checks active deadlines against the current time. When an approaching milestone enters a configured reminder window:

```markdown
⏰ **DEADLINE REMINDER**: 'Final JADC2 RFP Technical Submission' (Technical Bid Submission)
- Remaining: approximately 23 hour(s)
- Target Date: 2026-11-26 15:00 UTC
- Mandatory: YES
```

The reminder is posted directly to the Switch collaboration room associated with the tender workspace, alerting human reviewers and agents.
