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

from storage import db
from agent.models import ApplicationStatus

async def show_stats(as_json: bool):
    await db.init_db()
    stats = await db.get_funnel_stats()
    if as_json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    print("=" * 45)
    print("📊 Воронка откликов (SQLite CRM):")
    print("-" * 45)
    total = sum(stats.values())
    for status, count in stats.items():
        print(f"  {status:<25} : {count}")
    print("-" * 45)
    print(f"  Всего вакансий в воронке : {total}")
    print("=" * 45)

async def list_applications(limit: int, as_json: bool):
    await db.init_db()
    apps = await db.list_applications(limit=limit or 50)

    if as_json:
        print(json.dumps([a.model_dump() for a in apps], ensure_ascii=False, indent=2, default=str))
        return

    print("=" * 70)
    print(f"📋 Список вакансий в воронке (показано {len(apps)}):")
    print("=" * 70)
    for a in apps:
        app_id = a.id
        title = a.job_title
        company = a.company
        status = a.status.value if hasattr(a.status, 'value') else a.status
        score = a.score
        vector = a.vector.value if hasattr(a.vector, 'value') else a.vector
        print(f"#{app_id} [{status}] {title} ({company}) — Скоринг: {score}б. | Вектор: {vector}")
    print("=" * 70)

async def update_app(app_id: int, new_status: str, notes: str = None):
    await db.init_db()
    try:
        status_enum = ApplicationStatus(new_status)
    except ValueError:
        valid = [s.value for s in ApplicationStatus]
        print(f"❌ Неверный статус. Допустимые значения: {', '.join(valid)}")
        return

    await db.update_status(app_id, status_enum, notes=notes)
    print(f"✅ Статус заявки #{app_id} успешно обновлен на '{new_status}'")

def main():
    parser = argparse.ArgumentParser(description="Управление воронкой откликов CRM (SQLite)")
    parser.add_argument("--stats", action="store_true", help="Показать статистику воронки")
    parser.add_argument("--list", type=int, nargs="?", const=10, help="Вывести список вакансий (по умолчанию 10)")
    parser.add_argument("--update", type=int, metavar="ID", help="ID вакансии для обновления")
    parser.add_argument("--status", type=str, help="Новый статус (Новый, Подготовка, Отправлено, Скрининг, Интервью, Тестовое, Оффер, Отказ)")
    parser.add_argument("--notes", type=str, help="Заметки при обновлении статуса")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")

    args = parser.parse_args()

    if args.update:
        if not args.status:
            print("❌ Ошибка: укажите --status при использовании --update")
            sys.exit(1)
        asyncio.run(update_app(args.update, args.status, args.notes))
    elif args.list is not None:
        asyncio.run(list_applications(args.list, args.json))
    else:
        # Default action is stats
        asyncio.run(show_stats(args.json))

if __name__ == "__main__":
    main()
