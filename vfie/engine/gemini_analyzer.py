import os
import json
import google.generativeai as genai
from typing import Optional
from models.risk_result import GeminiAnalysis
from models.company import CompanyContext

def init_gemini(api_key: str):
    genai.configure(api_key=api_key)

def analyze_vulnerability(
    bug_type: str,
    file: str,
    line: int,
    code_context: str,
    message: str,
    exposure: str,
    company: CompanyContext,
    baseline_probability: float
) -> Optional[GeminiAnalysis]:
    """
    Ask Gemini to analyze a single vulnerability with full code context.
    Returns structured analysis including adjusted probability and fix.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")  # free tier

    prompt = f"""You are a senior application security engineer performing a vulnerability assessment.

COMPANY CONTEXT:
- Company: {company.company_name}
- Industry: {company.industry}
- Product: {company.product_description or 'Not specified'}
- Tech stack: {company.stack_description or 'Not specified'}
- Data stored: {', '.join(company.sensitive_data_types)}
- Deployment: {exposure} facing

VULNERABILITY DETECTED:
- Type: {bug_type}
- File: {file}, Line: {line}
- Scanner message: {message}
- Baseline exploit probability: {baseline_probability}

CODE CONTEXT (lines around the vulnerability):
```
{code_context if code_context else "Code context not available — reason from file name and bug type."}
```

Analyze this vulnerability and respond ONLY with valid JSON in exactly this format:
{{
  "is_exploitable": true or false,
  "exploitability_confidence": "high" or "medium" or "low",
  "exploitability_reasoning": "2-3 sentences explaining WHY this is or isn't exploitable based on the actual code",
  "business_context": "1-2 sentences describing what this code actually does and what business function it serves",
  "adjusted_probability": 0.0 to 1.0 (adjust the baseline based on what you see in the code),
  "false_positive_likelihood": "high" or "medium" or "low",
  "recommended_fix": "Specific fix — include actual code if possible, or precise instructions",
  "fix_complexity": "simple" or "moderate" or "complex"
}}

Rules:
- If code context is unavailable, reason from file name, bug type, and company context
- Be specific — reference actual variable names or patterns you see in the code
- If this looks like a test file or dead code, say so and lower the probability
- If the input appears to come directly from user requests, raise the probability
- The recommended_fix must be actionable — not generic advice"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
        return GeminiAnalysis(
            is_exploitable=data.get("is_exploitable", True),
            exploitability_confidence=data.get("exploitability_confidence", "medium"),
            exploitability_reasoning=data.get("exploitability_reasoning", ""),
            business_context=data.get("business_context", ""),
            adjusted_probability=float(data.get("adjusted_probability", baseline_probability)),
            false_positive_likelihood=data.get("false_positive_likelihood", "medium"),
            recommended_fix=data.get("recommended_fix", "Review and remediate manually."),
            fix_complexity=data.get("fix_complexity", "moderate")
        )
    except Exception as e:
        print(f"Gemini analysis failed for {file}:{line} — {e}")
        return None
