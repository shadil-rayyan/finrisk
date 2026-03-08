import json
import os
import re
import sys
import shutil
from datetime import datetime
from typing import Dict, Any, List

# Add current dir to sys.path for internal imports
sys.path.append(os.getcwd())

from models.company import CompanyContext
from engine.scanner import clone_repo, run_semgrep, parse_semgrep_findings
from main import run_risk_engine, generate_executive_summary

def parse_repo_json(file_path: str) -> List[Dict[str, Any]]:
    """Parse the markdown file and extract company info + JSON."""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by ## 
    sections = re.split(r'## \d+\.', content)[1:]
    experiments = []
    
    for section in sections:
        # Extract GitHub URL
        github_match = re.search(r'- \*\*GitHub\*\*: (https://github\.com/\S+)', section)
        # Extract Branch (if any)
        branch_match = re.search(r'- \*\*Branch\*\*: (\S+)', section)
        
        # Extract JSON block
        json_match = re.search(r'```json\n(.*?)\n```', section, re.DOTALL)
        
        if github_match and json_match:
            repo_url = github_match.group(1).strip()
            branch = branch_match.group(1).strip() if branch_match else "main"
            try:
                company_data = json.loads(json_match.group(1))
                experiments.append({
                    "repo_url": repo_url,
                    "branch": branch,
                    "company": company_data
                })
            except json.JSONDecodeError:
                continue
            
    return experiments

def run_experiment(exp: Dict[str, Any], output_dir: str):
    repo_url = exp["repo_url"]
    branch = exp["branch"]
    company_data = exp["company"]
    company = CompanyContext(**company_data)
    
    print(f"--- Starting Experiment: {company.company_name} ---")
    print(f"URL: {repo_url}")
    
    repo_path = None
    try:
        # 1. Clone
        print("Cloning repository...")
        repo_path = clone_repo(repo_url, branch)
        
        # 2. Raw Semgrep Scan
        print("Running Semgrep scan...")
        raw_findings = run_semgrep(repo_path)
        raw_count = len(raw_findings)
        print(f"Raw findings found: {raw_count}")
        
        # 3. Parsing for engine
        parsed_findings = parse_semgrep_findings(raw_findings, company.deployment_exposure, repo_path)
        
        # 4. AI-Enhanced Risk Engine
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found. AI features will be disabled.")
        
        print("Running Risk Analysis (AI Assistance Active)...")
        results, chains = run_risk_engine(parsed_findings, company, api_key)
        
        # AI Reduction Count: 
        # In our engine, if AI determines it's a false positive or low risk, 
        # it sets effective_probability to 0.01.
        # We define 'Filtered' findings as those that are truly exploitable according to AI.
        filtered_results = [r for r in results if r.effective_probability > 0.01]
        filtered_count = len(filtered_results)
        reduction_count = raw_count - filtered_count
        reduction_pct = (reduction_count / raw_count * 100) if raw_count > 0 else 0
        
        # 5. Save Report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{company.company_name.replace(' ', '_').lower()}_{timestamp}.md"
        output_path = os.path.join(output_dir, filename)
        
        # Rankings (results are already sorted by priority_score)
        summary = generate_executive_summary(results, company, chains)
        
        report_content = [
            f"# Experiment Report: {company.company_name}",
            f"- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Source Repo**: [{repo_url}]({repo_url})",
            f"- **Branch**: `{branch}`",
            "",
            "## 🔍 Scan Metrics",
            f"- **Total Raw Findings (Semgrep)**: {raw_count}",
            f"- **AI-Verified Exploitability Count**: {filtered_count}",
            f"- **AI-Assisted Reduction**: **{reduction_count}** ({reduction_pct:.1f}%)",
            "",
            "## 💰 Top Financial Risks (Ranked by ROI)",
            "| Rank | Type | Expected Loss | Priority (EL/Hour) | File |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        
        for i, r in enumerate(results[:10]):
            report_content.append(f"| {i+1} | {r.bug_type} | ${r.expected_loss:,.2f} | {r.priority_score:,.2f} | `{r.file}` |")
            
        report_content.append("\n## 📝 Executive Summary")
        report_content.append(summary)
        
        with open(output_path, 'w') as f:
            f.write("\n".join(report_content))
            
        print(f"Successfully generated report: {output_path}")
        
    except Exception as e:
        print(f"Error in experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if repo_path and os.path.exists(repo_path):
            print(f"Cleaning up {repo_path}...")
            shutil.rmtree(repo_path)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    INPUT_FILE = "/home/shadil/code/personal/test/finrisk/Doc/archive/experiment_log/repo_json.md"
    OUTPUT_DIR = "/home/shadil/code/personal/test/finrisk/Doc/experiment_log"
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    experiments = parse_repo_json(INPUT_FILE)
    
    if not experiments:
        print("No experiments found.")
        sys.exit(0)
    
    # Run based on arguments or first one
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
        if target == "all":
            for exp in experiments:
                run_experiment(exp, OUTPUT_DIR)
        else:
            found = False
            for exp in experiments:
                if target in exp["company"]["company_name"].lower():
                    run_experiment(exp, OUTPUT_DIR)
                    found = True
                    break
            if not found:
                 print(f"Could not find experiment matching: {target}")
    else:
        # Run first one
        run_experiment(experiments[0], OUTPUT_DIR)
