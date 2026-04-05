def sort_candidates(candidates: list):
    def strength_value(item):
        mapping = {
            "Strong": 3,
            "Medium": 2,
            "Weak": 1
        }
        return mapping.get(item.get("evidence_strength", "Weak"), 1)

    return sorted(
        candidates,
        key=lambda c: (
            c.get("final_score", 0),
            strength_value(c),
            1 if c.get("underrated_talent") else 0
        ),
        reverse=True
    )
