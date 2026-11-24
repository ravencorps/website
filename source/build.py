"""Build the Raven Corps website.

Run it from anywhere: python3 source/build.py

Every file in source/pages (and its subfolders) is one page. It starts with a
<!--meta {json} meta--> block: path, title, description, type and any structured
content (faq, steps, sources, event). The build wraps each page in the shared
header and footer, adds structured data (JSON-LD) for search engines and AI
assistants, and writes <path>/index.html at the top of the repo. It also writes sitemap.xml,
robots.txt, llms.txt and vercel.json.
"""
import html
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
SITE = "https://ravencorps.co.uk"
UPDATED = "2026-11-24"

css = (SRC / "style.css").read_text()

NAV = [
    ("/meetups/", "Meetups"),
    ("/skills/", "Skills guides"),
    ("/start-a-chapter/", "Start a chapter"),
    ("/faq/", "FAQ"),
    ("/about/", "About"),
]

ORG = {
    "@type": "Organization",
    "@id": SITE + "/#org",
    "name": "Raven Corps",
    "url": SITE + "/",
    "logo": SITE + "/assets/raven-corps-logo.png",
    "email": "hq@ravencorps.co.uk",
    "slogan": "Ready for anything",
    "sameAs": ["https://www.facebook.com/ravencorpsglobal/"],
    "areaServed": "United Kingdom",
    "description": ("A community group, started in Frodsham, Cheshire, for adults who want real-world skills: "
                    "map and compass, bushcraft, first aid, fitness and being ready for emergencies."),
}

faces = []
for fam, file, weight in [
    ("Barlow Condensed", "barlow-condensed-latin-600-normal", 600),
    ("Barlow Condensed", "barlow-condensed-latin-700-normal", 700),
    ("Barlow", "barlow-latin-400-normal", 400),
    ("Barlow", "barlow-latin-500-normal", 500),
    ("Barlow", "barlow-latin-600-normal", 600),
    ("IBM Plex Mono", "ibm-plex-mono-latin-400-normal", 400),
    ("IBM Plex Mono", "ibm-plex-mono-latin-500-normal", 500),
]:
    faces.append(
        f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{weight};font-display:swap;'
        f'src:url("/fonts/{file}.woff2") format("woff2");}}'
    )
font_css = "\n".join(faces)


def esc(s):
    return html.escape(s, quote=True)


def nav_links(path):
    out = []
    for href, label in NAV:
        cur = ' aria-current="page"' if path.startswith(href) else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return "\n        ".join(out)


def header(path):
    links = nav_links(path)
    return f"""<header class="topbar">
  <div class="wrap topbar-in">
    <a class="brand" href="/" aria-label="Raven Corps home">
      <img src="/assets/raven-corps-logo.png" alt="" width="32" height="40">
      <span>Raven Corps</span>
    </a>
    <nav class="nav" aria-label="Main">
        {links}
    </nav>
    <a class="btn btn-small" data-signup href="/#signup">Sign up</a>
    <details class="menu">
      <summary>Menu</summary>
      <nav aria-label="Main menu">
        {links}
        <a href="/#signup">Sign up</a>
      </nav>
    </details>
  </div>
</header>"""


FOOTER = """<footer class="foot">
  <div class="wrap foot-in">
    <div class="foot-brand">
      <img src="/assets/raven-corps-logo.png" alt="" width="28" height="35">
      <div>
        <strong>Raven Corps</strong>
        <span>Ready for anything</span>
      </div>
    </div>
    <nav class="foot-links" aria-label="Footer">
      <a href="/meetups/">Meetups</a>
      <a href="/skills/">Skills guides</a>
      <a href="/start-a-chapter/">Start a chapter</a>
      <a href="/faq/">FAQ</a>
      <a href="/about/">About</a>
    </nav>
    <p>Frodsham, Cheshire · <span class="mail">hq@ravencorps.co.uk</span></p>
    <p class="social"><a href="https://www.facebook.com/ravencorpsglobal/" target="_blank" rel="noopener">Facebook</a></p>
    <p class="small">© 2026 Raven Corps</p>
  </div>
</footer>"""


def crumbs_html(crumbs):
    if not crumbs:
        return ""
    items = []
    for i, (name, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            items.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            items.append(f'<li><a href="{href}">{esc(name)}</a></li>')
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(items) + "</ol></nav>"


def faq_html(faq):
    parts = ['<div class="faq">']
    for q, a in faq:
        parts.append(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{a}</p></div>')
    parts.append("</div>")
    return "\n".join(parts)


def steps_html(steps):
    parts = ['<ol class="steps">']
    for name, text in steps:
        parts.append(f"<li><h3>{esc(name)}</h3><p>{text}</p></li>")
    parts.append("</ol>")
    return "\n".join(parts)


def sources_html(sources):
    items = "".join(
        f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a></li>' for t, u in sources
    )
    return f'<h2>Sources</h2>\n<ul class="sources">{items}</ul>'


CTA = """<aside class="practise" aria-label="Learn it with us">
  <p class="eyebrow">Learn it with us</p>
  <p class="practise-title">Practise this at a Raven Corps meetup</p>
  <p>Monthly meetups for over-18s near Frodsham, Cheshire. Free for now, and no experience needed.</p>
  <div class="actions">
    <a class="btn" href="/#signup">Sign up</a>
    <a class="btn btn-quiet" href="/meetups/">About the meetups</a>
  </div>
</aside>"""


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def jsonld(meta):
    url = SITE + meta["path"]
    graph = []
    kind = meta.get("type", "page")
    if kind == "home":
        graph.append(ORG)
        graph.append({"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Raven Corps",
                      "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-GB"})
    else:
        graph.append({"@type": "WebPage", "@id": url, "url": url, "name": meta["title"],
                      "description": meta["description"], "inLanguage": "en-GB",
                      "isPartOf": {"@id": SITE + "/#site"}, "publisher": ORG})
    crumbs = meta.get("crumbs")
    if crumbs:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h}
            for i, (n, h) in enumerate(crumbs)]})
    if kind == "guide":
        graph.append({"@type": "Article", "headline": meta["h1"], "description": meta["description"],
                      "datePublished": meta.get("published", UPDATED), "dateModified": meta.get("updated", UPDATED),
                      "author": {"@type": "Organization", "name": "Raven Corps", "url": SITE + "/"},
                      "publisher": {"@type": "Organization", "name": "Raven Corps",
                                    "logo": {"@type": "ImageObject", "url": SITE + "/assets/raven-corps-logo.png"}},
                      "mainEntityOfPage": url, "image": SITE + "/assets/og.png", "inLanguage": "en-GB"})
    if meta.get("steps"):
        graph.append({"@type": "HowTo", "name": meta["h1"], "description": meta["description"],
                      "step": [{"@type": "HowToStep", "position": i + 1, "name": n, "text": strip_tags(t)}
                               for i, (n, t) in enumerate(meta["steps"])]})
    if meta.get("faq"):
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in meta["faq"]]})
    if meta.get("event"):
        graph.append(meta["event"])
    data = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


def render(meta, body):
    path = meta["path"]
    body = body.replace("{{crumbs}}", crumbs_html(meta.get("crumbs")))
    body = body.replace("{{faq}}", faq_html(meta.get("faq", [])))
    body = body.replace("{{steps}}", steps_html(meta.get("steps", [])))
    body = body.replace("{{sources}}", sources_html(meta.get("sources", [])))
    body = body.replace("{{cta}}", CTA)
    left = re.findall(r"\{\{\w+\}\}", body)
    assert not left, f"{path}: unfilled placeholders {left}"
    url = SITE + path
    og_title = meta.get("og_title", meta["title"])
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(meta["title"])}</title>
<meta name="description" content="{esc(meta["description"])}">
<meta name="theme-color" content="#eceee7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11130f" media="(prefers-color-scheme: dark)">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{'article' if meta.get('type') == 'guide' else 'website'}">
<meta property="og:site_name" content="Raven Corps">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(meta["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/barlow-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/barlow-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
{font_css}
{css}
</style>
<script type="application/ld+json">
{jsonld(meta)}
</script>
</head>
<body>
{header(path)}
{body.strip()}
{FOOTER}
</body>
</html>
"""


pages = []
for f in sorted((SRC / "pages").rglob("*.html")):
    text = f.read_text()
    m = re.match(r"<!--meta\s*(\{.*?\})\s*meta-->\s*", text, re.S)
    assert m, f"{f} has no meta block"
    meta = json.loads(m.group(1))
    body = text[m.end():]
    out = OUT / meta["path"].strip("/") / "index.html" if meta["path"] != "/" else OUT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(meta, body))
    pages.append(meta)

# sitemap.xml
urls = "\n".join(
    f"  <url><loc>{SITE}{p['path']}</loc><lastmod>{p.get('updated', UPDATED)}</lastmod></url>"
    for p in sorted(pages, key=lambda p: (p["path"] != "/", p["path"])))
(OUT / "sitemap.xml").write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')

(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

# llms.txt: a plain index of the site for AI assistants (llmstxt.org format)
def line(p):
    return f"- [{p.get('llms_title', p['title'])}]({SITE}{p['path']}): {p['description']}"

core = [p for p in pages if p.get("type") not in ("guide",) and p["path"] != "/"]
guides = [p for p in pages if p.get("type") == "guide"]
llms = ["# Raven Corps", "",
        "> " + ORG["description"] + " Monthly meetups near Frodsham start on Saturday 23 January 2027; "
        "they are free for now. Chapters in other UK towns will follow once Frodsham is running well.", "",
        "Contact: hq@ravencorps.co.uk. Sign up: " + SITE + "/#signup", "",
        "## About Raven Corps", ""] + [line(p) for p in core] + ["", "## Skills guides", ""] + [line(p) for p in guides]
(OUT / "llms.txt").write_text("\n".join(llms) + "\n")

(OUT / "vercel.json").write_text(json.dumps({"trailingSlash": True}, indent=2) + "\n")

print("built", len(pages), "pages:", ", ".join(p["path"] for p in pages))
