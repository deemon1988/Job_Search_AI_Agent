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

async def run_cover(source: str, detailed: bool, as_json: bool):
    p = Path(source)
    if p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = source

    agent = JobAgent()
    parsed = await agent.parser.parse(raw_text)
    cover = await agent.cover_letter.generate(parsed)

    text_to_show = cover.detailed_letter if detailed else cover.short_letter
    title_format = "Развернутое письмо для HR" if detailed else "Краткий отклик для формы hh.ru / SuperJob"

    if as_json:
        data = {
            "hook_phrase": cover.hook_phrase,
            "short_letter": cover.short_letter,
            "detailed_letter": cover.detailed_letter,
            "highlighted_projects": cover.highlighted_projects,
            "skills_covered": cover.skills_covered
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print(f"✉️ {title_format} ({len(text_to_show)} знаков):")
    print(f"🪝 Hook (Первые 2 строки): {cover.hook_phrase}")
    print("-" * 60)
    print(text_to_show)
    print("-" * 60)
    print(f"📂 Упомянутые проекты: {', '.join(cover.highlighted_projects)}")
    print(f"🎯 Закрытые требования: {', '.join(cover.skills_covered)}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Генерация сопроводительного письма по правилу первых 2 строк SuperJob Pro")
    parser.add_argument("source", help="URL вакансии, путь к файлу или текст")
    parser.add_argument("--detailed", action="store_true", help="Развернутое письмо для прямого обращения к HR/тимлиду")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")
    args = parser.parse_args()
    asyncio.run(run_cover(args.source, args.detailed, args.json))

if __name__ == "__main__":
    main()
