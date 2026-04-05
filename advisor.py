def build_improvement_plan(analysis: dict):
    actions = []

    if analysis["academic_readiness"] < 70:
        actions.append("Усилить академическую стабильность и повысить средний балл.")
    if analysis["leadership_potential"] < 60:
        actions.append("Добавить более конкретные доказательства лидерства: проект, инициатива, организация события, роль координатора.")
    if analysis["growth_trajectory"] < 50:
        actions.append("Сильнее раскрыть путь роста: трудность → действия → чему научился → что изменилось.")
    if analysis["motivation"] < 45:
        actions.append("Сделать мотивацию конкретнее и связать её с прошлыми действиями и будущим направлением.")
    if analysis["community_orientation"] < 40:
        actions.append("Показать больше вклада в людей и сообщество: помощь, наставничество, волонтёрство.")
    if analysis["teamwork_readiness"] < 40:
        actions.append("Добавить примеры командной работы, совместных проектов и ролей в группе.")
    if analysis["long_term_commitment"] < 45:
        actions.append("Показать устойчивые активности длиной 6+ месяцев и результаты этой вовлечённости.")
    if analysis["authenticity"] < 75:
        actions.append("Убрать шаблонные формулировки и заменить их конкретными действиями и фактами.")

    if not actions:
        actions.append("Сохранить текущий уровень и усилить доказательность профиля измеримыми результатами.")

    return actions


def build_candidate_profile_type(analysis: dict):
    leadership = analysis["leadership_potential"]
    growth = analysis["growth_trajectory"]
    teamwork = analysis["teamwork_readiness"]
    community = analysis["community_orientation"]
    academic = analysis["academic_readiness"]
    authenticity = analysis["authenticity"]
    hidden = analysis["hidden_potential"]

    if hidden:
        return {
            "title": "Скрытый потенциал",
            "reason": "Кандидат может выглядеть слабее на поверхности, чем есть на самом деле: сигналы роста и вклада сильнее, чем степень полировки профиля."
        }

    if leadership >= 70 and teamwork >= 50:
        return {
            "title": "Лидер-инициатор",
            "reason": "У кандидата выражены инициативность, способность брать ответственность и двигать командные процессы."
        }

    if teamwork >= 60 and community >= 50:
        return {
            "title": "Командный драйвер",
            "reason": "Кандидат вероятнее всего усиливает среду через сотрудничество, участие в проектах и взаимодействие с людьми."
        }

    if growth >= 65 and authenticity >= 75:
        return {
            "title": "Потенциал роста",
            "reason": "Кандидат особенно силён не текущей полировкой, а траекторией развития, обучаемостью и способностью усиливаться со временем."
        }

    if academic >= 80 and leadership < 60:
        return {
            "title": "Академически сильный исполнитель",
            "reason": "Кандидат выглядит устойчивым и сильным в учебной части, но лидерские сигналы выражены слабее."
        }

    return {
        "title": "Сбалансированный кандидат",
        "reason": "Профиль без ярко выраженного доминирующего паттерна, но с умеренно устойчивыми сигналами по нескольким направлениям."
    }


def build_university_value(analysis: dict):
    leadership = analysis["leadership_potential"]
    teamwork = analysis["teamwork_readiness"]
    community = analysis["community_orientation"]
    growth = analysis["growth_trajectory"]
    academic = analysis["academic_readiness"]

    value_points = []

    if leadership >= 60:
        value_points.append("Может усиливать университет через инициативы, студенческие клубы, проектную деятельность и лидерские роли.")

    if teamwork >= 50:
        value_points.append("Способен повышать качество командной работы и вовлечённости в студенческой среде.")

    if community >= 45:
        value_points.append("Может приносить пользу через наставничество, волонтёрство, взаимопомощь и социальные инициативы.")

    if academic >= 75:
        value_points.append("Может быть полезен академической среде благодаря дисциплине и учебной устойчивости.")

    if growth >= 60:
        value_points.append("Имеет потенциал быстро усиливаться внутри университетской среды и расти в более сложных форматах.")

    if not value_points:
        value_points.append("Потенциал пользы университету пока проявлен ограниченно и требует дополнительных подтверждений.")

    if leadership >= 70 and teamwork >= 50:
        summary = "Кандидат ценен для университета как возможный носитель инициативы, лидерства и организационной энергии."
    elif teamwork >= 50 or community >= 45:
        summary = "Кандидат ценен для университета как участник, который может усиливать студенческую среду и культуру сотрудничества."
    elif academic >= 75:
        summary = "Кандидат ценен для университета прежде всего как академически устойчивый и дисциплинированный участник среды."
    else:
        summary = "Ценность кандидата для университета пока не полностью раскрыта, но отдельные сигналы потенциала присутствуют."

    return {
        "summary": summary,
        "points": value_points
    }


def build_behavioral_risks(analysis: dict):
    risks = []

    if analysis["evidence_strength"] == "Слабая":
        risks.append({
            "title": "Риск переоценки слов без доказательств",
            "reason": "В профиле недостаточно конкретных подтверждений и измеримых результатов."
        })

    if analysis["authenticity"] < 75:
        risks.append({
            "title": "Риск шаблонного самопрезентования",
            "reason": "В тексте слишком много общих формулировок и недостаточно конкретных действий."
        })

    if analysis["motivation"] >= 50 and analysis["leadership_potential"] < 45:
        risks.append({
            "title": "Мотивация выше, чем практическая реализация",
            "reason": "Кандидат заявляет цели и стремления, но пока слабо показывает действия, подтверждающие их."
        })

    if analysis["academic_readiness"] < 60:
        risks.append({
            "title": "Риск академической нестабильности",
            "reason": "Учебная база может быть недостаточно устойчивой для более требовательной среды."
        })

    if analysis["teamwork_readiness"] < 40:
        risks.append({
            "title": "Риск слабой интеграции в командную среду",
            "reason": "Недостаточно сигналов совместной работы, командных ролей и сотрудничества."
        })

    if analysis["ai_assistance_risk"] == "Высокий":
        risks.append({
            "title": "Риск переоценки из-за чрезмерно полированного текста",
            "reason": "Есть несколько признаков того, что текст может быть слишком общим или чрезмерно сглаженным."
        })

    if not risks:
        risks.append({
            "title": "Критические поведенческие риски не выявлены",
            "reason": "По текущему профилю нет выраженных красных флагов, которые резко снижали бы надёжность оценки."
        })

    return risks


def build_campus_behavior_forecast(analysis: dict):
    leadership = analysis["leadership_potential"]
    teamwork = analysis["teamwork_readiness"]
    community = analysis["community_orientation"]
    growth = analysis["growth_trajectory"]
    academic = analysis["academic_readiness"]
    hidden = analysis["hidden_potential"]

    if hidden:
        return {
            "title": "Раскроется после адаптации",
            "reason": "С высокой вероятностью кандидат лучше проявит себя не сразу, а после включения в поддерживающую и структурированную среду."
        }

    if leadership >= 70 and teamwork >= 50:
        return {
            "title": "Вероятно быстро включится в инициативы",
            "reason": "Кандидат с высокой вероятностью будет брать на себя роли организатора, координатора или активного участника проектов."
        }

    if teamwork >= 55 and community >= 45:
        return {
            "title": "Вероятно усилит студенческую среду",
            "reason": "Кандидат, скорее всего, будет полезен в клубах, командах, мероприятиях и среде взаимодействия."
        }

    if academic >= 80 and leadership < 55:
        return {
            "title": "Вероятно проявится сначала в академической части",
            "reason": "Кандидат, скорее всего, сначала покажет себя через учебную устойчивость, а не через лидерские роли."
        }

    if growth >= 60:
        return {
            "title": "Вероятно быстро вырастет в среде университета",
            "reason": "Кандидат показывает высокую обучаемость и может заметно усилиться при доступе к возможностям."
        }

    return {
        "title": "Потребуется дополнительное наблюдение",
        "reason": "Профиль не даёт достаточно сильного сигнала о том, как именно кандидат будет вести себя в среде университета."
    }


def build_advice(analysis: dict):
    if analysis["final_score"] >= 82 and analysis["evidence_strength"] == "Сильная" and analysis["ai_assistance_risk"] != "Высокий":
        recommendation = "Продвигать вперёд"
        recommendation_type = "strong"
        committee_advice = "Кандидата стоит продвигать на следующий этап."
        why_recommendation = "Профиль сочетает сильные сигналы лидерства, роста, вклада и достаточную доказательность."
    elif analysis["final_score"] >= 64:
        recommendation = "Ручной обзор"
        recommendation_type = "review"
        committee_advice = "Кандидата стоит оставить на ручной обзор и дополнительно проверить на интервью."
        why_recommendation = "Профиль показывает потенциал, но отдельные сигналы требуют валидации."
    else:
        recommendation = "Удержание / низкий приоритет"
        recommendation_type = "hold"
        committee_advice = "Пока кандидат не выглядит приоритетным, но может остаться в резерве."
        why_recommendation = "По текущему профилю не хватает силы сигналов и/или доказательности."

    if analysis["hidden_potential"]:
        committee_advice = "Кандидата стоит отдельно пометить как случай скрытого потенциала."
        why_recommendation = "Траектория роста и вклад сильнее, чем степень полировки профиля."

    return {
        "recommendation": recommendation,
        "recommendation_type": recommendation_type,
        "committee_advice": committee_advice,
        "why_recommendation": why_recommendation,
        "improvement_plan": build_improvement_plan(analysis),
        "candidate_profile_type": build_candidate_profile_type(analysis),
        "university_value": build_university_value(analysis),
        "behavioral_risks": build_behavioral_risks(analysis),
        "campus_behavior_forecast": build_campus_behavior_forecast(analysis),
    }