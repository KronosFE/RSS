#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Kronos Fusion Energy news feed + sitemaps into site/.

Served by GitHub Pages at https://news.kronosfusionenergy.com. The story pages themselves live on the
main site at https://www.kronosfusionenergy.com/news/<slug>.

Sources (data/):
  science_log_items.csv  the Science Log, exported from the founder's master list (LIVE stories only)
  legacy_news_items.csv  the 2023–2026 news dossier (numbered stories)

Only stories dated on or before today (America/Los_Angeles) are emitted, so the scheduled GitHub
Action releases each day's three Science Log stories on their date. Nothing else is filtered.

Outputs (site/):
  rss.xml                  the feed, newest first
  news_sitemap.xml         every released story (for Search Console)
  news_google_sitemap.xml  stories from the last two days, Google News format
  index.html               sends people to /news; carries the feed autodiscovery tag
  robots.txt               points crawlers at the sitemaps

Try another day:  FEED_TODAY=2026-10-01 python3 build_feed.py
"""
import csv, os
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from email.utils import format_datetime
from xml.sax.saxutils import escape
import xml.dom.minidom as minidom

REPO = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(REPO, "data"); OUT = os.path.join(REPO, "site")
TZ = ZoneInfo("America/Los_Angeles")
SITE = "https://www.kronosfusionenergy.com"          # where the story pages live
FEED_HOST = "https://news.kronosfusionenergy.com"    # where this build is served
CHANNEL_TITLE = "Kronos Fusion Energy — News"
CHANNEL_DESC = ("News and dated research results from Kronos Fusion Energy, a family-owned American fusion "
                "company — each item linked to its published record. Breeder and generator physics, in the open.")
PUBLICATION_NAME = "Kronos Fusion Energy"            # must match the name in Google Publisher Center
LOGO_URL = f"{SITE}/logo.png"
STORY_TIME = time(6, 0)      # Science Log stories carry 06:00 Pacific on their date
LEGACY_TIME = time(9, 0)     # dossier stories keep their original 09:00 stamps

now = datetime.now(TZ)
today = date.fromisoformat(os.environ["FEED_TODAY"]) if os.environ.get("FEED_TODAY") else now.date()

def read(fn):
    with open(os.path.join(DATA, fn), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

items, queued = [], []
for seq, r in enumerate(read("science_log_items.csv")):
    d = date.fromisoformat(r["pubdate"].strip())
    if d > today:
        queued.append(d); continue
    desc = (r.get("summary") or "").strip()
    if not desc:
        bits = [(r.get("key_anchor") or "").strip(),
                f"DOI: {r['doi'].strip()}" if (r.get("doi") or "").strip() else ""]
        desc = " · ".join(b for b in bits if b) or r["headline"].strip()
    items.append(dict(title=r["headline"].strip(), url=f"{SITE}/news/{r['slug'].strip()}",
                      dt=datetime.combine(d, STORY_TIME, TZ), desc=desc,
                      category=(r.get("tag") or "").strip(), seq=seq, kind="science-log"))
n_science = len(items)
for seq, r in enumerate(read("legacy_news_items.csv")):
    d = date.fromisoformat(r["pubdate"].strip())
    if d > today: continue
    items.append(dict(title=r["title"].strip(), url=f"{SITE}/news/{r['slug'].strip()}",
                      dt=datetime.combine(d, LEGACY_TIME, TZ), desc=r["description"].strip(),
                      category="Company News", seq=seq, kind="legacy"))
n_legacy = len(items) - n_science
items.sort(key=lambda it: (it["dt"], it["seq"]), reverse=True)
if not items:
    raise SystemExit("No stories dated on or before today — nothing to build.")

# ---------- rss.xml ----------
p = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
     '  <channel>',
     f'    <title>{escape(CHANNEL_TITLE)}</title>',
     f'    <link>{SITE}/news</link>',
     f'    <description>{escape(CHANNEL_DESC)}</description>',
     '    <language>en-us</language>',
     '    <copyright>© 2026 Kronos Fusion Energy</copyright>',
     f'    <lastBuildDate>{format_datetime(now)}</lastBuildDate>',
     f'    <pubDate>{format_datetime(items[0]["dt"])}</pubDate>',
     '    <ttl>60</ttl>',
     '    <generator>Kronos build_feed.py</generator>',
     '    <docs>https://www.rssboard.org/rss-specification</docs>',
     '    <category>Fusion Energy</category>',
     f'    <atom:link href="{FEED_HOST}/rss.xml" rel="self" type="application/rss+xml"/>',
     '    <image>',
     f'      <url>{escape(LOGO_URL)}</url>',
     f'      <title>{escape(CHANNEL_TITLE)}</title>',
     f'      <link>{SITE}/news</link>',
     '    </image>']
for it in items:
    p += ['    <item>',
          f'      <title>{escape(it["title"])}</title>',
          f'      <link>{escape(it["url"])}</link>',
          f'      <guid isPermaLink="true">{escape(it["url"])}</guid>',
          f'      <pubDate>{format_datetime(it["dt"])}</pubDate>']
    if it["category"]:
        p.append(f'      <category>{escape(it["category"])}</category>')
    p += [f'      <description>{escape(it["desc"])}</description>',
          '    </item>']
p += ['  </channel>', '</rss>']
rss = "\n".join(p) + "\n"

# ---------- news_sitemap.xml (everything released) ----------
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for it in items:
    sm.append(f'  <url><loc>{escape(it["url"])}</loc><lastmod>{it["dt"].date().isoformat()}</lastmod></url>')
sm.append('</urlset>')
sitemap = "\n".join(sm) + "\n"

# ---------- news_google_sitemap.xml (last two days, Google News format) ----------
recent = [it for it in items if it["dt"].date() >= today - timedelta(days=1)]
gn = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
      'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">']
for it in recent:
    gn += ['  <url>',
           f'    <loc>{escape(it["url"])}</loc>',
           '    <news:news>',
           f'      <news:publication><news:name>{escape(PUBLICATION_NAME)}</news:name><news:language>en</news:language></news:publication>',
           f'      <news:publication_date>{it["dt"].isoformat()}</news:publication_date>',
           f'      <news:title>{escape(it["title"])}</news:title>',
           '    </news:news>',
           '  </url>']
gn.append('</urlset>')
google_sitemap = "\n".join(gn) + "\n"

# ---------- index.html + robots.txt ----------
index_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Kronos Fusion Energy — News feed</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={SITE}/news">
<link rel="canonical" href="{SITE}/news">
<link rel="alternate" type="application/rss+xml" title="{escape(CHANNEL_TITLE)}" href="{FEED_HOST}/rss.xml">
</head>
<body>
<p>Kronos Fusion Energy news feed: <a href="/rss.xml">rss.xml</a> ·
<a href="/news_sitemap.xml">news_sitemap.xml</a> · <a href="/news_google_sitemap.xml">news_google_sitemap.xml</a>.
Taking you to <a href="{SITE}/news">kronosfusionenergy.com/news</a>…</p>
</body>
</html>
"""
robots = f"User-agent: *\nAllow: /\nSitemap: {FEED_HOST}/news_sitemap.xml\nSitemap: {FEED_HOST}/news_google_sitemap.xml\n"

# ---------- validate + write ----------
for name, doc in (("rss.xml", rss), ("news_sitemap.xml", sitemap), ("news_google_sitemap.xml", google_sitemap)):
    minidom.parseString(doc.encode("utf-8"))          # well-formedness gate: raises on any error
os.makedirs(OUT, exist_ok=True)
for name, doc in (("rss.xml", rss), ("news_sitemap.xml", sitemap), ("news_google_sitemap.xml", google_sitemap),
                  ("index.html", index_html), ("robots.txt", robots)):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(doc)

nxt = min(queued) if queued else None
print(f"built for {today} → site/  |  {len(items)} stories in the feed "
      f"({n_science} Science Log + {n_legacy} dossier)  |  Google News sitemap: {len(recent)}  |  "
      f"queued: {len(queued)}" + (f", next release {nxt} ({queued.count(nxt)} stories)" if nxt else ""))
