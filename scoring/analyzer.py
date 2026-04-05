import re
import os
import json
import requests
from archetype import analyze_archetype


# ============================================================
# CLAUDE API INTEGRATION
# ============================================================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


import re
import os
import json
import requests
from archetype import analyze_archetype


# ============================================================
# CLAUDE API INTEGRATION
# ============================================================

# ✅ ВСТАВЛЕН API KEY
ANTHROPIC_API_KEY = "a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"


def call_claude(prompt: str, max_tokens: int = 800) -> dict:
    """Call Claude API and return parsed JSON. Returns None if unavailable."""
    if not ANTHROPIC_API_KEY:
        return None
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            text = data["content"][0]["text"]
            text = re.sub(r"```json|```", "", text).strip()
            return json.loads(text)
    except Exception as e:  # ✅ ИСПРАВЛЕНО
        print("Claude API error:", e)
    return None
def ai_analyze_essay(
    essay: str,
    achievements: str,
    activities: str,
    why_university: str,
    university_contribution: str,
    long_term_activities: str,
    gpa: float
) -> dict:
    """Use Claude to deeply analyze candidate. Falls back to None if API unavailable."""
    prompt = f"""You are an expert admissions evaluator for inVision U, 
an innovative university in Kazakhstan that values leadership, growth, community impact, 
and authentic potential — not just GPA.

Analyze this candidate and return ONLY valid JSON with no extra text or markdown.

GPA: {gpa}
Essay: {essay[:800]}
Achievements: {achievements[:400]}
Activities: {activities[:400]}
Why this university: {why_university[:300]}
Contribution: {university_contribution[:300]}
Long-term activities: {long_term_activities[:300]}

Return exactly this JSON (all scores 0-100):
{{
  "leadership_score": <int>,
  "growth_score": <int>,
  "motivation_score": <int>,
  "teamwork_score": <int>,
  "community_score": <int>,
  "authenticity_score": <int>,
  "hidden_potential": <bool>,
  "ai_writing_risk": "<Низкий|Средний|Высокий>",
  "key_strength": "<one sentence in Russian>",
  "key_weakness": "<one sentence in Russian>",
  "profile_insight": "<2 sentences in Russian about unique potential>"
}}

Rules:
- leadership_score: concrete leading/organizing examples (not just words)
- growth_score: overcoming challenges, learning trajectory
- motivation_score: specific university fit, not generic
- teamwork_score: real collaboration evidence
- community_score: helping others, mentoring, volunteering
- authenticity_score: specific vs generic (100 = very personal and concrete)
- hidden_potential: true if strong growth but weak self-presentation
- ai_writing_risk: high if generic, templated, lacks personal voice"""

    return call_claude(prompt, max_tokens=600)


def merge_ai_scores(base: dict, ai: dict) -> dict:
    """Blend regex scores (70%) with AI scores (30%)."""
    if not ai:
        return base

    def blend(base_val, ai_val):
        return int(base_val * 0.70 + ai_val * 0.30)

    merged = base.copy()
    merged["leadership_potential"]  = blend(base.get("leadership_potential", 50),  ai.get("leadership_score", 50))
    merged["growth_trajectory"]     = blend(base.get("growth_trajectory", 50),     ai.get("growth_score", 50))
    merged["motivation"]            = blend(base.get("motivation", 50),             ai.get("motivation_score", 50))
    merged["teamwork_readiness"]    = blend(base.get("teamwork_readiness", 50),     ai.get("teamwork_score", 50))
    merged["community_orientation"] = blend(base.get("community_orientation", 50),  ai.get("community_score", 50))
    merged["authenticity"]          = blend(base.get("authenticity", 50),           ai.get("authenticity_score", 50))

    if ai.get("hidden_potential"):
        merged["hidden_potential"] = True

    risk_level = {"Низкий": 0, "Средний": 1, "Высокий": 2}
    ai_risk = ai.get("ai_writing_risk", "Низкий")
    cur_risk = base.get("ai_assistance_risk", "Низкий")
    if risk_level.get(ai_risk, 0) > risk_level.get(cur_risk, 0):
        merged["ai_assistance_risk"] = ai_risk

    # Recalculate final score with blended values
    merged["final_score"] = max(0, min(100, int(
        0.14 * merged.get("academic_readiness", 50) +
        0.15 * merged.get("evidence_quality_score", 50) +
        0.13 * merged["leadership_potential"] +
        0.10 * merged["teamwork_readiness"] +
        0.12 * merged["growth_trajectory"] +
        0.10 * merged["community_orientation"] +
        0.10 * merged["motivation"] +
        0.10 * merged["authenticity"] +
        0.06 * merged.get("long_term_commitment", 50)
    )))

    merged["ai_key_strength"]    = ai.get("key_strength", "")
    merged["ai_key_weakness"]    = ai.get("key_weakness", "")
    merged["ai_profile_insight"] = ai.get("profile_insight", "")
    merged["ai_powered"]         = True
    return merged


# ============================================================
# ORIGINAL SCORING ENGINE (unchanged)
# ============================================================

def clamp(value, low=0, high=100):
    return max(low, min(value, high))


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def gpa_to_score(gpa: float) -> int:
    if gpa >= 3.9: return 100
    if gpa >= 3.7: return 90
    if gpa >= 3.5: return 82
    if gpa >= 3.3: return 74
    if gpa >= 3.0: return 62
    if gpa >= 2.7: return 50
    if gpa >= 2.4: return 38
    return 25


def validate_score(score: int) -> int:
    return clamp(score, 0, 100)


def baseline_a_score(gpa: float) -> int:
    return validate_score(gpa_to_score(gpa))


def baseline_a_label(score: int) -> str:
    if score >= 75: return "Сильный шорт-лист"
    if score >= 55: return "Ручной обзор"
    return "Удержание / низкий приоритет"


def baseline_b_score(gpa: float, achievements: str) -> int:
    achievements_n = normalize_text(achievements)
    evidence_patterns = [
        r"\bwon\b", r"\baward\b", r"\bcompetition\b", r"\bolympiad\b", r"\bmedal\b",
        r"\bscholarship\b", r"\borganized\b", r"\bled\b", r"\bcreated\b", r"\bfounded\b",
        r"\bcaptain\b", r"\bmentor(ed)?\b",
        r"\bпобед", r"\bнагра", r"\bконкурс", r"\bолимпиад", r"\bмедал", r"\bстипенд",
        r"\bорганиз", r"\bруковод", r"\bсозда", r"\bоснов", r"\bкапитан", r"\bнастав"
    ]
    matches = sum(1 for p in evidence_patterns if re.search(p, achievements_n, re.IGNORECASE))
    raw = int(0.7 * gpa_to_score(gpa) + 0.3 * min(matches * 12, 100))
    return validate_score(raw)


def baseline_b_label(score: int) -> str:
    if score >= 75: return "Сильный шорт-лист"
    if score >= 55: return "Ручной обзор"
    return "Удержание / низкий приоритет"


def split_sentences(text: str) -> list:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text: return []
    parts = re.split(r"(?<=[\.\!\?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def has_any_pattern(text: str, patterns: list) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def extract_numbers(text: str) -> list:
    return re.findall(r"\b\d+\b", text or "")


def has_duration(text: str) -> bool:
    duration_patterns = [
        r"\b\d+\s*(year|month|week|semester|day)s?\b",
        r"\bfor\s+\d+\s*(year|month|week|semester|day)s?\b",
        r"\b\d+\s*(год|месяц|недел|семестр|дн)\b",
        r"\bв течение\b", r"\blong[- ]term\b", r"\b2 years\b", r"\b1 year\b",
    ]
    return has_any_pattern(text, duration_patterns)


def detect_claim_type(sentence: str) -> str:
    s = normalize_text(sentence)
    reflection_patterns = [r"\bi learned\b", r"\bi realized\b", r"\bthis taught me\b", r"\bi understood\b", r"\bнауч", r"\bпонял", r"\bосознал", r"\bэто научило меня\b"]
    impact_patterns = [r"\bhelped\b", r"\bimproved\b", r"\bincreased\b", r"\bsupported\b", r"\bprepared\b", r"\bgrew to\b", r"\bresult\b", r"\boutcome\b", r"\bпомог", r"\bулучш", r"\bподдерж", r"\bрезульт", r"\bподготов"]
    action_patterns = [r"\bled\b", r"\borganized\b", r"\bfounded\b", r"\bcreated\b", r"\bbuilt\b", r"\bdeveloped\b", r"\bmanaged\b", r"\bcoordinated\b", r"\bmentor(ed)?\b", r"\btaught\b", r"\bstarted\b", r"\blaunched\b", r"\bsolved\b", r"\bруковод", r"\bорганиз", r"\bоснов", r"\bсозда", r"\bразработ", r"\bкоордин", r"\bнастав", r"\bобуч", r"\bзапуст", r"\bрешил"]
    future_patterns = [r"\bi will\b", r"\bi want to\b", r"\bi hope to\b", r"\bmy future\b", r"\bя буду\b", r"\bя хочу\b", r"\bв будущем\b"]
    generic_patterns = [r"\bi am hardworking\b", r"\bi am passionate\b", r"\bi am motivated\b", r"\bi always do my best\b", r"\bi want success\b", r"\bi am responsible\b", r"\bя трудолюб", r"\bя мотивирован", r"\bя всегда стараюсь\b", r"\bя ответственный\b", r"\bя хочу успеха\b"]

    if has_any_pattern(s, reflection_patterns): return "reflection"
    if has_any_pattern(s, impact_patterns): return "impact"
    if has_any_pattern(s, action_patterns): return "action"
    if has_any_pattern(s, generic_patterns): return "generic"
    if has_any_pattern(s, future_patterns): return "future"
    return "other"


def analyze_text_block(text: str) -> dict:
    sentences = split_sentences(text)
    action_sentences, impact_sentences, reflection_sentences = [], [], []
    future_sentences, generic_sentences, evidence_units = [], [], []

    for sentence in sentences:
        sentence_type = detect_claim_type(sentence)
        lowered = normalize_text(sentence)
        has_number = len(extract_numbers(sentence)) > 0
        duration = has_duration(sentence)
        outcome = sentence_type == "impact" or has_any_pattern(lowered, [r"\bhelped\b", r"\bimproved\b", r"\bresult\b", r"\boutcome\b", r"\bпомог", r"\bулучш", r"\bрезульт"])

        if sentence_type == "action":
            action_sentences.append(sentence)
            strength = 1
            if has_number: strength += 1
            if duration: strength += 1
            if outcome: strength += 1
            evidence_units.append({"sentence": sentence, "strength": strength, "has_number": has_number, "has_duration": duration, "has_outcome": outcome})
        elif sentence_type == "impact": impact_sentences.append(sentence)
        elif sentence_type == "reflection": reflection_sentences.append(sentence)
        elif sentence_type == "future": future_sentences.append(sentence)
        elif sentence_type == "generic": generic_sentences.append(sentence)

    return {
        "sentences": sentences, "action_sentences": action_sentences,
        "impact_sentences": impact_sentences, "reflection_sentences": reflection_sentences,
        "future_sentences": future_sentences, "generic_sentences": generic_sentences,
        "evidence_units": evidence_units, "sentence_count": len(sentences),
        "word_count": len((text or "").split()),
    }


def evaluate_thesis_clarity(essay_block: dict) -> int:
    if essay_block["sentence_count"] == 0: return 0
    first_two = " ".join(essay_block["sentences"][:2]).lower()
    score = 40
    if len(first_two.split()) >= 12: score += 10
    if has_any_pattern(first_two, [r"\bi\b", r"\bmy\b", r"\bthis\b", r"\bbecause\b", r"\bafter\b", r"\bя\b", r"\bмой\b", r"\bпотому что\b", r"\bпосле\b"]): score += 10
    if essay_block["action_sentences"]: score += 20
    if essay_block["reflection_sentences"]: score += 10
    return clamp(score)


def evaluate_specificity(*blocks: dict) -> int:
    evidence_units, generic_count, total_sentences = [], 0, 0
    for block in blocks:
        evidence_units.extend(block["evidence_units"])
        generic_count += len(block["generic_sentences"])
        total_sentences += block["sentence_count"]

    score = 20
    score += min(len(evidence_units) * 12, 48)
    strong_units = sum(1 for unit in evidence_units if unit["strength"] >= 3)
    score += min(strong_units * 8, 24)

    if total_sentences > 0:
        generic_ratio = generic_count / total_sentences
        if generic_ratio > 0.35: score -= 22
        elif generic_ratio > 0.20: score -= 12
        elif generic_ratio > 0.10: score -= 6
    return clamp(score)


def evaluate_evidence_quality(*blocks: dict) -> int:
    evidence_units = []
    for block in blocks:
        evidence_units.extend(block["evidence_units"])
    if not evidence_units: return 15

    score = 20
    for unit in evidence_units:
        unit_score = 10
        if unit["has_number"]: unit_score += 8
        if unit["has_duration"]: unit_score += 6
        if unit["has_outcome"]: unit_score += 8
        score += min(unit_score, 22)
    return clamp(score)


def evaluate_leadership(essay_block, achievements_block, activities_block, programs_block) -> int:
    leadership_patterns = [r"\bled\b", r"\borganized\b", r"\bfounded\b", r"\bmanaged\b", r"\bcoordinated\b", r"\bcaptain\b", r"\bmentor(ed)?\b", r"\bheaded\b", r"\bруковод", r"\bорганиз", r"\bоснов", r"\bкоордин", r"\bкапитан", r"\bнастав"]
    score = 10
    for block in [essay_block, achievements_block, activities_block, programs_block]:
        for sentence in block["sentences"]:
            if has_any_pattern(sentence.lower(), leadership_patterns):
                score += 14
                if len(extract_numbers(sentence)) > 0 or has_duration(sentence):
                    score += 12
    return clamp(score)


def evaluate_growth(essay_block, long_term_block) -> int:
    growth_patterns = [r"\bimproved\b", r"\bovercame\b", r"\bstruggled\b", r"\blearned\b", r"\bgrew\b", r"\bdeveloped\b", r"\bdiscipline\b", r"\bresilien", r"\bулучш", r"\bпреодол", r"\bнауч", r"\bвырос", r"\bразвил", r"\bдисциплин"]
    score = 15
    for sentence in essay_block["sentences"] + long_term_block["sentences"]:
        if has_any_pattern(sentence.lower(), growth_patterns):
            score += 16
    score += min(len(essay_block["reflection_sentences"]) * 10, 20)
    score += min(len(long_term_block["reflection_sentences"]) * 8, 16)
    return clamp(score)


def evaluate_motivation(why_block, essay_block, future_block) -> int:
    score = 20
    if why_block["word_count"] >= 20: score += 12
    if future_block["word_count"] >= 20: score += 10
    fit_patterns = [r"\bthis university\b", r"\bprogram\b", r"\bresearch\b", r"\bcommunity\b", r"\bengineering\b", r"\btechnology\b", r"\binnovation\b", r"\bуниверситет\b", r"\bпрограмма\b", r"\bисслед", r"\bсообще", r"\bинновац"]
    if has_any_pattern(" ".join(why_block["sentences"]).lower(), fit_patterns): score += 18
    if essay_block["action_sentences"] and future_block["future_sentences"]: score += 18
    return clamp(score)


def evaluate_community(essay_block, activities_block, contribution_block) -> int:
    community_patterns = [r"\bhelped\b", r"\bsupported\b", r"\bmentored\b", r"\btaught\b", r"\bvolunteer\b", r"\bcommunity\b", r"\bstudents\b", r"\bпомог", r"\bподдерж", r"\bнастав", r"\bобуч", r"\bволонтер", r"\bсообще", r"\bстудент"]
    score = 10
    total_hits, strong_hits = 0, 0
    for sentence in essay_block["sentences"] + activities_block["sentences"] + contribution_block["sentences"]:
        if has_any_pattern(sentence.lower(), community_patterns):
            total_hits += 1
            if len(extract_numbers(sentence)) > 0 or has_duration(sentence):
                strong_hits += 1
    score += min(total_hits * 12, 48)
    score += min(strong_hits * 10, 20)
    return clamp(score)


def evaluate_teamwork(activities_block, programs_block, contribution_block) -> int:
    teamwork_patterns = [r"\bteam\b", r"\bgroup\b", r"\bcollaboration\b", r"\bcollaborated\b", r"\bcommittee\b", r"\bpeer\b", r"\btogether\b", r"\bкоманд", r"\bгрупп", r"\bсовмест", r"\bсотруднич", r"\bкомитет", r"\bвместе"]
    score = 10
    hits, strong_hits = 0, 0
    for sentence in activities_block["sentences"] + programs_block["sentences"] + contribution_block["sentences"]:
        if has_any_pattern(sentence.lower(), teamwork_patterns):
            hits += 1
            if len(extract_numbers(sentence)) > 0 or has_duration(sentence):
                strong_hits += 1
    score += min(hits * 14, 42)
    score += min(strong_hits * 12, 24)
    return clamp(score)


def evaluate_long_term_commitment(long_term_block, activities_block) -> int:
    score = 10
    if long_term_block["word_count"] >= 20: score += 15
    if long_term_block["word_count"] >= 40: score += 10
    if any(unit["has_duration"] for unit in long_term_block["evidence_units"]): score += 25
    if len(long_term_block["evidence_units"]) >= 2: score += 20
    if len(activities_block["action_sentences"]) >= 2: score += 10
    return clamp(score)


def evaluate_authenticity(essay_block, why_block, contribution_block, future_block) -> int:
    total_sentences = sum(b["sentence_count"] for b in [essay_block, why_block, contribution_block, future_block])
    total_generic = sum(len(b["generic_sentences"]) for b in [essay_block, why_block, contribution_block, future_block])
    total_reflection = sum(len(b["reflection_sentences"]) for b in [essay_block, why_block, contribution_block, future_block])
    total_evidence = sum(len(b["evidence_units"]) for b in [essay_block, why_block, contribution_block, future_block])

    score = 70
    score += min(total_reflection * 8, 16)
    score += min(total_evidence * 4, 16)

    if total_sentences > 0:
        generic_ratio = total_generic / total_sentences
        if generic_ratio > 0.35: score -= 35
        elif generic_ratio > 0.20: score -= 22
        elif generic_ratio > 0.10: score -= 10

    if essay_block["word_count"] < 60: score -= 10
    if why_block["word_count"] < 12: score -= 8
    if contribution_block["word_count"] < 12: score -= 8
    if future_block["word_count"] < 12: score -= 8
    return clamp(score)


def build_weaknesses_explained(essay, achievements, activities, why_university, long_term_activities, signals, scores):
    weaknesses = []
    if scores["leadership_potential"] < 50:
        weaknesses.append({"title": "Слабые доказательства лидерства", "reason": "Кандидат заявляет о потенциале, но в профиле мало чётких примеров, где он реально вёл людей, координировал процесс или запускал инициативу."})
    if signals["essay_word_count"] < 80:
        weaknesses.append({"title": "Недостаточная глубина эссе", "reason": "Основное эссе короткое и не до конца раскрывает путь кандидата, его решения, уроки и влияние на других."})
    if scores["evidence_quality_score"] < 55:
        weaknesses.append({"title": "Недостаточная доказательность", "reason": "Есть заявления о качествах и действиях, но не хватает масштаба, длительности, чисел или измеримого результата."})
    if scores["teamwork_readiness"] < 45:
        weaknesses.append({"title": "Слабые доказательства командной работы", "reason": "Профиль недостаточно показывает реальные роли кандидата в команде, сотрудничестве и совместных результатах."})
    if scores["motivation"] < 55:
        weaknesses.append({"title": "Неясная связь с университетом", "reason": "Ответ о выборе университета пока недостаточно конкретно связывает прошлый опыт кандидата с будущими академическими и социальными целями."})
    if scores["long_term_commitment"] < 50:
        weaknesses.append({"title": "Слабая долгосрочная вовлечённость", "reason": "Не до конца раскрыто, что кандидат делал устойчиво и последовательно на протяжении длительного времени."})
    if scores["authenticity"] < 75:
        weaknesses.append({"title": "Риск шаблонного профиля", "reason": "Часть формулировок звучит слишком общей. Нужны более живые и подтверждённые примеры вместо деклараций."})
    return weaknesses


def build_strengths_explained(scores):
    strengths = []
    if scores["leadership_potential"] >= 70:
        strengths.append({"title": "Сильные сигналы лидерства", "reason": "Профиль содержит конкретные признаки инициативы, координации и ответственности за других."})
    elif scores["leadership_potential"] >= 50:
        strengths.append({"title": "Формирующийся лидерский потенциал", "reason": "Есть убедимые признаки инициативности, но масштаб и стабильность лидерских ролей раскрыты не полностью."})
    if scores["growth_trajectory"] >= 60:
        strengths.append({"title": "Выраженная траектория роста", "reason": "Кандидат показывает, как проходил через трудности, учился и усиливал себя через опыт."})
    if scores["motivation"] >= 60:
        strengths.append({"title": "Понятная мотивация", "reason": "Есть читаемая связь между прошлым опытом, текущими целями и направлением развития."})
    if scores["community_orientation"] >= 50:
        strengths.append({"title": "Потенциал вклада в сообщество", "reason": "Профиль показывает готовность помогать другим, поддерживать среду и усиливать сообщество."})
    if scores["teamwork_readiness"] >= 50:
        strengths.append({"title": "Сигналы командной работы", "reason": "Есть примеры сотрудничества, совместной ответственности и работы в групповых форматах."})
    if scores["academic_readiness"] >= 80:
        strengths.append({"title": "Сильная академическая готовность", "reason": "Уровень GPA указывает на хорошую учебную базу и устойчивость в академической части."})
    if scores["authenticity"] >= 80:
        strengths.append({"title": "Аутентичный профиль", "reason": "Текст выглядит достаточно живым, конкретным и не сводится к набору общих фраз."})
    if scores["evidence_quality_score"] >= 70:
        strengths.append({"title": "Хорошая доказательная база", "reason": "В профиле есть действия, контекст, иногда масштаб и результат, а не только красивые утверждения."})
    return strengths


def build_behavioral_signals(scales_10):
    return [
        {"name": "Лидерство", "score": scales_10["leadership"], "reason": "Оценено по реальным примерам координации, ответственности и инициативы."},
        {"name": "Рост", "score": scales_10["growth"], "reason": "Оценено по траектории развития, преодолению трудностей и рефлексии."},
        {"name": "Командность", "score": scales_10["teamwork"], "reason": "Оценено по описаниям совместной работы, групповых ролей и сотрудничества."},
        {"name": "Вклад в сообщество", "score": scales_10["community"], "reason": "Оценено по реальным сигналам помощи другим, наставничества и общественной пользы."},
        {"name": "Аутентичность", "score": scales_10["authenticity"], "reason": "Оценено по степени конкретности, рефлексии и соотношению доказательств к общим фразам."},
    ]


def build_contribution_potential(scores):
    if scores["leadership_potential"] >= 70 and scores["teamwork_readiness"] >= 50:
        return {"level": "Высокий потенциал влияния", "roles": ["Лидер студенческого клуба или координатор инициатив", "Организатор проектов и событий", "Наставник или человек, усиливающий среду"], "reason": "Оценка основана на сочетании лидерства, конкретных действий и командных сигналов."}
    if scores["teamwork_readiness"] >= 45 or scores["community_orientation"] >= 45:
        return {"level": "Активный вклад в университетскую среду", "roles": ["Участник студенческих проектов", "Волонтёр / организатор мероприятий", "Человек, усиливающий культуру сотрудничества"], "reason": "Есть сигналы того, что кандидат сможет быть полезен командам, инициативам и сообществу."}
    return {"level": "Ограниченно проявленный вклад", "roles": ["Потенциал лучше раскроется после интервью или в поддерживающей среде", "Нужны дополнительные подтверждения"], "reason": "Пока сигналов лидерства, вклада и командного влияния недостаточно для уверенного вывода."}


def fairness_block():
    return {
        "used_features": ["Эссе", "Достижения", "Деятельность", "Мотивация", "Сигналы лидерства", "Командная работа", "Конкретность и доказательность", "Рефлексия и траектория роста"],
        "excluded_features": ["Пол", "Этничность", "Религия", "Доход семьи", "Политические взгляды", "Медицинские данные"]
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def analyze_candidate_text(
    gpa: float,
    essay: str,
    achievements: str,
    activities: str,
    why_university: str,
    university_contribution: str,
    university_future_contribution: str,
    programs_participated: str,
    long_term_activities: str,
    archetype_name: str = ""
):
    essay_block        = analyze_text_block(essay)
    achievements_block = analyze_text_block(achievements)
    activities_block   = analyze_text_block(activities)
    why_block          = analyze_text_block(why_university)
    contribution_block = analyze_text_block(university_contribution)
    future_block       = analyze_text_block(university_future_contribution)
    programs_block     = analyze_text_block(programs_participated)
    long_term_block    = analyze_text_block(long_term_activities)

    thesis_clarity       = evaluate_thesis_clarity(essay_block)
    specificity          = evaluate_specificity(essay_block, achievements_block, activities_block, contribution_block, future_block, long_term_block)
    evidence_quality_score = evaluate_evidence_quality(essay_block, achievements_block, activities_block, contribution_block, future_block, long_term_block)
    leadership_potential = evaluate_leadership(essay_block, achievements_block, activities_block, programs_block)
    growth_trajectory    = evaluate_growth(essay_block, long_term_block)
    motivation           = evaluate_motivation(why_block, essay_block, future_block)
    community_orientation = evaluate_community(essay_block, activities_block, contribution_block)
    teamwork_readiness   = evaluate_teamwork(activities_block, programs_block, contribution_block)
    academic_readiness   = gpa_to_score(gpa)
    long_term_commitment = evaluate_long_term_commitment(long_term_block, activities_block)
    authenticity         = evaluate_authenticity(essay_block, why_block, contribution_block, future_block)

    archetype_result = analyze_archetype(
        archetype_name=archetype_name, essay=essay, achievements=achievements,
        activities=activities, why_university=why_university,
        university_contribution=university_contribution,
        university_future_contribution=university_future_contribution,
        programs_participated=programs_participated, long_term_activities=long_term_activities
    )
    archetype_score = int(archetype_result["score"] * 100)

    raw_final = int(
        0.14 * academic_readiness + 0.15 * evidence_quality_score +
        0.13 * leadership_potential + 0.10 * teamwork_readiness +
        0.12 * growth_trajectory + 0.10 * community_orientation +
        0.10 * motivation + 0.10 * authenticity + 0.06 * long_term_commitment
    )
    final_score = validate_score(raw_final)

    evidence_strength = "Сильная" if evidence_quality_score >= 72 else ("Средняя" if evidence_quality_score >= 50 else "Слабая")
    confidence = {"Сильная": "Высокая", "Средняя": "Средняя", "Слабая": "Низкая"}[evidence_strength]

    ai_assistance_risk = "Низкий"
    ai_risk_signals = []
    total_generic = sum(len(b["generic_sentences"]) for b in [essay_block, why_block, contribution_block, future_block])
    total_key_sentences = sum(b["sentence_count"] for b in [essay_block, why_block, contribution_block, future_block])
    generic_ratio = total_generic / total_key_sentences if total_key_sentences > 0 else 0

    if generic_ratio > 0.30: ai_risk_signals.append("Слишком высокая доля общих декларативных фраз без достаточного содержания")
    if evidence_quality_score < 40 and sum(b["word_count"] for b in [essay_block, why_block, contribution_block, future_block]) > 140:
        ai_risk_signals.append("Текст объёмный, но содержит мало доказательств, масштаба и результата")
    if len(essay_block["reflection_sentences"]) == 0 and essay_block["word_count"] > 90:
        ai_risk_signals.append("Эссе описывает качества, но почти не показывает внутреннюю рефлексию")
    if motivation >= 60 and evidence_quality_score < 45:
        ai_risk_signals.append("Мотивация звучит хорошо, но плохо подкреплена прошлым опытом и действиями")
    if why_block["word_count"] < 12:
        ai_risk_signals.append("Блок 'Почему этот университет' слишком короткий и общий")
    if contribution_block["word_count"] < 12 and future_block["word_count"] < 12:
        ai_risk_signals.append("Ответы о вкладе в университетскую среду остаются поверхностными")

    if len(ai_risk_signals) >= 4: ai_assistance_risk = "Высокий"
    elif len(ai_risk_signals) >= 2: ai_assistance_risk = "Средний"

    hidden_potential = (
        growth_trajectory >= 60 and community_orientation >= 45 and
        teamwork_readiness >= 40 and evidence_quality_score >= 45 and
        (academic_readiness < 75 or leadership_potential < 60)
    )

    scales_10 = {
        "leadership": round(leadership_potential / 10, 1),
        "growth": round(growth_trajectory / 10, 1),
        "motivation": round(motivation / 10, 1),
        "teamwork": round(teamwork_readiness / 10, 1),
        "community": round(community_orientation / 10, 1),
        "academic": round(academic_readiness / 10, 1),
        "authenticity": round(authenticity / 10, 1),
    }

    baseline_a = baseline_a_score(gpa)
    baseline_b = baseline_b_score(gpa, achievements)

    score_map = {
        "leadership_potential": leadership_potential, "growth_trajectory": growth_trajectory,
        "motivation": motivation, "community_orientation": community_orientation,
        "teamwork_readiness": teamwork_readiness, "academic_readiness": academic_readiness,
        "long_term_commitment": long_term_commitment, "authenticity": authenticity,
        "evidence_quality_score": evidence_quality_score, "specificity": specificity,
        "thesis_clarity": thesis_clarity,
    }

    signals = {
        "essay_word_count": essay_block["word_count"], "why_word_count": why_block["word_count"],
        "contribution_word_count": contribution_block["word_count"] + future_block["word_count"],
        "program_word_count": programs_block["word_count"], "long_term_word_count": long_term_block["word_count"],
        "generic_ratio": generic_ratio,
        "total_evidence_units": sum(len(b["evidence_units"]) for b in [essay_block, achievements_block, activities_block, contribution_block, future_block, long_term_block]),
    }

    # ── AI LAYER ──────────────────────────────────────────
    ai_result = ai_analyze_essay(
        print("ai result:",ai_result)
        essay=essay, achievements=achievements, activities=activities,
        why_university=why_university, university_contribution=university_contribution,
        long_term_activities=long_term_activities, gpa=gpa
    )

    base_scores = {
        "leadership_potential": leadership_potential, "growth_trajectory": growth_trajectory,
        "motivation": motivation, "teamwork_readiness": teamwork_readiness,
        "community_orientation": community_orientation, "authenticity": authenticity,
        "academic_readiness": academic_readiness, "evidence_quality_score": evidence_quality_score,
        "long_term_commitment": long_term_commitment, "hidden_potential": hidden_potential,
        "ai_assistance_risk": ai_assistance_risk, "final_score": final_score,
    }

    if ai_result:
        merged = merge_ai_scores(base_scores, ai_result)
        leadership_potential  = merged["leadership_potential"]
        growth_trajectory     = merged["growth_trajectory"]
        motivation            = merged["motivation"]
        teamwork_readiness    = merged["teamwork_readiness"]
        community_orientation = merged["community_orientation"]
        authenticity          = merged["authenticity"]
        hidden_potential      = merged["hidden_potential"]
        ai_assistance_risk    = merged["ai_assistance_risk"]
        final_score           = merged["final_score"]
        ai_key_strength       = merged.get("ai_key_strength", "")
        ai_key_weakness       = merged.get("ai_key_weakness", "")
        ai_profile_insight    = merged.get("ai_profile_insight", "")
        ai_powered            = True
    else:
        ai_key_strength    = ""
        ai_key_weakness    = ""
        ai_profile_insight = ""
        ai_powered         = False
    # ─────────────────────────────────────────────────────

    # Rebuild score_map with updated values
    score_map.update({
        "leadership_potential": leadership_potential,
        "growth_trajectory": growth_trajectory,
        "motivation": motivation,
        "community_orientation": community_orientation,
        "teamwork_readiness": teamwork_readiness,
        "authenticity": authenticity,
    })

    return {
        "gpa": gpa,
        "final_score": final_score,
        "evidence_strength": evidence_strength,
        "confidence": confidence,
        "ai_assistance_risk": ai_assistance_risk,
        "ai_risk_signals": ai_risk_signals,
        "hidden_potential": hidden_potential,
        "scales_10": scales_10,
        "baseline_a_score": baseline_a,
        "baseline_a_label": baseline_a_label(baseline_a),
        "baseline_b_score": baseline_b,
        "baseline_b_label": baseline_b_label(baseline_b),
        "improvement_vs_baseline_a": final_score - baseline_a,
        "improvement_vs_baseline_b": final_score - baseline_b,
        "validation_note": "Счёт основан на анализе смысловых единиц: действие, доказательство, результат, рефлексия, вклад и связность мотивации.",
        "fairness": fairness_block(),
        "leadership_potential": leadership_potential,
        "growth_trajectory": growth_trajectory,
        "motivation": motivation,
        "community_orientation": community_orientation,
        "teamwork_readiness": teamwork_readiness,
        "academic_readiness": academic_readiness,
        "long_term_commitment": long_term_commitment,
        "authenticity": authenticity,
        "strengths": build_strengths_explained(score_map),
        "weaknesses_explained": build_weaknesses_explained(essay, achievements, activities, why_university, long_term_activities, signals, score_map),
        "archetype": archetype_result["archetype"],
        "archetype_score": archetype_score,
        "archetype_flag": archetype_result["potential_flag"],
        "behavioral_signals": build_behavioral_signals(scales_10),
        "contribution_potential": build_contribution_potential(score_map),
        "ai_risk": ai_assistance_risk,
        # AI Layer fields
        "ai_powered": ai_powered,
        "ai_key_strength": ai_key_strength,
        "ai_key_weakness": ai_key_weakness,
        "ai_profile_insight": ai_profile_insight,
    }
