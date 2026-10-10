import asyncio
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup
import re
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

async def search_jabka(query: str, remote_only: bool = True, location_rf: bool = True, limit: int = 5):
    encoded_q = urllib.parse.quote(query)
    # Using search parameter + country=ru if location_rf + remote=true if remote_only
    params = [f"search={encoded_q}"]
    if remote_only:
        params.append("remote=true")
    if location_rf:
        params.append("country=ru")
        
    url = f"https://jabka.work/?{'&'.join(params)}"
    print(f"Fetching Jabka URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    results = []
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                print("Jabka returned status", resp.status)
                return []
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    job_links = soup.find_all("a", href=lambda h: h and h.startswith("/jobs/"))
    seen_urls = set()

    # Foreign locations to filter out when location_rf is True
    foreign_markers = ["сша", "кипр", "германи", "польш", "испани", "нидерланд", "великобритан", "дубай", "оаэ", "серби", "грузи", "армени", "турци"]

    for a in job_links:
        href = a.get("href", "")
        if not href or href in seen_urls:
            continue
        full_url = "https://jabka.work" + href
        seen_urls.add(href)

        # Get parent container
        parent = a.find_parent("article") or a.find_parent("div", class_=lambda c: c and ("card" in c or "job" in c)) or a
        parent_text = parent.get_text(separator=" | ").strip()
        lower_text = parent_text.lower()

        # Remote check
        is_remote = "удален" in lower_text or "remote" in lower_text
        if remote_only and not is_remote:
            continue

        # Location check
        if location_rf:
            # If explicit foreign location without RF mention, skip
            if any(fm in lower_text for fm in foreign_markers) and not any(rf in lower_text for rf in ["россия", "рф", "москва", "спб", "питер"]):
                continue

        # Parse details
        # Try to extract title, company, salary from parent_text or link
        parts = [p.strip() for p in parent_text.split("|") if p.strip()]
        
        # Salary is usually first part with ₽ or $
        salary = "Не указана"
        title = a.get_text().strip() or "Вакансия"
        company = "Компания"

        for idx, pt in enumerate(parts):
            if "₽" in pt or "$" in pt:
                salary = pt
            if pt.startswith("@"):
                company = pt.lstrip("@").strip()
            elif "developer" in pt.lower() or "разработчик" in pt.lower() or "инженер" in pt.lower() or "стажер" in pt.lower():
                if len(pt) > 5 and len(pt) < 100:
                    title = pt

        results.append({
            "title": title,
            "company": company,
            "platform": "jabka.work",
            "url": full_url,
            "salary": salary,
            "location": "Россия (Удаленно)",
            "snippet": parent_text[:220],
            "schedule": "Удаленная работа"
        })

        if len(results) >= limit:
            break

    return results

async def main():
    res = await search_jabka("Python", remote_only=True, location_rf=True, limit=5)
    print(f"\nFound {len(res)} jobs on jabka.work:")
    for r in res:
        print(f"- [{r['company']}] {r['title']} | {r['salary']} | {r['url']}")
        print(f"  Snippet: {r['snippet']}")

asyncio.run(main())
