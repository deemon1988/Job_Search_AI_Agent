import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def test_hh(query, experience="between1And3"):
    params = [
        f"text={urllib.parse.quote(query)}",
        "schedule=remote",
        f"experience={experience}",
        "order_by=publication_time"
    ]
    web_url = f"https://hh.ru/search/vacancy?{'&'.join(params)}"
    print(f"Requesting: {web_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }
    req = urllib.request.Request(web_url, headers=headers)
    html = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("[data-qa='vacancy-serp__vacancy']")
    if not cards:
        cards = soup.find_all("div", class_=lambda c: c and "vacancy" in c.lower() and "card" in c.lower())
    print(f"Cards found: {len(cards)}")

    for idx, c in enumerate(cards[:10], 1):
        title_elem = c.select_one("[data-qa='serp-item__title']") or c.find("a", href=lambda h: h and "/vacancy/" in h)
        comp_elem = c.select_one("[data-qa='vacancy-serp__vacancy-employer']")
        sal_elem = c.select_one("[data-qa='vacancy-serp__vacancy-compensation']")
        loc_elem = c.select_one("[data-qa='vacancy-serp__vacancy-address']")
        if title_elem:
            t_text = title_elem.get_text(strip=True)
            t_href = title_elem.get("href", "").split("?")[0]
            c_text = comp_elem.get_text(strip=True) if comp_elem else "Компания"
            s_text = sal_elem.get_text(strip=True) if sal_elem else "Не указана"
            l_text = loc_elem.get_text(strip=True) if loc_elem else "Удаленно"
            print(f"{idx}. [{c_text}] {t_text} | {s_text} | {l_text}")
            print(f"   {t_href}")

print("=== TEST 1: Python noExperience ===")
test_hh("Python", "noExperience")

print("\n=== TEST 2: Junior Python ===")
test_hh("Junior Python", "between1And3")
