# TENDERFORGE — TENDER WAR ROOM GUIDE

**Project:** TenderForge — From Tender to Trustworthy Proposal  
**Phase:** Phase 2  
**Date:** November 2026  

---

## 1. Concept: The Tender War Room

The **Tender War Room** is a dedicated, collaborative multi-agent communication channel established for each active procurement opportunity. It connects human bid managers, legal counsels, and technical subject matter experts with five specialized AI agents.

Inside the War Room, collaboration is transparent, auditable, and interactive. Agents communicate in natural language, mention colleagues (`@ComplianceOfficer`, `@EvidenceResearcher`), post progress indicators, and request human decisions.

---

## 2. Room Lifecycle & Channel Mapping

```
Workspace Creation ──► Switch Room Generated ──► Agents Registered ──► Collaboration Loop ──► Human Sign-Off ──► Package Export
(e.g. Federal RFP)     (#tender-rfp-2026)        (5 Bot Personas)     (Mentions & Prompts)    (Digital Hash)       (Submission ZIP)
```

1. **Room Creation:** When a tender is registered, `SwitchRoomManager.create_or_get_room()` creates an isolated channel (e.g. `#tender-rfp-2026-defense`).
2. **Channel Isolation:** Each tender opportunity possesses its own dedicated room. Documents, evidence, draft proposals, and audits cannot leak across rooms.
3. **Agent Registration:** The five specialized agents join the channel as recognized personas with distinct handles, avatars, and role descriptions.
4. **Human Participation:** The Bid Director, Legal Counsel, and Technical Lead join the channel to direct the workflow and make critical decisions.

---

## 3. Interactive Slash Commands

Human team members can direct the war room using interactive slash commands:

| Command | Action Performed | Responsible Agent |
| :--- | :--- | :--- |
| `/analyze` | Deconstructs linked tender documents into structured clauses with page coordinates. | `@TenderAnalyst` |
| `/check-compliance` | Evaluates requirements against evidence and prints the compliance matrix. | `@ComplianceOfficer` |
| `/search-evidence [query]` | Searches company repository for proof records matching a query. | `@EvidenceResearcher` |
| `/draft-proposal [title]` | Generates the 5-chapter evidence-backed proposal and builds DOCX. | `@ProposalArchitect` |
| `/audit [proposal_id]` | Audits proposal draft, computes Readiness Score, and issues verdict. | `@BidAuditor` |
| `/approve [comments]` | Records authorized human approval with SHA-256 digital signature hash. | Human Bid Director |
| `/export` | Generates the final submission ZIP bundle (DOCX, XLSX, audit, certificate). | System / Human |

---

## 4. Collaborative Dialogue Example

```
[System] Tender War Room #tender-rfp-2026-defense created.
[Bid Director] @TenderAnalyst Please analyze the uploaded procurement RFP.
[@TenderAnalyst] Analysis completed for RFP-2026-DEFENSE-01-SPEC.txt. Extracted 6 requirements (3 Eligibility, 2 Technical, 1 Financial). Handing off to @ComplianceOfficer.
[@ComplianceOfficer] Evaluating mandatory eligibility. Turnover requirement is USD 3,000,000. @EvidenceResearcher, please verify our audited revenue.
[@EvidenceResearcher] Audited financial statement (PWC-AUD-2025-09) on file verifies 3-year average turnover of USD $4,933,333. Grounding ProofLink citation [Status: Verified].
[@ComplianceOfficer] All mandatory requirements compliant. Risk profile: LOW. Handing off to @ProposalArchitect.
[@ProposalArchitect] Technical proposal v1.0 drafted with 5 chapters and 12 verified ProofLink citations. DOCX generated. Handing off to @BidAuditor.
[@BidAuditor] Independent audit completed. Readiness score: 100.0%. Verdict: READY FOR SUBMISSION. Awaiting formal human sign-off from @BidDirector.
[Bid Director] /approve All technical clauses and turnover metrics verified. Approved for formal submission.
[System] Digital signature certificate [473d79d1d81b2928...] generated. Final submission package export unlocked.
```
