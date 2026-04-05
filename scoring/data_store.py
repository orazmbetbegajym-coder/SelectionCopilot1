CANDIDATES = []
NEXT_ID = 1


def clear_candidates():
    global CANDIDATES, NEXT_ID
    CANDIDATES = []
    NEXT_ID = 1


def add_candidate(candidate: dict):
    global NEXT_ID
    candidate["id"] = NEXT_ID
    candidate["review_decision"] = candidate.get("review_decision", "Pending")
    NEXT_ID += 1
    CANDIDATES.append(candidate)
    return candidate


def get_all_candidates():
    return CANDIDATES


def get_candidate_by_id(candidate_id: int):
    for candidate in CANDIDATES:
        if candidate["id"] == candidate_id:
            return candidate
    return None


def update_candidate_decision(candidate_id: int, decision: str):
    candidate = get_candidate_by_id(candidate_id)
    if candidate:
        candidate["review_decision"] = decision
    return candidate
