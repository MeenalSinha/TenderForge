# TENDERFORGE — INDEPENDENT BID AUDITOR GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Overview & Objective

The **Independent Bid Auditor Service** (`backend/app/services/audit_service.py`) acts as an adversarial, objective quality-assurance gate. It evaluates proposal drafts independently against:
1. **Original Tender Clauses:** To ensure complete coverage of all mandatory requirements.
2. **Company Evidence Repository:** To verify that every factual assertion is substantiated and uncontradicted.
3. **Format & Integrity Guidelines:** To detect unresolved action markers (`[ACTION REQUIRED]`).

---

## 2. Severity Classification Framework

Audit findings are categorized into four severity tiers:

| Severity | Description | Score Deduction | Impact on Submission |
| :--- | :--- | :---: | :--- |
| **Critical** | Missing mandatory clause, contradicted turnover, expired certificate, unsupported critical claim | **-25.0 pts** | **Blocks submission immediately.** Triggers `Submission Blocked - High Risk`. |
| **Major** | Unconfirmed candidate proof link, weak past project relevance, unresolved `[ACTION REQUIRED]` placeholder | **-10.0 pts** | Requires remediation or formal sign-off. |
| **Minor** | Ambiguous phrasing, minor specification omission, style discrepancy | **-3.0 pts** | Advisory notes; does not block submission. |
| **Advisory** | Best practice recommendations, formatting enhancements | **0.0 pts** | Informational tips for scoring optimization. |

---

## 3. Bid Readiness Score & Submission Verdicts

### 3.1 Bid Readiness Score Formula
$$\text{Readiness Score} = \max\left(0, \min\left(100, \text{Base Score} - \sum \text{Deductions}\right)\right)$$

Where $\text{Base Score} = \left(\frac{\text{Verified Claims}}{\text{Total Claims}}\right) \times 100$.

### 3.2 Submission Verdicts
- **`Ready for Submission`:** Score $\ge 90.0\%$ and zero Critical findings. Unlocks the human approval workflow.
- **`Conditional Approval Required`:** Score $\ge 75.0\%$ and zero Critical findings. Unlocks approval provided the human director explicitly reviews and accepts major findings.
- **`Submission Blocked - High Risk`:** Score $< 75.0\%$ or **any** Critical finding present. Proposal cannot proceed to sign-off without revision.

---

## 4. Auditor Persona Independence

The `@BidAuditor` agent persona is strictly segregated from drafting tools:
- Cannot create or edit proposal sections.
- Has zero incentive to overlook gaps or soften ratings.
- Evaluates drafts blindly against original requirements and evidence.
