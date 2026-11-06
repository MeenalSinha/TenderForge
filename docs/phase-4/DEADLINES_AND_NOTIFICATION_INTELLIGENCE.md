# TenderForge Phase 4: Deadlines & Notification Intelligence

## 1. Overview & Operational Urgency

Tender submission deadlines are non-negotiable hard boundaries; a submission delivered even one second past the procurement portal cutoff is rejected with zero recourse. TenderForge incorporates an intelligent **Deadline & Milestone Tracking Engine** that automatically calculates countdown clocks, triggers multi-channel alerts, and interfaces with Switch room reminders.

---

## 2. Automated Milestone Extraction

When a tender document is parsed, the engine identifies and schedules the critical procurement calendar:

```
[RFP Published] ---> [Pre-Bid Queries Deadline] ---> [Clarifications Issued]
                             |
                             v
[Internal Draft Complete] ---> [Executive Review] ---> [FINAL SUBMISSION CUTOFF]
```

### Configurable Alert Thresholds (from `config/application.yaml`)
- **T - 14 Days**: Initial Bid/No-Bid Decision & Partner Mobilization.
- **T - 7 Days**: Pre-Bid Clarifications cut-off & Technical Draft Review.
- **T - 72 Hours**: High-Urgency Amber Alert; Financial BOQ lock.
- **T - 24 Hours**: Critical Red Alert; Final compliance check and cryptographic manifest generation.
- **T - 6 Hours**: Emergency War Room Lockdown; Deliverable package assembled for portal upload.

---

## 3. Real-Time UI Countdown & Visual Alerts

```
+-----------------------------------------------------------------------------------------+
|                                DEADLINE INTELLIGENCE                                    |
+-----------------------------------------------------------------------------------------+
| [ALERT: 18h 42m Remaining]  Final Submission Cutoff: 2026-11-06T15:00:00Z               |
+-----------------------------------------------------------------------------------------+
| Milestone Name                 | Scheduled Date & Time  | Status     | Time Delta       |
+--------------------------------+------------------------+------------+------------------+
| Pre-Bid Clarifications Due     | 2026-10-25 17:00 UTC   | COMPLETED  | - 11 days ago    |
| Internal Technical Draft Sign  | 2026-11-03 18:00 UTC   | COMPLETED  | - 2 days ago     |
| Commercial BOQ Executive Lock  | 2026-11-05 12:00 UTC   | COMPLETED  | - 6 hours ago    |
| Final Compliance Audit Signoff | 2026-11-05 22:00 UTC   | IN PROGRESS| DUE IN 2 HOURS   |
| Official Portal Upload Cutoff  | 2026-11-06 15:00 UTC   | PENDING    | 18h 42m REMAINING|
+-----------------------------------------------------------------------------------------+
```

---

## 4. Multi-Agent & Switch Notification Relay
- **Switch War Room Event Push**: Milestone status transitions broadcast automatic notification alerts into the active Switch collaboration room.
- **Agent Task Acceleration**: When time delta reaches `< 72 hours`, agents prioritize remaining incomplete sections and unresolved compliance items over optional styling enhancements.

