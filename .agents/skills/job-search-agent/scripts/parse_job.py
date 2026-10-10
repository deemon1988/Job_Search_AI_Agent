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

async def run_parse(source: str, as_json: bool):
    p = Path(source)
    if p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = source

    agent = JobAgent()
    parsed = await agent.parser.parse(raw_text)

    if as_json:
        print(json.dumps(parsed.model_dump(), ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print(f"📌 Должность: {parsed.title}")
    print(f"🏢 Компания: {parsed.company} | Платформа: {parsed.platform}")
    print(f"💰 Зарплата: {parsed.salary_raw or 'Не указана'} | График: {parsed.employment_type}")
    print(f"📍 Локация: {parsed.location or 'Не указана'} | Грейд: {parsed.grade}")
    if parsed.url:
        print(f"🔗 Ссылка: {parsed.url}")
    print(f"🛠 Стек: {', '.join(parsed.key_skills)}")
    print("\n🔍 Hard Skills требования:")
    for r in parsed.requirements_hard:
        print(f"  • {r}")
    if parsed.responsibilities:
        print("\n📋 Обязанности:")
        for resp in parsed.responsibilities[:5]:
            print(f"  ▹ {resp}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Глубокий парсинг вакансии по ссылке (hh.ru, SuperJob) или тексту")
    parser.add_argument("source", help="URL вакансии, путь к текстовому файлу или сырой текст вакансии")
    parser.add_argument("--json", action="store_true", help="Вывод результата в JSON")
    args = parser.parse_args()
    asyncio.run(run_parse(args.source, args.json))

if __name__ == "__main__":
    main()
