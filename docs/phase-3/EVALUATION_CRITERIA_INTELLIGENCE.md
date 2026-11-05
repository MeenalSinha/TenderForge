# Tender Evaluation Criteria Intelligence Architecture

## 1. Overview & Objective

Tenders are evaluated based on published scoring schemes, formulas, and evaluation rubrics (e.g., QCBS — Quality and Cost Based Selection, Lowest Compliant Commercial, or Weighted Multi-Factor Technical Scoring).

The **Evaluation Criteria Intelligence Service** parses tender documentation, extracts evaluation formulas, structures criteria hierarchies, and establishes maximum attainable marks for each component.

---

## 2. Evaluation Criteria Data Model

Each evaluation criterion is modeled with exact scoring weights:

```json
{
  "criterion_code": "CRIT-TECH-01",
  "title": "Technical Architecture & System Design",
  "category": "Technical",
  "weight_percentage": 30.0,
  "max_marks": 30.0,
  "description": "Comprehensiveness of proposed architecture, modularity, security, and scalability.",
  "mandatory": true,
  "scoring_rules": {
    "excellent": "Full modular architecture with high availability and security certification.",
    "acceptable": "Standard multi-tier architecture meeting minimum SLA requirements.",
    "poor": "Vague architecture with unaddressed single points of failure."
  }
}
```

---

## 3. Extraction & Evaluation Rubrics

The service extracts criteria across 5 major categories:

1. **Technical Architecture & Specifications**: Modular design, interoperability, SLAs, security posture, scalability.
2. **Past Performance & Experience**: Relevance of past enterprise references, scale, client commendations.
3. **Management & Methodology**: Agile delivery, WBS, QA protocols, risk management plans, key personnel qualifications.
4. **Commercial & Financial**: BOQ transparency, unit rate reasonableness, lifecycle support costs.
5. **Statutory & Compliance**: ISO standards, local content compliance, sustainability covenants.

---

## 4. Integration with Proposal Optimization

By linking each `EvaluationCriteria` record directly to proposal sections:
- TenderForge computes the **Response Coverage Matrix** (Complete, Partial, Weak, Missing).
- Gaps where criteria have no corresponding proposal sections are automatically identified.
- Proposal writers receive actionable recommendations to maximize the score allocated by the evaluation committee.
