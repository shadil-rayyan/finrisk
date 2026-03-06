from pydantic import BaseModel
from typing import Dict

class ImpactBreakdown(BaseModel):
    data_breach_cost: float
    incident_response_cost: float
    downtime_cost: float
    regulatory_penalty: float
    reputation_damage: float

class RiskResult(BaseModel):
    vulnerability_id: str
    bug_type: str
    file: str
    line: int
    severity: str
    exposure: str
    probability_of_exploit: float
    impact_breakdown: ImpactBreakdown
    total_impact: float
    expected_loss: float
    fix_effort_hours: float
    priority_score: float          # expected_loss / fix_effort_hours
    explanation: str
