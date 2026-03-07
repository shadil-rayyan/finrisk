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

        breakdown, total_impact = compute_total_impact(company, bug_type, gemini_result)
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
