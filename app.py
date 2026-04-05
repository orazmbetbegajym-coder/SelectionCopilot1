import csv
import io
import uuid
from pathlib import Path
from typing import List
from collections import Counter

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scoring.analyzer import analyze_candidate_text
from scoring.advisor import build_advice
from scoring.ranker import sort_candidates
from scoring.data_store import (
    add_candidate,
    get_all_candidates,
    get_candidate_by_id,
    update_candidate_decision,
    clear_candidates,
)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
VALIDATION_FILE = BASE_DIR / "validation_cases.csv"

if UPLOAD_DIR.exists() and not UPLOAD_DIR.is_dir():
    UPLOAD_DIR.unlink()

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


def save_uploaded_files(files: List[UploadFile]) -> list[dict]:
    saved = []

    for file in files:
        if not file or not file.filename:
            continue

        ext = Path(file.filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / unique_name

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        saved.append({
            "filename": file.filename,
            "path": f"/uploads/{unique_name}",
            "is_image": ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"]
        })

    return saved


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_expected_label(label: str) -> str:
    label = (label or "").strip().lower()
    mapping = {
        "advance": "Продвигать вперёд",
        "review": "Ручной обзор",
        "hold": "Удержание / низкий приоритет",
        "strong shortlist": "Продвигать вперёд",
        "review manually": "Ручной обзор",
        "hold / low priority": "Удержание / низкий приоритет",
        "продвигать вперёд": "Продвигать вперёд",
        "ручной обзор": "Ручной обзор",
        "удержание / низкий приоритет": "Удержание / низкий приоритет",
    }
    return mapping.get(label, label)


def build_candidate_record(
    name: str,
    gpa: float,
    essay: str,
    achievements: str,
    activities: str,
    why_university: str,
    university_contribution: str,
    university_future_contribution: str,
    programs_participated: str,
    long_term_activities: str,
    evidence_files: list[dict],
    archetype_name: str = "",
    tg_nick: str = "",
):
    analysis = analyze_candidate_text(
        gpa,
        essay,
        achievements,
        activities,
        why_university,
        university_contribution,
        university_future_contribution,
        programs_participated,
        long_term_activities,
        archetype_name
    )

    advice = build_advice(analysis)

    recommendation = advice.get("recommendation", "Ручной обзор")
    if recommendation == "Продвигать вперёд":
        recommendation_type = "strong"
    elif recommendation == "Ручной обзор":
        recommendation_type = "review"
    else:
        recommendation_type = "hold"

    candidate = {
        "name": name,
        "gpa": gpa,
        "essay": essay,
        "achievements": achievements,
        "activities": activities,
        "why_university": why_university,
        "university_contribution": university_contribution,
        "university_future_contribution": university_future_contribution,
        "programs_participated": programs_participated,
        "long_term_activities": long_term_activities,
        "evidence_files": evidence_files,
        "review_decision": "Pending",
        "recommendation_type": recommendation_type,
        "tg_nick": (tg_nick or "").replace("@", ""),
        **analysis,
        **advice,
    }
    return candidate


def build_admissions_summary(candidates: list[dict]) -> dict:
    total = len(candidates)
    strong_shortlist = sum(1 for c in candidates if c.get("recommendation_type") == "strong")
    hidden_potential_cases = sum(1 for c in candidates if c.get("hidden_potential"))
    high_ai_risk_cases = sum(1 for c in candidates if c.get("ai_assistance_risk") == "Высокий")

    average_score = 0
    if total > 0:
        average_score = round(sum(c.get("final_score", 0) for c in candidates) / total, 1)

    profile_counter = Counter()
    for c in candidates:
        profile = c.get("candidate_profile_type", {})
        title = profile.get("title")
        if title:
            profile_counter[title] += 1

    top_profiles = profile_counter.most_common(3)

    return {
        "total_candidates": total,
        "strong_shortlist": strong_shortlist,
        "hidden_potential_cases": hidden_potential_cases,
        "high_ai_risk_cases": high_ai_risk_cases,
        "average_score": average_score,
        "top_recommended_profile_types": top_profiles,
    }


def build_validation_summary(candidates: list[dict]) -> dict:
    if not candidates:
        return {
            "baseline_a_avg": 0,
            "baseline_b_avg": 0,
            "model_avg": 0,
            "avg_improvement_a": 0,
            "avg_improvement_b": 0,
        }

    total = len(candidates)
    baseline_a_avg = round(sum(c.get("baseline_a_score", 0) for c in candidates) / total, 1)
    baseline_b_avg = round(sum(c.get("baseline_b_score", 0) for c in candidates) / total, 1)
    model_avg = round(sum(c.get("final_score", 0) for c in candidates) / total, 1)
    avg_improvement_a = round(sum(c.get("improvement_vs_baseline_a", 0) for c in candidates) / total, 1)
    avg_improvement_b = round(sum(c.get("improvement_vs_baseline_b", 0) for c in candidates) / total, 1)

    return {
        "baseline_a_avg": baseline_a_avg,
        "baseline_b_avg": baseline_b_avg,
        "model_avg": model_avg,
        "avg_improvement_a": avg_improvement_a,
        "avg_improvement_b": avg_improvement_b,
    }


def build_error_analysis(candidates: list[dict]) -> dict:
    baseline_false_negatives = 0
    baseline_false_positives = 0
    hidden_cases_captured = 0
    high_ai_review_cases = 0

    for c in candidates:
        model_rec = c.get("recommendation", "")
        base_a = c.get("baseline_a_label", "")
        hidden = c.get("hidden_potential", False)
        ai_risk = c.get("ai_assistance_risk", "")

        if hidden and model_rec in ["Ручной обзор", "Продвигать вперёд"] and base_a == "Удержание / низкий приоритет":
            baseline_false_negatives += 1

        if model_rec == "Ручной обзор" and base_a == "Сильный шорт-лист":
            baseline_false_positives += 1

        if hidden and model_rec in ["Ручной обзор", "Продвигать вперёд"]:
            hidden_cases_captured += 1

        if ai_risk == "Высокий" and model_rec != "Продвигать вперёд":
            high_ai_review_cases += 1

    return {
        "baseline_false_negatives": baseline_false_negatives,
        "baseline_false_positives": baseline_false_positives,
        "hidden_cases_captured": hidden_cases_captured,
        "high_ai_review_cases": high_ai_review_cases,
    }


def run_validation_dataset() -> dict:
    if not VALIDATION_FILE.exists():
        return {
            "exists": False,
            "total_cases": 0,
            "model_accuracy": 0,
            "baseline_a_accuracy": 0,
            "baseline_b_accuracy": 0,
            "cases": [],
            "top_error_cases": [],
        }

    cases = []

    with open(VALIDATION_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue

            gpa = safe_float(row.get("gpa"), 0.0)
            expected_label = normalize_expected_label(row.get("expected_label", ""))

            analysis = analyze_candidate_text(
                gpa,
                (row.get("essay") or "").strip(),
                (row.get("achievements") or "").strip(),
                (row.get("activities") or "").strip(),
                (row.get("why_university") or "").strip(),
                (row.get("university_contribution") or "").strip(),
                (row.get("university_future_contribution") or "").strip(),
                (row.get("programs_participated") or "").strip(),
                (row.get("long_term_activities") or "").strip(),
                ""
            )
            advice = build_advice(analysis)

            model_label = advice.get("recommendation", "")
            baseline_a = analysis.get("baseline_a_label", "")
            baseline_b = analysis.get("baseline_b_label", "")
            hidden_expected = (row.get("expected_hidden_potential") or "").strip().lower()
            hidden_predicted = "yes" if analysis.get("hidden_potential") else "no"

            cases.append({
                "name": name,
                "gpa": gpa,
                "expected_label": expected_label,
                "model_label": model_label,
                "baseline_a_label": baseline_a,
                "baseline_b_label": baseline_b,
                "model_correct": model_label == expected_label,
                "baseline_a_correct": baseline_a == expected_label,
                "baseline_b_correct": baseline_b == expected_label,
                "expected_hidden_potential": hidden_expected,
                "predicted_hidden_potential": hidden_predicted,
                "hidden_correct": hidden_expected == hidden_predicted,
                "final_score": analysis.get("final_score", 0),
                "main_profile_type": advice.get("candidate_profile_type", {}).get("title", ""),
                "main_risk": advice.get("behavioral_risks", [{}])[0].get("title", ""),
            })

    total_cases = len(cases)
    if total_cases == 0:
        return {
            "exists": True,
            "total_cases": 0,
            "model_accuracy": 0,
            "baseline_a_accuracy": 0,
            "baseline_b_accuracy": 0,
            "cases": [],
            "top_error_cases": [],
        }

    model_correct = sum(1 for c in cases if c["model_correct"])
    baseline_a_correct = sum(1 for c in cases if c["baseline_a_correct"])
    baseline_b_correct = sum(1 for c in cases if c["baseline_b_correct"])

    model_accuracy = round((model_correct / total_cases) * 100, 1)
    baseline_a_accuracy = round((baseline_a_correct / total_cases) * 100, 1)
    baseline_b_accuracy = round((baseline_b_correct / total_cases) * 100, 1)

    top_error_cases = [c for c in cases if not c["model_correct"]][:5]

    return {
        "exists": True,
        "total_cases": total_cases,
        "model_accuracy": model_accuracy,
        "baseline_a_accuracy": baseline_a_accuracy,
        "baseline_b_accuracy": baseline_b_accuracy,
        "cases": cases,
        "top_error_cases": top_error_cases,
    }


@app.get("/", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {})


@app.post("/register")
async def register_submit(
    name: str = Form(...),
    tg_nick: str = Form(""),
):
    return RedirectResponse(url=f"/apply?name={name}&tg={tg_nick}", status_code=302)


@app.get("/apply", response_class=HTMLResponse)
async def home(request: Request, name: str = "", tg: str = ""):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "result": None,
            "prefill_name": name,
            "prefill_tg": tg,
        }
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    name: str = Form(...),
    gpa: float = Form(...),
    essay: str = Form(...),
    achievements: str = Form(...),
    activities: str = Form(...),
    why_university: str = Form(...),
    university_contribution: str = Form(...),
    university_future_contribution: str = Form(...),
    programs_participated: str = Form(...),
    long_term_activities: str = Form(...),
    archetype_name: str = Form(""),
    tg_nick: str = Form(""),
    files: List[UploadFile] = File(default=[]),
):
    uploaded_files = save_uploaded_files(files)

    candidate = build_candidate_record(
        name=name,
        gpa=gpa,
        essay=essay,
        achievements=achievements,
        activities=activities,
        why_university=why_university,
        university_contribution=university_contribution,
        university_future_contribution=university_future_contribution,
        programs_participated=programs_participated,
        long_term_activities=long_term_activities,
        evidence_files=uploaded_files,
        archetype_name=archetype_name,
        tg_nick=tg_nick,
    )

    add_candidate(candidate)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "result": candidate,
            "prefill_name": name,
            "prefill_tg": tg_nick,
        }
    )


@app.get("/shortlist", response_class=HTMLResponse)
async def shortlist(request: Request):
    candidates = sort_candidates(get_all_candidates())

    admissions_summary = build_admissions_summary(candidates)
    validation_summary = build_validation_summary(candidates)
    error_analysis = build_error_analysis(candidates)
    validation_dataset = run_validation_dataset()

    return templates.TemplateResponse(
        request,
        "shortlist.html",
        {
            "candidates": candidates,
            "admissions_summary": admissions_summary,
            "validation_summary": validation_summary,
            "error_analysis": error_analysis,
            "validation_dataset": validation_dataset,
        }
    )


@app.get("/candidate/{candidate_id}", response_class=HTMLResponse)
async def candidate_page(request: Request, candidate_id: int):
    candidate = get_candidate_by_id(candidate_id)

    if candidate is None:
        return RedirectResponse(url="/shortlist", status_code=302)

    return templates.TemplateResponse(
        request,
        "candidate.html",
        {
            "candidate": candidate
        }
    )


@app.post("/candidate/{candidate_id}/decision")
async def decision(candidate_id: int, decision: str = Form(...)):
    update_candidate_decision(candidate_id, decision)
    return RedirectResponse(url=f"/candidate/{candidate_id}", status_code=302)


@app.get("/download-template")
async def download_template():
    csv_content = (
        "name,gpa,essay,achievements,activities,why_university,university_contribution,university_future_contribution,programs_participated,long_term_activities\n"
        "\"Candidate A\",3.8,"
        "\"Main essay text here\","
        "\"Achievements text here\","
        "\"Activities text here\","
        "\"Why this university text here\","
        "\"Contribution to university life\","
        "\"Contribution to future university development\","
        "\"Programs participated in\","
        "\"Long-term activities and lessons\"\n"
    )

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates_template.csv"}
    )


@app.post("/bulk-upload")
async def bulk_upload(
    file: UploadFile = File(...),
    replace_existing: str = Form("no")
):
    if replace_existing == "yes":
        clear_candidates()

    content = await file.read()
    decoded = content.decode("utf-8-sig")
    csv_stream = io.StringIO(decoded)
    reader = csv.DictReader(csv_stream)

    required_columns = {
        "name",
        "gpa",
        "essay",
        "achievements",
        "activities",
        "why_university",
        "university_contribution",
        "university_future_contribution",
        "programs_participated",
        "long_term_activities",
    }

    uploaded_columns = set(reader.fieldnames or [])
    if not required_columns.issubset(uploaded_columns):
        return RedirectResponse(url="/shortlist", status_code=302)

    for row in reader:
        name = (row.get("name") or "").strip()
        if not name:
            continue

        candidate = build_candidate_record(
            name=name,
            gpa=safe_float(row.get("gpa"), 0.0),
            essay=(row.get("essay") or "").strip(),
            achievements=(row.get("achievements") or "").strip(),
            activities=(row.get("activities") or "").strip(),
            why_university=(row.get("why_university") or "").strip(),
            university_contribution=(row.get("university_contribution") or "").strip(),
            university_future_contribution=(row.get("university_future_contribution") or "").strip(),
            programs_participated=(row.get("programs_participated") or "").strip(),
            long_term_activities=(row.get("long_term_activities") or "").strip(),
            evidence_files=[],
            archetype_name="",
            tg_nick="",
        )
        add_candidate(candidate)

    return RedirectResponse(url="/shortlist", status_code=302)