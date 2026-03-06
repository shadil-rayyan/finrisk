import json
import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.company import CompanyContext
from models.vulnerability import Vulnerability
from models.risk_result import RiskResult

from engine.scanner import clone_repo, run_semgrep, parse_semgrep_findings
from engine.classifier import classify_bug, get_fix_effort, load_taxonomy
from engine.probability_model import load_probabilities, get_probability
from engine.impact_model import compute_total_impact
from engine.expected_loss import compute_expected_loss, compute_priority_score
from engine.ranker import rank_vulnerabilities
from engine.explainer import generate_explanation

app = FastAPI(title="Vulnerability Financial Impact Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    company: CompanyContext


class ManualScanRequest(BaseModel):
    """For testing without cloning a repo — supply vulnerabilities directly."""
    vulnerabilities: List[dict]
    company: CompanyContext


def run_risk_engine(parsed_findings: List[dict], company: CompanyContext) -> List[RiskResult]:
    taxonomy = load_taxonomy()
    probabilities = load_probabilities()
    results = []
    
    for finding in parsed_findings:
        bug_type = classify_bug(
            finding.get("raw_rule_id", ""),
            finding.get("message", "")
        )
        fix_effort = get_fix_effort(bug_type, taxonomy)
        exposure = finding.get("exposure", company.deployment_exposure.upper())
        
        probability = get_probability(bug_type, exposure, probabilities)
        impact_breakdown, total_impact = compute_total_impact(company, bug_type)
        expected_loss = compute_expected_loss(probability, total_impact)
        priority_score = compute_priority_score(expected_loss, fix_effort)
        
        result = RiskResult(
            vulnerability_id=finding["id"],
            bug_type=bug_type,
            file=finding["file"],
            line=finding["line"],
            severity=finding.get("severity", "medium"),
            exposure=exposure,
            probability_of_exploit=probability,
            impact_breakdown=impact_breakdown,
            total_impact=total_impact,
            expected_loss=expected_loss,
            fix_effort_hours=fix_effort,
            priority_score=priority_score,
            explanation=""  # filled below
        )
        result.explanation = generate_explanation(result, company)
        results.append(result)
    
    return rank_vulnerabilities(results)


@app.post("/scan-repo", response_model=List[RiskResult])
async def scan_repo(request: ScanRequest):
    """Clone a GitHub repo, run Semgrep, compute financial risk for each finding."""
    repo_path = None
    try:
        repo_path = clone_repo(request.repo_url, request.branch)
        raw_findings = run_semgrep(repo_path)
        parsed = parse_semgrep_findings(raw_findings, request.company.deployment_exposure)
        results = run_risk_engine(parsed, request.company)
        
        # Save results
        os.makedirs("data", exist_ok=True)
        with open("data/risk_results.json", "w") as f:
            json.dump([r.dict() for r in results], f, indent=2)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)


@app.post("/analyze-manual", response_model=List[RiskResult])
async def analyze_manual(request: ManualScanRequest):
    """
    Submit vulnerabilities manually (no repo needed).
    Useful for testing and demo.
    
    Each vuln dict: { "id": "VULN_001", "raw_rule_id": "sqli", "file": "api.py",
                      "line": 42, "message": "SQL injection", "severity": "high",
                      "exposure": "PUBLIC" }
    """
    results = run_risk_engine(request.vulnerabilities, request.company)
    return results


@app.get("/risk-report")
async def get_last_report():
    """Return the last saved risk report."""
    path = "data/risk_results.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="No report found. Run /scan-repo first.")
    with open(path) as f:
        return json.load(f)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
