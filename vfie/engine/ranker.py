from typing import List
from models.risk_result import RiskResult


def rank_vulnerabilities(results: List[RiskResult]) -> List[RiskResult]:
    """Sort by priority_score descending (highest ROI fixes first)."""
    return sorted(results, key=lambda r: r.priority_score, reverse=True)
