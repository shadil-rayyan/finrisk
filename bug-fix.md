# bug-fix.md

## VFIE (Vulnerability Financial Impact Engine) — Critical Model & Reporting Fixes

This document lists **all known structural issues discovered during early testing of VFIE**.
The goal is for the AI developer agent to **systematically correct flaws in vulnerability interpretation, financial modeling, and reporting logic**.

These are **not feature requests** — they are **critical correctness fixes** required for credible outputs.

---

# 1. Duplicate Vulnerabilities Counted as Independent Risks

## Problem

Static analysis tools (Semgrep etc.) often detect the **same vulnerability pattern across multiple lines or files**.

Example:

```
tracker/compiler/analyze-sizes.js:294
tracker/compiler/analyze-sizes.js:295
tracker/compiler/analyze-sizes.js:314
```

These are treated as **separate vulnerabilities**, inflating risk.

### Consequences

* Artificially inflated vulnerability counts
* Overestimated financial exposure
* Incorrect ROI calculations

### Required Fix

Implement **root-cause clustering**.

Group findings by:

```
vulnerability_type
+ sink_function
+ data_flow_pattern
+ endpoint
```

Example:

```
10 XSS findings
→ cluster into 1 root vulnerability
```

Financial impact should be calculated **once per root cause**, not per instance.

---

# 2. Static Financial Model Per Vulnerability Type

## Problem

Currently:

```
SQL Injection → same impact
XSS → same impact
IDOR → same impact
```

Regardless of context.

Example output:

```
Total Potential Loss: $600M
Expected Loss: $132M
Fix Cost: $660
```

Repeated across multiple findings.

### Consequences

Risk model ignores:

* endpoint sensitivity
* authentication requirement
* data scope
* database access level

### Required Fix

Impact must be derived from **vulnerability context**:

```
endpoint_type
authentication_required
data_scope
database_access
user_privilege_level
```

Example:

| Vulnerability      | Data Scope    | Impact |
| ------------------ | ------------- | ------ |
| Public SQLi        | full DB       | high   |
| Authenticated SQLi | single table  | medium |
| Admin-only XSS     | admin session | low    |

---

# 3. Hardcoded Dataset Size

## Problem

Breach scenarios use **hardcoded record counts**:

```
download all 20,000,000 customer records
```

even when the company context provides a different value.

### Required Fix

Dataset size must always be derived from:

```
estimated_records_stored
```

If unavailable:

```
mark impact as uncertain
```

Never inject default numbers.

---

# 4. Business Context Ignored

Example issue:

Repo analyzed: analytics platform
Scenario generated: payment card theft.

This occurs when AI ignores:

```
product_description
stack_description
industry
```

### Required Fix

Exploit scenarios must incorporate:

```
product_description
industry
data_types
```

Example:

Analytics platform → event data exposure
E-commerce platform → order / payment exposure

---

# 5. Framework vs SaaS Misclassification

Many open-source repos are **frameworks or infrastructure**, not hosted products.

Examples:

* framework
* infrastructure engine
* developer library

### Current incorrect assumption

```
repo == SaaS product
repo == company data owner
```

### Required Fix

Introduce **system role classification**.

User must select:

```
system_role:
- SaaS product
- infrastructure component
- framework/library
- internal tool
- microservice
```

Financial modeling must adapt accordingly.

Example:

Framework vulnerability → affects downstream adopters, not framework maintainers.

---

# 6. Test / Example Code Treated as Production

Scanners detect vulnerabilities in:

```
tests/
examples/
docs/
dev-tools/
```

### Current issue

These are treated as **production attack surfaces**.

### Required Fix

Ignore or downgrade findings in:

```
/tests
/examples
/docs
/dev
/scripts
```

These should be labeled:

```
non-production code
```

and excluded from financial modeling.

---

# 7. Dev Credentials Misidentified as Real Secrets

Open-source repos commonly contain:

```
.env.example
API_KEY="test123"
PASSWORD="changeme"
```

These are **documentation placeholders**.

### Required Fix

Credential detection must verify:

```
secret_entropy
secret_usage
environment_context
```

Files matching:

```
.env.example
docker-compose.yml
docs
```

should be marked as **example credentials**.

---

# 8. Infrastructure Components Misinterpreted

Infrastructure repos (search engines, event pipelines) do not store **user account data**.

### Current issue

Engine assumes:

```
customer accounts
payment data
session tokens
```

### Required Fix

Infer system role:

```
search engine
analytics pipeline
message broker
database layer
```

Then adjust:

```
data exposure assumptions
breach narratives
financial impact
```

---

# 9. Authentication Context Missing

Many vulnerabilities require authentication.

Example:

```
/admin/users_controller
```

But engine assumes:

```
public attacker
```

### Required Fix

Infer authentication requirement from:

```
route paths
middleware
role checks
controller namespace
```

Impact model must differentiate:

```
public endpoint
authenticated endpoint
admin endpoint
internal endpoint
```

---

# 10. Database Scope Overestimation

Current model assumes:

```
SQL injection → full database dump
```

Reality:

```
read-only queries
limited tables
row-level security
```

### Required Fix

Estimate accessible data based on:

```
query structure
ORM patterns
table references
endpoint purpose
```

---

# 11. Vulnerability Aggregation Error

Current board summary assumes:

```
all vulnerabilities exploited independently
```

Financial exposure becomes:

```
sum(all_losses)
```

### Required Fix

Risk aggregation must account for:

```
shared exploit paths
duplicate root causes
overlapping breach impact
```

Use:

```
max_loss_per_attack_chain
```

instead of simple addition.

---

# 12. Attack Chain Detection Missing

Multiple vulnerabilities often form chains.

Example:

```
credential leak
→ auth bypass
→ database query
```

Current system reports:

```
Attack Chains: 0
```

### Required Fix

Construct attack graphs:

Nodes:

```
vulnerability
endpoint
privilege escalation
data access
```

Edges:

```
exploit dependency
```

Chains should be ranked by **combined risk**.

---

# 13. Temporary File Paths in Reports

Example output:

```
/tmp/tmp9y3agxj6/spree/admin/users_controller.rb
```

This occurs due to repository cloning.

### Required Fix

Convert paths to:

```
repository-relative paths
```

Example:

```
spree/admin/app/controllers/users_controller.rb:59
```

---

# 14. False Precision in Financial Outputs

Example output:

```
Expected Loss: $328,320
ROI: 951.7×
```

These numbers appear **exact but rely on estimates**.

### Required Fix

Use **ranges instead of precise values**.

Example:

```
Expected Loss: $250k – $400k
Fix Cost: $300 – $600
ROI Range: 500× – 1000×
```

---

# 15. Exploit Probability Not Evidence-Based

Current outputs show probabilities like:

```
18% exploitation likelihood
```

without justification.

### Required Fix

Exploit probability should incorporate:

```
vulnerability type
internet exposure
authentication requirement
exploit availability
historical breach rates
```

Probabilities must include **explainable reasoning**.

---

# 16. Repo Size Explosion

Large repos produce:

```
hundreds of findings
```

Financial modeling may produce absurd totals:

```
$90B expected loss
```

### Required Fix

Introduce:

```
risk normalization
root-cause clustering
impact deduplication
```

Only **unique attack paths** should contribute to total exposure.

---

# Core Principle for All Fixes

The engine must stop modeling vulnerabilities as:

```
source_code_issue → guaranteed company breach
```

Instead model:

```
source_code_issue
→ exploitability
→ reachable data
→ realistic breach scenario
→ financial impact
```

---

# Expected Result After Fixes

Reports should produce:

* realistic vulnerability counts
* contextual breach scenarios
* credible financial ranges
* deduplicated risk totals
* explainable probability models
* accurate exploit chains

This will transform VFIE from a **static vulnerability scanner** into a **credible risk prioritization engine**.
