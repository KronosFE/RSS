#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Kronos News rss.xml (RSS 2.0) + a branded PDF from the same data.
Items = the 40 real /news briefings for 2023-2026 (#11-#50), backdated,
with real permalinks harvested from the live sitemap."""

import os
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from xml.sax.saxutils import escape

BASE = "https://www.kronosfusionenergy.com"
# Staged output (not the live deploy path). Set this to the real /rss deploy folder when publishing.
# Original path was: .../Kronos Fusion Energy July 2026 Publication/05 - Website 2026/rss
OUTDIR = "/Users/pford/Desktop/Kronos Fusion Energy/04 - IT INFRASTRUCTURE/07 - IT Infrastructure & Code Repos/Code Repos (live)/RSS/_news_feed_staging"
# Channel logo shown by feed readers — must be ≤144×144 and actually resolve. CONFIRM this URL points to a real image.
LOGO_URL = f"{BASE}/logo.png"

# (num, slug, title, description, (Y,M,D))
ITEMS = [
(11,"11-general-robert-pat-white-assumes-role-as-ceo","General Robert 'Pat' White Assumes Role as CEO","Kronos names General Robert 'Pat' White as Chief Executive Officer, bringing decades of military logistics and program-execution experience to the S.M.A.R.T. generator program.",(2023,2,15)),
(12,"12-strategic-tritium-breeding-program-initiated","Staged Fuel-Cycle Strategy Initiated","Kronos launches its staged fuel-cycle strategy — bridging a brief deuterium–tritium commissioning stage toward low-neutron deuterium–helium-3 operation, with helium-3 bred in situ via catalyzed D–D (no breeding blanket).",(2023,2,22)),
(13,"13-paul-weiss-elevated-to-lead-material-sciences-nano-technology","Paul Weiss Elevated to Lead Material Sciences & Nano Technology","Dr. Paul Weiss, holder of the Fred Kavli Chair in NanoSystems Sciences, formally takes the helm of Material Sciences & Nano Technology.",(2023,2,28)),
(14,"14-the-s-m-a-r-t-40-approach-unleashed-to-the-public","The S.M.A.R.T. 40 Approach Unleashed to the Public","Kronos publishes the 'S.M.A.R.T. Approach,' detailing the engineering and physics pathways behind its compact spherical-tokamak architecture.",(2023,4,5)),
(15,"15-unveiling-of-the-ai-ml-powered-simulation-suite","Unveiling of the AI/ML-Powered Simulation Suite","Kronos unveils its AI/ML-powered simulation suite - the computational backbone that would grow into the company's digital twin.",(2023,4,12)),
(16,"16-global-community-invited-to-beta-test-algorithms","Global Community Invited to Beta Test Algorithms","In an unusual move for a private fusion developer, Kronos opens its simulation suite to a global community of beta testers.",(2023,4,24)),
(17,"17-alignment-with-the-doe-milestone-based-fusion-program","Alignment with the DOE Milestone-Based Fusion Program","Kronos aligns its development plan with the U.S. Department of Energy's Milestone-Based Fusion Development Program.",(2023,5,31)),
(18,"18-puzzle-x-2023-the-helium-3-dawn-presented","PUZZLE X 2023: The Helium-3 Dawn Presented","Founder Priyanca Ford delivers the keynote 'From Star Power to Earth: Helium-3 & the Dawn of the Fusion Era' at PUZZLE X in Barcelona.",(2023,11,17)),
(19,"19-exploring-synergies-with-slac-and-the-infuse-program","Exploring Synergies with SLAC and the INFUSE Program","Kronos explores research synergies with SLAC National Accelerator Laboratory through the INFUSE program.",(2023,12,1)),
(20,"20-establishing-the-kfeds-defense-security-posture","Establishing the KFEDS Defense Security Posture","Kronos formalizes the KFEDS defense security posture, highlighting the resilience advantages of compact fusion for critical infrastructure.",(2023,12,15)),
(21,"21-global-call-for-supply-chain-partnerships","Global Call for Supply Chain Partnerships","Kronos launches a Supply Chain Partnership Portal, marking the transition from design toward manufacturing readiness.",(2024,7,15)),
(22,"22-jon-michel-greenwood-spearheads-digital-twin-architecture","Jon Michel Greenwood Spearheads Digital Twin Architecture","CTO Jon Michel Greenwood elevates the Kronos simulation suite into a fully realized digital-twin platform.",(2024,8,1)),
(23,"23-world-s-first-component-factory-established-in-india","World's First Component Factory Established in India","Kronos establishes its first Fusion Energy Component Factory in India, executing on international scaling.",(2024,8,15)),
(24,"24-synergies-with-maglab-enhance-high-temperature-superconductors","Synergies with MagLab Enhance High-Temperature Superconductors","Work at the National High Magnetic Field Laboratory advances characterization of the high-temperature superconducting (REBCO) tapes central to the magnet system.",(2024,9,9)),
(25,"25-the-kronos-fusion-energy-podcast-expands-educational-reach","\"The Kronos Fusion Energy Podcast\" Expands Educational Reach","'The Kronos Fusion Energy Podcast,' hosted by Priyanca Ford, expands to demystify fusion and engage tier-one talent.",(2024,10,1)),
(26,"26-dr-gerald-kulcinski-champions-the-aneutronic-vision","Dr. Gerald Kulcinski Champions the Aneutronic Vision","Fusion pioneer Dr. Gerald Kulcinski joins the podcast, validating the low-neutron D-3He pathway and its aneutronic p-11B endpoint.",(2024,10,15)),
(27,"27-ruben-fair-s-expertise-applied-to-magnetic-shielding","Ruben Fair's Expertise Applied to Magnetic Shielding","Board advisor Ruben Fair brings three decades of magnet-design and magnetic-shielding expertise to the program.",(2024,11,1)),
(28,"28-sushma-bhatia-steers-legislative-and-environmental-strategy","Sushma Bhatia Steers Legislative and Environmental Strategy","Advisory board member Sushma Bhatia steers the company's legislative and environmental strategy.",(2024,11,15)),
(29,"29-jack-dongarra-optimizes-exascale-computing-workflows","Jack Dongarra Optimizes Exascale Computing Workflows","Turing Award winner Jack Dongarra advises on optimizing the exascale computing workflows behind the digital twin.",(2024,12,2)),
(30,"30-simulation-validates-negative-triangularity-plasma-shaping","Simulation Validates Negative Triangularity Plasma Shaping","Kronos's simulation suite validates negative-triangularity plasma shaping for the S.M.A.R.T. reactor - suppressing edge instabilities without H-mode.",(2024,12,16)),
(31,"31-priyanca-ford-s-q1-founder-update-the-10-mwh-target","Priyanca Ford's Q1 Founder Update","Founder Priyanca Ford's Q1 update on the company's long-run ambitions and program direction.",(2025,2,3)),
(32,"32-formal-introduction-of-the-metro-volt-urban-generator","Formal Introduction of the MetroVolt Urban Generator","Kronos formally introduces MetroVolt, its commercial urban fusion generator.",(2025,3,3)),
(33,"33-the-aegis-system-for-modular-defense-applications","The AEGIS System for Modular Defense Applications","Kronos unveils AEGIS, a hardened, modular generator line for defense, remote, and critical-infrastructure missions.",(2025,4,1)),
(34,"34-the-5-channel-direct-energy-conversion-dec-blueprint","The 5-Channel Direct Energy Conversion (DEC) Blueprint","Kronos publishes the complete engineering blueprint for its 5-channel Direct Energy Conversion system.",(2025,5,1)),
(35,"35-channel-1-2-electrostatic-and-mhd-extraction-maturation","Channel 1 & 2: Electrostatic and MHD Extraction Maturation","DEC Channels 1 and 2 - electrostatic retarding-field and MHD extraction - mature through 2025 engineering.",(2025,6,2)),
(36,"36-channel-3-4-thermionic-and-photovoltaic-energy-capture","Channel 3 & 4: Thermionic and Photovoltaic Energy Capture","DEC Channels 3 and 4 - thermionic emission and photovoltaic capture - finalize designs to harvest surface heat and radiation.",(2025,7,1)),
(37,"37-expansion-of-the-simulation-suite-to-12-modules","Expansion of the Simulation Suite to 12 Modules","The Kronos AI simulation suite expands to twelve interoperable modules spanning magnets, plasma, and balance-of-plant.",(2025,8,1)),
(38,"38-the-3-stage-fuel-cycle-strategy-solidified","The Staged Fuel Cycle Strategy Solidified","Kronos solidifies its staged fuel-cycle strategy, bridging near-term commissioning toward low-neutron D-3He operation.",(2025,9,1)),
(40,"40-the-autonomous-ai-immune-system-operationalized","The Autonomous AI Stability System Detailed","Kronos details the design of its autonomous AI stability ('immune') system for real-time plasma control.",(2025,11,3)),
(41,"41-entering-the-pre-commercial-validation-stage","Entering the Pre-Commercial Validation Stage","Kronos transitions out of conceptual R&D into the pre-commercial validation stage for the S.M.A.R.T. generator family.",(2026,1,6)),
(42,"42-the-2026-tech-audit-presentation-delivered","The 2026 Tech Audit Presentation Delivered","Kronos delivers its 2026 Tech Audit - a full disclosure of generator physics and engineering.",(2026,1,27)),
(43,"43-30-tesla-on-axis-field-conductor-survivability-confirmed","24.6 T Peak Conductor Field: Survivability Analyzed","The 2026 audit analyzes REBCO HTS magnet conductor survivability at the 24.6 T peak conductor field — just above the 24.4 T demonstrated single-coil, with a 1.59× strain margin.",(2026,2,17)),
(44,"44-1d-thermal-gradient-and-vacuum-vessel-structural-analysis-published","1-D Thermal Gradient and Vacuum Vessel Structural Analysis Published","Kronos publishes its 1-D thermal-gradient (1700 C plasma edge) data and full vacuum-vessel structural analysis.",(2026,3,10)),
(45,"45-the-20k-closed-cycle-cryogenic-network-design-locked","The 20 K Closed-Cycle Cryogenic Network Design Locked","Kronos locks the design of its 20 K closed-cycle cryogenic network, eliminating liquid-helium infrastructure from the balance-of-plant.",(2026,3,31)),
(46,"46-active-blanket-architecture-and-tritium-multiplier-validation","Center-Stack Neutron Shield and Fluence Budget Analyzed","2026 simulation campaigns analyze the shielded center-stack neutron-fluence budget for the low-neutron design — no breeding blanket required.",(2026,4,21)),
(47,"47-microsecond-ai-control-overcomes-vertical-displacement-events","Microsecond AI Control Modeled for Vertical Displacement Events","Simulations show the microsecond AI digital twin can mitigate vertical displacement events (VDEs) in the design.",(2026,5,12)),
(48,"48-modular-manufacturing-logistics-finalized","Modular Manufacturing Logistics Finalized","Kronos finalizes the modular-manufacturing logistics behind its S.M.A.R.T. generator family.",(2026,6,2)),
(49,"49-load-following-capability-validated-for-grid-integration","Load-Following Capability Modeled for Grid Integration","Kronos models load-following capability for grid integration in its design point, ahead of the gated program.",(2026,6,23)),
(50,"50-the-horizon-finalizing-vendor-contracts-for-physical-construction","The Horizon: Toward Gate-Stage Hardware","As 2026 closes, Kronos looks ahead to its gated program — engaging vendors and the supply chain on the path from a validated design toward first hardware.",(2026,7,10)),
(51,"51-kodex-35-open-source-ai-ml-fusion-codes-released","KODEX — 35 Open-Source AI/ML Fusion Codes Released","Kronos releases KODEX, the Kronos Family of Codes — 35 benchmarked, open-source AI/ML surrogate and quantum codes spanning turbulence and transport, magnets and quench, neutronics, materials, control, and fuel cycle. Every one is trained and tested on open data with fixed seeds and calibrated uncertainty, and knows when to abstain. Install with pip install kronos-fusion-ml.",(2026,9,10)),
(52,"52-115-open-papers-permanently-archived-with-dois","115 Open Papers Permanently Archived with DOIs","Kronos publishes its complete open corpus — 115 open-access papers across the Hyperion breeder and the Aegis/MetroVolt generator, each with a permanent DOI and mirrored across Zenodo, OSF, Figshare, and the Internet Archive. Written to be refereed; the flagship series is in submission for peer review.",(2026,9,11)),
(53,"53-245-gate-de-risking-register-and-cgyro-confinement-map","245-Gate De-Risking Register and CGYRO Confinement Map","Kronos posts a 245-gate physics de-risking register spanning the breeder and both burners, alongside a CGYRO gyrokinetic campaign that closes a 16-point confinement map at real electron mass — confirming negative triangularity suppresses turbulent transport at the breeder operating point (DOI 10.5281/zenodo.22136279).",(2026,9,12)),
]

def dt_for(ymd):
    y,m,d = ymd
    off = -7 if 3 <= m <= 10 else -8   # PDT vs PST, approximate
    return datetime(y,m,d,9,0,0, tzinfo=timezone(timedelta(hours=off)))

# newest first
items_sorted = sorted(ITEMS, key=lambda it: dt_for(it[4]), reverse=True)
build_dt = datetime(2026,9,13,9,0,0, tzinfo=timezone(timedelta(hours=-7)))

# ---------- RSS ----------
parts = []
parts.append('<?xml version="1.0" encoding="UTF-8"?>')
parts.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
parts.append('  <channel>')
parts.append('    <title>Kronos Fusion Energy — News</title>')
parts.append(f'    <link>{BASE}/news</link>')
parts.append('    <description>Chronological dossier and news briefings from Kronos Fusion Energy — leadership, S.M.A.R.T. architecture, digital twin, direct energy conversion, and supply-chain milestones.</description>')
parts.append('    <language>en-us</language>')
parts.append('    <copyright>© 2026 Kronos Fusion Energy</copyright>')
parts.append(f'    <lastBuildDate>{format_datetime(build_dt)}</lastBuildDate>')
parts.append(f'    <pubDate>{format_datetime(dt_for(items_sorted[0][4]))}</pubDate>')
parts.append('    <ttl>60</ttl>')
parts.append('    <generator>Kronos build_rss.py</generator>')
parts.append('    <docs>https://www.rssboard.org/rss-specification</docs>')
parts.append('    <category>Fusion Energy</category>')
parts.append('    <category>Clean Energy</category>')
parts.append(f'    <atom:link href="{BASE}/rss.xml" rel="self" type="application/rss+xml"/>')
parts.append('    <image>')
parts.append(f'      <url>{escape(LOGO_URL)}</url>')
parts.append('      <title>Kronos Fusion Energy — News</title>')
parts.append(f'      <link>{BASE}/news</link>')
parts.append('    </image>')
for num,slug,title,desc,ymd in items_sorted:
    url = f"{BASE}/news/{slug}"
    parts.append('    <item>')
    parts.append(f'      <title>{escape(title)}</title>')
    parts.append(f'      <link>{escape(url)}</link>')
    parts.append(f'      <guid isPermaLink="true">{escape(url)}</guid>')
    parts.append(f'      <pubDate>{format_datetime(dt_for(ymd))}</pubDate>')
    parts.append(f'      <description>{escape(desc)}</description>')
    parts.append('    </item>')
parts.append('  </channel>')
parts.append('</rss>')
rss = "\n".join(parts) + "\n"

rss_path = os.path.join(OUTDIR, "rss.xml")
with open(rss_path, "w", encoding="utf-8") as f:
    f.write(rss)

# validate well-formedness
import xml.dom.minidom as minidom
minidom.parseString(rss.encode("utf-8"))
print("RSS written & well-formed:", rss_path, "| items:", len(items_sorted))

# ---------- News sitemaps ----------
# (a) Regular sitemap of all /news URLs — merge into the main site sitemap so Google indexes them.
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for num,slug,title,desc,ymd in items_sorted:
    sm.append(f'  <url><loc>{BASE}/news/{slug}</loc><lastmod>{dt_for(ymd).date().isoformat()}</lastmod></url>')
sm.append('</urlset>')
open(os.path.join(OUTDIR,"news_sitemap.xml"),"w",encoding="utf-8").write("\n".join(sm)+"\n")

# (b) Google News sitemap — Google News only accepts articles from the LAST 2 DAYS, so backdated
#     items won't appear. This regenerates automatically and will populate when fresh news is added.
now = datetime.now(timezone.utc)
recent = [it for it in items_sorted if (now - dt_for(it[4])).days <= 2]
gn = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">']
for num,slug,title,desc,ymd in recent:
    gn += ['  <url>', f'    <loc>{BASE}/news/{slug}</loc>', '    <news:news>',
           '      <news:publication><news:name>Kronos Fusion Energy — News</news:name><news:language>en</news:language></news:publication>',
           f'      <news:publication_date>{dt_for(ymd).isoformat()}</news:publication_date>',
           f'      <news:title>{escape(title)}</news:title>', '    </news:news>', '  </url>']
gn.append('</urlset>')
open(os.path.join(OUTDIR,"news_google_sitemap.xml"),"w",encoding="utf-8").write("\n".join(gn)+"\n")
print(f"Sitemaps: news_sitemap.xml ({len(items_sorted)} urls) · news_google_sitemap.xml ({len(recent)} recent, ≤2 days)")

# ---------- PDF ----------
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
                                Table, TableStyle, Preformatted)
from reportlab.lib.enums import TA_LEFT

NAVY = colors.HexColor("#12233f"); GOLD = colors.HexColor("#9a6f16")
INK  = colors.HexColor("#101724"); MUT  = colors.HexColor("#5a6472")
LINE = colors.HexColor("#d9dce2"); WASH = colors.HexColor("#f7f6f2")

ss = getSampleStyleSheet()
def S(name,**kw):
    kw.setdefault("fontName","Times-Roman")
    return ParagraphStyle(name, parent=ss["Normal"], **kw)
brand   = S("brand", fontName="Helvetica-Bold", fontSize=9, textColor=NAVY, spaceAfter=2)
eyebrow = S("eyebrow", fontName="Helvetica-Bold", fontSize=8, textColor=GOLD, spaceAfter=6, leading=10)
h1      = S("h1", fontName="Times-Bold", fontSize=22, textColor=INK, leading=25, spaceAfter=6)
lede    = S("lede", fontSize=11, textColor=MUT, leading=15, spaceAfter=10)
yearh   = S("yearh", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceBefore=12, spaceAfter=4)
itmt    = S("itmt", fontName="Times-Bold", fontSize=11.5, textColor=INK, leading=14, spaceAfter=1)
meta    = S("meta", fontName="Helvetica", fontSize=7.5, textColor=GOLD, leading=10, spaceAfter=2)
body    = S("body", fontSize=10, textColor=INK, leading=13.5, spaceAfter=2)
link    = S("link", fontName="Helvetica", fontSize=7.5, textColor=MUT, leading=10, spaceAfter=8)
note    = S("note", fontSize=9.5, textColor=INK, leading=13)
codest  = ParagraphStyle("code", parent=ss["Code"], fontName="Courier", fontSize=6.4, leading=7.6, textColor=colors.HexColor("#26303f"))

pdf_path = os.path.join(OUTDIR, "Kronos News RSS Feed (2023-2026).pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=LETTER,
    leftMargin=0.9*inch, rightMargin=0.9*inch, topMargin=0.8*inch, bottomMargin=0.7*inch,
    title="Kronos Fusion Energy — News RSS Feed")
F = []
F.append(Paragraph("KRONOS FUSION ENERGY", brand))
F.append(HRFlowable(width="100%", thickness=1.4, color=NAVY, spaceAfter=10))
F.append(Paragraph("RSS FEED · REFERENCE COPY · 13 JUL 2026", eyebrow))
F.append(Paragraph("Kronos News Feed — rss.xml", h1))
F.append(Paragraph("A syndicatable RSS 2.0 feed of the Kronos news dossier, backdated across 2023–2026 "
    "(40 briefings). This PDF is a human-readable reference; the live feed is the file <b>rss.xml</b>, "
    "served at <b>https://www.kronosfusionenergy.com/rss.xml</b>.", lede))

# how-to box
how = [[Paragraph("<b>How to publish</b>  Drop <b>rss.xml</b> into your Lovable <b>public/</b> folder so it serves at "
    "<b>/rss.xml</b> (feed readers fetch raw XML — it cannot be a React route). Add a &lt;link rel=\"alternate\" "
    "type=\"application/rss+xml\" href=\"/rss.xml\"&gt; in the &lt;head&gt; and an RSS link in the footer. "
    "Validate at validator.w3.org/feed.", note)]]
t = Table(how, colWidths=[6.7*inch])
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),WASH),("BOX",(0,0),(-1,-1),0.5,LINE),
    ("LINEBEFORE",(0,0),(0,-1),2,GOLD),("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
    ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
F.append(t); F.append(Spacer(1,14))

cur_year = None
for num,slug,title,desc,ymd in items_sorted:
    y = ymd[0]
    if y != cur_year:
        cur_year = y
        F.append(Paragraph(str(y), yearh))
        F.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=6))
    dstr = dt_for(ymd).strftime("%d %b %Y").upper()
    F.append(Paragraph(f"#{num:02d} · {dstr}", meta))
    F.append(Paragraph(title.replace("&","&amp;"), itmt))
    F.append(Paragraph(desc.replace("&","&amp;"), body))
    F.append(Paragraph(f"{BASE}/news/{slug}", link))

# raw XML appendix
from reportlab.platypus import PageBreak
F.append(PageBreak())
F.append(Paragraph("APPENDIX — RAW rss.xml", eyebrow))
F.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=8))
for line in rss.split("\n"):
    F.append(Preformatted(line if line.strip() else " ", codest))

doc.build(F)
print("PDF written:", pdf_path)
