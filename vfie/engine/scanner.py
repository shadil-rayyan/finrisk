import subprocess
import json
import os
import tempfile
from typing import List, Dict, Any
import git


def clone_repo(repo_url: str, branch: str = "main") -> str:
    """Clone repo to temp dir, return path."""
    tmp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, tmp_dir, branch=branch, depth=1)
    return tmp_dir


def run_semgrep(repo_path: str) -> List[Dict[str, Any]]:
    """Run semgrep with security ruleset, return raw findings."""
    result = subprocess.run(
        [
            "semgrep",
            "--config", "p/security-audit",
            "--config", "p/owasp-top-ten",
            "--json",
            "--quiet",
            repo_path
        ],
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"Semgrep failed: {result.stderr}")
    
    try:
        data = json.loads(result.stdout)
        return data.get("results", [])
    except json.JSONDecodeError:
        return []


def parse_semgrep_findings(findings: List[Dict], exposure: str) -> List[Dict]:
    """Normalize semgrep output into our internal schema."""
    parsed = []
    for i, f in enumerate(findings):
        parsed.append({
            "id": f"VULN_{i+1:03d}",
            "raw_rule_id": f.get("check_id", "unknown"),
            "file": f.get("path", "unknown"),
            "line": f.get("start", {}).get("line", 0),
            "message": f.get("extra", {}).get("message", ""),
            "severity": f.get("extra", {}).get("severity", "WARNING").lower(),
            "exposure": exposure.upper()
        })
    return parsed
