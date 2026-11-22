import json, re, datetime, requests
from bs4 import BeautifulSoup

URL = "https://www.freejobalert.com/pwd-jobs/"
BLOCK = re.compile(r"agniveer|agnipath|\bcds\b|afcat|\barmy\b|\bnavy\b|air force", re.I)

html = requests.get(URL, timeout=60, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

jobs = []
for tr in soup.select("table tr"):
    tds = tr.find_all("td")
    if len(tds) < 4:
        continue
    org = tds[0].get_text(" ", strip=True)
    title = tds[1].get_text(" ", strip=True)
    last_raw = tds[2].get_text(" ", strip=True)
    a = tds[3].find("a")
    if not (org and title and a):
        continue
    if BLOCK.search(org + " " + title):
        continue
    m = re.match(r"(\d{2})-(\d{2})-(\d{4})", last_raw)
    last = f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""
    n = re.match(r"(\d+)\s+(.*)", title)
    posts = n.group(1) if n else ""
    name = n.group(2) if n else title
    kind = "offline" if "offline" in a["href"].lower() else "gov"
    jobs.append({
        "kind": kind, "title": name, "org": org,
        "posts": (posts + " कुल पोस्ट (इनमें PwBD आरक्षित)") if posts else "देखें",
        "last": last, "link": a["href"], "pwbd": 1,
    })

out = {"updated": datetime.datetime.utcnow().isoformat() + "Z", "jobs": jobs}
with open("jobs.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(len(jobs), "jobs saved")
