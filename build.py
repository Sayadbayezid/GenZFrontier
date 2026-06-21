import os
import sys
import shutil
import markdown
import json
import re
from datetime import datetime
import subprocess
import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib.parse

def get_git_date(file_path):
    """Fetches the last commit date for a given file from Git history."""
    try:
        git_date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", file_path],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        if git_date:
            return git_date
    except Exception:
        pass
    return None

def sanitize_url(url):
    return url.replace(' ', '-').replace('#', '').replace('"', '').replace("'", "")

def normalize_date(date_str):
    if not date_str: return datetime.now().strftime("%Y-%m-%d")
    try:
        if "T" in date_str: return date_str.split("T")[0]
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y", "%d %B %Y"):
            try: return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except: continue
        return date_str
    except: return datetime.now().strftime("%Y-%m-%d")

# ==========================================================
# GenZ Frontier Build Configuration
# ==========================================================
NEWS_DIR = "news"
BASE_URL = "https://www.genzfrontir.com/"
OUTPUT_DIR = "public"
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"
ADS_DIR = "ads"

DEFAULT_CATEGORIES = ["world", "politics", "business", "tech", "science", "health", "sports", "entertainment", "careers", "legacy-archives"]

def clean_and_prepare():
    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, ADS_DIR), exist_ok=True)
    for f in ["index.html", "404.html", "contact.html", "about.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html", "CNAME", "sitemap.xml", "robots.txt", "style.css", "favicon.ico"]:
        if os.path.exists(f): shutil.copy2(f, os.path.join(OUTPUT_DIR, f))
    
    # Handle Legacy Archives
    legacy_src = "legacy-archives"
    if os.path.exists(legacy_src):
        shutil.copytree(legacy_src, os.path.join(OUTPUT_DIR, "legacy-archives"), dirs_exist_ok=True)

def generate_sitemap(articles):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    added_links = set()
    static_pages = ["", "about.html", "contact.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html"]
    for page in static_pages:
        full_url = f"{BASE_URL}{page}"
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = full_url
        ET.SubElement(url_elem, "lastmod").text = normalize_date(get_git_date(page))
        ET.SubElement(url_elem, "priority").text = "1.0" if page == "" else "0.8"
        added_links.add(full_url)
    for art in articles:
        if art["url"] not in added_links:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = art["url"]
            ET.SubElement(url_elem, "lastmod").text = normalize_date(art["date"])
            ET.SubElement(url_elem, "priority").text = "0.6"
            added_links.add(art["url"])
    xml_str = ET.tostring(urlset, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f: f.write(pretty_xml)
    shutil.copy2(os.path.join(OUTPUT_DIR, "sitemap.xml"), "sitemap.xml")

# ==========================================================
# Main Execution
# ==========================================================
clean_and_prepare()
md_parser = markdown.Markdown(extensions=["meta"])
template = open(TEMPLATE_FILE, "r", encoding="utf-8").read()
index_template = open(INDEX_FILE, "r", encoding="utf-8").read()

cat_arts = {cat: [] for cat in DEFAULT_CATEGORIES}
all_arts = []

for root, _, files in os.walk(NEWS_DIR):
    for file in files:
        if not file.endswith(".md"): continue
        cat = os.path.basename(root)
        if cat not in cat_arts: continue
        with open(os.path.join(root, file), "r", encoding="utf-8") as f: txt = f.read()
        md_parser.convert(txt)
        meta = md_parser.Meta; md_parser.reset()
        art = {
            "title": meta.get("title", [file.replace(".md", "").title()])[0],
            "file": file.replace(".md", ".html"),
            "cat": cat,
            "desc": meta.get("description", [""])[0],
            "img": meta.get("image", [f"{BASE_URL}default.jpg"])[0],
            "date": meta.get("date", [get_git_date(os.path.join(root, file)) or datetime.now().isoformat()])[0],
            "url": f"{BASE_URL}{cat}/{sanitize_url(file.replace('.md', '.html'))}"
        }
        cat_arts[cat].append(art)
        all_arts.append(art)

all_arts.sort(key=lambda x: x["date"], reverse=True)

# 1. Hero Section & 3. Live Update Section
hero_post = all_arts[0] if all_arts else None
live_updates_posts = all_arts[:15]
hero_html = ""
if hero_post:
    hero_html = f'''
<section class="hero-section">
    <div class="hero-container">
        <div class="hero-main">
            <span class="red-tag">LATEST NEWS</span>
            <a href="/{hero_post["cat"]}/{hero_post["file"]}">
                <h1>{hero_post["title"]}</h1>
            </a>
            <p>{hero_post["desc"]}</p>
            <a href="/{hero_post["cat"]}/{hero_post["file"]}">
                <img src="{hero_post["img"]}" alt="{hero_post["title"]}" loading="eager" fetchpriority="high">
            </a>
        </div>
        <div class="hero-sidebar hero-sidebar-scroll">
            <div class="section-header"><h2>LIVE UPDATES</h2></div>
'''
    for a in live_updates_posts:
        hero_html += f'''
            <div class="hero-side-item">
                <a href="/{a["cat"]}/{a["file"]}">
                    <img src="{a["img"]}" alt="{a["title"]}" loading="lazy">
                </a>
                <div>
                    <h3><a href="/{a["cat"]}/{a["file"]}">{a["title"]}</a></h3>
                </div>
            </div>
'''
    hero_html += '</div></div></section>'

# 2. Breaking News Ticker
ticker_posts = all_arts[:15]
ticker_items = "".join([f'<span>🔴 <a href="/{a["cat"]}/{a["file"]}" style="color: white; text-decoration: none;">{a["title"]}</a></span>' for a in ticker_posts])
ticker = f'<div class="breaking-news-ticker"><div class="breaking-label">BREAKING</div><marquee class="breaking-marquee" behavior="scroll" direction="left" onmouseover="this.stop();" onmouseout="this.start();">{ticker_items}</marquee></div>'

# 4. Latest Mix Section (BBC Style)
mix_posts = all_arts[:20]
dyn_html = ""
if mix_posts:
    featured_mix = mix_posts[0]
    dyn_html += f'''
<div class="section-header"><h2>Latest Mix</h2></div>
<div class="grid-featured">
    <div class="featured-large">
        <a href="/{featured_mix["cat"]}/{featured_mix["file"]}">
            <img src="{featured_mix["img"]}" alt="{featured_mix["title"]}" loading="lazy">
            <div class="overlay">
                <h3>{featured_mix["title"]}</h3>
            </div>
        </a>
    </div>
    <div class="hero-sidebar hero-sidebar-scroll">
'''
    for a in mix_posts[1:]:
        dyn_html += f'''
        <div class="hero-side-item">
            <div>
                <h3><a href="/{a["cat"]}/{a["file"]}">{a["title"]}</a></h3>
            </div>
        </div>
'''
    dyn_html += '</div></div>'

# 5. Category Sections (10 Blocks)
for cat in DEFAULT_CATEGORIES:
    if cat in ["ads", "legacy-archives"]: continue
    c_posts = sorted(cat_arts[cat], key=lambda x: x["date"], reverse=True)[:5]
    if not c_posts: continue
    
    cat_html = f'<div class="section-header"><h2>{cat.title()}</h2><a href="/{cat}/" class="see-all">See All →</a></div><div class="grid-featured">'
    featured = c_posts[0]
    cat_html += f'''
    <div class="featured-large">
        <a href="/{featured["cat"]}/{featured["file"]}">
            <img src="{featured["img"]}" alt="{featured["title"]}" loading="lazy">
            <div class="overlay">
                <h3>{featured["title"]}</h3>
            </div>
        </a>
    </div>
    <div class="hero-sidebar hero-sidebar-scroll">
'''
    for a in c_posts[1:]:
        cat_html += f'''
        <div class="hero-side-item">
            <div>
                <h3><a href="/{a["cat"]}/{a["file"]}">{a["title"]}</a></h3>
            </div>
        </div>
'''
    cat_html += '</div></div>'
    dyn_html += cat_html

# Generate Pages
for art in all_arts:
    with open(os.path.join(NEWS_DIR, art["cat"], art["file"].replace(".html", ".md")), "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # 1. Related Posts Fetching (4 posts, same category preferred)
    related_candidates = [a for a in cat_arts[art["cat"]] if a["file"] != art["file"]]
    if len(related_candidates) < 4:
        global_recent = [a for a in all_arts if a["file"] != art["file"] and a not in related_candidates]
        related_candidates += global_recent[:(4 - len(related_candidates))]
    
    related_html = '<div class="related-section"><div class="section-header"><h2>Suggested For You</h2></div><div class="grid-4">'
    for r in related_candidates[:4]:
        related_html += f'''
        <article class="news-card">
            <img src="{r["img"]}" alt="{r["title"]}" loading="lazy">
            <a href="/{r["cat"]}/{r["file"]}"><h3>{r["title"]}</h3></a>
        </article>'''
    related_html += '</div></div>'

    video_url = ""
    iframe_match = re.search(r'<iframe.*?src=["\"](.*?)["\"]', md_content)
    if iframe_match: video_url = iframe_match.group(1)

    final_html = template.replace("{{NEWS_CONTENT}}", md_parser.convert(md_content)).replace("{{ARTICLE_TITLE}}", art["title"]) \
                         .replace("{{BREAKING_NEWS_TICKER}}", ticker).replace("{{VIDEO_URL}}", video_url) \
                         .replace("{{RELATED_POSTS}}", related_html)
    
    os.makedirs(os.path.join(OUTPUT_DIR, art["cat"]), exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, art["cat"], art["file"]), "w", encoding="utf-8") as f: f.write(final_html)

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
    f.write(index_template.replace("{{HERO_SECTION}}", hero_html).replace("{{DYNAMIC_CONTENT}}", dyn_html).replace("{{BREAKING_NEWS_TICKER}}", ticker))

generate_sitemap(all_arts)
print("✅ Build Complete!")
