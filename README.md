# Kronos Fusion Energy — news feed

The RSS feed and sitemaps for the Kronos Fusion Energy news pages, served by GitHub Pages at
**https://news.kronosfusionenergy.com** (feed: `/rss.xml`). The story pages themselves live on the main
site at `https://www.kronosfusionenergy.com/news/<slug>`.

## How it works

- `data/science_log_items.csv` — the Science Log stories (dated, three a day), exported from the
  founder's master list by `sync_from_master.py`.
- `data/legacy_news_items.csv` — the 2023–2026 news dossier stories.
- `build_feed.py` — builds `site/` (rss.xml, news_sitemap.xml, news_google_sitemap.xml, index.html,
  robots.txt). Only stories dated on or before the build day are included.
- `.github/workflows/daily-feed.yml` — runs the build every morning (Pacific) and on every push,
  publishes `site/` to GitHub Pages, and commits the rebuilt `site/` back to `main`.

## Adding stories

1. Add the row to `SCIENCE_LOG_ITEMS_MASTER.csv` (status `LIVE`; give a date or leave it blank for the
   next free slot).
2. Run `python3 sync_from_master.py` (on the Mac) — it rewrites `data/science_log_items.csv`.
3. Commit and push. The Action rebuilds and publishes within a few minutes.

## Older files

`rss.xml`, `news_sitemap.xml` and `news_google_sitemap.xml` at the repo root, and `build_rss.py`, are the
copies that were uploaded to the main site by hand before the feed moved here. `build_feed.py` replaces
`build_rss.py`; the root files are kept for reference.
