def compute_expected_loss(probability: float, total_impact: float) -> float:
    """EL = P(exploit) × Total Financial Impact"""
    return round(probability * total_impact, 2)


def compute_priority_score(expected_loss: float, fix_effort_hours: float) -> float:
    """Higher = fix this first. Measures $ saved per engineering hour."""
    if fix_effort_hours <= 0:
        return 0.0
    return round(expected_loss / fix_effort_hours, 2)
