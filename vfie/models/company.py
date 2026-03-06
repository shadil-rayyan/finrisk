from pydantic import BaseModel
from typing import List, Optional

class CompanyContext(BaseModel):
    company_name: str
    industry: str                          # "finance", "healthcare", "technology", "retail"
    annual_revenue: float                  # in USD
    active_users: int
    arpu: float                            # average revenue per user per month
    engineer_hourly_cost: float            # default 80
    infrastructure_type: str               # "cloud", "on_prem", "hybrid"
    deployment_exposure: str               # "public", "internal", "private"
    sensitive_data_types: List[str]        # ["PII", "financial", "health"]
    regulatory_frameworks: List[str]       # ["GDPR", "PCI_DSS", "HIPAA"]
    estimated_records_stored: int
    estimated_downtime_cost_per_hour: Optional[float] = None  # auto-computed if None
    company_size: str                      # "startup", "mid_size", "enterprise"
