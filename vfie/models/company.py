from pydantic import BaseModel
from typing import List, Optional

class CompanyContext(BaseModel):
    company_name: str
    industry: str                        # "finance", "healthcare", "technology", "retail", "saas"
    annual_revenue: float
    monthly_revenue: float
    active_users: int
    arpu: float                          # monthly revenue per user
    engineer_hourly_cost: float
    deployment_exposure: str             # "public", "internal", "private"
    infrastructure_type: str             # "cloud", "on_prem", "hybrid"
    sensitive_data_types: List[str]      # ["PII", "financial", "health", "credentials"]
    regulatory_frameworks: List[str]     # ["GDPR", "PCI_DSS", "HIPAA", "CCPA"]
    estimated_records_stored: int
    estimated_downtime_cost_per_hour: Optional[float] = None
    company_size: str                    # "startup", "mid_size", "enterprise"
    stack_description: Optional[str] = None   # e.g. "Django REST API, PostgreSQL, AWS"
    product_description: Optional[str] = None # e.g. "B2B payments platform"
