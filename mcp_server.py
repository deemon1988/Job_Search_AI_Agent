#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Job Search AI Agent.
Exposes career search, SuperJob Pro scoring, cover letter generation,
STAR interview prep, and CRM tools to AI environments (Cursor, Claude, Antigravity, etc.).
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from mcp.server.mcpserver import MCPServer
from agent import JobAgent
from agent.models import ApplicationStatus, JobApplication
from storage import db
from config import settings

server = MCPServer("job-search-agent", version="1.0.0")
_agent: Optional[JobAgent] = None

def get_agent() -> JobAgent:
    global _agent
    if _agent is None:
        _agent = JobAgent()
    return _agent

def _resolve_source_text(source: str) -> str:
    p = Path(source)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return source

@server.tool()
async def search_vacancies(
    query: str = "Python стажер",
    remote_only: bool = True,
    limit: int = 5,
    include_internships: bool = True
) -> str:
    """
    Поиск вакансий и стажировок по открытым источникам (hh.ru, Хабр Карьера, ТрудВсем)
    и корпоративным программам (Сбер, Т-Банк, ИнфоТеКС, Яндекс).
    """
    agent = get_agent()
    res = await agent.searcher.search_all(query, remote_only=remote_only, limit_per_source=limit)
    
    hh_list = res.get("hh", [])
    trud_list = res.get("trudvsem", [])
    habr_list = res.get("habr", [])
    jabka_list = res.get("jabka", [])
    all_jobs = hh_list + habr_list + trud_list + jabka_list

    internships = []
    if include_internships:
        internships = agent.searcher.get_corporate_internships()

    payload = {
        "query": query,
        "remote_only": remote_only,
        "total_vacancies": len(all_jobs),
        "vacancies": [j.to_dict() if hasattr(j, "to_dict") else j.model_dump() for j in all_jobs],
        "corporate_internships": internships
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

@server.tool()
async def parse_vacancy(source: str) -> str:
    """
    Глубокий парсинг вакансии по URL (hh.ru, SuperJob) или по тексту описания.
    Извлекает название, компанию, стек, зарплату, график, грейд и требования.
    """
    agent = get_agent()
    text = _resolve_source_text(source)
    parsed = await agent.parser.parse(text)
    return json.dumps(parsed.model_dump(), ensure_ascii=False, indent=2)

@server.tool()
async def score_vacancy(source: str, save_to_crm: bool = False) -> str:
    """
    Экспертный расчет скоринга вакансии по стандарту SuperJob Pro (0-100 баллов).
    Оценивает Hard Skills, Опыт, СПО МТИ, Условия, штрафы за Red Flags и риски.
    Опционально сохраняет вакансию в воронку SQLite CRM.
    """
    agent = get_agent()
    text = _resolve_source_text(source)
    parsed = await agent.parser.parse(text)
    score = await agent.scorer.score(parsed)

    crm_id = None
    if save_to_crm:
        await db.init_db()
        app = JobApplication(
            company=parsed.company,
            job_title=parsed.title,
            platform=parsed.platform,
            job_url=parsed.url or "",
            vector=score.recommended_vector,
            score=score.total_score,
            status=ApplicationStatus.NEW,
            why_fits="\n".join(score.pros),
            gaps="\n".join(score.missing_gaps),
            salary_info=parsed.salary_raw,
            remote_status=parsed.employment_type,
            full_job_text=parsed.raw_text
        )
        crm_id = await db.add_application(app)

    payload = {
        "job_title": parsed.title,
        "company": parsed.company,
        "total_score": score.total_score,
        "tier": score.priority_tier,
        "recommended_vector": score.recommended_vector.value,
        "score_details": {
            "hard_skills": f"{score.hard_skills_score}/40",
            "experience_grade": f"{score.experience_grade_score}/25",
            "education_domain": f"{score.education_domain_score}/15",
            "conditions": f"{score.conditions_score}/10",
            "red_flags_penalty": f"{score.red_flags_penalty} pts"
        },
        "pros": score.pros,
        "cons_and_risks": score.cons_and_risks,
        "missing_gaps": score.missing_gaps,
        "strategy": score.application_strategy,
        "crm_id": crm_id
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

@server.tool()
async def generate_cover_letter(source: str, detailed: bool = False) -> str:
    """
    Генерация отклика по стандарту SuperJob Pro с правилом первых 2 строк (Hook),
    пруфами на gorizont-blog.ru и GitHub, без пустых клише.
    Форматы: краткий (hh.ru/SuperJob) или развернутый (HR email/Telegram).
    """
    agent = get_agent()
    text = _resolve_source_text(source)
    parsed = await agent.parser.parse(text)
    cover = await agent.cover_letter.generate(parsed)

    payload = {
        "hook_phrase": cover.hook_phrase,
        "target_format": "detailed" if detailed else "short",
        "letter": cover.detailed_letter if detailed else cover.short_letter,
        "highlighted_projects": cover.highlighted_projects,
        "skills_covered": cover.skills_covered
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

@server.tool()
async def prepare_interview(source: str) -> str:
    """
    Комплексная подготовка к собеседованию в 3 блока (SuperJob Pro):
    1. 10 точечных вопросов технического скрининга с тезисами ответа.
    2. Поведенческие вопросы по STAR-методологии (включая Elevator Pitch и кейс бага).
    3. Вопросы кандидата к работодателю для повышения шанса оффера.
    """
    agent = get_agent()
    text = _resolve_source_text(source)
    parsed = await agent.parser.parse(text)
    prep = await agent.interview.generate_prep_questions(parsed)

    payload = {
        "role_summary": prep.role_summary,
        "technical_screening_questions": [q.model_dump() for q in prep.technical_questions],
        "star_behavioral_questions": [b.model_dump() for b in prep.behavioral_star_questions],
        "questions_for_employer": prep.questions_for_employer
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

@server.tool()
async def debrief_interview(interview_notes: str) -> str:
    """
    Разбор вопросов после прошедшего собеседования:
    анализ сильных сторон, эталонные ответы на сложные вопросы и микро-план прокачки.
    """
    agent = get_agent()
    text = _resolve_source_text(interview_notes)
    debrief = await agent.interview.debrief_interview(text)
    payload = {
        "strengths_observed": debrief.strengths_observed,
        "gap_analysis": [g.model_dump() for g in debrief.gap_analysis],
        "overall_recommendations": debrief.overall_recommendations
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

@server.tool()
async def get_candidate_profile() -> str:
    """
    Получение верифицированного профиля кандидата Дмитрия Турейко
    (образование СПО МТИ, подтвержденный стек, проекты, ограничения и целевые зарплаты).
    """
    from agent.prompts import load_profile_context
    profile = load_profile_context(settings.PROFILE_CONTEXT_PATH)
    return json.dumps(profile.get("personal", {}), ensure_ascii=False, indent=2)

@server.tool()
async def get_crm_funnel() -> str:
    """
    Получение текущей статистики воронки откликов из SQLite CRM.
    """
    await db.init_db()
    stats = await db.get_funnel_stats()
    return json.dumps(stats, ensure_ascii=False, indent=2)

@server.tool()
async def update_crm_status(application_id: int, new_status: str, notes: str = "") -> str:
    """
    Обновление статуса отклика в CRM (Новый, Отправлено, Скрининг, Собеседование, Тестовое, Оффер, Отказ).
    """
    await db.init_db()
    try:
        st = ApplicationStatus(new_status)
    except ValueError:
        return f"Error: Недопустимый статус. Разрешены: {[s.value for s in ApplicationStatus]}"
    await db.update_status(application_id, st, notes=notes or None)
    return f"Success: Заявка #{application_id} обновлена на статус '{new_status}'"

async def _test_tools():
    print("🧪 Запуск теста инструментов MCP-сервера...")
    agent = get_agent()
    print("1. Тест профиля кандидата...")
    prof = await get_candidate_profile()
    assert "Турейко" in prof, "Candidate profile check failed"
    print("   ✅ Профиль кандидата получен корректно!")

    print("2. Тест поиска вакансий (hh.ru)...")
    res_str = await search_vacancies(query="Python стажер", remote_only=True, limit=2)
    res = json.loads(res_str)
    print(f"   ✅ Поиск вернул {res['total_vacancies']} вакансий")

    print("3. Тест CRM воронки...")
    funnel = await get_crm_funnel()
    print(f"   ✅ Воронка CRM доступна: {funnel[:60]}...")

    print("🎉 Все тесты инструментов MCP сервера успешно пройдены!")

def main():
    if "--test" in sys.argv:
        asyncio.run(_test_tools())
        return

    # Run standard MCP stdio server
    server.run()

if __name__ == "__main__":
    main()
