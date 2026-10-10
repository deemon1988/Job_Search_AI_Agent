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

async def run_search(query: str, remote: bool, limit: int, as_json: bool, include_internships: bool):
    agent = JobAgent()
    
    # 1. Multi-source search
    results = await agent.searcher.search_all(query, remote_only=remote, limit_per_source=limit)
    hh_list = results.get("hh", [])
    trud_list = results.get("trudvsem", [])
    habr_list = results.get("habr", [])
    jabka_list = results.get("jabka", [])
    all_jobs = hh_list + habr_list + trud_list + jabka_list
    
    internships = []
    if include_internships:
        internships = agent.searcher.get_corporate_internships()

    if as_json:
        data = {
            "query": query,
            "remote": remote,
            "total_found": len(all_jobs),
            "vacancies": [j.to_dict() if hasattr(j, "to_dict") else j.model_dump() for j in all_jobs],
            "corporate_internships": internships
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print("=" * 65)
    print(f"🎯 Результаты поиска по запросу: '{query}' (remote={remote})")
    print(f"Всего найдено вакансий: {len(all_jobs)}")
    print("=" * 65)

    for idx, item in enumerate(all_jobs, 1):
        print(f"\n{idx}. [{item.platform}] {item.title}")
        print(f"   🏢 Компания: {item.company} | 📍 {item.location}")
        print(f"   💰 Зарплата: {item.salary} | ⏰ {item.schedule}")
        print(f"   🔗 Ссылка: {item.url}")
        if item.snippet:
            print(f"   📝 Описание: {item.snippet[:180]}...")

    if internships:
        print("\n" + "=" * 65)
        print("🏢 Каталог актуальных стажировок IT-корпораций РФ:")
        print("=" * 65)
        for idx, it in enumerate(internships, 1):
            print(f"{idx}. {it['company']} — {it['program_name']}")
            print(f"   🔗 Подать заявку: {it['url']}")
            print(f"   🎯 Стек: {it['focus']} ({it['target_audience']})")

def main():
    parser = argparse.ArgumentParser(description="Поиск вакансий и стажировок (hh.ru, Habr, ТрудВсем)")
    parser.add_argument("query", nargs="?", default="Python стажер", help="Поисковый запрос (по умолчанию 'Python стажер')")
    parser.add_argument("--remote", action="store_true", default=True, help="Только удаленная работа (по умолчанию True)")
    parser.add_argument("--no-remote", dest="remote", action="store_false", help="Включая офисные позиции")
    parser.add_argument("--limit", type=int, default=5, help="Лимит на источник (по умолчанию 5)")
    parser.add_argument("--internships", action="store_true", help="Включить каталог корпоративных стажировок")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")

    args = parser.parse_args()
    asyncio.run(run_search(args.query, args.remote, args.limit, args.json, args.internships))

if __name__ == "__main__":
    main()
