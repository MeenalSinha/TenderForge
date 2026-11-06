# Phase 5: 9-Dimension Opportunity Matching & Explainability Engine

## 1. Overview

Tender opportunities require substantial human time to evaluate and prepare. Bidding on misaligned or disqualified tenders drains enterprise resources and reduces overall win rates.

TenderForge implements an **objective, 9-dimension opportunity evaluation engine** that balances qualification rules, strategic alignment, and delivery risk. Crucially, the engine implements **non-compensable mandatory eligibility hard gates**, preventing high scores in soft areas from masking disqualification on critical compliance hurdles.

---

## 2. 9 Evaluation Dimensions

Each dimension is scored on a standardized interval of $[0.0, 100.0]$:

| # | Dimension Name | Default Weight | Description & Evaluation Logic |
| :--- | :--- | :---: | :--- |
| **1** | **Mandatory Eligibility** | 20% | Binary hard gate verification. Scored 100.0 if all mandatory qualification criteria are met; 20.0 if any gate fails. |
| **2** | **Technical Capability** | 18% | Semantic and keyword overlap between organization's core capability tags and the tender's scope/category ($40.0 + 25.0 \times \text{matches}$). |
| **3** | **Past Performance** | 15% | Count and relevance of verified case studies, completed contract records, and client testimonials in the Evidence Vault ($30.0 + 18.0 \times \text{artifacts}$). |
| **4** | **Financial Capacity** | 12% | Compares organization annual turnover against tender estimated budget. Full score (95.0) if turnover $\ge 1.0\times$ budget; 75.0 if $\ge 0.7\times$. |
| **5** | **Resource Availability** | 10% | Operational bandwidth, delivery capacity, and key personnel availability benchmarks (default 75.0). |
| **6** | **Geographic Alignment** | 8% | Cross-references delivery territory requirements against organization operating jurisdictions and physical presence. |
| **7** | **Client Relationship** | 7% | History with the contracting buyer entity. 65.0 baseline with positive adjustments for documented past successful deliveries. |
| **8** | **Strategic Fit** | 5% | Strategic alignment with executive domain priorities and multi-year corporate initiatives. |
| **9** | **Risk vs. Runway Horizon** | 5% | Measures preparation window against deadline: $>15$ days = 85.0; $7-14$ days = 60.0; $<7$ days = 35.0 (Critical rush penalty). |

---

## 3. Mathematical Formulation & Weighted Score

$$\text{Overall Score} = \sum_{i=1}^{9} w_i \cdot S_i, \quad \text{where } \sum_{i=1}^{9} w_i = 1.0$$

### The Non-Compensable Gate Rule (Disqualification Ceiling)
In real-world public procurement, having exceptional technical capability cannot overcome a missing mandatory statutory license, lack of requisite ISO certification, or failure to meet the minimum turnover floor.

If $\text{mandatory\_gates\_passed} = \text{False}$:
$$\text{Overall Score} \leftarrow \min(\text{Overall Score}, 48.0)$$
$$\text{Recommendation Tier} \leftarrow \text{"PURSUIT NOT RECOMMENDED"}$$

---

## 4. Recommendation Tiers

Configured in `config/opportunity_matching.yaml`:

- **Strongly Recommended** ($\text{Score} \ge 75.0$ and All Hard Gates Passed): Immediate priority pursuit.
- **Recommended with Conditions** ($55.0 \le \text{Score} < 75.0$ and All Hard Gates Passed): Viable pursuit; requires mitigation of flagged weaknesses.
- **Pursuit Not Recommended** ($\text{Score} < 55.0$ OR Any Hard Gate Failed): Disqualified or high risk.

---

## 5. Explainability Breakdown

The engine does not output a black-box percentage. Every evaluation populates an explainability structure:

```json
{
  "strengths": [
    "Possesses mandatory required credential: 'ISO 27001'.",
    "Strong financial turnover ($35,000,000) comfortably covers estimated budget of $4,850,000.",
    "Domain capability match: 3 core areas overlap with scope specifications."
  ],
  "weaknesses": [
    "Prior direct contract history with 'State Department of Administrative Services' has not been recorded."
  ],
  "uncertainties": [],
  "gate_failures": [],
  "missing_evidence": []
}
```

If gates fail, `gate_failures` lists the specific unmet criteria and `missing_evidence` specifies the document needed to unlock eligibility.

