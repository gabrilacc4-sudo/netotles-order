#!/usr/bin/env python3
"""Fetch the RealtyCalendar iCal feed and write busy.json (dates only)."""
import re, json, sys, urllib.request, datetime as dt
URL = "https://realtycalendar.ru/apartments/export.ics?q=Mjc5NDcx%0A"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) busy-sync"})
txt = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
if "BEGIN:VCALENDAR" not in txt:
    sys.exit("feed did not return a calendar")
txt = re.sub(r"\r?\n[ \t]", "", txt)
nights = set()
for ev in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", txt, re.S):
    a = re.search(r"DTSTART[^:]*:(\d{8})", ev); z = re.search(r"DTEND[^:]*:(\d{8})", ev)
    if not a or not z: continue
    d = dt.datetime.strptime(a.group(1), "%Y%m%d").date(); e = dt.datetime.strptime(z.group(1), "%Y%m%d").date()
    n = 0
    while d < e and n < 400:
        nights.add(d.isoformat()); d += dt.timedelta(1); n += 1
today = dt.date.today().isoformat()
out = {"updated": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "nights": sorted(x for x in nights if x >= today)}
new = json.dumps(out, ensure_ascii=False, indent=0)
try:
    old = json.load(open("busy.json"))
    if old.get("nights") == out["nights"]:
        sys.exit(0)  # nothing changed: keep file (no needless commit)
except Exception:
    pass
open("busy.json", "w").write(new + "\n")
print("busy.json updated:", len(out["nights"]), "nights")
