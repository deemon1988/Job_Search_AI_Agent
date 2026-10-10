import urllib.request
import urllib.parse
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def search_hh(query, exp):
    params = {
        "text": query,
        "schedule": "remote",
        "experience": exp,
        "per_page": 20,
        "order_by": "publication_time"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    url = f"https://api.hh.ru/vacancies?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("items", [])
    except Exception as e:
        print(f"Error fetching hh.ru with {query}, {exp}: {e}")
        return []

items_no_exp = search_hh("Python", "noExperience")
items_junior = search_hh("Junior Python", "between1And3")
all_items = items_no_exp + items_junior

print(f"Total hh.ru items found: {len(all_items)}")
seen = set()
for idx, it in enumerate(all_items, 1):
    url = it.get("alternate_url")
    if url in seen:
        continue
    seen.add(url)
    title = it.get("name")
    company = it.get("employer", {}).get("name", "Компания")
    sal = "Не указана"
    if it.get("salary"):
        s = it["salary"]
        f = s.get("from")
        t = s.get("to")
        c = s.get("currency")
        sal = f"{f or ''} - {t or ''} {c}"
    sched = it.get("schedule", {}).get("name", "")
    print(f"{idx}. [{company}] {title} | {sal} | {sched}")
    print(f"   {url}")
