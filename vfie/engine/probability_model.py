import json
from typing import Dict


def load_probabilities() -> Dict:
    with open("knowledge_base/exploit_probability.json") as f:
        return json.load(f)


def get_probability(bug_type: str, exposure: str, probabilities: Dict) -> float:
    """
    Return P(exploit) for this bug type and exposure level.
    Exposure: PUBLIC, INTERNAL, PRIVATE
    """
    bug_probs = probabilities.get(bug_type, probabilities["UNKNOWN"])
    return bug_probs.get(exposure.upper(), 0.05)
