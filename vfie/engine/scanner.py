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
