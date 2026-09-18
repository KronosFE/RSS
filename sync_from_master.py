#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export the LIVE Science Log stories from the founder's master list into data/science_log_items.csv.

Run this on the Mac after editing SCIENCE_LOG_ITEMS_MASTER.csv (add rows, set status LIVE, give each a
date or leave it blank), then commit + push. The GitHub Action rebuilds the feed from the exported file.

  * LIVE rows only. Held rows never leave the master.
  * A LIVE row with no date gets the next free 3-a-day slot after the last dated story (printed).
  * Each story's feed summary is the first paragraph of its LinkedIn post (PUBLER_SOCIAL_POSTS.json);
    when no post exists the feed falls back to the key result + DOI.
"""
import csv, json, os, re, collections
from datetime import date, timedelta

DRAFTS = "/Users/pford/Desktop/Kronos Fusion Energy/05 - MEDIA PUBLICATIONS/KRONOS_SCIENCE_LOG_DRAFTS"
MASTER = os.path.join(DRAFTS, "SCIENCE_LOG_ITEMS_MASTER.csv")
PUBLER = os.path.join(DRAFTS, "PUBLER_SOCIAL_POSTS.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "science_log_items.csv")
PER_DAY = 3
COLS = ["gid", "track", "track_name", "tag", "headline", "slug", "doi", "key_anchor", "pubdate", "summary"]

def summary_from_post(text):
    para = re.split(r"\n\s*\n", text.strip())[0]
    para = re.sub(r"https?://\S+", "", para)
    para = re.sub(r"(?:^|\s)#\w+", "", para)
    para = re.sub(r"\s+", " ", para).strip()
    if len(para) > 320:
        cut = para[:320]; end = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
        para = cut[:end + 1] if end > 120 else cut.rstrip() + "…"
    return para

rows = list(csv.DictReader(open(MASTER, newline="", encoding="utf-8")))
for i, r in enumerate(rows): r["_i"] = i
live = [r for r in rows if r["status"].strip().upper() == "LIVE" and r["slug"].strip()]
dated = [r for r in live if r["pubdate"].strip()]
undated = [r for r in live if not r["pubdate"].strip()]
counts = collections.Counter(r["pubdate"].strip() for r in dated)
if undated:
    d = max(date.fromisoformat(x) for x in counts) if counts else date.today()
    for r in undated:
        while counts[d.isoformat()] >= PER_DAY: d += timedelta(days=1)
        r["pubdate"] = d.isoformat(); counts[d.isoformat()] += 1
        print(f"  assigned {r['pubdate']} to gid {r['gid']}: {r['headline'][:60]}")

summ = {}
if os.path.exists(PUBLER):
    for p in json.load(open(PUBLER, encoding="utf-8")):
        if p.get("platform") == "LinkedIn" and p.get("post_text"):
            summ[str(p["gid"])] = summary_from_post(p["post_text"])

live.sort(key=lambda r: (r["pubdate"], r["_i"]))
prev = {}
if os.path.exists(OUT):
    prev = {r["gid"]: r for r in csv.DictReader(open(OUT, newline="", encoding="utf-8"))}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in live:
        r["summary"] = summ.get(r["gid"], ""); w.writerow(r)

bd = collections.Counter(r["pubdate"] for r in live)
new = {r["gid"] for r in live}
added = sorted(new - set(prev), key=int); removed = sorted(set(prev) - new, key=int)
moved = [g for g in new & set(prev) if prev[g]["pubdate"] != next(r["pubdate"] for r in live if r["gid"] == g)]
print(f"exported {len(live)} LIVE stories → data/science_log_items.csv | {min(bd)} → {max(bd)} | "
      f"days≠{PER_DAY}: { {d: c for d, c in bd.items() if c != PER_DAY} or 'none'} | "
      f"no summary: {sum(1 for r in live if not r['summary'])}")
if prev:
    print(f"vs previous export: +{len(added)} {added[:10]} | −{len(removed)} {removed[:10]} | dates moved: {len(moved)}")
