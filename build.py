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
import html

# === GA4 Imports (Optional) ===
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
except ImportError:
    BetaAnalyticsDataClient = None
    DateRange = Dimension = Metric = RunReportRequest = None
# =================================

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

def absolute_url(path):
    """Convert a site-relative asset path into a stable absolute URL."""
    if not path:
        return f"{BASE_URL}default.webp"
    if path.startswith(("http://", "https://")):
        return path
    return urllib.parse.urljoin(BASE_URL, path.lstrip("/"))

def published_image_url(path):
    """Use WebP for local SVG article art when the optimized asset exists."""
    if path and not path.startswith(("http://", "https://")) and path.lower().endswith(".svg"):
        path = path[:-4] + ".webp"
    return absolute_url(path)

def slug_from_filename(filename):
    return sanitize_url(os.path.splitext(filename)[0]).lower()

def article_href(category, filename):
    """Return the canonical clean URL path for a generated article."""
    return f"/{category}/{slug_from_filename(filename)}/"

def add_avif_picture(html_content):
    """Wrap the first local WebP article image with an AVIF source and WebP fallback."""
    pattern = r'<p><img alt="([^"]*)" src="([^" ]+\.webp)" /></p>'

    def replacement(match):
        alt_text = html.escape(match.group(1), quote=True)
        webp_url = html.escape(match.group(2), quote=True)
        avif_url = html.escape(match.group(2)[:-5] + ".avif", quote=True)
        return (
            '<p><picture>'
            f'<source type="image/avif" srcset="{avif_url}">'
            f'<img alt="{alt_text}" src="{webp_url}" loading="eager" fetchpriority="high" decoding="async">'
            '</picture></p>'
        )

    return re.sub(pattern, replacement, html_content, count=1, flags=re.IGNORECASE)

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
# GA4 Data Fetch Function (New)
# ==========================================================
def get_ga4_pageviews(property_id):
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if BetaAnalyticsDataClient is None:
        print("⚠️ google-analytics-data package not found! Skipping analytics data.")
        return {}
    if not creds_json:
        print("⚠️ GA4 Credentials not found! Skipping analytics data.")
        return {}

    with open("temp_ga_key.json", "w", encoding="utf-8") as f:
        f.write(creds_json)
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_ga_key.json"
    
    try:
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date="2026-01-01", end_date="today")],
        )
        response = client.run_report(request)
        views_data = {row.dimension_values[0].value: row.metric_values[0].value for row in response.rows}
        return views_data
    except Exception as e:
        print(f"Error fetching GA4 data: {e}")
        return {}
    finally:
        if os.path.exists("temp_ga_key.json"):
            os.remove("temp_ga_key.json")

# ==========================================================
# GenZ Frontier Build Configuration
# ==========================================================
NEWS_DIR = "news"
BASE_URL = "https://www.genzfrontir.com/"
OUTPUT_DIR = "public"
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"
ADS_DIR = "ads"

# ⚠️ GA4 Property ID (Updated) ⚠️
GA4_PROPERTY_ID = "524639425"

# ==========================================================
# 🔴 LIVE TV CONFIGURATION (NEW)
# ==========================================================
IS_LIVE = False
LIVE_VIDEO_URL = "https://www.youtube.com/embed/h7tqrdSOkog"

LIVE_SCRIPT_HTML = f"""
<script>
    window.LIVE_STATUS = {'true' if IS_LIVE else 'false'};
    window.LIVE_URL = '{LIVE_VIDEO_URL}';
</script>
"""
# ==========================================================

DEFAULT_CATEGORIES = ["world", "politics", "business", "tech", "science", "health", "sports", "entertainment", "careers", "legacy-archives","mind-manipulation"]

def clean_and_prepare():
    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, ADS_DIR), exist_ok=True)
    
    # Copy basic files
    for f in ["index.html", "404.html", "contact.html", "about.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html", "CNAME", "sitemap.xml", "robots.txt", "style.css", "favicon.ico"]:
        if os.path.exists(f): shutil.copy2(f, os.path.join(OUTPUT_DIR, f))
    
    # 🚀 FIX: Copy all image files from 'news' directory to 'public/news'
    for root, _, files in os.walk(NEWS_DIR):
        for file in files:
            # Check if the file is an image (handling both lowercase and uppercase extensions)
            if file.lower().endswith(('.svg', '.webp', '.avif', '.jpg', '.jpeg', '.png', '.gif')):
                src_file = os.path.join(root, file)
                dest_dir = os.path.join(OUTPUT_DIR, root) 
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src_file, os.path.join(dest_dir, file))
                
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
    for art in all_arts:
        if art["cat"] == "ads": continue
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

# === Fetch GA4 Data Before Building HTML (New) ===
print("Fetching GA4 Page Views...")
all_page_views = get_ga4_pageviews(GA4_PROPERTY_ID)
# =================================================

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
        output_file = file.replace(".md", ".html")
        clean_path = article_href(cat, output_file)
        art = {
            "title": meta.get("title", [file.replace(".md", "").title()])[0],
            "file": output_file,
            "slug": slug_from_filename(output_file),
            "href": clean_path,
            "cat": cat,
            "desc": meta.get("description", [""])[0],
            "img": published_image_url(meta.get("image", ["/default.webp"])[0]),
            "date": meta.get("date", [get_git_date(os.path.join(root, file)) or datetime.now().isoformat()])[0],
            "url": urllib.parse.urljoin(BASE_URL, clean_path.lstrip("/"))
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
            <a href="{hero_post["href"]}">
                <h1>{hero_post["title"]}</h1>
            </a>
            <p>{hero_post["desc"]}</p>
            <a href="{hero_post["href"]}">
                <img src="{hero_post["img"]}" alt="{hero_post["title"]}" loading="eager" fetchpriority="high" width="1069" height="713" decoding="async">
            </a>
        </div>
        <div class="hero-sidebar hero-sidebar-scroll">
            <div class="section-header"><h2>LIVE UPDATES</h2></div>
'''
    for a in live_updates_posts:
        hero_html += f'''
            <div class="hero-side-item">
                <a href="{a["href"]}">
                    <img src="{a["img"]}" alt="{a["title"]}" loading="lazy" width="80" height="80" decoding="async">
                </a>
                <div>
                    <h3><a href="{a["href"]}">{a["title"]}</a></h3>
                </div>
            </div>
'''
    hero_html += '</div></div></section>'

# 2. Breaking News Ticker
ticker_posts = all_arts[:15]
ticker_items = "".join([f'<span>🔴 <a href="{a["href"]}" class="ticker-link">{a["title"]}</a></span>' for a in ticker_posts])
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
        <a href="{featured_mix["href"]}">
            <img src="{featured_mix["img"]}" alt="{featured_mix["title"]}" loading="lazy" width="800" height="450" decoding="async">
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
                <h3><a href="{a["href"]}">{a["title"]}</a></h3>
            </div>
        </div>
'''
    dyn_html += '</div></div>'

# 5. Category Sections (10 Blocks)
for cat in DEFAULT_CATEGORIES:
    if cat in ["ads"]: continue
    c_posts = sorted(cat_arts[cat], key=lambda x: x["date"], reverse=True)
    if not c_posts: continue
    
    cat_block_html = f'<div class="section-header"><h2>{cat.title()}</h2><a href="/{cat}/" class="see-all">See All →</a></div><div class="grid-featured">'
    featured = c_posts[0]
    cat_block_html += f'''
    <div class="featured-large">
        <a href="{featured["href"]}">
            <img src="{featured["img"]}" alt="{featured["title"]}" loading="lazy" width="800" height="450" decoding="async">
            <div class="overlay">
                <h3>{featured["title"]}</h3>
            </div>
        </a>
    </div>
    <div class="hero-sidebar hero-sidebar-scroll">
'''
    for a in c_posts[1:5]:
        cat_block_html += f'''
        <div class="hero-side-item">
            <div>
                <h3><a href="{a["href"]}">{a["title"]}</a></h3>
            </div>
        </div>
'''
    cat_block_html += '</div></div>'
    dyn_html += cat_block_html

    # Generate Category Index Page
    os.makedirs(os.path.join(OUTPUT_DIR, cat), exist_ok=True)
    cat_grid_html = f'<div class="section-header"><h2>{cat.title()}</h2></div><div class="grid-4">'
    for a in c_posts:
        cat_grid_html += f'''
        <article class="news-card">
            <img src="{a["img"]}" alt="{a["title"]}" loading="lazy" width="400" height="225" decoding="async">
            <a href="{a["href"]}"><h3>{a["title"]}</h3></a>
        </article>'''
    cat_grid_html += '</div>'
    cat_index_content = index_template.replace("{{HERO_SECTION}}", "").replace("{{DYNAMIC_CONTENT}}", cat_grid_html).replace("{{BREAKING_NEWS_TICKER}}", ticker)
    cat_index_content = cat_index_content.replace("{{META_TAGS}}", "").replace("{{SCHEMA_DATA}}", "").replace("{{LIVE_STATUS_SCRIPT}}", LIVE_SCRIPT_HTML)
    with open(os.path.join(OUTPUT_DIR, cat, "index.html"), "w", encoding="utf-8") as f: f.write(cat_index_content)

# Generate Article Pages
for art in all_arts:
    with open(os.path.join(NEWS_DIR, art["cat"], art["file"].replace(".html", ".md")), "r", encoding="utf-8") as f:
        md_content = f.read()
    
    related_candidates = [a for a in cat_arts[art["cat"]] if a["file"] != art["file"]]
    if len(related_candidates) < 4:
        global_recent = [a for a in all_arts if a["file"] != art["file"] and a not in related_candidates]
        related_candidates += global_recent[:(4 - len(related_candidates))]
    
    related_html = '<div class="related-section"><div class="section-header"><h2>Suggested For You</h2></div><div class="grid-4">'
    for r in related_candidates[:4]:
        related_html += f'''
        <article class="news-card">
            <img src="{r["img"]}" alt="{r["title"]}" loading="lazy" width="400" height="225" decoding="async">
            <a href="{r["href"]}"><h3>{r["title"]}</h3></a>
        </article>'''
    related_html += '</div></div>'

    video_url = ""
    iframe_match = re.search(r'<iframe.*?src=["\'](.*?)["\']', md_content, re.IGNORECASE)
    video_tag_match = re.search(r'<video.*?src=["\'](.*?)["\']', md_content, re.IGNORECASE)
    direct_video_match = re.search(r'\[.*?\]\((.*?\.(mp4|webm|ogg))\)', md_content, re.IGNORECASE)
    
    if iframe_match: video_url = iframe_match.group(1)
    elif video_tag_match: video_url = video_tag_match.group(1)
    elif direct_video_match: video_url = direct_video_match.group(1)
    
    if video_url and video_url.startswith("//"): video_url = "https:" + video_url

    safe_title = html.escape(art["title"], quote=True)
    safe_desc = html.escape(art["desc"], quote=True)
    safe_img = html.escape(art["img"], quote=True)
    safe_url = html.escape(art["url"], quote=True)
    meta_tags = f'''
    <meta name="description" content="{safe_desc}">
    <meta property="og:title" content="{safe_title} - GenZ Frontier">
    <meta property="og:description" content="{safe_desc}">
    <meta property="og:image" content="{safe_img}">
    <meta property="og:url" content="{safe_url}">
    <meta name="twitter:card" content="summary_large_image">
    '''
    # Build JSON-LD as a Python object instead of interpolating fragments into a
    # hand-written JSON string. This prevents malformed commas/braces and safely
    # escapes characters that could terminate the script element.
    schema_object = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": art["title"],
        "image": [art["img"]],
        "datePublished": normalize_date(art["date"]),
        "dateModified": normalize_date(art["date"]),
        "author": {"@type": "Organization", "name": "GenZ Frontier"},
        "publisher": {
            "@type": "Organization",
            "name": "GenZ Frontier",
            "url": BASE_URL
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": art["url"]}
    }
    schema_json = json.dumps(schema_object, ensure_ascii=False, separators=(",", ":"))
    schema_json = (schema_json.replace("<", "\\u003c")
                             .replace(">", "\\u003e")
                             .replace("&", "\\u0026"))
    schema_data = f'<script type="application/ld+json">{schema_json}</script>'

    # Convert markdown to HTML
    article_html = md_parser.convert(md_content)
    # Source Markdown may retain historical SVG references; render optimized WebP instead.
    article_html = re.sub(r'(?P<prefix>/news/mind-manipulation/images/[^"\']+)\.svg(?P<suffix>["\'])', r'\g<prefix>.webp\g<suffix>', article_html, flags=re.IGNORECASE)
    article_html = add_avif_picture(article_html)
    
    # Third-party ad scripts can redirect readers through popunder/affiliate flows.
    # Keep the existing ads for other categories, but disable them in this safety-focused cluster.
    ads_enabled = art["cat"] != "mind-manipulation"
    native_banner_html = '''
            <!-- Adsterra Native Banner -->
            <div style="margin-top: 30px; margin-bottom: 20px; text-align: center;">
                <script async="async" data-cfasync="false" src="https://pl30308054.effectivecpmnetwork.com/ec56a821de60d9845e8059349f970dbf/invoke.js"></script>
                <div id="container-ec56a821de60d9845e8059349f970dbf"></div>
            </div>
    ''' if ads_enabled else ""
    article_desktop_ad_html = '''
        <div class="desktop-only-ad" style="margin-top: 20px; text-align: center;">
            <script type="text/javascript">
                atOptions = {
                    'key' : 'b9782458d33b2a813bcaf2fe42023033',
                    'format' : 'iframe',
                    'height' : 600,
                    'width' : 160,
                    'params' : {}
                };
            </script>
            <script type="text/javascript" src="https://www.highperformanceformat.com/b9782458d33b2a813bcaf2fe42023033/invoke.js"></script>
        </div>
    ''' if ads_enabled else ""
    social_bar_html = '<script src="https://pl30308055.effectivecpmnetwork.com/59/2a/2f/592a2f2aee609d98fa5fc89b35dfe700.js"></script>' if ads_enabled else ""
    if "</p>" in article_html:
        article_html = article_html.replace("</p>", "</p>" + native_banner_html, 1)
    else:
        article_html = native_banner_html + article_html

    # === Map Views to Article (New) ===
    article_path = art["href"]
    total_views = all_page_views.get(article_path, "0")
    # ==================================

    final_html = template.replace("{{NEWS_CONTENT}}", article_html).replace("{{ARTICLE_TITLE}}", art["title"]) \
                         .replace("{{BREAKING_NEWS_TICKER}}", ticker).replace("{{VIDEO_URL}}", video_url) \
                         .replace("{{RELATED_POSTS}}", related_html).replace("{{META_TAGS}}", meta_tags).replace("{{SCHEMA_DATA}}", schema_data) \
                         .replace("{{CANONICAL_URL}}", art["url"]) \
                         .replace("{{ARTICLE_DESKTOP_AD}}", article_desktop_ad_html) \
                         .replace("{{SOCIAL_BAR_SCRIPT}}", social_bar_html) \
                         .replace('id="total-views">--', f'id="total-views">{total_views}') \
                         .replace("{{LIVE_STATUS_SCRIPT}}", LIVE_SCRIPT_HTML) # === Inject Live Script ===
    
    article_output_dir = os.path.join(OUTPUT_DIR, art["cat"], art["slug"])
    os.makedirs(article_output_dir, exist_ok=True)
    with open(os.path.join(article_output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(final_html)

    # Preserve old .html URLs while consolidating SEO signals on the clean URL.
    legacy_path = os.path.join(OUTPUT_DIR, art["cat"], art["file"])
    legacy_redirect = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><link rel="canonical" href="{art["url"]}"><meta http-equiv="refresh" content="0; url={art["href"]}"><title>Redirecting…</title></head><body><p>This article moved to <a href="{art["href"]}">{art["url"]}</a>.</p></body></html>'''
    with open(legacy_path, "w", encoding="utf-8") as f:
        f.write(legacy_redirect)

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
    home_html = index_template.replace("{{HERO_SECTION}}", hero_html).replace("{{DYNAMIC_CONTENT}}", dyn_html).replace("{{BREAKING_NEWS_TICKER}}", ticker)
    home_html = home_html.replace("{{META_TAGS}}", "").replace("{{SCHEMA_DATA}}", "").replace("{{LIVE_STATUS_SCRIPT}}", LIVE_SCRIPT_HTML)
    f.write(home_html)

generate_sitemap(all_arts)
print("✅ Build Complete with GA4 Data!")