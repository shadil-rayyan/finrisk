from pydantic import BaseModel
from typing import List, Optional

class CompanyContext(BaseModel):
    company_name: str
    industry: str
    annual_revenue: float
    monthly_revenue: float
    active_users: Optional[int] = 0
    # Support for variations in the user's test list
    active_customers: Optional[int] = None
    active_stores: Optional[int] = None
    developers_using_platform: Optional[int] = None
    
    arpu: float
    engineer_hourly_cost: float
    deployment_exposure: str             # "public", "internal", "private"
    infrastructure_type: str             # "cloud", "on_prem", "hybrid"
    sensitive_data_types: List[str]      # ["PII", "financial", "health", "credentials"]
    regulatory_frameworks: List[str]     # ["GDPR", "PCI_DSS", "HIPAA", "CCPA"]
    estimated_records_stored: int
    estimated_downtime_cost_per_hour: Optional[float] = None
    company_size: str = "mid_size"
    stack_description: Optional[str] = None
    product_description: Optional[str] = None

    def get_total_users(self) -> int:
        return self.active_users or self.active_customers or self.active_stores or self.developers_using_platform or 0
