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

async def run_debrief(notes: str, as_json: bool):
    p = Path(notes)
    if p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = notes

    agent = JobAgent()
    debrief = await agent.interview.debrief_interview(raw_text)

    if as_json:
        data = {
            "strengths_observed": debrief.strengths_observed,
            "gap_analysis": [g.model_dump() for g in debrief.gap_analysis],
            "overall_recommendations": debrief.overall_recommendations
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print("🎯 Разбор результатов собеседования (Interview Debrief)")
    print("=" * 60)
    print(f"💪 Выявленные сильные стороны:\n{debrief.strengths_observed}\n")
    print("-" * 60)
    print("🔍 Детальный разбор вопросов и пробелов:")
    for idx, item in enumerate(debrief.gap_analysis, 1):
        print(f"\nВопрос {idx}: {item.question}")
        print(f"✅ Эталонный ответ:\n{item.ideal_answer}")
        print(f"📚 Микро-план подготовки:\n{item.quick_plan}")
    print("\n" + "-" * 60)
    print(f"🎯 Итоговые рекомендации эксперта:\n{debrief.overall_recommendations}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Анализ сложных вопросов собеседования и составление плана прокачки")
    parser.add_argument("notes", help="Текст с вопросами собеседования или путь к файлу")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    args = parser.parse_args()
    asyncio.run(run_debrief(args.notes, args.json))

if __name__ == "__main__":
    main()
