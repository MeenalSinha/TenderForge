# TenderForge Proposal Revision Management & Quality Validation

## 1. Overview & Objectives

In high-stakes bids, proposals undergo numerous revisions across human authors, review teams, and AI agents. Two critical vulnerabilities exist in this workflow:
1. **Approval Staling**: An executive approves Version 2, but a team member subsequently modifies Section 3 in Version 3 without the executive's knowledge.
2. **Document Hygiene Defects**: Submitting proposals containing placeholder markers (e.g., `[TODO: Insert Date]`, `TBD`, `XXX`) or missing ProofLink citations.

The **Proposal Revision & Quality Validation Service** provides complete changelog tracking, automated approval invalidation, and pre-submission hygiene auditing.

---

## 2. Automated Approval Invalidation

Whenever any proposal section content is updated:
1. The service checks the current `proposal.status`.
2. If `status == "approved"`, it is **immediately reset to `"drafting"`**.
3. All linked `ClaimLineage` nodes are flagged for delta-review.
4. A warning event is logged and broadcast to the Switch room:
   > "Proposal approval invalidated due to modification of section 2.1 by user Jane Doe."

This guarantees that an approved proposal package can never contain unreviewed edits.

---

## 3. Line-by-Line Revision Diffing

Using Python's standard `difflib`, the service computes unified diffs across any two historical version snapshots:

```json
{
  "section_number": "2.0",
  "change_type": "MODIFIED",
  "title": "Technical Architecture",
  "diff": "--- v1_2.0\n+++ v2_2.0\n@@ -1,2 +1,3 @@\n-We implement high availability architecture across dual data centers.\n+We implement high availability active-active clustering across three availability zones.\n"
}
```

---

## 4. Pre-Submission Document Quality Auditing

Before a proposal can proceed to final human approval or package export, `validate_proposal_quality()` executes:

1. **Placeholder Pattern Scanner**:
   Regex detection across:
   - `[TODO...]`
   - `[TBD...]`
   - `[INSERT...]`
   - `\bTODO\b`
   - `\bTBD\b`
   - `\bXXX+\b`
   - `<insert...>`
2. **Citation Verification**: Detects factual qualifications or metrics mentioned without an associated `ProofLink` reference.
3. **Word Count & Page Estimates**: Formats page count estimates based on industry-standard 400 words per page.
4. **Formatting Score**:
   - Deducts 15 points per placeholder.
   - Deducts 5 points per uncited factual claim.
   - Proposal fails submission quality if score $< 80.0$ or any unresolved placeholder is present.
