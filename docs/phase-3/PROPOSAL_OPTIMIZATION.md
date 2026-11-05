# TenderForge Proposal Coverage & Optimization Engine

## 1. Executive Summary

A common failure in tender proposals is submitting technically sound text that fails to answer the specific scoring rubrics of the evaluation committee. For instance, a section may explain a system architecture well, but fail to explicitly state the 99.95% uptime SLA or omit the required ISO certification citation, losing critical marks.

The **Proposal Coverage & Optimization Engine** audits draft proposals against the published tender evaluation criteria and generates side-by-side **Before-and-After improvement recommendations**.

---

## 2. Coverage Evaluation Lifecycle

```
[Draft Proposal Sections]       [Published Evaluation Criteria]
           |                                  |
           +----------------+-----------------+
                            |
                            v
          [Proposal Optimization Engine Audit]
                            |
        +-------------------+-------------------+
        | Coverage Status Determination:        |
        | - Complete (Score: 90-100%)           |
        | - Partial  (Score: 50-70%)            |
        | - Weak     (Score: 20-40%)            |
        | - Missing  (Score: 0%)                |
        +-------------------+-------------------+
                            |
                            v
       [Side-by-Side Before/After Optimization Plan]
                            |
        +-------------------+-------------------+
        | Human Review & Acceptance             |
        | - Apply Optimization                  |
        | - Invalidate Approval for Delta-Review|
        +---------------------------------------+
```

---

## 3. Side-by-Side Optimization Recommendations

For every identified deficit, the engine produces an actionable `ProposalOptimization` record:

### Example Optimization Record
- **Criterion**: `CRIT-TECH-01: Technical Architecture & System Design` (30 Marks)
- **Coverage Status**: `Weak`
- **Gap Analysis**: "Section 2.0 lacks explicit uptime SLA guarantees and ISO security citations required by the evaluation rubric."
- **Score Impact**: Estimated current score `15.0 / 30.0` $\rightarrow$ Potential score `28.5 / 30.0`.
- **Before Text**:
  ```markdown
  We implement high availability architecture across dual data centers.
  ```
- **After Text**:
  ```markdown
  We implement high availability active-active clustering across three availability zones.
  
  ### Verified Evidence & Performance Benchmarks
  - Architecture conforms to ISO 27001 security standards [ProofLink: SEC-CERT-01].
  - High availability SLA guaranteed at 99.95% uptime with automated multi-zone failover.
  - Verified delivery metrics from past client deployments show 100% on-time milestone completion.
  ```
- **Improvement Rationale**: "Explicitly quantifying SLAs and citing ISO 27001 ProofLinks addresses the highest tier in the evaluation rubric."

---

## 4. Application & Governance

- Users or agents can invoke `POST /api/v1/optimizations/{id}/apply` to apply the accepted enhancement directly to the live section.
- If the proposal was previously in an `approved` state, modifying text automatically invalidates the approval and requires delta-review, guaranteeing that unreviewed edits are never exported.
