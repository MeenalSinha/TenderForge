# TenderForge Configuration Architecture

## 1. Principle of "Nothing Hardcoded"

Every operational threshold, formula weight, tax rate, risk score boundary, parser rule, and role permission in TenderForge is governed by external configuration files. No business constants are embedded in Python source code.

---

## 2. Configuration Hierarchy

```
  .env / Environment Variables
            |
            v
  config/application.yaml         (Core app, security, logging, workspaces)
  config/document_processing.yaml (MIME types, segmentation, parser rules)
  config/bid_evaluation.yaml      (Dimensions, weights, gates, thresholds)
  config/financial_policies.yaml  (Tax rates, margins, scenarios, currencies)
  config/risk_matrix.yaml         (5x5 severity grid, probability bands, categories)
  config/agents/*.yaml            (5 specialized agent prompts, tools, triggers)
```

---

## 3. Configuration Access via `Settings`

Configuration is loaded through Pydantic `BaseSettings` in `backend/app/core/config.py`:
- `settings.bid_evaluation_config`
- `settings.financial_policies_config`
- `settings.risk_matrix_config`
- `settings.deadlines_config`
- `settings.rbac_config`.

Sensitive keys (e.g. `AI_API_KEY`, database passwords) are masked by `settings.masked_dict()`.
