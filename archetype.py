import re


ARCHETYPE_PATTERNS = {
    "Hero": {
        "action_patterns": [
            r"\bovercame\b",
            r"\bstruggled\b",
            r"\bimproved\b",
            r"\bpersever(ed|ance)?\b",
            r"\bresilien(t|ce)\b",
            r"\bdiscipline(d)?\b",
            r"\bchallenge(d|s)?\b",
            r"\bgrew\b",
            r"\bпреодол",
            r"\bтрудност",
            r"\bулучш",
            r"\bдисциплин",
            r"\bрост",
            r"\bвырос",
            r"\bустойчив",
        ],
        "meaning": "Преодоление сложностей, стойкость, дисциплина, рост через препятствия."
    },
    "Creator": {
        "action_patterns": [
            r"\bbuilt\b",
            r"\bcreated\b",
            r"\bdesigned\b",
            r"\bdeveloped\b",
            r"\blaunched\b",
            r"\bprototype\b",
            r"\bproduct\b",
            r"\bapp(s)?\b",
            r"\binvent(ed)?\b",
            r"\bimplemented\b",
            r"\bсозда",
            r"\bразработ",
            r"\bзапуст",
            r"\bпрототип",
            r"\bпроект",
            r"\bприложен",
            r"\bсистем",
        ],
        "meaning": "Создание нового, проектное мышление, материальный или цифровой результат."
    },
    "Sage": {
        "action_patterns": [
            r"\bresearched\b",
            r"\bstudied\b",
            r"\banalyzed\b",
            r"\blearned\b",
            r"\bcuriosity\b",
            r"\bknowledge\b",
            r"\bunderstand\b",
            r"\binsight\b",
            r"\breflection\b",
            r"\bнауч",
            r"\bизуч",
            r"\bанализ",
            r"\bпоним",
            r"\bзнани",
            r"\bосознал",
            r"\bвывод",
        ],
        "meaning": "Интеллектуальная глубина, любознательность, анализ, обучение и осмысление."
    },
    "Explorer": {
        "action_patterns": [
            r"\bself[- ]taught\b",
            r"\bindependent\b",
            r"\bexplored\b",
            r"\bexperimented\b",
            r"\badapted\b",
            r"\btried\b",
            r"\boutside\b",
            r"\bown path\b",
            r"\bсамостоят",
            r"\bсам обуч",
            r"\bисслед",
            r"\bэксперимент",
            r"\bадапт",
            r"\bсвой путь",
        ],
        "meaning": "Самостоятельность, исследование, движение вне готовых рамок."
    },
    "Leader": {
        "action_patterns": [
            r"\bled\b",
            r"\borganized\b",
            r"\bcoordinated\b",
            r"\bmanaged\b",
            r"\bcaptain\b",
            r"\bmentor(ed)?\b",
            r"\bfounded\b",
            r"\bheaded\b",
            r"\brun\b",
            r"\bруковод",
            r"\bорганиз",
            r"\bкоордин",
            r"\bнастав",
            r"\bкапитан",
            r"\bоснов",
            r"\bвозглав",
        ],
        "meaning": "Ответственность за людей, организация процессов, координация, влияние на среду."
    }
}


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[\.\!\?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def _find_matches(sentence: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, sentence, flags=re.IGNORECASE):
            return True
    return False


def _has_number_or_scale(sentence: str) -> bool:
    return bool(
        re.search(r"\b\d+\b", sentence) or
        re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|dozen)\b", sentence, re.IGNORECASE) or
        re.search(r"\b(один|два|три|четыре|пять|шесть|семь|восемь|девять|десять)\b", sentence, re.IGNORECASE)
    )


def _has_duration(sentence: str) -> bool:
    return bool(
        re.search(r"\b\d+\s*(year|month|week|semester|day)s?\b", sentence, re.IGNORECASE) or
        re.search(r"\bfor\s+\d+\s*(year|month|week|semester|day)s?\b", sentence, re.IGNORECASE) or
        re.search(r"\b\d+\s*(год|месяц|недел|семестр|дн)\b", sentence, re.IGNORECASE) or
        re.search(r"\bв течение\b", sentence, re.IGNORECASE)
    )


def _has_impact(sentence: str) -> bool:
    impact_patterns = [
        r"\bhelped\b",
        r"\bimproved\b",
        r"\bincreased\b",
        r"\bsupported\b",
        r"\bprepared\b",
        r"\bresult\b",
        r"\boutcome\b",
        r"\bimpact\b",
        r"\bпомог",
        r"\bулучш",
        r"\bподдерж",
        r"\bрезульт",
        r"\bвлияни",
        r"\bподготов",
    ]
    return _find_matches(sentence, impact_patterns)


def _manual_hint_score(archetype_name: str) -> tuple[str, int]:
    name = (archetype_name or "").strip()
    if not name:
        return "", 0

    safe_bonus = {
        "Hero": 8,
        "Creator": 8,
        "Sage": 8,
        "Explorer": 8,
        "Leader": 8,
    }
    return name, safe_bonus.get(name, 0)


def analyze_archetype(
    archetype_name: str = "",
    essay: str = "",
    achievements: str = "",
    activities: str = "",
    why_university: str = "",
    university_contribution: str = "",
    university_future_contribution: str = "",
    programs_participated: str = "",
    long_term_activities: str = ""
):
    full_text = " ".join([
        essay or "",
        achievements or "",
        activities or "",
        why_university or "",
        university_contribution or "",
        university_future_contribution or "",
        programs_participated or "",
        long_term_activities or "",
    ]).strip()

    sentences = _split_sentences(_normalize_text(full_text))

    archetype_scores = {}
    archetype_evidence = {}

    for archetype, config in ARCHETYPE_PATTERNS.items():
        score = 0
        evidence = []

        for sentence in sentences:
            if _find_matches(sentence, config["action_patterns"]):
                sentence_score = 18

                if _has_number_or_scale(sentence):
                    sentence_score += 8
                if _has_duration(sentence):
                    sentence_score += 6
                if _has_impact(sentence):
                    sentence_score += 8

                score += sentence_score

                if len(evidence) < 3:
                    evidence.append(sentence[:220])

        archetype_scores[archetype] = min(score, 100)
        archetype_evidence[archetype] = evidence

    hinted_archetype, bonus = _manual_hint_score(archetype_name)
    if hinted_archetype in archetype_scores:
        archetype_scores[hinted_archetype] = min(archetype_scores[hinted_archetype] + bonus, 100)

    ranked = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)

    dominant_archetype = ranked[0][0] if ranked else "Unknown"
    dominant_score = ranked[0][1] if ranked else 0
    secondary_archetype = ranked[1][0] if len(ranked) > 1 else "Unknown"

    if dominant_score >= 70:
        potential_flag = "high"
    elif dominant_score >= 40:
        potential_flag = "medium"
    else:
        potential_flag = "low"

    summary = ARCHETYPE_PATTERNS.get(dominant_archetype, {}).get(
        "meaning",
        "Поведенческий паттерн выражен слабо или неоднозначно."
    )

    return {
        "archetype": dominant_archetype,
        "secondary_archetype": secondary_archetype,
        "score": round(dominant_score / 100, 2),
        "potential_flag": potential_flag,
        "archetype_scores": archetype_scores,
        "archetype_evidence": archetype_evidence,
        "summary": summary
    }