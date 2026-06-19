import os
import sys
import shutil
import markdown
import json
import re
from datetime import datetime
import subprocess

# ==========================================================
# GenZ Frontier Build Configuration
# ==========================================================
NEWS_DIR = "news"
BASE_URL = "https://www.genzfrontir.com/"
OUTPUT_DIR = "public"
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"
ADS_DIR = "ads"

DEFAULT_CATEGORIES = ["world", "politics", "business", "tech", "science", "health", "sports", "entertainment", "careers", "ads", "legacy-archives"]

def clean_and_prepare():
    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, ADS_DIR), exist_ok=True)
    for f in ["index.html", "404.html", "contact.html", "about.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html", "CNAME", "sitemap.xml", "robots.txt"]:
        if os.path.exists(f): shutil.copy2(f, os.path.join(OUTPUT_DIR, f))
    
    # Copy legacy-archives folder (prioritize root legacy-archives, then news/legacy-archives)
    if os.path.exists("legacy-archives"):
        shutil.copytree("legacy-archives", os.path.join(OUTPUT_DIR, "legacy-archives"), dirs_exist_ok=True)
    elif os.path.exists(os.path.join(NEWS_DIR, "legacy-archives")):
        shutil.copytree(os.path.join(NEWS_DIR, "legacy-archives"), os.path.join(OUTPUT_DIR, "legacy-archives"), dirs_exist_ok=True)

def get_ticker_html(breaking_arts):
    if not breaking_arts: return ""
    items = "".join([f'<span>🔴 <a href="/{a["cat"]}/{a["file"]}" style="color: white; text-decoration: none;">{a["title"]}</a></span>' for a in breaking_arts])
    return f'<div class="breaking-news-ticker"><div class="breaking-label">BREAKING</div><marquee class="breaking-marquee" behavior="scroll" direction="left" onmouseover="this.stop();" onmouseout="this.start();">{items}</marquee></div>'

def get_meta(art):
    return f'<meta name="description" content="{art["desc"]}"><meta property="og:title" content="{art["title"]}"><meta property="og:image" content="{art["img"]}"><meta property="og:url" content="{art["url"]}">'

def get_json_ld(art):
    schema = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": art["title"], "image": [art["img"]], "description": art["desc"]}
    return f'<script type="application/ld+json">{json.dumps(schema)}</script>'

# ==========================================================
# Main Execution
# ==========================================================
clean_and_prepare()
md_parser = markdown.Markdown(extensions=["meta"])
template = open(TEMPLATE_FILE, "r", encoding="utf-8").read()
index_template = open(INDEX_FILE, "r", encoding="utf-8").read()

cat_arts = {cat: [] for cat in DEFAULT_CATEGORIES}
all_arts = []
breaking_arts = []

# Processing Files
for root, _, files in os.walk(NEWS_DIR):
    for file in files:
        if not file.endswith(".md"): continue
        cat = os.path.basename(root)
        if cat not in cat_arts: continue
        
        with open(os.path.join(root, file), "r", encoding="utf-8") as f: txt = f.read()
        html_cont = md_parser.convert(txt)
        meta = md_parser.Meta; md_parser.reset()
        
        art = {
            "title": meta.get('title', [file.replace(".md", "").title()])[0],
            "file": file.replace(".md", ".html"),
            "cat": cat,
            "desc": meta.get('description', [""])[0],
            "img": meta.get('image', [f"{BASE_URL}default.jpg"])[0],
            "date": datetime.now().isoformat(),
            "url": f"{BASE_URL}{cat}/{file.replace('.md', '.html')}"
        }
        cat_arts[cat].append(art)
        all_arts.append(art)
        if meta.get('breaking', [''])[0].lower() == 'true': breaking_arts.append(art)

        # Generate Individual Post
        # Enhanced Related/Suggested News System
        related_arts = [a for a in cat_arts[cat] if a['file'] != art['file']]
        # If not enough in same category, pull from others
        if len(related_arts) < 4:
            other_arts = [a for a in all_arts if a['cat'] != cat and a['file'] != art['file']]
            related_arts += other_arts[:(4 - len(related_arts))]
        
        related_html = '<div class="related-section"><div class="section-header"><h2>Suggested For You</h2></div><div class="grid-4">'
        for r in related_arts[:8]: # Show up to 8 suggested news items
            related_html += f'<article class="news-card"><img src="{r["img"]}"><a href="../{r["cat"]}/{r["file"]}"><h3>{r["title"]}</h3></a></article>'
        related_html += '</div></div>'
        
        final_html = template.replace("{{NEWS_CONTENT}}", html_cont).replace("{{ARTICLE_TITLE}}", art['title']) \
                             .replace("{{RELATED_POSTS}}", related_html).replace("{{META_TAGS}}", get_meta(art)) \
                             .replace("{{SCHEMA_DATA}}", get_json_ld(art)).replace("{{BREAKING_NEWS_TICKER}}", get_ticker_html(breaking_arts)) \
                             .replace("{{CANONICAL_URL}}", art['url'])
        
        os.makedirs(os.path.join(OUTPUT_DIR, cat), exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, cat, art['file']), "w", encoding="utf-8") as f: f.write(final_html)

# Generate Home & Categories
all_arts.sort(key=lambda x: x['date'], reverse=True)
ticker = get_ticker_html(breaking_arts)

# Hero Section
hero_arts = all_arts[:10]
hero_html = f'<section class="hero-section"><div class="hero-container"><div class="hero-main"><span class="red-tag">LIVE UPDATES</span><a href="./{hero_arts[0]["cat"]}/{hero_arts[0]["file"]}"><h1>{hero_arts[0]["title"]}</h1></a><p>{hero_arts[0]["desc"]}</p><a href="./{hero_arts[0]["cat"]}/{hero_arts[0]["file"]}"><img src="{hero_arts[0]["img"]}"></a></div><div class="hero-sidebar hero-sidebar-scroll">'
for a in hero_arts[1:]: hero_html += f'<div class="hero-side-item"><a href="./{a["cat"]}/{a["file"]}"><img src="{a["img"]}"></a><div><h3>{a["title"]}</h3></div></div>'
hero_html += '</div></div></section>'

# Dynamic Content
dyn_html = '<div class="section-header"><h2>Latest Mix</h2></div><div class="grid-4">'
for a in all_arts[:12]: dyn_html += f'<article class="news-card"><img src="{a["img"]}"><a href="./{a["cat"]}/{a["file"]}"><h3>{a["title"]}</h3></a></article>'
dyn_html += '</div>'

for cat in DEFAULT_CATEGORIES:
    arts = sorted(cat_arts[cat], key=lambda x: x['date'], reverse=True)
    cat_index_html = index_template.replace("{{HERO_SECTION}}", "").replace("{{DYNAMIC_CONTENT}}", f'<div class="section-header"><h2>{cat.title()}</h2></div><div class="grid-4">' + "".join([f'<article class="news-card"><img src="{a["img"]}"><a href="../{a["cat"]}/{a["file"]}"><h3>{a["title"]}</h3></a></article>' for a in arts]) + '</div>').replace("{{BREAKING_NEWS_TICKER}}", ticker)
    with open(os.path.join(OUTPUT_DIR, cat, "index.html"), "w", encoding="utf-8") as f: f.write(cat_index_html.replace('href="./', 'href="../'))
    
    limit = 2 if cat == 'ads' else 10
    dyn_html += f'<div class="section-header"><h2>{cat.title()}</h2><a href="./{cat}/" class="see-all">See All →</a></div><div class="grid-4">'
    for a in arts[:limit]: dyn_html += f'<article class="news-card"><img src="{a["img"]}"><a href="./{cat}/{a["file"]}"><h3>{a["title"]}</h3></a></article>'
    dyn_html += '</div>'

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
    f.write(index_template.replace("{{HERO_SECTION}}", hero_html).replace("{{DYNAMIC_CONTENT}}", dyn_html).replace("{{BREAKING_NEWS_TICKER}}", ticker))

# Run Sitemap Generator
print("Generating Sitemap...")
try:
    subprocess.run(["python3", "sitemap_generator.py"], check=True)
except Exception as e:
    print(f"❌ Sitemap generation failed: {e}")

print("✅ Build Complete!")