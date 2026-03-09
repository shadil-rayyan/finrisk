# VFIE Test Targets — Enriched Company Contexts
Use these JSON contexts to test the Risk Engine for different open-source projects.

## 1. Analytics SaaS: Plausible Analytics
- **GitHub**: https://github.com/plausible/analytics
- **Branch**: master 
- **Profile**: Privacy-friendly analytics alternative.

```json
{
  "company_name": "Plausible Analytics",
  "industry": "technology",
  "annual_revenue": 2500000,
  "monthly_revenue": 210000,
  "active_users": 4000,
  "arpu": 50,
  "estimated_records_stored": 20000000,
  "deployment_exposure": "public",
  "infrastructure_type": "cloud",
  "engineer_hourly_cost": 110,
  "estimated_downtime_cost_per_hour": 8000,
  "regulatory_frameworks": ["GDPR"],
  "sensitive_data_types": ["PII", "credentials"],
  "company_size": "startup",
  "product_description": "Privacy-friendly website analytics platform used as a cookie-less alternative to Google Analytics.",
  "stack_description": "Elixir (Phoenix), PostgreSQL, ClickHouse for large-scale event storage, hosted on DigitalOcean/Fastly."
}
```
Below is a **diverse list of open‑source repositories** across *different industries and technology stacks* (not just analytics/SaaS). Each entry is structured like your *Plausible Analytics* example so you can plug them into your VFIE evaluation directly.

---

## 1. **E‑Commerce Platform: Spree Commerce**

* **GitHub**: [https://github.com/spree/spree](https://github.com/spree/spree)
* **Branch**: `main`
* **Profile**: Open‑source, API‑first e‑commerce framework supporting multi‑store, multi‑vendor, and headless commerce. ([Wikipedia][1])

```json
{
  "company_name": "Spree Commerce",
  "industry": "retail / e-commerce",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public",
  "infrastructure_type": "cloud/self‑hosted",
  "engineer_hourly_cost": 130,
  "estimated_downtime_cost_per_hour": 90000,
  "regulatory_frameworks": ["PCI_DSS", "GDPR"],
  "sensitive_data_types": ["PII", "financial", "credentials"],
  "company_size": "open source ecosystem",
  "product_description": "API‑first open‑source e‑commerce platform with multi‑store, headless support and extensible marketplace architecture.",
  "stack_description": "Ruby on Rails backend with optional TypeScript/React headless frontend."
}
```

---

## 2. **Enterprise ERP: ERPNext**

* **GitHub**: [https://github.com/frappe/erpnext](https://github.com/frappe/erpnext)
* **Branch**: `main`
* **Profile**: Full enterprise resource planning (ERP) system covering accounting, CRM, inventories, manufacturing, HR, and more. ([GitHub][2])

```json
{
  "company_name": "ERPNext",
  "industry": "enterprise / operations",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public / self‑hosted",
  "infrastructure_type": "cloud / on‑premise",
  "engineer_hourly_cost": 150,
  "estimated_downtime_cost_per_hour": 120000,
  "regulatory_frameworks": ["GDPR"],
  "sensitive_data_types": ["financial", "PII", "operations"],
  "company_size": "large open source project",
  "product_description": "Fully featured open‑source ERP covering accounting, CRM, HR, inventory, projects, and more for multiple industries.",
  "stack_description": "Python (backend), JavaScript (frontend), MariaDB backend."
}
```

---

## 3. **Open‑Source Wiki: Gollum**

* **GitHub**: [https://github.com/gollum/gollum](https://github.com/gollum/gollum)
* **Branch**: `master`
* **Profile**: Wiki system powered by Git; used for documentation, knowledge bases, and versioned content. ([Wikipedia][3])

```json
{
  "company_name": "Gollum Wiki",
  "industry": "knowledge / documentation",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public / self‑hosted",
  "infrastructure_type": "cloud / private servers",
  "engineer_hourly_cost": 100,
  "estimated_downtime_cost_per_hour": 20000,
  "regulatory_frameworks": ["GDPR"],
  "sensitive_data_types": ["documentation", "user edits"],
  "company_size": "open‑source project",
  "product_description": "Git‑backed wiki system for collaborative documentation and knowledge bases.",
  "stack_description": "Ruby backend with Git storage for versioned pages."
}
```

---

## 4. **Industrial Machine Learning Library: Infer.NET**

* **GitHub**: [https://github.com/dotnet/infer](https://github.com/dotnet/infer)
* **Branch**: `main`
* **Profile**: Microsoft Research library for probabilistic programming and Bayesian inference — used in AI/ML systems across industries. ([Wikipedia][4])

```json
{
  "company_name": "Infer.NET",
  "industry": "machine learning / research",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public",
  "infrastructure_type": "software library",
  "engineer_hourly_cost": 180,
  "estimated_downtime_cost_per_hour": 50000,
  "regulatory_frameworks": [],
  "sensitive_data_types": ["models", "training data"],
  "company_size": "enterprise‑open source",
  "product_description": "Machine learning library for probabilistic inference across domains such as healthcare, AI, and decision systems.",
  "stack_description": "C# / .NET library for Bayesian modelling and inference."
}
```

---

## 5. **Legacy E‑Commerce: osCommerce**

* **GitHub**: [https://github.com/osCommerce/osCommerce-V4](https://github.com/osCommerce/osCommerce-V4)
* **Branch**: `main`
* **Profile**: Classic open‑source e‑commerce store platform widely used in smaller online retail setups. ([Wikipedia][5])

```json
{
  "company_name": "osCommerce",
  "industry": "e‑commerce / SMB retail",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public / self‑hosted",
  "infrastructure_type": "cloud / private hosting",
  "engineer_hourly_cost": 110,
  "estimated_downtime_cost_per_hour": 25000,
  "regulatory_frameworks": ["GDPR"],
  "sensitive_data_types": ["financial", "credentials"],
  "company_size": "open source project",
  "product_description": "Open‑source webshop system built in PHP with broad adoption in small and medium retail sites.",
  "stack_description": "PHP backend with MySQL."
}
```


## 1. **Mojaloop — Open Financial Interoperability Platform**

* **GitHub**: [https://github.com/mojaloop/](https://github.com/mojaloop/)
* **Branch**: `main`
* **Profile**: Platform enabling **interoperable digital payments**, designed to facilitate financial inclusion by connecting banks, mobile money providers, and fintechs. Used as a reference implementation for national/region‑wide payments rails. ([Wikipedia][1])

```json
{
  "company_name": "Mojaloop",
  "industry": "financial services / fintech",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public",
  "infrastructure_type": "cloud/microservices",
  "engineer_hourly_cost": 140,
  "estimated_downtime_cost_per_hour": 150000,
  "regulatory_frameworks": ["global payments compliance"],
  "sensitive_data_types": ["financial transactions", "PII"],
  "company_size": "open source ecosystem",
  "product_description": "Open‑source interoperable digital payments platform reference implementation for inclusive financial systems.",
  "stack_description": "Node.js/TypeScript microservices (routing, clearing, settlement) with REST APIs."
}
```

---

## 2. **FarmBot — Precision Agriculture Robotics**

* **GitHub Source**: (Repo implied, project originates from [https://github.com/FarmBot](https://github.com/FarmBot))
* **Profile**: **Precision agriculture CNC robot** that automates farming tasks — planting seeds, watering, performing repeatable crop care. Useful for agritech and robotics research. ([Wikipedia][2])

```json
{
  "company_name": "FarmBot",
  "industry": "agriculture / robotics",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "on‑farm/public",
  "infrastructure_type": "embedded/IoT",
  "engineer_hourly_cost": 130,
  "estimated_downtime_cost_per_hour": 5000,
  "regulatory_frameworks": ["agriculture safety"],
  "sensitive_data_types": ["farm operational data"],
  "company_size": "open source community",
  "product_description": "Open‑source autonomous farming robot for precision agriculture tasks.",
  "stack_description": "Firmware + web control stack with CNC motion control and crop planning modules."
}
```

---

## 3. **Imhotep Smart Clinic — Healthcare Management System**

* **GitHub**: [https://github.com/topics/open-source-healthcare](https://github.com/topics/open-source-healthcare)
* **Profile**: **Clinic management and medical records platform** that supports patient scheduling, prescriptions, and practice workflows. Suitable for healthtech domain testing. ([GitHub][3])

```json
{
  "company_name": "Imhotep Smart Clinic",
  "industry": "healthcare management",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public/self‑hosted",
  "infrastructure_type": "cloud / on‑premise",
  "engineer_hourly_cost": 150,
  "estimated_downtime_cost_per_hour": 80000,
  "regulatory_frameworks": ["HIPAA (US)", "GDPR (EU)"],
  "sensitive_data_types": ["medical records", "PII"],
  "company_size": "open source project",
  "product_description": "Healthcare clinic management application with patient records, scheduling and prescribing features.",
  "stack_description": "Django/Python backend with modern frontend components."
}
```

---

## 4. **OpenMRS — Electronic Medical Records (EMR) Platform**

* **GitHub**: [https://github.com/openmrs](https://github.com/openmrs)
* **Profile**: Widely used **open‑source healthcare EMR/EHR** system for clinical workflows, patient record management, lab results, and health data interoperability. (Directory includes multiple repos.) ([Facile Technolab][4])

```json
{
  "company_name": "OpenMRS",
  "industry": "healthcare / clinical systems",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public / hosted",
  "infrastructure_type": "cloud / on‑premise",
  "engineer_hourly_cost": 160,
  "estimated_downtime_cost_per_hour": 100000,
  "regulatory_frameworks": ["HIPAA", "GDPR"],
  "sensitive_data_types": ["EMR", "clinical diagnostics"],
  "company_size": "global open source initiative",
  "product_description": "Open source electronic medical records system used by clinics and health organizations worldwide.",
  "stack_description": "Java backend with REST APIs and modular service architecture."
}
```

---

## 5. **Ekylibre — Farm & Business Management**

* **GitHub**: (Listed on Awesome agriculture but widely available on GitHub)
* **Profile**: **Farm business and agricultural management** software — tracks production, planning, inventory and farm economics. Good for business/ops domain analysis. ([GitHub][5])

```json
{
  "company_name": "Ekylibre",
  "industry": "agriculture / enterprise",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public / self‑hosted",
  "infrastructure_type": "cloud / on‑premise",
  "engineer_hourly_cost": 140,
  "estimated_downtime_cost_per_hour": 30000,
  "regulatory_frameworks": ["GDPR"],
  "sensitive_data_types": ["operational data"],
  "company_size": "open source project",
  "product_description": "Open‑source enterprise farm and crop management platform for agricultural operations.",
  "stack_description": "Rails/Python (varies) with business process and dashboard components."
}
```

## 6. **Sarvwigyan — Educational Content Platform**

* **GitHub**: [https://github.com/Sarvwigyan](https://github.com/Sarvwigyan) (example static repo)
* **Profile**: **Open educational content and knowledge portal** with science/tech learning resources — representing edtech and community knowledge systems. ([Wikipedia][6])

```json
{
  "company_name": "Sarvwigyan",
  "industry": "education / edtech",
  "annual_revenue": 0,
  "monthly_revenue": 0,
  "active_users": null,
  "arpu": null,
  "estimated_records_stored": null,
  "deployment_exposure": "public",
  "infrastructure_type": "static web / cloud",
  "engineer_hourly_cost": 90,
  "estimated_downtime_cost_per_hour": 10000,
  "regulatory_frameworks": ["GDPR"],
  "sensitive_data_types": ["public learning content"],
  "company_size": "community project",
  "product_description": "Open source educational content portal with science and technology learning materials.",
  "stack_description": "Static site hosted via GitHub Pages."
}
```

