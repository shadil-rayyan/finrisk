# AGENT.md — Vulnerability Business Impact Engine v3
# Gemini LLM + Full UI + Attack Chain Analysis
# Build this exactly as specified. Every section is actionable.

---

## WHAT THIS BUILDS

A full-stack web application that:
1. Takes a GitHub repo URL + company context via a clean UI
2. Scans the repo with Semgrep
3. Sends each finding to Gemini to assess real exploitability, business context, and attack chains
4. Computes financial impact per vulnerability
5. Renders a management-ready dashboard with executive briefs
6. Produces a board-level summary report

---

## THE CORE PROBLEM THIS SOLVES

Engineers say:    "SQL Injection in payments/api.py — CVE severity HIGH"
Management hears: "Add it to the backlog."

This system says: "22% chance we lose $1.4M this quarter from one unfixed bug.
                   Fix costs 6 hours. We are choosing $480 over $1.4M.
                   Here is the exact press headline if we don't fix it."

---

## STACK

```
Backend:  Python 3.11+, FastAPI, Semgrep CLI, Google Gemini API
Frontend: Single HTML file with vanilla JS (no framework needed)
Storage:  JSON files (no database for MVP)
```

```bash
pip install fastapi uvicorn semgrep gitpython httpx pydantic google-generativeai
```

---

## COMPLETE DIRECTORY STRUCTURE

```
vfie/
├── main.py
├── frontend/
│   └── index.html                    ← FULL UI (built below)
├── engine/
│   ├── __init__.py
│   ├── scanner.py
│   ├── classifier.py
│   ├── probability_model.py
│   ├── impact_model.py
│   ├── expected_loss.py
│   ├── ranker.py
│   ├── gemini_analyzer.py            ← NEW: LLM analysis
│   ├── attack_chain.py               ← NEW: cross-vuln chain detection
│   └── business_brief.py
├── knowledge_base/
│   ├── attack_stories.json
│   ├── bug_taxonomy.json
│   ├── exploit_probability.json
│   ├── breach_costs.json
│   ├── regulatory_models.json
│   └── downtime_estimates.json
├── models/
│   ├── company.py
│   ├── vulnerability.py
│   └── risk_result.py
└── data/
    └── .gitkeep
```

---

## MODELS

### models/company.py

```python
from pydantic import BaseModel
from typing import List, Optional

class CompanyContext(BaseModel):
    company_name: str
    industry: str                        # "finance", "healthcare", "technology", "retail", "saas"
    annual_revenue: float
    monthly_revenue: float
    active_users: int
    arpu: float                          # monthly revenue per user
    engineer_hourly_cost: float
    deployment_exposure: str             # "public", "internal", "private"
    infrastructure_type: str             # "cloud", "on_prem", "hybrid"
    sensitive_data_types: List[str]      # ["PII", "financial", "health", "credentials"]
    regulatory_frameworks: List[str]     # ["GDPR", "PCI_DSS", "HIPAA", "CCPA"]
    estimated_records_stored: int
    estimated_downtime_cost_per_hour: Optional[float] = None
    company_size: str                    # "startup", "mid_size", "enterprise"
    stack_description: Optional[str] = None   # e.g. "Django REST API, PostgreSQL, AWS"
    product_description: Optional[str] = None # e.g. "B2B payments platform"
```

### models/risk_result.py

```python
from pydantic import BaseModel
from typing import Optional, List

class ImpactBreakdown(BaseModel):
    data_breach_cost: float
    incident_response_cost: float
    downtime_cost: float
    regulatory_penalty: float
    reputation_damage: float

class GeminiAnalysis(BaseModel):
    is_exploitable: bool
    exploitability_confidence: str       # "high", "medium", "low"
    exploitability_reasoning: str        # plain English explanation
    business_context: str                # what this endpoint/code actually does
    adjusted_probability: float          # Gemini-adjusted probability (vs table default)
    false_positive_likelihood: str       # "high", "medium", "low"
    recommended_fix: str                 # actual fix code or instructions
    fix_complexity: str                  # "simple", "moderate", "complex"

class AttackChain(BaseModel):
    chain_id: str
    vulnerability_ids: List[str]
    chain_description: str               # plain English attack path
    combined_severity: str               # "critical", "high", "medium"
    combined_expected_loss: float
    chain_steps: List[str]               # step-by-step attack narrative

class RiskResult(BaseModel):
    vulnerability_id: str
    bug_type: str
    file: str
    line: int
    severity: str
    exposure: str
    probability_of_exploit: float        # table-based baseline
    gemini_analysis: Optional[GeminiAnalysis] = None
    effective_probability: float         # final probability after Gemini adjustment
    impact_breakdown: ImpactBreakdown
    total_impact: float
    expected_loss: float
    fix_effort_hours: float
    fix_cost_usd: float
    priority_score: float
    roi_of_fixing: float
    business_brief: str
    attack_chains: Optional[List[str]] = None   # chain IDs this vuln belongs to
```

---

## KNOWLEDGE BASE FILES

### knowledge_base/attack_stories.json

```json
{
  "SQL_INJECTION": {
    "victim_label": "customer financial data",
    "attacker_effort": "low — automated tools find and exploit this in under an hour",
    "detection_difficulty": "hard — SQL injection attacks leave no obvious trace in standard logs",
    "steps": [
      "Attacker discovers our payment API using automated scanning tools (Shodan, Google dorks). Thousands of APIs are scanned this way every day.",
      "They send a crafted request that tricks our database into returning all records instead of just one. No password required. A free tool does this automatically.",
      "In minutes, they download all {records} customer records including {data_types}.",
      "We do not know this happened. They sell the data on dark web markets, use it for fraud, or contact us with a ransom demand."
    ],
    "real_world_analogy": "Like leaving your filing cabinet unlocked in a public lobby. Anyone walking past can take everything inside.",
    "headline_template": "{company} Exposes {records} Customer Records in SQL Injection Attack",
    "comparable_breach": "Heartland Payment Systems — SQL injection through a single web form stole 130 million credit card numbers. $140M in settlements. Stock dropped 77%."
  },
  "HARDCODED_CREDENTIALS": {
    "victim_label": "entire system access",
    "attacker_effort": "extremely low — bots scan public code repositories 24/7 for exactly this",
    "detection_difficulty": "very hard — looks like legitimate access in logs",
    "steps": [
      "Our source code contains an API key or password written directly in the code.",
      "Automated bots scan GitHub, npm, and public repositories constantly for credential patterns. Discovery often happens within hours of exposure.",
      "Attacker uses the credential to authenticate as us — with full system permissions.",
      "They read all data, move money, delete records, or install backdoors. The breach may go undetected for months because they appear as a legitimate user."
    ],
    "real_world_analogy": "Like printing your house keys on your business card.",
    "headline_template": "{company} Suffers Breach After API Keys Found Exposed in Source Code",
    "comparable_breach": "Toyota (2023) — a hardcoded key in code pushed to GitHub exposed 2.15 million customers' vehicle data for 5 years before discovery."
  },
  "AUTH_BYPASS": {
    "victim_label": "all accounts and admin functions",
    "attacker_effort": "medium — requires knowledge of authentication systems but tools exist",
    "detection_difficulty": "medium",
    "steps": [
      "Attacker identifies our login or authentication endpoint.",
      "They send a crafted request that skips the password check by exploiting a logic flaw.",
      "They are now authenticated as any user they choose — including administrators.",
      "From here they access all customer data, change account settings, initiate transactions, or lock out legitimate users."
    ],
    "real_world_analogy": "The front door lock opens if you jiggle the handle in a specific way. A determined person will find it.",
    "headline_template": "{company} Authentication Flaw Allowed Unauthorized Access to {records} Customer Accounts",
    "comparable_breach": "Uber (2022) — an attacker bypassed authentication then used hardcoded admin credentials to access AWS, GCP, and all internal systems. $148M fine, CISO faced criminal charges."
  },
  "XSS": {
    "victim_label": "customer sessions and credentials",
    "attacker_effort": "medium — requires crafting malicious links and targeting users",
    "detection_difficulty": "hard — runs inside user browsers, invisible to server logs",
    "steps": [
      "Attacker crafts a malicious link containing hidden code and sends it to our customers via email or social media.",
      "When a logged-in customer clicks the link, the malicious script runs silently in their browser.",
      "The script steals their session token — functionally equivalent to their password — and sends it to the attacker.",
      "Attacker logs in as the customer without needing their password. Customer has no idea this happened."
    ],
    "real_world_analogy": "Someone slips a listening device into an envelope. When you open it, it starts recording everything in the room.",
    "headline_template": "{company} Customer Accounts Hijacked via Website Security Flaw",
    "comparable_breach": "British Airways (2018) — XSS-related attack injected a script into the payment page. 500,000 customers had card details stolen in real time. £20M ICO fine."
  },
  "IDOR": {
    "victim_label": "all customer records",
    "attacker_effort": "very low — just change a number in the URL",
    "detection_difficulty": "very hard — looks like normal API usage",
    "steps": [
      "Attacker creates a legitimate free account on our platform.",
      "They notice their user ID appears in the URL (e.g. /api/invoices/1042).",
      "They change that number to 1041, 1040... and discover they can access other customers' data with no error.",
      "They write a script that iterates through all IDs and downloads every customer record in the system."
    ],
    "real_world_analogy": "Every hotel room uses sequential key cards. If card 301 opens room 302, a guest can enter every room in the building.",
    "headline_template": "{company} API Flaw Let Any User Access Other Customers' Data",
    "comparable_breach": "Optus (2022) — sequential API IDs let one attacker download 9.8 million customer passport and license records. $1.4B market cap loss overnight."
  },
  "SSRF": {
    "victim_label": "internal infrastructure and cloud credentials",
    "attacker_effort": "medium-high",
    "detection_difficulty": "very hard",
    "steps": [
      "Attacker finds a feature in our app that fetches external URLs — image upload, webhook, PDF generator.",
      "They point that feature at internal addresses: our database, cloud metadata service, internal admin panels.",
      "Our server fetches those internal resources on the attacker's behalf — from the server's perspective it is a legitimate request.",
      "Attacker retrieves cloud credentials or database connection strings and achieves full infrastructure access."
    ],
    "real_world_analogy": "Tricking an employee into faxing confidential internal documents to an outside number by disguising it as a normal work request.",
    "headline_template": "{company} Internal Systems Exposed via Server-Side Request Forgery",
    "comparable_breach": "Capital One (2019) — SSRF vulnerability let an attacker access AWS credentials and steal 106 million customer records. $190M settlement."
  },
  "RCE": {
    "victim_label": "complete server control",
    "attacker_effort": "high — but payoff is total system compromise",
    "detection_difficulty": "varies",
    "steps": [
      "Attacker finds an input point that reaches code execution — a file upload, template renderer, or deserialization endpoint.",
      "They send a crafted payload that causes our server to execute their code.",
      "They now have a shell on our server with the same permissions as our application.",
      "From here: steal all data, install ransomware, pivot to internal systems, or create a persistent backdoor. This is the worst possible outcome."
    ],
    "real_world_analogy": "Handing someone the ability to type commands directly into our servers remotely.",
    "headline_template": "{company} Servers Compromised in Remote Code Execution Attack",
    "comparable_breach": "Equifax (2017) — one unpatched RCE vulnerability. 147M Social Security numbers stolen. $700M settlement — the largest data breach settlement in history."
  },
  "COMMAND_INJECTION": {
    "victim_label": "operating system and all server data",
    "attacker_effort": "low-medium",
    "detection_difficulty": "medium",
    "steps": [
      "Our application passes user input to a system command without sanitizing it.",
      "Attacker appends extra commands using shell syntax (e.g. adding ; rm -rf or ; curl attacker.com).",
      "Our server executes both the intended command and the attacker's command with application permissions.",
      "Attacker can read all data, create backdoors, or destroy systems."
    ],
    "real_world_analogy": "An automated message-reading system that also obeys OS commands embedded in any message.",
    "headline_template": "{company} Systems Compromised via Command Injection in Web Application",
    "comparable_breach": "Accellion (2021) — command injection exploited by Clop ransomware group, breaching 100+ organizations simultaneously."
  },
  "INSECURE_DESERIALIZATION": {
    "victim_label": "server execution and all stored data",
    "attacker_effort": "high — requires crafted payloads",
    "detection_difficulty": "hard",
    "steps": [
      "Our application accepts serialized data (cookies, API payloads, file uploads) and converts it to objects without validating it.",
      "Attacker crafts a malicious payload that, when our server processes it, executes attacker-controlled code.",
      "Attacker gains full server control — equivalent to RCE.",
      "This is especially dangerous because the exploit happens before any business logic validation runs."
    ],
    "real_world_analogy": "Accepting a package from an unknown sender and opening it in the server room — it contains a remote detonator.",
    "headline_template": "{company} Backdoored via Insecure Data Handling Vulnerability",
    "comparable_breach": "Log4Shell (2021) — deserialization-class vulnerability. Estimated $4B in global remediation. Apple, Amazon, governments all affected simultaneously."
  },
  "PATH_TRAVERSAL": {
    "victim_label": "server files including config, credentials, source code",
    "attacker_effort": "low — simple URL manipulation",
    "detection_difficulty": "medium",
    "steps": [
      "Attacker finds a file download or read endpoint in our application.",
      "They manipulate the filename with ../ sequences to navigate outside the intended directory.",
      "They read sensitive server files: application config, private keys, database credentials.",
      "Using retrieved credentials they escalate to full system compromise."
    ],
    "real_world_analogy": "A file request system that lets you request any file on the company network if you phrase the request correctly.",
    "headline_template": "{company} Server Credentials Exposed via File Access Vulnerability",
    "comparable_breach": "Pulse Secure VPN (2020) — path traversal let attackers steal credentials and breach government agencies and defense contractors."
  },
  "WEAK_CRYPTO": {
    "victim_label": "encrypted customer passwords and sensitive data",
    "attacker_effort": "medium — GPU cracking is now cheap and fast",
    "detection_difficulty": "only discovered after a breach",
    "steps": [
      "Our application uses outdated encryption (MD5, SHA1) to store passwords or sensitive data.",
      "Attacker breaches our database via another vulnerability or insider threat.",
      "Despite data being 'encrypted', they crack the weak hashes in hours using commodity hardware and public rainbow tables.",
      "They now have plaintext passwords which customers reuse across banking, email, and other services."
    ],
    "real_world_analogy": "Locking a safe with one of the top 1,000 most common combinations.",
    "headline_template": "{company} Breach Worse Than Expected — Customer Passwords Cracked Due to Weak Encryption",
    "comparable_breach": "LinkedIn (2012) — 6.5M hashes stolen. Because they used unsalted SHA1, 90% were cracked within days and used across the internet."
  },
  "CSRF": {
    "victim_label": "customer account actions performed without their knowledge",
    "attacker_effort": "medium",
    "detection_difficulty": "very hard — appears as legitimate user action",
    "steps": [
      "Attacker crafts a malicious webpage containing a hidden form targeting our application.",
      "When a logged-in customer visits the page, their browser silently submits the form using their active session.",
      "Our server sees a legitimate request from a logged-in user and processes it — a money transfer, password change, or deletion.",
      "The customer had no idea the action was taken on their behalf."
    ],
    "real_world_analogy": "Someone tricks you into signing a contract by hiding it behind a button you think says OK.",
    "headline_template": "{company} Customers' Accounts Manipulated Without Their Knowledge via Website Flaw",
    "comparable_breach": "A CSRF flaw in a major bank allowed attackers to initiate transfers from customers' accounts via a single malicious link sent by email."
  },
  "UNKNOWN": {
    "victim_label": "undetermined assets",
    "attacker_effort": "unknown — requires manual assessment",
    "detection_difficulty": "unknown",
    "steps": [
      "A security issue was detected in the codebase that does not match known patterns.",
      "Manual review by a security engineer is required to assess actual risk.",
      "Until assessed, this should be treated as a potential vulnerability.",
      "Delay in review increases window of exposure if the issue is legitimate."
    ],
    "real_world_analogy": "An unlabelled container in your server room — could be harmless, could be dangerous. Needs inspection.",
    "headline_template": "{company} Security Review Reveals Unassessed Vulnerabilities",
    "comparable_breach": "Unknown security issues are the ones most likely to become breaches — because nobody looked closely enough."
  }
}
```

### knowledge_base/bug_taxonomy.json

```json
{
  "SQL_INJECTION":            { "data_exfiltration": true,  "typical_fix_hours": 6,  "severity_default": "critical" },
  "XSS":                      { "data_exfiltration": false, "typical_fix_hours": 3,  "severity_default": "high"     },
  "AUTH_BYPASS":              { "data_exfiltration": true,  "typical_fix_hours": 12, "severity_default": "critical" },
  "INSECURE_DESERIALIZATION": { "data_exfiltration": true,  "typical_fix_hours": 16, "severity_default": "critical" },
  "SSRF":                     { "data_exfiltration": true,  "typical_fix_hours": 8,  "severity_default": "high"     },
  "IDOR":                     { "data_exfiltration": true,  "typical_fix_hours": 5,  "severity_default": "high"     },
  "RCE":                      { "data_exfiltration": true,  "typical_fix_hours": 20, "severity_default": "critical" },
  "PATH_TRAVERSAL":           { "data_exfiltration": true,  "typical_fix_hours": 4,  "severity_default": "high"     },
  "HARDCODED_CREDENTIALS":    { "data_exfiltration": true,  "typical_fix_hours": 2,  "severity_default": "critical" },
  "CSRF":                     { "data_exfiltration": false, "typical_fix_hours": 4,  "severity_default": "medium"   },
  "OPEN_REDIRECT":            { "data_exfiltration": false, "typical_fix_hours": 2,  "severity_default": "medium"   },
  "COMMAND_INJECTION":        { "data_exfiltration": true,  "typical_fix_hours": 8,  "severity_default": "critical" },
  "WEAK_CRYPTO":              { "data_exfiltration": true,  "typical_fix_hours": 6,  "severity_default": "high"     },
  "INSECURE_RANDOM":          { "data_exfiltration": false, "typical_fix_hours": 2,  "severity_default": "medium"   },
  "UNKNOWN":                  { "data_exfiltration": false, "typical_fix_hours": 4,  "severity_default": "medium"   }
}
```

### knowledge_base/exploit_probability.json

```json
{
  "SQL_INJECTION":             { "PUBLIC": 0.22, "INTERNAL": 0.06, "PRIVATE": 0.01 },
  "XSS":                       { "PUBLIC": 0.18, "INTERNAL": 0.05, "PRIVATE": 0.01 },
  "AUTH_BYPASS":               { "PUBLIC": 0.15, "INTERNAL": 0.05, "PRIVATE": 0.02 },
  "INSECURE_DESERIALIZATION":  { "PUBLIC": 0.12, "INTERNAL": 0.04, "PRIVATE": 0.01 },
  "SSRF":                      { "PUBLIC": 0.14, "INTERNAL": 0.05, "PRIVATE": 0.01 },
  "IDOR":                      { "PUBLIC": 0.20, "INTERNAL": 0.08, "PRIVATE": 0.02 },
  "RCE":                       { "PUBLIC": 0.10, "INTERNAL": 0.03, "PRIVATE": 0.01 },
  "PATH_TRAVERSAL":            { "PUBLIC": 0.16, "INTERNAL": 0.05, "PRIVATE": 0.01 },
  "HARDCODED_CREDENTIALS":     { "PUBLIC": 0.25, "INTERNAL": 0.10, "PRIVATE": 0.03 },
  "CSRF":                      { "PUBLIC": 0.12, "INTERNAL": 0.03, "PRIVATE": 0.01 },
  "OPEN_REDIRECT":             { "PUBLIC": 0.10, "INTERNAL": 0.02, "PRIVATE": 0.005 },
  "COMMAND_INJECTION":         { "PUBLIC": 0.12, "INTERNAL": 0.04, "PRIVATE": 0.01 },
  "WEAK_CRYPTO":               { "PUBLIC": 0.08, "INTERNAL": 0.03, "PRIVATE": 0.01 },
  "INSECURE_RANDOM":           { "PUBLIC": 0.06, "INTERNAL": 0.02, "PRIVATE": 0.005 },
  "UNKNOWN":                   { "PUBLIC": 0.05, "INTERNAL": 0.02, "PRIVATE": 0.005 }
}
```

### knowledge_base/breach_costs.json

```json
{
  "cost_per_record_by_industry": {
    "finance": 250, "healthcare": 400, "technology": 150,
    "retail": 130,  "education": 100,  "default": 165
  },
  "incident_response_cost": {
    "startup": 30000, "mid_size": 100000, "enterprise": 500000
  },
  "downtime_cost_per_hour": {
    "startup": 2000, "mid_size": 12000, "enterprise": 60000
  },
  "churn_rate_after_breach": {
    "low_sensitivity": 0.02, "medium_sensitivity": 0.05, "high_sensitivity": 0.10
  }
}
```

### knowledge_base/regulatory_models.json

```json
{
  "GDPR":    { "fine_percentage_of_arr": 0.04, "max_fine_usd": 20000000 },
  "PCI_DSS": { "avg_fine": 250000 },
  "HIPAA":   { "max_annual": 1900000 },
  "CCPA":    { "per_record_intentional": 750, "max_fine": 7500 }
}
```

### knowledge_base/downtime_estimates.json

```json
{
  "downtime_hours_by_bug_type": {
    "SQL_INJECTION": 4, "AUTH_BYPASS": 6, "RCE": 8,
    "COMMAND_INJECTION": 6, "INSECURE_DESERIALIZATION": 5,
    "SSRF": 3, "HARDCODED_CREDENTIALS": 4,
    "XSS": 1, "IDOR": 2, "PATH_TRAVERSAL": 2,
    "CSRF": 1, "WEAK_CRYPTO": 2, "INSECURE_RANDOM": 1,
    "OPEN_REDIRECT": 0.5, "UNKNOWN": 2
  }
}
```

---

## ENGINE MODULES

### engine/scanner.py

```python
import subprocess, json, tempfile, shutil
from typing import List, Dict
import git

def clone_repo(repo_url: str, branch: str = "main") -> str:
    tmp = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, tmp, branch=branch, depth=1)
    return tmp

def run_semgrep(repo_path: str) -> List[Dict]:
    result = subprocess.run(
        ["semgrep", "--config", "p/security-audit",
         "--config", "p/owasp-top-ten", "--json", "--quiet", repo_path],
        capture_output=True, text=True, timeout=300
    )
    try:
        return json.loads(result.stdout).get("results", [])
    except:
        return []

def read_code_context(file_path: str, line: int, context_lines: int = 40) -> str:
    """Read lines around a vulnerability for LLM context."""
    try:
        with open(file_path) as f:
            lines = f.readlines()
        start = max(0, line - context_lines)
        end   = min(len(lines), line + context_lines)
        numbered = [f"{i+1}: {l}" for i, l in enumerate(lines[start:end], start=start)]
        return "".join(numbered)
    except:
        return ""

def parse_semgrep_findings(findings: List[Dict], exposure: str, repo_path: str = "") -> List[Dict]:
    parsed = []
    for i, f in enumerate(findings):
        file_path = f.get("path", "unknown")
        line      = f.get("start", {}).get("line", 0)
        code_ctx  = ""
        if repo_path:
            full_path = f"{repo_path}/{file_path}"
            code_ctx  = read_code_context(full_path, line)
        parsed.append({
            "id":          f"VULN_{i+1:03d}",
            "raw_rule_id": f.get("check_id", "unknown"),
            "file":        file_path,
            "line":        line,
            "message":     f.get("extra", {}).get("message", ""),
            "severity":    f.get("extra", {}).get("severity", "WARNING").lower(),
            "exposure":    exposure.upper(),
            "code_context": code_ctx
        })
    return parsed
```

### engine/classifier.py

```python
import json
from typing import Dict

def load_taxonomy() -> Dict:
    with open("knowledge_base/bug_taxonomy.json") as f:
        return json.load(f)

RULE_MAPPING = {
    "sql": "SQL_INJECTION", "sqli": "SQL_INJECTION", "injection": "SQL_INJECTION",
    "xss": "XSS", "cross-site": "XSS",
    "auth": "AUTH_BYPASS", "authentication": "AUTH_BYPASS",
    "deserializ": "INSECURE_DESERIALIZATION", "pickle": "INSECURE_DESERIALIZATION",
    "ssrf": "SSRF", "idor": "IDOR",
    "rce": "RCE", "remote-code": "RCE",
    "path-traversal": "PATH_TRAVERSAL", "directory-traversal": "PATH_TRAVERSAL",
    "hardcoded": "HARDCODED_CREDENTIALS", "secret": "HARDCODED_CREDENTIALS",
    "password": "HARDCODED_CREDENTIALS", "api-key": "HARDCODED_CREDENTIALS",
    "csrf": "CSRF", "redirect": "OPEN_REDIRECT",
    "xxe": "XXE", "xml": "XXE",
    "command": "COMMAND_INJECTION", "exec": "COMMAND_INJECTION", "subprocess": "COMMAND_INJECTION",
    "crypto": "WEAK_CRYPTO", "md5": "WEAK_CRYPTO", "sha1": "WEAK_CRYPTO",
    "random": "INSECURE_RANDOM"
}

def classify_bug(raw_rule_id: str, message: str) -> str:
    combined = (raw_rule_id + " " + message).lower()
    for keyword, bug_type in RULE_MAPPING.items():
        if keyword in combined:
            return bug_type
    return "UNKNOWN"

def get_fix_effort(bug_type: str, taxonomy: Dict) -> float:
    return taxonomy.get(bug_type, {}).get("typical_fix_hours", 4)
```

### engine/probability_model.py

```python
import json
from typing import Dict

def load_probabilities() -> Dict:
    with open("knowledge_base/exploit_probability.json") as f:
        return json.load(f)

def get_probability(bug_type: str, exposure: str, probabilities: Dict) -> float:
    return probabilities.get(bug_type, probabilities["UNKNOWN"]).get(exposure.upper(), 0.05)
```

### engine/impact_model.py

```python
import json
from models.company import CompanyContext
from models.risk_result import ImpactBreakdown

def compute_total_impact(company: CompanyContext, bug_type: str):
    with open("knowledge_base/breach_costs.json")     as f: bc  = json.load(f)
    with open("knowledge_base/regulatory_models.json") as f: rm  = json.load(f)
    with open("knowledge_base/downtime_estimates.json") as f: de  = json.load(f)
    with open("knowledge_base/bug_taxonomy.json")     as f: tax = json.load(f)

    bug_info = tax.get(bug_type, {})

    # Data breach cost
    if bug_info.get("data_exfiltration", False):
        cpr = bc["cost_per_record_by_industry"].get(
            company.industry.lower(), bc["cost_per_record_by_industry"]["default"])
        data_breach = int(company.estimated_records_stored * 0.20) * cpr
    else:
        data_breach = 0.0

    # Incident response
    incident = bc["incident_response_cost"].get(company.company_size, 100000)

    # Downtime
    hours    = de["downtime_hours_by_bug_type"].get(bug_type, 2)
    cph      = company.estimated_downtime_cost_per_hour or \
               bc["downtime_cost_per_hour"].get(company.company_size, 12000)
    downtime = hours * cph

    # Regulatory fines
    reg = 0.0
    fw  = [r.upper() for r in company.regulatory_frameworks]
    dt  = [d.upper() for d in company.sensitive_data_types]
    if "GDPR"    in fw or "PII"       in dt:
        reg += min(company.annual_revenue * rm["GDPR"]["fine_percentage_of_arr"],
                   rm["GDPR"]["max_fine_usd"])
    if "PCI_DSS" in fw or "FINANCIAL" in dt:
        reg += rm["PCI_DSS"]["avg_fine"]
    if "HIPAA"   in fw or "HEALTH"    in dt:
        reg += rm["HIPAA"]["max_annual"]

    # Churn / reputation
    if any(d in dt for d in ["FINANCIAL", "HEALTH"]):
        cr = bc["churn_rate_after_breach"]["high_sensitivity"]
    elif "PII" in dt:
        cr = bc["churn_rate_after_breach"]["medium_sensitivity"]
    else:
        cr = bc["churn_rate_after_breach"]["low_sensitivity"]
    reputation = company.active_users * cr * company.arpu * 12

    breakdown = ImpactBreakdown(
        data_breach_cost=round(data_breach, 2),
        incident_response_cost=round(incident, 2),
        downtime_cost=round(downtime, 2),
        regulatory_penalty=round(reg, 2),
        reputation_damage=round(reputation, 2)
    )
    return breakdown, round(data_breach + incident + downtime + reg + reputation, 2)
```

### engine/expected_loss.py

```python
def compute_expected_loss(probability: float, total_impact: float) -> float:
    return round(probability * total_impact, 2)

def compute_priority_score(expected_loss: float, fix_effort_hours: float) -> float:
    if fix_effort_hours <= 0: return 0.0
    return round(expected_loss / fix_effort_hours, 2)

def compute_fix_cost(fix_effort_hours: float, engineer_hourly_cost: float) -> float:
    return round(fix_effort_hours * engineer_hourly_cost, 2)

def compute_roi(expected_loss: float, fix_cost: float) -> float:
    if fix_cost <= 0: return 0.0
    return round(expected_loss / fix_cost, 1)
```

### engine/ranker.py

```python
from typing import List
from models.risk_result import RiskResult

def rank_vulnerabilities(results: List[RiskResult]) -> List[RiskResult]:
    return sorted(results, key=lambda r: r.priority_score, reverse=True)
```

---

## GEMINI LLM ANALYZER — THE KEY NEW MODULE

### engine/gemini_analyzer.py

This is the module that replaces lookup-table reasoning with actual code understanding.
It sends each vulnerability's code context to Gemini and asks the questions a
real security engineer would ask.

```python
import os
import json
import google.generativeai as genai
from typing import Optional
from models.risk_result import GeminiAnalysis
from models.company import CompanyContext

def init_gemini(api_key: str):
    genai.configure(api_key=api_key)

def analyze_vulnerability(
    bug_type: str,
    file: str,
    line: int,
    code_context: str,
    message: str,
    exposure: str,
    company: CompanyContext,
    baseline_probability: float
) -> Optional[GeminiAnalysis]:
    """
    Ask Gemini to analyze a single vulnerability with full code context.
    Returns structured analysis including adjusted probability and fix.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")  # free tier

    prompt = f"""You are a senior application security engineer performing a vulnerability assessment.

COMPANY CONTEXT:
- Company: {company.company_name}
- Industry: {company.industry}
- Product: {company.product_description or 'Not specified'}
- Tech stack: {company.stack_description or 'Not specified'}
- Data stored: {', '.join(company.sensitive_data_types)}
- Deployment: {exposure} facing

VULNERABILITY DETECTED:
- Type: {bug_type}
- File: {file}, Line: {line}
- Scanner message: {message}
- Baseline exploit probability: {baseline_probability}

CODE CONTEXT (lines around the vulnerability):
```
{code_context if code_context else "Code context not available — reason from file name and bug type."}
```

Analyze this vulnerability and respond ONLY with valid JSON in exactly this format:
{{
  "is_exploitable": true or false,
  "exploitability_confidence": "high" or "medium" or "low",
  "exploitability_reasoning": "2-3 sentences explaining WHY this is or isn't exploitable based on the actual code",
  "business_context": "1-2 sentences describing what this code actually does and what business function it serves",
  "adjusted_probability": 0.0 to 1.0 (adjust the baseline based on what you see in the code),
  "false_positive_likelihood": "high" or "medium" or "low",
  "recommended_fix": "Specific fix — include actual code if possible, or precise instructions",
  "fix_complexity": "simple" or "moderate" or "complex"
}}

Rules:
- If code context is unavailable, reason from file name, bug type, and company context
- Be specific — reference actual variable names or patterns you see in the code
- If this looks like a test file or dead code, say so and lower the probability
- If the input appears to come directly from user requests, raise the probability
- The recommended_fix must be actionable — not generic advice"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        return GeminiAnalysis(
            is_exploitable=data.get("is_exploitable", True),
            exploitability_confidence=data.get("exploitability_confidence", "medium"),
            exploitability_reasoning=data.get("exploitability_reasoning", ""),
            business_context=data.get("business_context", ""),
            adjusted_probability=float(data.get("adjusted_probability", baseline_probability)),
            false_positive_likelihood=data.get("false_positive_likelihood", "medium"),
            recommended_fix=data.get("recommended_fix", "Review and remediate manually."),
            fix_complexity=data.get("fix_complexity", "moderate")
        )
    except Exception as e:
        print(f"Gemini analysis failed for {file}:{line} — {e}")
        return None
```

---

## ATTACK CHAIN ANALYZER — CROSS-VULNERABILITY REASONING

### engine/attack_chain.py

This is what changes "3 medium bugs" into "1 critical breach path."
Send all vulnerabilities together to Gemini and ask it to find chains.

```python
import json
import google.generativeai as genai
from typing import List, Dict
from models.risk_result import AttackChain, RiskResult
from models.company import CompanyContext


def find_attack_chains(
    results: List[RiskResult],
    company: CompanyContext
) -> List[AttackChain]:
    """
    Send all vulnerabilities to Gemini together.
    Ask it to identify which ones could be chained into multi-step attack paths.
    """
    if len(results) < 2:
        return []

    model = genai.GenerativeModel("gemini-1.5-flash")

    # Build vulnerability summary for Gemini
    vuln_summary = []
    for r in results:
        vuln_summary.append({
            "id":       r.vulnerability_id,
            "type":     r.bug_type,
            "file":     r.file,
            "line":     r.line,
            "exposure": r.exposure,
            "gemini_context": r.gemini_analysis.business_context if r.gemini_analysis else "",
            "exploitable": r.gemini_analysis.is_exploitable if r.gemini_analysis else True
        })

    prompt = f"""You are a senior penetration tester analyzing a set of vulnerabilities
found in {company.company_name}'s codebase ({company.industry} company, {company.deployment_exposure} deployment).

VULNERABILITIES FOUND:
{json.dumps(vuln_summary, indent=2)}

TASK: Identify attack chains — sequences of 2 or more vulnerabilities that an attacker
could exploit in sequence to cause greater damage than any single vulnerability alone.

Classic chain examples:
- XSS → steal session → auth bypass → access admin → SQLi → full database
- Path traversal → read credentials → auth bypass → RCE
- IDOR → enumerate users → credential stuffing → account takeover

Respond ONLY with valid JSON in exactly this format:
{{
  "chains": [
    {{
      "chain_id": "CHAIN_001",
      "vulnerability_ids": ["VULN_001", "VULN_002"],
      "chain_description": "Plain English description of the full attack path (2-3 sentences, no jargon)",
      "combined_severity": "critical" or "high" or "medium",
      "severity_reasoning": "Why chaining makes this worse than the individual bugs",
      "steps": [
        "Step 1: Attacker exploits [VULN_001] to...",
        "Step 2: Using what they gained, they exploit [VULN_002] to...",
        "Step 3: The result is..."
      ]
    }}
  ]
}}

If no meaningful chains exist, return {{"chains": []}}.
Only include chains where the combination is genuinely more dangerous.
Write all descriptions for a non-technical CEO audience — no CVE IDs, no jargon."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)

        chains = []
        for c in data.get("chains", []):
            # Compute combined expected loss
            involved_results = [r for r in results if r.vulnerability_id in c["vulnerability_ids"]]
            combined_loss = sum(r.expected_loss for r in involved_results) * 1.5  # 50% amplifier for chaining

            chains.append(AttackChain(
                chain_id=c["chain_id"],
                vulnerability_ids=c["vulnerability_ids"],
                chain_description=c["chain_description"],
                combined_severity=c.get("combined_severity", "high"),
                combined_expected_loss=round(combined_loss, 2),
                chain_steps=c.get("steps", [])
            ))
        return chains
    except Exception as e:
        print(f"Attack chain analysis failed: {e}")
        return []
```

---

## BUSINESS BRIEF GENERATOR

### engine/business_brief.py

```python
import json
from models.risk_result import RiskResult, GeminiAnalysis
from models.company import CompanyContext


def load_attack_stories() -> dict:
    with open("knowledge_base/attack_stories.json") as f:
        return json.load(f)


def fmt(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    return f"${amount:,.0f}"


def humanize_data_types(data_types: list) -> str:
    mapping = {
        "pii": "customer personal information",
        "financial": "payment and financial data",
        "health": "medical records",
        "credentials": "login credentials"
    }
    labels = [mapping.get(d.lower(), d) for d in data_types]
    if len(labels) == 1: return labels[0]
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def get_urgency(expected_loss: float) -> dict:
    if expected_loss >= 100000:
        return {"icon": "🔴", "label": "CRITICAL BUSINESS RISK", "subtitle": "Requires decision this week",
                "action": "Fix immediately — this sprint, not next."}
    elif expected_loss >= 30000:
        return {"icon": "🟠", "label": "HIGH BUSINESS RISK",     "subtitle": "Requires decision this sprint",
                "action": "Fix this sprint. Do not defer to backlog."}
    elif expected_loss >= 5000:
        return {"icon": "🟡", "label": "MEDIUM BUSINESS RISK",   "subtitle": "Schedule within 30 days",
                "action": "Assign to next sprint. Monitor in the meantime."}
    return     {"icon": "🟢", "label": "LOW BUSINESS RISK",      "subtitle": "Schedule within 90 days",
                "action": "Add to backlog. Fix during next refactor cycle."}


def generate_business_brief(result: RiskResult, company: CompanyContext) -> str:
    stories    = load_attack_stories()
    story      = stories.get(result.bug_type, stories["UNKNOWN"])
    urgency    = get_urgency(result.expected_loss)
    bug_label  = result.bug_type.replace("_", " ").title()
    prob_pct   = round(result.effective_probability * 100)
    b          = result.impact_breakdown
    records    = f"{company.estimated_records_stored:,}"
    data_label = humanize_data_types(company.sensitive_data_types)
    fix_cost   = result.fix_effort_hours * company.engineer_hourly_cost
    roi_mult   = int(result.expected_loss / fix_cost) if fix_cost > 0 else 0
    frameworks = "/".join(company.regulatory_frameworks)

    # Format attack steps with company context
    steps_text = ""
    for i, step in enumerate(story["steps"]):
        step = step.replace("{records}", records).replace("{data_types}", data_label)\
                   .replace("{company}", company.company_name)
        steps_text += f"  Step {i+1}: {step}\n"

    headline = story["headline_template"]\
        .replace("{company}", company.company_name).replace("{records}", records)

    # Gemini enhancement block
    gemini_block = ""
    if result.gemini_analysis:
        g = result.gemini_analysis
        if not g.is_exploitable:
            gemini_block = f"""
AI ANALYSIS: POTENTIAL FALSE POSITIVE
  Confidence: {g.exploitability_confidence}
  Reason: {g.exploitability_reasoning}
  Recommendation: Have a security engineer verify before prioritizing.
"""
        else:
            gemini_block = f"""
AI ANALYSIS OF THIS SPECIFIC CODE
  What this code does: {g.business_context}
  Why it's exploitable: {g.exploitability_reasoning}
  Confidence level: {g.exploitability_confidence}
"""

    # Cost lines
    cost_lines = ""
    if b.data_breach_cost > 0:
        cost_lines += f"  {'Customer data breach cost:':<42} {fmt(b.data_breach_cost)}\n"
    if b.regulatory_penalty > 0:
        cost_lines += f"  {f'Regulatory fines ({frameworks}):':<42} {fmt(b.regulatory_penalty)}\n"
    if b.reputation_damage > 0:
        cost_lines += f"  {'Lost customers (estimated churn):':<42} {fmt(b.reputation_damage)}\n"
    cost_lines += f"  {'Incident response + legal:':<42} {fmt(b.incident_response_cost)}\n"
    cost_lines += f"  {'System downtime cost:':<42} {fmt(b.downtime_cost)}\n"

    # Fix guidance from Gemini
    fix_guidance = ""
    if result.gemini_analysis and result.gemini_analysis.recommended_fix:
        fix_guidance = f"""
HOW TO FIX IT
  Complexity: {result.gemini_analysis.fix_complexity}
  {result.gemini_analysis.recommended_fix}
"""

    return f"""{'='*65}
  {urgency['icon']} {urgency['label']}
  {urgency['subtitle']}
  Location: {result.file}, line {result.line}
{'='*65}

WHAT IS BROKEN (plain English)
  {story['real_world_analogy']}
  Technical name: {bug_label}
  Accessible from: {'The public internet' if result.exposure == 'PUBLIC' else 'Internal network only'}
{gemini_block}
HOW A REAL BREACH HAPPENS — STEP BY STEP
{steps_text}
  Attacker effort required: {story['attacker_effort']}
  How hard to detect:       {story['detection_difficulty']}
  Real-world precedent:     {story.get('comparable_breach', 'N/A')}

WHAT THIS COSTS {company.company_name.upper()} IF NOT FIXED
{cost_lines}  {'─'*55}
  {'TOTAL POTENTIAL LOSS:':<42} {fmt(result.total_impact)}

  Probability of exploitation: {prob_pct}%
  {'(AI-adjusted from baseline based on code analysis)' if result.gemini_analysis else '(Based on industry data for this exposure level)'}

  EXPECTED LOSS (probability × impact): {fmt(result.expected_loss)}
  This is the actuarial cost of carrying this risk unresolved.

WHAT THE FIX COSTS
  Engineer time:  {result.fix_effort_hours} hours
  Salary cost:    {fmt(fix_cost)}
  ROI of fixing:  {roi_mult}× — every $1 spent saves ${roi_mult} in expected loss.
{fix_guidance}
WHAT THE PRESS WOULD WRITE IF THIS IS EXPLOITED
  "{headline}"

DECISION REQUIRED
  {urgency['action']}
  → Approve fix this sprint?   [ YES / NO ]
  → Accept risk and delay?     [ YES — requires written sign-off / NO ]
{'='*65}""".strip()


def generate_executive_summary(results: list, company: CompanyContext,
                                 chains: list = None) -> str:
    total_loss     = sum(r.expected_loss for r in results)
    total_impact   = sum(r.total_impact for r in results)
    total_hours    = sum(r.fix_effort_hours for r in results)
    total_fix_cost = total_hours * company.engineer_hourly_cost
    roi            = int(total_loss / total_fix_cost) if total_fix_cost > 0 else 0

    critical = [r for r in results if r.expected_loss >= 100000]
    high     = [r for r in results if 30000 <= r.expected_loss < 100000]
    other    = [r for r in results if r.expected_loss < 30000]

    top3 = ""
    for i, r in enumerate(results[:3]):
        label = r.bug_type.replace("_", " ").title()
        gemini_note = " ✓ AI-verified" if (r.gemini_analysis and r.gemini_analysis.is_exploitable) else ""
        top3 += f"  #{i+1}  {label:<32} Expected loss: {fmt(r.expected_loss):<12}  Fix: {r.fix_effort_hours}h{gemini_note}\n"

    chain_block = ""
    if chains:
        chain_block = f"\nATTACK CHAINS DETECTED: {len(chains)}\n"
        for c in chains:
            chain_block += f"  {c.chain_id}: {c.chain_description}\n"
            chain_block += f"  Combined exposure: {fmt(c.combined_expected_loss)} | Severity: {c.combined_severity.upper()}\n\n"

    gemini_note = "\n  Note: Probabilities have been adjusted by AI analysis of actual code context." \
                  if any(r.gemini_analysis for r in results) else ""

    return f"""{'='*65}
  SECURITY RISK EXECUTIVE SUMMARY
  {company.company_name} — Board / Leadership Review
{'='*65}

BOTTOM LINE
  We have {len(results)} known security vulnerabilities.
  Total exposure if all exploited:              {fmt(total_impact)}
  Expected loss (probability-adjusted):        {fmt(total_loss)}
  Total cost to fix everything:                {fmt(total_fix_cost)} ({total_hours:.0f} hours)
  Fixing costs {roi}× less than the expected loss of not fixing.
{gemini_note}

RISK BREAKDOWN
  🔴 Critical — act this week:   {len(critical)} {'vulnerability' if len(critical)==1 else 'vulnerabilities'}
  🟠 High — act this sprint:     {len(high)} {'vulnerability' if len(high)==1 else 'vulnerabilities'}
  🟡 Medium / Low — schedule:    {len(other)} {'vulnerability' if len(other)==1 else 'vulnerabilities'}

TOP 3 RISKS BY FINANCIAL EXPOSURE
{top3}{chain_block}
WHAT HAPPENS IF WE DO NOTHING
  Based on breach rates for {company.industry} companies our size, at least one
  of these vulnerabilities is likely to be found and exploited within
  6–18 months if unaddressed.

WHAT WE ARE ASKING FOR
  Approval to allocate {total_hours:.0f} engineering hours to address
  the {len(critical)} critical and {len(high)} high-priority vulnerabilities.
  Estimated cost: {fmt(total_fix_cost)}.

{'='*65}""".strip()
```

---

## MAIN FASTAPI SERVER

### main.py

```python
import json, os, shutil
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from models.company import CompanyContext
from models.risk_result import RiskResult, AttackChain
from engine.scanner import clone_repo, run_semgrep, parse_semgrep_findings
from engine.classifier import classify_bug, get_fix_effort, load_taxonomy
from engine.probability_model import load_probabilities, get_probability
from engine.impact_model import compute_total_impact
from engine.expected_loss import (compute_expected_loss, compute_priority_score,
                                   compute_fix_cost, compute_roi)
from engine.ranker import rank_vulnerabilities
from engine.gemini_analyzer import init_gemini, analyze_vulnerability
from engine.attack_chain import find_attack_chains
from engine.business_brief import generate_business_brief, generate_executive_summary

app = FastAPI(title="Vulnerability Business Impact Engine", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_ui():
    return FileResponse("frontend/index.html")


class ManualScanRequest(BaseModel):
    vulnerabilities: List[dict]
    company: CompanyContext
    gemini_api_key: Optional[str] = None

class ScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    company: CompanyContext
    gemini_api_key: Optional[str] = None

class AnalysisResponse(BaseModel):
    results: List[RiskResult]
    attack_chains: List[AttackChain]
    executive_summary: str
    total_expected_loss: float
    total_fix_cost: float
    vulnerability_count: int
    gemini_enabled: bool


def run_risk_engine(
    findings: list,
    company: CompanyContext,
    gemini_api_key: Optional[str] = None
) -> tuple:
    if gemini_api_key:
        init_gemini(gemini_api_key)

    taxonomy      = load_taxonomy()
    probabilities = load_probabilities()
    results       = []

    for f in findings:
        bug_type    = classify_bug(f.get("raw_rule_id", ""), f.get("message", ""))
        fix_effort  = get_fix_effort(bug_type, taxonomy)
        exposure    = f.get("exposure", company.deployment_exposure.upper())
        baseline_p  = get_probability(bug_type, exposure, probabilities)

        # --- Gemini analysis ---
        gemini_result = None
        effective_p   = baseline_p
        if gemini_api_key and f.get("code_context"):
            gemini_result = analyze_vulnerability(
                bug_type=bug_type,
                file=f["file"],
                line=f["line"],
                code_context=f.get("code_context", ""),
                message=f.get("message", ""),
                exposure=exposure,
                company=company,
                baseline_probability=baseline_p
            )
            if gemini_result:
                effective_p = gemini_result.adjusted_probability
                # Skip confirmed false positives
                if gemini_result.false_positive_likelihood == "high" and \
                   not gemini_result.is_exploitable:
                    effective_p = 0.01  # near-zero but keep in report

        breakdown, total_impact = compute_total_impact(company, bug_type)
        expected_loss  = compute_expected_loss(effective_p, total_impact)
        priority_score = compute_priority_score(expected_loss, fix_effort)
        fix_cost       = compute_fix_cost(fix_effort, company.engineer_hourly_cost)
        roi            = compute_roi(expected_loss, fix_cost)

        result = RiskResult(
            vulnerability_id       = f["id"],
            bug_type               = bug_type,
            file                   = f["file"],
            line                   = f["line"],
            severity               = f.get("severity", "medium"),
            exposure               = exposure,
            probability_of_exploit = baseline_p,
            gemini_analysis        = gemini_result,
            effective_probability  = effective_p,
            impact_breakdown       = breakdown,
            total_impact           = total_impact,
            expected_loss          = expected_loss,
            fix_effort_hours       = fix_effort,
            fix_cost_usd           = fix_cost,
            priority_score         = priority_score,
            roi_of_fixing          = roi,
            business_brief         = ""
        )
        result.business_brief = generate_business_brief(result, company)
        results.append(result)

    ranked = rank_vulnerabilities(results)

    # --- Attack chain analysis ---
    chains = []
    if gemini_api_key and len(ranked) >= 2:
        chains = find_attack_chains(ranked, company)
        # Tag each result with its chains
        for chain in chains:
            for r in ranked:
                if r.vulnerability_id in chain.vulnerability_ids:
                    if r.attack_chains is None:
                        r.attack_chains = []
                    r.attack_chains.append(chain.chain_id)

    return ranked, chains


@app.post("/analyze-manual", response_model=AnalysisResponse)
async def analyze_manual(req: ManualScanRequest):
    results, chains = run_risk_engine(
        req.vulnerabilities, req.company, req.gemini_api_key
    )
    summary = generate_executive_summary(results, req.company, chains)
    return AnalysisResponse(
        results=results,
        attack_chains=chains,
        executive_summary=summary,
        total_expected_loss=sum(r.expected_loss for r in results),
        total_fix_cost=sum(r.fix_cost_usd for r in results),
        vulnerability_count=len(results),
        gemini_enabled=bool(req.gemini_api_key)
    )


@app.post("/scan-repo", response_model=AnalysisResponse)
async def scan_repo(req: ScanRequest):
    repo_path = None
    try:
        repo_path = clone_repo(req.repo_url, req.branch)
        raw       = run_semgrep(repo_path)
        parsed    = parse_semgrep_findings(raw, req.company.deployment_exposure, repo_path)
        results, chains = run_risk_engine(parsed, req.company, req.gemini_api_key)
        os.makedirs("data", exist_ok=True)
        with open("data/risk_results.json", "w") as f:
            json.dump({"results": [r.dict() for r in results],
                       "chains":  [c.dict() for c in chains]}, f, indent=2)
        summary = generate_executive_summary(results, req.company, chains)
        return AnalysisResponse(
            results=results, attack_chains=chains, executive_summary=summary,
            total_expected_loss=sum(r.expected_loss for r in results),
            total_fix_cost=sum(r.fix_cost_usd for r in results),
            vulnerability_count=len(results),
            gemini_enabled=bool(req.gemini_api_key)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}
```

---

## FRONTEND — COMPLETE UI

Save this as `frontend/index.html`.
This is the complete single-file UI with all inputs and result rendering.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VFIE — Vulnerability Business Impact Engine</title>
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c28;
    --border: #2a2a3d;
    --text: #e8e8f0;
    --muted: #6b6b8a;
    --accent: #e63946;
    --accent2: #ff6b6b;
    --green: #2ecc71;
    --orange: #f39c12;
    --yellow: #f1c40f;
    --blue: #3498db;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    min-height: 100vh;
    line-height: 1.6;
  }

  /* Header */
  .header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 20px 40px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .header-logo {
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 18px; color: white;
  }
  .header-title { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; }
  .header-subtitle { font-size: 12px; color: var(--muted); margin-left: auto; }
  .header-badge {
    background: rgba(230,57,70,0.15);
    border: 1px solid rgba(230,57,70,0.3);
    color: var(--accent);
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  /* Layout */
  .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

  /* Tabs */
  .tabs { display: flex; gap: 4px; margin-bottom: 32px; }
  .tab {
    padding: 10px 20px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: var(--muted);
    transition: all 0.15s;
  }
  .tab:hover { color: var(--text); border-color: var(--muted); }
  .tab.active {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }

  /* Cards */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
  }
  .card-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-title::before {
    content: '';
    width: 3px; height: 14px;
    background: var(--accent);
    border-radius: 2px;
    display: inline-block;
  }

  /* Form elements */
  label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }
  input, select, textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.15s;
    margin-bottom: 16px;
  }
  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--accent);
  }
  input::placeholder, textarea::placeholder { color: var(--muted); }
  textarea { resize: vertical; min-height: 80px; font-family: var(--font-mono); font-size: 13px; }
  select option { background: var(--surface); }

  .checkbox-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .checkbox-item {
    display: flex; align-items: center; gap: 6px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 12px;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 13px;
  }
  .checkbox-item:hover { border-color: var(--accent); }
  .checkbox-item input[type=checkbox] {
    width: auto; margin: 0; padding: 0;
    accent-color: var(--accent);
  }
  .checkbox-item.checked { border-color: var(--accent); background: rgba(230,57,70,0.08); }

  /* Buttons */
  .btn {
    padding: 12px 28px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.15s;
  }
  .btn-primary {
    background: var(--accent);
    color: white;
  }
  .btn-primary:hover { background: var(--accent2); transform: translateY(-1px); }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
  .btn-outline {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text);
  }
  .btn-outline:hover { border-color: var(--accent); color: var(--accent); }
  .btn-lg { padding: 16px 40px; font-size: 16px; width: 100%; margin-top: 8px; }

  /* Metric cards */
  .metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }
  .metric-value {
    font-size: 28px;
    font-weight: 800;
    font-family: var(--font-mono);
    color: var(--accent);
    line-height: 1;
    margin-bottom: 4px;
  }
  .metric-value.green { color: var(--green); }
  .metric-value.orange { color: var(--orange); }
  .metric-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }

  /* Vuln cards */
  .vuln-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 16px;
    overflow: hidden;
    transition: border-color 0.15s;
  }
  .vuln-card:hover { border-color: var(--muted); }
  .vuln-header {
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    user-select: none;
  }
  .vuln-tier { font-size: 20px; flex-shrink: 0; }
  .vuln-title { font-weight: 700; font-size: 15px; flex: 1; }
  .vuln-file { font-family: var(--font-mono); font-size: 12px; color: var(--muted); }
  .vuln-loss {
    font-family: var(--font-mono);
    font-weight: 800;
    font-size: 18px;
    color: var(--accent);
    flex-shrink: 0;
  }
  .vuln-expand { color: var(--muted); font-size: 12px; flex-shrink: 0; }
  .vuln-body {
    padding: 0 20px 20px;
    display: none;
  }
  .vuln-body.open { display: block; }

  /* Brief pre */
  .brief-pre {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    font-family: var(--font-mono);
    font-size: 12px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    color: #c5c5d8;
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 12px;
  }

  /* Chain card */
  .chain-card {
    background: linear-gradient(135deg, rgba(230,57,70,0.08), rgba(243,156,18,0.05));
    border: 1px solid rgba(230,57,70,0.3);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
  }
  .chain-title {
    font-weight: 700;
    font-size: 14px;
    color: var(--accent2);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .chain-steps { margin: 12px 0; }
  .chain-step {
    padding: 8px 12px;
    border-left: 2px solid var(--accent);
    margin-bottom: 6px;
    font-size: 13px;
    color: #b0b0c8;
    background: rgba(0,0,0,0.2);
    border-radius: 0 6px 6px 0;
  }
  .chain-loss {
    font-family: var(--font-mono);
    font-size: 18px;
    font-weight: 800;
    color: var(--accent);
  }

  /* Gemini badge */
  .ai-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(52,152,219,0.15);
    border: 1px solid rgba(52,152,219,0.3);
    color: var(--blue);
    padding: 2px 8px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
  }

  /* Loading */
  .loading {
    display: none;
    text-align: center;
    padding: 60px;
  }
  .loading.show { display: block; }
  .spinner {
    width: 48px; height: 48px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 20px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading-steps { font-size: 13px; color: var(--muted); }
  .loading-step { padding: 4px 0; transition: color 0.3s; }
  .loading-step.active { color: var(--text); }
  .loading-step.done { color: var(--green); }

  /* Results section */
  #results { display: none; }
  #results.show { display: block; }

  /* Section title */
  .section-title {
    font-size: 22px;
    font-weight: 800;
    margin: 32px 0 20px;
    letter-spacing: -0.5px;
  }
  .section-title span { color: var(--accent); }

  /* Summary pre */
  .summary-pre {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px;
    font-family: var(--font-mono);
    font-size: 13px;
    line-height: 1.8;
    white-space: pre-wrap;
    color: #d0d0e0;
    margin-bottom: 32px;
  }

  /* Error */
  .error-box {
    background: rgba(230,57,70,0.1);
    border: 1px solid rgba(230,57,70,0.3);
    border-radius: 8px;
    padding: 16px 20px;
    color: var(--accent2);
    display: none;
    margin-top: 12px;
    font-size: 14px;
  }
  .error-box.show { display: block; }

  /* Gemini toggle */
  .toggle-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 16px;
  }
  .toggle { position: relative; width: 44px; height: 24px; flex-shrink: 0; }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .toggle-slider {
    position: absolute; inset: 0;
    background: var(--border);
    border-radius: 24px;
    cursor: pointer;
    transition: 0.2s;
  }
  .toggle-slider:before {
    content: '';
    position: absolute;
    width: 18px; height: 18px;
    left: 3px; top: 3px;
    background: white;
    border-radius: 50%;
    transition: 0.2s;
  }
  input:checked + .toggle-slider { background: var(--accent); }
  input:checked + .toggle-slider:before { transform: translateX(20px); }
  .toggle-label { font-size: 14px; font-weight: 500; }
  .toggle-desc { font-size: 12px; color: var(--muted); }

  .hidden { display: none; }

  @media (max-width: 768px) {
    .container { padding: 20px; }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .header { padding: 16px 20px; }
  }
</style>
</head>
<body>

<div class="header">
  <div class="header-logo">V</div>
  <div class="header-title">Vulnerability Business Impact Engine</div>
  <div class="header-badge">v3.0</div>
  <div class="header-subtitle">Turn security bugs into financial decisions</div>
</div>

<div class="container">

  <!-- TABS -->
  <div class="tabs">
    <div class="tab active" onclick="switchTab('scan')">🔍 Scan Repository</div>
    <div class="tab" onclick="switchTab('manual')">📋 Manual Input</div>
  </div>

  <!-- SCAN TAB -->
  <div id="tab-scan">
    <div class="grid-2">
      <!-- Left: Company Context -->
      <div>
        <div class="card">
          <div class="card-title">Company Context</div>

          <label>Company Name</label>
          <input type="text" id="company_name" placeholder="PayFlow Inc" />

          <div class="grid-2">
            <div>
              <label>Industry</label>
              <select id="industry">
                <option value="finance">Finance / Fintech</option>
                <option value="healthcare">Healthcare</option>
                <option value="technology">Technology / SaaS</option>
                <option value="retail">Retail / E-commerce</option>
                <option value="education">Education</option>
              </select>
            </div>
            <div>
              <label>Company Size</label>
              <select id="company_size">
                <option value="startup">Startup (&lt;50 employees)</option>
                <option value="mid_size" selected>Mid-size (50–500)</option>
                <option value="enterprise">Enterprise (500+)</option>
              </select>
            </div>
          </div>

          <div class="grid-2">
            <div>
              <label>Annual Revenue (USD)</label>
              <input type="number" id="annual_revenue" placeholder="12000000" />
            </div>
            <div>
              <label>Monthly Revenue (USD)</label>
              <input type="number" id="monthly_revenue" placeholder="1000000" />
            </div>
          </div>

          <div class="grid-2">
            <div>
              <label>Active Users</label>
              <input type="number" id="active_users" placeholder="20000" />
            </div>
            <div>
              <label>Avg Revenue per User / Month</label>
              <input type="number" id="arpu" placeholder="50" />
            </div>
          </div>

          <div class="grid-2">
            <div>
              <label>Engineer Hourly Cost (USD)</label>
              <input type="number" id="engineer_cost" placeholder="80" />
            </div>
            <div>
              <label>Records Stored</label>
              <input type="number" id="records" placeholder="200000" />
            </div>
          </div>

          <div class="grid-2">
            <div>
              <label>Deployment Exposure</label>
              <select id="exposure">
                <option value="public">Public Internet</option>
                <option value="internal">Internal Only</option>
                <option value="private">Private / Air-gapped</option>
              </select>
            </div>
            <div>
              <label>Downtime Cost / Hour (USD)</label>
              <input type="number" id="downtime_cost" placeholder="12000" />
            </div>
          </div>

          <label>Sensitive Data Types</label>
          <div class="checkbox-group" id="data_types">
            <label class="checkbox-item checked"><input type="checkbox" value="PII" checked> PII</label>
            <label class="checkbox-item checked"><input type="checkbox" value="financial" checked> Financial</label>
            <label class="checkbox-item"><input type="checkbox" value="health"> Health</label>
            <label class="checkbox-item"><input type="checkbox" value="credentials"> Credentials</label>
          </div>

          <label>Regulatory Frameworks</label>
          <div class="checkbox-group" id="regulations">
            <label class="checkbox-item checked"><input type="checkbox" value="GDPR" checked> GDPR</label>
            <label class="checkbox-item checked"><input type="checkbox" value="PCI_DSS" checked> PCI DSS</label>
            <label class="checkbox-item"><input type="checkbox" value="HIPAA"> HIPAA</label>
            <label class="checkbox-item"><input type="checkbox" value="CCPA"> CCPA</label>
          </div>

          <label>Product Description (helps AI understand business context)</label>
          <textarea id="product_desc" placeholder="e.g. B2B SaaS payments platform serving SMBs. Handles invoicing, payouts, and financial reporting."></textarea>

          <label>Tech Stack (helps AI assess real exploitability)</label>
          <textarea id="stack_desc" placeholder="e.g. Django REST API, PostgreSQL, Redis, hosted on AWS ECS. Public API behind Cloudflare WAF."></textarea>
        </div>
      </div>

      <!-- Right: Scan Config + Gemini -->
      <div>
        <div class="card">
          <div class="card-title">Repository Scan</div>

          <label>GitHub Repository URL</label>
          <input type="text" id="repo_url" placeholder="https://github.com/company/payment-api" />

          <label>Branch</label>
          <input type="text" id="branch" placeholder="main" value="main" />
        </div>

        <div class="card">
          <div class="card-title">AI Analysis (Gemini)</div>

          <div class="toggle-row">
            <label class="toggle">
              <input type="checkbox" id="gemini_toggle" onchange="toggleGemini(this)">
              <span class="toggle-slider"></span>
            </label>
            <div>
              <div class="toggle-label">Enable Gemini AI Analysis</div>
              <div class="toggle-desc">Assesses real exploitability + finds attack chains</div>
            </div>
          </div>

          <div id="gemini_fields" class="hidden">
            <label>Gemini API Key (free at aistudio.google.com)</label>
            <input type="password" id="gemini_key" placeholder="AIza..." />

            <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:16px;font-size:13px;color:var(--muted);">
              <strong style="color:var(--text);">With AI enabled, the engine will:</strong><br>
              • Read actual code context to filter false positives<br>
              • Adjust exploit probability based on real code patterns<br>
              • Understand what each endpoint actually does<br>
              • Find attack chains across multiple vulnerabilities<br>
              • Generate specific fix code for each vulnerability
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">What Happens Next</div>
          <div style="font-size:13px;color:var(--muted);line-height:1.8;">
            1. Repository is cloned and scanned with Semgrep<br>
            2. Each finding is classified and financially modeled<br>
            3. <span id="ai_step_desc">Financial impact calculated from company context</span><br>
            4. Results ranked by expected dollar loss<br>
            5. Executive brief generated per vulnerability<br>
            6. Board-level summary produced
          </div>
        </div>

        <button class="btn btn-primary btn-lg" onclick="runScan()" id="scan_btn">
          🔍 Run Security Scan
        </button>
        <div class="error-box" id="scan_error"></div>
      </div>
    </div>
  </div>

  <!-- MANUAL TAB -->
  <div id="tab-manual" class="hidden">
    <div class="grid-2">
      <div>
        <div class="card">
          <div class="card-title">Company Context</div>
          <p style="font-size:13px;color:var(--muted);margin-bottom:16px;">
            Same as the Scan tab. Fill in the fields there — they are shared.
          </p>
          <a href="#" onclick="switchTab('scan');return false;" style="color:var(--accent);font-size:13px;">
            ← Fill in company context in the Scan tab
          </a>
        </div>
      </div>
      <div>
        <div class="card">
          <div class="card-title">Vulnerabilities (JSON)</div>
          <p style="font-size:13px;color:var(--muted);margin-bottom:12px;">
            Paste vulnerability data directly. Useful for testing without a repo.
          </p>
          <textarea id="manual_vulns" style="min-height:300px;" placeholder='[
  {
    "id": "VULN_001",
    "raw_rule_id": "sql-injection",
    "file": "payments/api.py",
    "line": 102,
    "message": "Unsanitized input in SQL query",
    "severity": "high",
    "exposure": "PUBLIC"
  },
  {
    "id": "VULN_002",
    "raw_rule_id": "hardcoded-secret",
    "file": "config/settings.py",
    "line": 14,
    "message": "Hardcoded API key found",
    "severity": "critical",
    "exposure": "PUBLIC"
  }
]'></textarea>
          <button class="btn btn-primary btn-lg" onclick="runManual()" id="manual_btn">
            📊 Analyze Vulnerabilities
          </button>
          <div class="error-box" id="manual_error"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- LOADING -->
  <div class="loading" id="loading">
    <div class="spinner"></div>
    <div style="font-size:16px;font-weight:600;margin-bottom:16px;">Analyzing your codebase...</div>
    <div class="loading-steps" id="loading_steps">
      <div class="loading-step" id="step1">⏳ Scanning repository for vulnerabilities</div>
      <div class="loading-step" id="step2">⏳ Classifying and modeling financial impact</div>
      <div class="loading-step" id="step3">⏳ Running AI analysis on code context</div>
      <div class="loading-step" id="step4">⏳ Detecting attack chains</div>
      <div class="loading-step" id="step5">⏳ Generating executive briefs</div>
    </div>
  </div>

  <!-- RESULTS -->
  <div id="results">

    <!-- Metric bar -->
    <div class="section-title">
      Risk Assessment — <span id="result_company">Company</span>
      <span id="ai_badge_header" class="hidden" style="margin-left:12px;">
        <span class="ai-badge">✦ AI Analyzed</span>
      </span>
    </div>

    <div class="grid-3" id="metrics" style="margin-bottom:32px;"></div>

    <!-- Executive Summary -->
    <div class="section-title">Board Summary</div>
    <div class="summary-pre" id="executive_summary"></div>

    <!-- Attack Chains -->
    <div id="chains_section" class="hidden">
      <div class="section-title">⚠️ Attack <span>Chains Detected</span></div>
      <p style="font-size:13px;color:var(--muted);margin-bottom:20px;">
        These vulnerabilities can be combined by an attacker into a single multi-step breach path,
        causing greater damage than any individual bug.
      </p>
      <div id="chains_list"></div>
    </div>

    <!-- Vulnerability List -->
    <div class="section-title">Vulnerabilities — <span>Ranked by Financial Priority</span></div>
    <div id="vuln_list"></div>

    <button class="btn btn-outline" onclick="resetUI()" style="margin-top:20px;">
      ← Run Another Scan
    </button>
  </div>

</div>

<script>
  // --- Tab switching ---
  function switchTab(tab) {
    document.querySelectorAll('.tab').forEach((t,i) => {
      t.classList.toggle('active', (i === 0 && tab === 'scan') || (i === 1 && tab === 'manual'));
    });
    document.getElementById('tab-scan').classList.toggle('hidden', tab !== 'scan');
    document.getElementById('tab-manual').classList.toggle('hidden', tab !== 'manual');
  }

  // --- Gemini toggle ---
  function toggleGemini(cb) {
    document.getElementById('gemini_fields').classList.toggle('hidden', !cb.checked);
    document.getElementById('ai_step_desc').textContent = cb.checked
      ? 'Gemini analyzes actual code to filter false positives'
      : 'Financial impact calculated from company context';
  }

  // Checkbox items visual state
  document.querySelectorAll('.checkbox-item input[type=checkbox]').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.closest('.checkbox-item').classList.toggle('checked', cb.checked);
    });
  });

  // --- Collect company context ---
  function getCompany() {
    const checked = (id) => [...document.querySelectorAll(`#${id} input:checked`)].map(c => c.value);
    return {
      company_name: document.getElementById('company_name').value || 'Demo Company',
      industry: document.getElementById('industry').value,
      annual_revenue: parseFloat(document.getElementById('annual_revenue').value) || 12000000,
      monthly_revenue: parseFloat(document.getElementById('monthly_revenue').value) || 1000000,
      active_users: parseInt(document.getElementById('active_users').value) || 20000,
      arpu: parseFloat(document.getElementById('arpu').value) || 50,
      engineer_hourly_cost: parseFloat(document.getElementById('engineer_cost').value) || 80,
      deployment_exposure: document.getElementById('exposure').value,
      infrastructure_type: 'cloud',
      sensitive_data_types: checked('data_types').length ? checked('data_types') : ['PII'],
      regulatory_frameworks: checked('regulations').length ? checked('regulations') : ['GDPR'],
      estimated_records_stored: parseInt(document.getElementById('records').value) || 200000,
      estimated_downtime_cost_per_hour: parseFloat(document.getElementById('downtime_cost').value) || null,
      company_size: document.getElementById('company_size').value,
      product_description: document.getElementById('product_desc').value || null,
      stack_description: document.getElementById('stack_desc').value || null,
    };
  }

  // --- Loading animation ---
  let loadingInterval;
  function startLoading(withGemini) {
    document.getElementById('loading').classList.add('show');
    document.getElementById('results').classList.remove('show');
    document.getElementById('results').style.display = 'none';
    const steps = [1,2,3,4,5];
    steps.forEach(i => {
      const el = document.getElementById(`step${i}`);
      el.className = 'loading-step';
      el.textContent = el.textContent.replace(/^[✅⏳]/, '⏳');
    });
    if (!withGemini) {
      document.getElementById('step3').style.opacity = '0.3';
      document.getElementById('step4').style.opacity = '0.3';
    }
    let current = 1;
    loadingInterval = setInterval(() => {
      if (current > 1) {
        const prev = document.getElementById(`step${current-1}`);
        prev.classList.add('done');
        prev.textContent = prev.textContent.replace('⏳', '✅');
      }
      if (current <= 5) {
        const curr = document.getElementById(`step${current}`);
        curr.classList.add('active');
        current++;
      }
    }, withGemini ? 2500 : 1200);
  }

  function stopLoading() {
    clearInterval(loadingInterval);
    document.getElementById('loading').classList.remove('show');
  }

  // --- Format money ---
  function fmtMoney(n) {
    if (n >= 1000000) return `$${(n/1000000).toFixed(1)}M`;
    if (n >= 1000)    return `$${(n/1000).toFixed(0)}K`;
    return `$${n.toFixed(0)}`;
  }

  // --- Render results ---
  function renderResults(data) {
    stopLoading();
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').classList.add('show');

    const { results, attack_chains, executive_summary,
            total_expected_loss, total_fix_cost, gemini_enabled } = data;

    document.getElementById('result_company').textContent =
      document.getElementById('company_name').value || 'Company';

    if (gemini_enabled) {
      document.getElementById('ai_badge_header').classList.remove('hidden');
    }

    // Metrics
    const totalImpact = results.reduce((s,r) => s + r.total_impact, 0);
    const critical = results.filter(r => r.expected_loss >= 100000).length;
    const roi = total_fix_cost > 0 ? Math.round(total_expected_loss / total_fix_cost) : 0;

    document.getElementById('metrics').innerHTML = `
      <div class="metric-card">
        <div class="metric-value">${fmtMoney(total_expected_loss)}</div>
        <div class="metric-label">Total Expected Loss</div>
      </div>
      <div class="metric-card">
        <div class="metric-value green">${fmtMoney(total_fix_cost)}</div>
        <div class="metric-label">Total Fix Cost</div>
      </div>
      <div class="metric-card">
        <div class="metric-value orange">${roi}×</div>
        <div class="metric-label">ROI of Fixing Everything</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">${results.length}</div>
        <div class="metric-label">Vulnerabilities Found</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">${critical}</div>
        <div class="metric-label">Critical This Sprint</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">${attack_chains.length}</div>
        <div class="metric-label">Attack Chains</div>
      </div>
    `;

    // Executive summary
    document.getElementById('executive_summary').textContent = executive_summary;

    // Attack chains
    if (attack_chains.length > 0) {
      document.getElementById('chains_section').classList.remove('hidden');
      document.getElementById('chains_list').innerHTML = attack_chains.map(c => `
        <div class="chain-card">
          <div class="chain-title">
            ⛓️ ${c.chain_id}
            <span style="font-size:12px;background:rgba(230,57,70,0.2);padding:2px 8px;border-radius:4px;">${c.combined_severity.toUpperCase()}</span>
          </div>
          <div style="font-size:14px;margin-bottom:12px;color:#c0c0d8;">${c.chain_description}</div>
          <div class="chain-steps">
            ${c.chain_steps.map(s => `<div class="chain-step">${s}</div>`).join('')}
          </div>
          <div style="margin-top:12px;display:flex;gap:16px;align-items:center;">
            <div>
              <div style="font-size:11px;color:var(--muted);text-transform:uppercase;">Combined Expected Loss</div>
              <div class="chain-loss">${fmtMoney(c.combined_expected_loss)}</div>
            </div>
            <div style="font-size:12px;color:var(--muted);">
              Involves: ${c.vulnerability_ids.join(', ')}
            </div>
          </div>
        </div>
      `).join('');
    }

    // Vulnerability list
    document.getElementById('vuln_list').innerHTML = results.map((r, i) => {
      const tier = r.expected_loss >= 100000 ? '🔴'
                 : r.expected_loss >= 30000  ? '🟠'
                 : r.expected_loss >= 5000   ? '🟡' : '🟢';
      const gBadge = r.gemini_analysis
        ? `<span class="ai-badge">✦ AI</span>` : '';
      const fpWarn = r.gemini_analysis && r.gemini_analysis.false_positive_likelihood === 'high'
        ? `<span style="font-size:11px;background:rgba(241,196,15,0.2);color:var(--yellow);padding:2px 8px;border-radius:4px;">⚠️ Possible false positive</span>` : '';
      const chainBadge = r.attack_chains && r.attack_chains.length
        ? `<span style="font-size:11px;background:rgba(230,57,70,0.2);color:var(--accent);padding:2px 8px;border-radius:4px;">⛓️ In attack chain</span>` : '';

      return `
        <div class="vuln-card">
          <div class="vuln-header" onclick="toggleVuln(${i})">
            <div class="vuln-tier">${tier}</div>
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span class="vuln-title">${r.bug_type.replace(/_/g,' ')}</span>
                ${gBadge} ${fpWarn} ${chainBadge}
              </div>
              <div class="vuln-file">${r.file}:${r.line} · ${r.exposure}</div>
            </div>
            <div style="text-align:right;">
              <div class="vuln-loss">${fmtMoney(r.expected_loss)}</div>
              <div style="font-size:11px;color:var(--muted);">expected loss</div>
            </div>
            <div class="vuln-expand" id="expand_${i}">▼</div>
          </div>
          <div class="vuln-body" id="vuln_body_${i}">
            ${r.gemini_analysis ? `
              <div style="background:rgba(52,152,219,0.08);border:1px solid rgba(52,152,219,0.2);border-radius:8px;padding:14px;margin-bottom:16px;">
                <div style="font-size:11px;font-weight:700;color:var(--blue);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">✦ Gemini AI Analysis</div>
                <div style="font-size:13px;color:#b0cce8;margin-bottom:6px;"><strong>What this code does:</strong> ${r.gemini_analysis.business_context}</div>
                <div style="font-size:13px;color:#b0cce8;margin-bottom:6px;"><strong>Exploitable?</strong> ${r.gemini_analysis.is_exploitable ? 'Yes' : 'No'} (${r.gemini_analysis.exploitability_confidence} confidence)</div>
                <div style="font-size:13px;color:#b0cce8;margin-bottom:6px;"><strong>Why:</strong> ${r.gemini_analysis.exploitability_reasoning}</div>
                <div style="font-size:13px;color:#b0cce8;"><strong>Fix:</strong> ${r.gemini_analysis.recommended_fix}</div>
              </div>` : ''}
            <div class="brief-pre">${r.business_brief}</div>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
              <div style="flex:1;min-width:140px;background:var(--surface2);border-radius:8px;padding:12px;text-align:center;">
                <div style="font-size:20px;font-weight:800;font-family:var(--font-mono);color:var(--accent);">${fmtMoney(r.expected_loss)}</div>
                <div style="font-size:11px;color:var(--muted);">Expected Loss</div>
              </div>
              <div style="flex:1;min-width:140px;background:var(--surface2);border-radius:8px;padding:12px;text-align:center;">
                <div style="font-size:20px;font-weight:800;font-family:var(--font-mono);color:var(--green);">${fmtMoney(r.fix_cost_usd)}</div>
                <div style="font-size:11px;color:var(--muted);">Fix Cost (${r.fix_effort_hours}h)</div>
              </div>
              <div style="flex:1;min-width:140px;background:var(--surface2);border-radius:8px;padding:12px;text-align:center;">
                <div style="font-size:20px;font-weight:800;font-family:var(--font-mono);color:var(--orange);">${r.roi_of_fixing}×</div>
                <div style="font-size:11px;color:var(--muted);">ROI of Fixing</div>
              </div>
              <div style="flex:1;min-width:140px;background:var(--surface2);border-radius:8px;padding:12px;text-align:center;">
                <div style="font-size:20px;font-weight:800;font-family:var(--font-mono);">${Math.round(r.effective_probability*100)}%</div>
                <div style="font-size:11px;color:var(--muted);">${r.gemini_analysis ? 'AI-Adjusted' : 'Exploit'} Probability</div>
              </div>
            </div>
          </div>
        </div>`;
    }).join('');
  }

  function toggleVuln(i) {
    const body   = document.getElementById(`vuln_body_${i}`);
    const expand = document.getElementById(`expand_${i}`);
    const open   = body.classList.toggle('open');
    expand.textContent = open ? '▲' : '▼';
  }

  // --- Run scan ---
  async function runScan() {
    const btn = document.getElementById('scan_btn');
    const err = document.getElementById('scan_error');
    err.classList.remove('show');
    const gemini_api_key = document.getElementById('gemini_toggle').checked
      ? document.getElementById('gemini_key').value : null;
    startLoading(!!gemini_api_key);
    btn.disabled = true;
    try {
      const res = await fetch('/scan-repo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          repo_url: document.getElementById('repo_url').value,
          branch:   document.getElementById('branch').value || 'main',
          company:  getCompany(),
          gemini_api_key
        })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || 'Scan failed');
      }
      renderResults(await res.json());
    } catch(e) {
      stopLoading();
      err.textContent = `Error: ${e.message}`;
      err.classList.add('show');
    } finally {
      btn.disabled = false;
    }
  }

  // --- Run manual ---
  async function runManual() {
    const btn = document.getElementById('manual_btn');
    const err = document.getElementById('manual_error');
    err.classList.remove('show');
    let vulns;
    try {
      vulns = JSON.parse(document.getElementById('manual_vulns').value);
    } catch {
      err.textContent = 'Invalid JSON. Please check the vulnerability input.';
      err.classList.add('show');
      return;
    }
    const gemini_api_key = document.getElementById('gemini_toggle').checked
      ? document.getElementById('gemini_key').value : null;
    startLoading(!!gemini_api_key);
    btn.disabled = true;
    try {
      const res = await fetch('/analyze-manual', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          vulnerabilities: vulns,
          company: getCompany(),
          gemini_api_key
        })
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || 'Analysis failed');
      }
      renderResults(await res.json());
    } catch(e) {
      stopLoading();
      err.textContent = `Error: ${e.message}`;
      err.classList.add('show');
    } finally {
      btn.disabled = false;
    }
  }

  function resetUI() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').classList.remove('show');
    document.getElementById('chains_section').classList.add('hidden');
    window.scrollTo(0,0);
  }
</script>
</body>
</html>
```

---

## RUN EVERYTHING

```bash
# Install
pip install fastapi uvicorn semgrep gitpython pydantic google-generativeai

# Start server
cd vfie
uvicorn main:app --reload --port 8000

# Open UI
open http://localhost:8000
```

---

## GET A FREE GEMINI API KEY

1. Go to https://aistudio.google.com
2. Sign in with a Google account
3. Click "Get API key"
4. Copy the key into the UI toggle field

Free tier: 60 requests/minute — more than enough for a full repo scan.

---

## QUICK TEST WITHOUT A REPO

Use the Manual Input tab and paste this:

```json
[
  { "id": "VULN_001", "raw_rule_id": "sql-injection",    "file": "payments/api.py",   "line": 102, "message": "Unsanitized input in SQL query",       "severity": "high",     "exposure": "PUBLIC" },
  { "id": "VULN_002", "raw_rule_id": "hardcoded-secret", "file": "config/settings.py","line": 14,  "message": "Hardcoded API key found",              "severity": "critical", "exposure": "PUBLIC" },
  { "id": "VULN_003", "raw_rule_id": "auth-bypass",      "file": "auth/login.py",     "line": 78,  "message": "Authentication logic can be bypassed", "severity": "critical", "exposure": "PUBLIC" },
  { "id": "VULN_004", "raw_rule_id": "idor",             "file": "api/users.py",      "line": 33,  "message": "Object reference not validated",       "severity": "high",     "exposure": "PUBLIC" }
]
```

---

## WHAT GEMINI CHANGES PER VULNERABILITY

| Without Gemini | With Gemini |
|---|---|
| 22% probability (table) | Adjusted based on whether input is actually user-controlled |
| Generic fix advice | Specific fix code for your exact ORM/framework |
| No false positive filter | "This is a test file — low priority" |
| No business context | "This handles payment processing for premium users" |
| Bugs scored independently | "These 3 bugs form a critical attack chain" |

---

## WHAT GEMINI STILL CANNOT DO

- See your live infrastructure (WAF rules, network topology)
- Verify the fix actually worked (needs code execution)
- Access real-time threat intelligence feeds
- Replace a senior security engineer's full assessment

---

## HONEST LIMITATIONS FOR DEMOS

All dollar figures are order-of-magnitude estimates for prioritization decisions.
Probabilities are calibrated industry estimates, adjusted by AI code analysis.
Expected loss is actuarial — it measures risk carrying cost, not guaranteed outcomes.
Gemini analysis is bounded by the code context sent — it cannot see your full system.

---
*End of AGENT.md v3 — Gemini + full UI + attack chains.*
*Build it in one sitting. Demo it in one meeting. Get the sprint approved.*