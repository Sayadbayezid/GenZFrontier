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

def extract_video_url(html_content):
    """Extracts the first video URL from iframe or video tags in HTML content."""
    # Regex for iframe src
    iframe_match = re.search(r'<iframe[^>]+src=["\"](https?:\/\/[^"\\]+)["\"]', html_content, re.IGNORECASE)
    if iframe_match: return iframe_match.group(1)

    # Regex for video src
    video_match = re.search(r'<video[^>]+src=["\"](https?:\/\/[^"\\]+)["\"]', html_content, re.IGNORECASE)
    if video_match: return video_match.group(1)

    return None

def sanitize_url(url):
    """Removes or encodes invalid characters from URLs for sitemap compliance."""
    # Remove # and anything after it (fragment identifiers are invalid in sitemaps)
    url = re.sub(r'#[^/]*', '', url)
    # Remove leading/trailing spaces in path segments
    url = '/'.join(part.strip() for part in url.split('/'))
    # Collapse multiple slashes (except after protocol)
    url = re.sub(r'(?<!:)//', '/', url)
    return url.strip()

def normalize_date(date_str):
    """Normalizes various date formats to ISO 8601 YYYY-MM-DD for sitemap compliance."""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    # Already ISO 8601 with time — strip to date part
    iso_match = re.match(r'(\d{4}-\d{2}-\d{2})', str(date_str))
    if iso_match:
        return iso_match.group(1)
    # Try common human-readable formats
    for fmt in ["%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(str(date_str).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Fallback
    return datetime.now().strftime("%Y-%m-%d")

def get_git_date(file_path):
    """Fetches the last commit date for a given file from Git history."""
    try:
        # Get the last commit date in ISO 8601 format (e.g., 2023-10-27T10:00:00+05:30)
        git_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cI', file_path],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        if git_date:
            return git_date
    except Exception:
        pass
    return None


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
    legacy_src = "legacy-archives" if os.path.exists("legacy-archives") else os.path.join(NEWS_DIR, "legacy-archives")
    if os.path.exists(legacy_src):
        shutil.copytree(legacy_src, os.path.join(OUTPUT_DIR, "legacy-archives"), dirs_exist_ok=True)
        
        # Auto-generate cards for legacy-archives/index.html
        legacy_index_path = os.path.join(OUTPUT_DIR, "legacy-archives", "index.html")
        if os.path.exists(legacy_index_path):
            with open(legacy_index_path, "r", encoding="utf-8") as f:
                legacy_index_content = f.read()
            
            cards_html = ""
            for file in sorted(os.listdir(legacy_src)):
                if file.endswith(".html") and file != "index.html":
                    with open(os.path.join(legacy_src, file), "r", encoding="utf-8") as f:
                        html_content = f.read()
                    
                    # Extract title, image, and description using regex
                    title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
                    title = title_match.group(1).split("|")[0].strip() if title_match else file.replace(".html", "").title()
                    
                    desc_match = re.search(r'<meta name="description" content="(.*?)">', html_content, re.IGNORECASE)
                    desc = desc_match.group(1).strip() if desc_match else "আর্কাইভের বিস্তারিত দেখতে ক্লিক করুন।"
                    
                    img_match = re.search(r'image": "(.*?)"', html_content, re.IGNORECASE)
                    if not img_match:
                        img_match = re.search(r'background-image: url\(\\'(.*?)\\'\)', html_content, re.IGNORECASE)
                    if not img_match:
                        img_match = re.search(r'<img src="(.*?)"', html_content, re.IGNORECASE)
                    
                    img_url = img_match.group(1) if img_match else "https://www.genzfrontir.com/default.jpg"
                    
                    card_link = file.replace(".html", "")
                    cards_html += f'''
                <a href="/legacy-archives/{card_link}" class="archive-card group block bg-[#0f172a] border border-slate-800 rounded-2xl overflow-hidden relative">
                    <div class="card-img-wrapper h-64 w-full bg-slate-900 relative">
                        <img src="{img_url}" alt="{title}" class="card-img w-full h-full object-cover object-top opacity-70 group-hover:opacity-100 grayscale group-hover:grayscale-0">
                        <div class="absolute inset-0 bg-gradient-to-t from-[#0f172a] to-transparent"></div>
                        <span class="absolute top-4 left-4 bg-red-600/80 text-white text-xs font-bold px-3 py-1 rounded-full bangla-font backdrop-blur-sm">Legacy</span>
                    </div>
                    <div class="p-8">
                        <h3 class="text-2xl font-bold bangla-font text-white mb-3 group-hover:text-cyan-400 transition-colors">{title}</h3>
                        <p class="text-slate-400 bangla-font text-sm leading-relaxed mb-6">{desc}</p>
                        <div class="flex items-center text-cyan-500 font-bold bangla-font text-sm">
                            আর্কাইভ দেখুন <span class="ml-2 transition-transform group-hover:translate-x-2">→</span>
                        </div>
                    </div>
                </a>'''
            
            # Add a "Coming Soon" card at the end
            cards_html += '''
                <div class="archive-card group block bg-[#0f172a] border border-slate-800 border-dashed rounded-2xl overflow-hidden relative cursor-not-allowed">
                    <div class="card-img-wrapper h-64 w-full bg-slate-900/50 flex items-center justify-center relative">
                        <svg class="w-16 h-16 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <div class="absolute inset-0 bg-gradient-to-t from-[#0f172a] to-transparent"></div>
                    </div>
                    <div class="p-8 opacity-60">
                        <h3 class="text-2xl font-bold bangla-font text-slate-500 mb-3">নতুন আর্কাইভ</h3>
                        <p class="text-slate-500 bangla-font text-sm leading-relaxed mb-6">আমাদের গবেষণা ও তথ্য সংগ্রহের কাজ চলমান রয়েছে। খুব শীঘ্রই নতুন আর্কাইভ যুক্ত করা হবে।</p>
                        <div class="flex items-center text-slate-600 font-bold bangla-font text-sm">
                            শীঘ্রই আসছে...
                        </div>
                    </div>
                </div>'''
            
            new_index_content = legacy_index_content.replace("{{LEGACY_CARDS_PLACEHOLDER}}", cards_html)
            with open(legacy_index_path, "w", encoding="utf-8") as f:
                f.write(new_index_content)

def get_ticker_html(breaking_arts):
    if not breaking_arts: return ""
    items = "".join([f'<span>🔴 <a href="/{a["cat"]}/{a["file"]}" style="color: white; text-decoration: none;">{a["title"]}</a></span>' for a in breaking_arts])
    return f'<div class="breaking-news-ticker"><div class="breaking-label">BREAKING</div><marquee class="breaking-marquee" behavior="scroll" direction="left" onmouseover="this.stop();" onmouseout="this.start();">{items}</marquee></div>'

def get_meta(art):
    return f'<meta name="description" content="{art["desc"]}"><meta property="og:title" content="{art["title"]}"><meta property="og:image" content="{art["img"]}"><meta property="og:url" content="{art["url"]}">'

def get_json_ld(art):
    schema = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": art["title"], "image": [art["img"]], "description": art["desc"]}
    return f'<script type="application/ld+json">{json.dumps(schema)}</script>'

def generate_sitemap(articles):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    added_links = set()

    # Add static pages (assuming they are copied to public/)
    static_pages = ["", "about.html", "contact.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html"]
    for page in static_pages:
        full_url = f"{BASE_URL}{page}"
        if full_url not in added_links:
            url_elem = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_elem, "loc")
            loc.text = full_url
            lastmod = ET.SubElement(url_elem, "lastmod")
            # For static pages, use the git date of the file in the root directory
            lastmod.text = normalize_date(get_git_date(page))
            priority = ET.SubElement(url_elem, "priority")
            priority.text = "1.0" if page == "" else "0.8"
            added_links.add(full_url)

    # Add news articles
    for art in articles:
        full_url = art["url"]
        if full_url not in added_links:
            url_elem = ET.SubElement(urlset, "url")
            loc = ET.SubElement(url_elem, "loc")
            loc.text = full_url
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = normalize_date(art["date"])  # Always valid ISO 8601
            priority = ET.SubElement(url_elem, "priority")
            priority.text = "0.6"
            added_links.add(full_url)

    # Convert to standard XML and pretty print
    xml_str = ET.tostring(urlset, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines() if s.strip()])

    # Save to public directory for deployment
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    # Save to root directory to keep it in the main branch
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"✅ Sitemap.xml successfully generated in root and {OUTPUT_DIR} with {len(added_links)} links.")

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
            "date": meta.get("date", [get_git_date(os.path.join(root, file)) or datetime.now().isoformat()])[0],
            "url": sanitize_url(f"{BASE_URL}{cat}/{file.replace('.md', '.html')}"),
            "video_url": extract_video_url(html_cont)
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
            related_html += f'<article class="news-card"><img src="{r["img"]}" alt="{r["title"]}" loading="lazy" decoding="async" width="400" height="225"><a href="../{r["cat"]}/{r["file"]}" aria-label="Read article: {r["title"]}"><h3>{r["title"]}</h3></a></article>'
        related_html += '</div></div>'
        
        final_html = template.replace("{{NEWS_CONTENT}}", html_cont).replace("{{ARTICLE_TITLE}}", art['title']) \
                             .replace("{{RELATED_POSTS}}", related_html).replace("{{META_TAGS}}", get_meta(art)) \
                             .replace("{{SCHEMA_DATA}}", get_json_ld(art)).replace("{{BREAKING_NEWS_TICKER}}", get_ticker_html(breaking_arts)) \
                             .replace("{{CANONICAL_URL}}", art["url"]) \
                             .replace("{{VIDEO_URL}}", art["video_url"] if art.get("video_url") else "")
        
        os.makedirs(os.path.join(OUTPUT_DIR, cat), exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, cat, art['file']), "w", encoding="utf-8") as f: f.write(final_html)

# Generate Home & Categories
all_arts.sort(key=lambda x: x['date'], reverse=True)
ticker = get_ticker_html(breaking_arts)

# Hero Section
hero_arts = all_arts[:10]
hero_html = f'<section class="hero-section"><div class="hero-container"><div class="hero-main"><span class="red-tag" style="background-color: #CC0000; color: #FFFFFF;">LIVE UPDATES</span><a href="./{hero_arts[0]["cat"]}/{hero_arts[0]["file"]}"><h1>{hero_arts[0]["title"]}</h1></a><p>{hero_arts[0]["desc"]}</p><a href="./{hero_arts[0]["cat"]}/{hero_arts[0]["file"]}" aria-label="Read hero article: {hero_arts[0]["title"]}"><img src="{hero_arts[0]["img"]}" alt="{hero_arts[0]["title"]}" fetchpriority="high" decoding="async" width="800" height="450"></a></div><div class="hero-sidebar hero-sidebar-scroll">'
for a in hero_arts[1:]: hero_html += f'<div class="hero-side-item"><a href="./{a["cat"]}/{a["file"]}" aria-label="Read sidebar article: {a["title"]}"><img src="{a["img"]}" alt="{a["title"]}" loading="lazy" decoding="async" width="120" height="80"></a><div><h2>{a["title"]}</h2></div></div>'
hero_html += '</div></div></section>'

# Dynamic Content
dyn_html = '<div class="section-header"><h2>Latest Mix</h2></div><div class="grid-4">'
for a in all_arts[:12]: dyn_html += f'<article class="news-card"><img src="{a["img"]}" alt="{a["title"]}" loading="lazy" decoding="async" width="400" height="225"><a href="./{a["cat"]}/{a["file"]}" aria-label="Read article: {a["title"]}"><h3>{a["title"]}</h3></a></article>'
dyn_html += '</div>'

for cat in DEFAULT_CATEGORIES:
    arts = sorted(cat_arts[cat], key=lambda x: x['date'], reverse=True)
    cat_index_html = index_template.replace("{{HERO_SECTION}}", "").replace("{{DYNAMIC_CONTENT}}", f'<div class="section-header"><h2>{cat.title()}</h2></div><div class="grid-4">' + "".join([f'<article class="news-card"><img src="{a["img"]}" alt="{a["title"]}" loading="lazy" decoding="async" width="400" height="225"><a href="../{a["cat"]}/{a["file"]}" aria-label="Read article: {a["title"]}"><h3>{a["title"]}</h3></a></article>' for a in arts]) + '</div>').replace("{{BREAKING_NEWS_TICKER}}", ticker)
    with open(os.path.join(OUTPUT_DIR, cat, "index.html"), "w", encoding="utf-8") as f: f.write(cat_index_html.replace('href="./', 'href="../'))
    
    limit = 2 if cat == 'ads' else 10
    dyn_html += f'<div class="section-header"><h2>{cat.title()}</h2><a href="./{cat}/" class="see-all">See All →</a></div><div class="grid-4">'
    for a in arts[:limit]: dyn_html += f'<article class="news-card"><img src="{a["img"]}" alt="{a["title"]}" loading="lazy" decoding="async" width="400" height="225"><a href="./{cat}/{a["file"]}" aria-label="Read article: {a["title"]}"><h3>{a["title"]}</h3></a></article>'
    dyn_html += '</div>'

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
    f.write(index_template.replace("{{HERO_SECTION}}", hero_html).replace("{{DYNAMIC_CONTENT}}", dyn_html).replace("{{BREAKING_NEWS_TICKER}}", ticker))

# Generate Sitemap
print("Generating Sitemap...")
generate_sitemap(all_arts)

# Generate llms.txt for AI crawlers
print("Generating llms.txt...")
llms_content = f"# GenZ Frontier\n\nGenZ Frontier is a modern digital news portal and technology journal. It provides the latest updates on world news, politics, business, technology, science, health, sports, and entertainment.\n\n## Categories\n"
for cat in DEFAULT_CATEGORIES:
    llms_content += f"- [{cat.title()}](https://www.genzfrontir.com/{cat}/)\n"
llms_content += "\n## Latest News\n"
for a in all_arts[:10]:
    llms_content += f"- [{a['title']}]({a['url']})\n"

with open(os.path.join(OUTPUT_DIR, "llms.txt"), "w", encoding="utf-8") as f:
    f.write(llms_content)
with open("llms.txt", "w", encoding="utf-8") as f:
    f.write(llms_content)

print("✅ Build Complete!")
