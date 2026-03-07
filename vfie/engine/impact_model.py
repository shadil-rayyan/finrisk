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
