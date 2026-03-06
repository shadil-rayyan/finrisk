import json
from typing import Dict, Tuple
from models.company import CompanyContext
from models.risk_result import ImpactBreakdown


def load_breach_costs() -> Dict:
    with open("knowledge_base/breach_costs.json") as f:
        return json.load(f)


def load_regulatory_models() -> Dict:
    with open("knowledge_base/regulatory_models.json") as f:
        return json.load(f)


def load_downtime_estimates() -> Dict:
    with open("knowledge_base/downtime_estimates.json") as f:
        return json.load(f)


def compute_data_breach_cost(company: CompanyContext, bug_type: str, breach_costs: Dict) -> float:
    """Records exposed × cost per record (industry-adjusted)."""
    taxonomy_raw = open("knowledge_base/bug_taxonomy.json").read()
    taxonomy = json.loads(taxonomy_raw)
    bug_info = taxonomy.get(bug_type, {})
    
    # Only apply breach cost if this bug can exfiltrate data
    if not bug_info.get("data_exfiltration", False):
        return 0.0
    
    industry = company.industry.lower()
    cost_per_record = breach_costs["cost_per_record_by_industry"].get(
        industry, breach_costs["cost_per_record_by_industry"]["default"]
    )
    
    # Assume worst case: 20% of records exposed
    records_exposed = int(company.estimated_records_stored * 0.20)
    return records_exposed * cost_per_record


def compute_incident_response_cost(company: CompanyContext, breach_costs: Dict) -> float:
    return breach_costs["incident_response_cost"].get(company.company_size, 100000)


def compute_downtime_cost(company: CompanyContext, bug_type: str, downtime_estimates: Dict) -> float:
    downtime_hours = downtime_estimates["downtime_hours_by_bug_type"].get(bug_type, 2)
    
    # Use provided value or fall back to lookup table
    if company.estimated_downtime_cost_per_hour:
        cost_per_hour = company.estimated_downtime_cost_per_hour
    else:
        breach_costs = load_breach_costs()
        cost_per_hour = breach_costs["downtime_cost_per_hour"].get(
            company.company_size, 12000
        )
    
    return downtime_hours * cost_per_hour


def compute_regulatory_penalty(company: CompanyContext, reg_models: Dict) -> float:
    """Apply applicable regulatory fines based on frameworks + data types."""
    total_fine = 0.0
    arr = company.annual_revenue
    frameworks = [r.upper() for r in company.regulatory_frameworks]
    data_types = [d.upper() for d in company.sensitive_data_types]
    
    if "GDPR" in frameworks or "PII" in data_types:
        gdpr = reg_models["GDPR"]
        fine = min(arr * gdpr["fine_percentage_of_arr"], gdpr["max_fine_usd"])
        total_fine += fine
    
    if "PCI_DSS" in frameworks or "FINANCIAL" in data_types:
        pci = reg_models["PCI_DSS"]
        total_fine += pci["avg_fine"]
    
    if "HIPAA" in frameworks or "HEALTH" in data_types:
        hipaa = reg_models["HIPAA"]
        total_fine += hipaa["max_annual"]
    
    return total_fine


def compute_reputation_damage(
    company: CompanyContext,
    breach_cost: float,
    breach_costs: Dict
) -> float:
    """Churn-based reputation damage."""
    data_types = [d.upper() for d in company.sensitive_data_types]
    
    if any(d in data_types for d in ["FINANCIAL", "HEALTH"]):
        churn_rate = breach_costs["churn_rate_after_breach"]["high_sensitivity"]
    elif "PII" in data_types:
        churn_rate = breach_costs["churn_rate_after_breach"]["medium_sensitivity"]
    else:
        churn_rate = breach_costs["churn_rate_after_breach"]["low_sensitivity"]
    
    lost_users = company.active_users * churn_rate
    lost_revenue = lost_users * company.arpu * 12  # annualized
    return lost_revenue


def compute_total_impact(
    company: CompanyContext,
    bug_type: str
) -> Tuple[ImpactBreakdown, float]:
    """Run all impact components and return breakdown + total."""
    breach_costs = load_breach_costs()
    reg_models = load_regulatory_models()
    downtime_estimates = load_downtime_estimates()
    
    data_breach = compute_data_breach_cost(company, bug_type, breach_costs)
    incident_response = compute_incident_response_cost(company, breach_costs)
    downtime = compute_downtime_cost(company, bug_type, downtime_estimates)
    regulatory = compute_regulatory_penalty(company, reg_models)
    reputation = compute_reputation_damage(company, data_breach, breach_costs)
    
    breakdown = ImpactBreakdown(
        data_breach_cost=round(data_breach, 2),
        incident_response_cost=round(incident_response, 2),
        downtime_cost=round(downtime, 2),
        regulatory_penalty=round(regulatory, 2),
        reputation_damage=round(reputation, 2)
    )
    
    total = data_breach + incident_response + downtime + regulatory + reputation
    return breakdown, round(total, 2)
