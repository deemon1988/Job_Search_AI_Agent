#!/usr/bin/env python3
import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
current = Path(__file__).resolve()
while current.parent != current:
    if (current / "agent").is_dir() and (current / "config.py").is_file():
        if str(current) not in sys.path:
            sys.path.insert(0, str(current))
        break
    current = current.parent

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from agent import JobAgent
from storage import db

async def run_score(source: str, as_json: bool, save_crm: bool):
    p = Path(source)
    if p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = source

    agent = JobAgent()
    parsed = await agent.parser.parse(raw_text)
    score = await agent.scorer.score(parsed)

    saved_id = None
    if save_crm:
        await db.init_db()
        from agent.models import JobApplication, ApplicationStatus
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
        saved_id = await db.add_application(app)

    if as_json:
        data = {
            "parsed_job": parsed.model_dump(),
            "score_breakdown": score.model_dump(),
            "crm_id": saved_id
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print(f"📌 {parsed.title} ({parsed.company})")
    print(f"🏆 Скоринг соответствия SuperJob Pro: {score.total_score}/100 [{score.priority_tier}]")
    print(f"🎯 Рекомендуемый карьерный вектор: {score.recommended_vector.value}")
    print("-" * 60)
    print(f"• Hard Skills: {score.hard_skills_score}/40")
    print(f"• Опыт и грейд: {score.experience_grade_score}/25")
    print(f"• Образование (МТИ / ИС): {score.education_domain_score}/15")
    print(f"• Условия и прозрачность: {score.conditions_score}/10")
    print(f"• Штраф за Red Flags: {score.red_flags_penalty} б.")
    print("-" * 60)
    print("👍 Плюсы вакансии:")
    for pros in score.pros:
        print(f"  ✅ {pros}")
    print("\n🚩 Риски / Red Flags:")
    for r in score.cons_and_risks:
        print(f"  ⚠️ {r}")
    print("\n📚 Пробелы в стеке (Gaps):")
    for g in score.missing_gaps:
        print(f"  ▹ {g}")
    print(f"\n💡 Стратегия отклика (SuperJob Pro):\n{score.application_strategy}")
    if saved_id:
        print(f"\n💾 Сохранено в воронку CRM с ID: {saved_id}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Расчет скоринга вакансии по SuperJob Pro и выявление Red Flags")
    parser.add_argument("source", help="URL вакансии, путь к файлу или текст")
    parser.add_argument("--save-crm", action="store_true", help="Автоматически сохранить вакансию в воронку SQLite CRM")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    args = parser.parse_args()
    asyncio.run(run_score(args.source, args.json, args.save_crm))

if __name__ == "__main__":
    main()
