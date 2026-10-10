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

async def run_interview(source: str, as_json: bool):
    p = Path(source)
    if p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = source

    agent = JobAgent()
    parsed = await agent.parser.parse(raw_text)
    prep = await agent.interview.generate_prep_questions(parsed)

    if as_json:
        data = {
            "role_summary": prep.role_summary,
            "technical_questions": [q.model_dump() for q in prep.technical_questions],
            "behavioral_star_questions": [b.model_dump() for b in prep.behavioral_star_questions],
            "questions_for_employer": prep.questions_for_employer
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print("=" * 65)
    print(f"📌 Подготовка к интервью: {parsed.title} ({parsed.company})")
    print(f"💡 Фокус роли: {prep.role_summary}")
    print("=" * 65)
    print("\n🛠 БЛОК 1: Технический скрининг (10 вопросов с тезисами ответа):")
    for q in prep.technical_questions:
        print(f"\n{q.number}. [{q.topic}] {q.question}")
        for pt in q.key_points:
            print(f"    ▹ {pt}")

    print("\n" + "-" * 65)
    print("🌟 БЛОК 2: Поведенческие вопросы по STAR-модели:")
    for idx, s in enumerate(prep.behavioral_star_questions, 1):
        print(f"\n{idx}. ❓ {s.question}")
        print(f"  • S (Ситуация): {s.situation_context}")
        print(f"  • T (Задача): {s.task_description}")
        print(f"  • A (Действие): {s.action_taken}")
        print(f"  • R (Результат): {s.result_metric}")
        print(f"  💡 Совет SuperJob Pro: {s.expert_tip}")

    print("\n" + "-" * 65)
    print("🤝 БЛОК 3: Умные вопросы кандидата к работодателю (повышают конверсию в оффер):")
    for eq in prep.questions_for_employer:
        print(f"  • {eq}")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="Подготовка к собеседованию в 3 блока (SuperJob Pro: Tech + STAR + Questions)")
    parser.add_argument("source", help="URL вакансии, путь к файлу или текст")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    args = parser.parse_args()
    asyncio.run(run_interview(args.source, args.json))

if __name__ == "__main__":
    main()
