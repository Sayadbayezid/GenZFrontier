import os
import sys
import shutil
import markdown
import json
import re
from datetime import datetime

# ==========================================================
# GenZ Frontier Build Configuration
# ==========================================================

NEWS_DIR = "news"
BASE_URL = "https://www.genzfrontir.com/" # Updated to your actual domain
OUTPUT_DIR = "public"
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"
ADS_DIR = "ads"

# Static pages that must always be copied
STATIC_FILES = [
    INDEX_FILE,
    "404.html",
    "contact.html",
    "about.html",
    "privacy-policy.html",
    "terms.html",
    "disclaimer.html",
    "cookie-policy.html",
    "CNAME",
    "sitemap.xml",
    "robots.txt"
]

# Default news categories
DEFAULT_CATEGORIES = [
    "world",
    "politics",
    "business",
    "tech",
    "science",
    "health",
    "sports",
    "entertainment",
    "ads", 
]

print("🚀 Starting GenZ Frontier Build Process...")

# ==========================================================
# Helper Functions
# ==========================================================

def clean_output_directory():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, ADS_DIR), exist_ok=True)
    print(f"✅ Created fresh '{OUTPUT_DIR}' directory")

def copy_static_files():
    print("\n📦 Copying static files...")
    for filename in STATIC_FILES:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(OUTPUT_DIR, filename))
            print(f"✅ Copied {filename}")
        else:
            print(f"⚠️ Skipped missing file: {filename}")
    
    if os.path.exists(ADS_DIR):
        for item in os.listdir(ADS_DIR):
            s = os.path.join(ADS_DIR, item)
            d = os.path.join(OUTPUT_DIR, ADS_DIR, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
        print(f"✅ Copied ads from {ADS_DIR}")

def load_template(template_path):
    if not os.path.exists(template_path):
        print(f"\n❌ BUILD FAILED\nRequired template file '{template_path}' was not found.")
        sys.exit(1)
    with open(template_path, "r", encoding="utf-8") as file:
        return file.read()

def create_markdown_parser():
    return markdown.Markdown(extensions=["meta", "tables", "fenced_code", "toc", "attr_list"])

def generate_meta_tags(article_data, page_type="article"):
    title = article_data.get("title", "GenZ Frontier")
    description = article_data.get("description", "Breaking News, Latest News and Videos from GenZ Frontier.")
    image = article_data.get("image", f"{BASE_URL}default-social-image.jpg")
    url = article_data.get("url", BASE_URL)

    meta_tags = f"""
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="{page_type}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image}">
    """
    return meta_tags

def generate_json_ld_schema(article_data):
    if not article_data:
        return ""
    headline = article_data.get("title", "GenZ Frontier News")
    image = article_data.get("image", f"{BASE_URL}default-social-image.jpg")
    date_published = article_data.get("date_published", datetime.now().isoformat())
    description = article_data.get("description", "Breaking News, Latest News and Videos from GenZ Frontier.")
    url = article_data.get("url", BASE_URL)

    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "headline": headline,
        "image": [image],
        "datePublished": date_published,
        "dateModified": datetime.now().isoformat(),
        "author": {"@type": "Person", "name": article_data.get("author", "GenZ Frontier")},
        "publisher": {"@type": "Organization", "name": "GenZ Frontier", "logo": {"@type": "ImageObject", "url": f"{BASE_URL}logo.png"}},
        "description": description
    }
    return f"<script type=\"application/ld+json\">{json.dumps(schema, indent=4)}</script>"

def generate_latest_news_html(articles):
    latest_news_html = """
        <div class="section-header">
            <h2>Latest News</h2>
            <a href="./world/" class="see-all">See all →</a>
        </div>
        <div class="grid-4" id="newsGrid">
    """
    for article in articles[:4]:
        latest_news_html += f"""
            <article class="news-card">
                <img src="{article["image"]}" alt="{article["title"]}">
                <span class="tag">{article["category"].title()}</span>
                <a href="./{article["category"]}/{article["filename"]}"><h3>{article["title"]}</h3></a>
                <p>{article["description"]}</p>
            </article>
        """
    latest_news_html += "</div>"
    return latest_news_html

def generate_category_archive_links(category_articles):
    archive_links_html = """
        <div class="section-header">
            <h2>More top stories</h2>
            <a href="./world/" class="see-all">See all →</a>
        </div>
        <div class="grid-featured">
            <div class="featured-large">
                <img src="https://images.unsplash.com/photo-1614729939124-03290b55c9ce?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" alt="Space Feature">
                <div class="overlay">
                    <span class="tag" style="color: var(--primary-red); font-weight: bold;">SPACE AND SCIENCE</span>
                    <a href="./science/"><h3>Historic mission successfully deploys critical instruments in orbit</h3></a>
                </div>
            </div>
            <div class="hero-sidebar" style="gap: 30px;">
                <article class="news-card">
                    <img src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" alt="Business Building">
                    <span class="tag">Business</span>
                    <a href="./business/"><h3>Commercial real estate sector sees unexpected growth</h3></a>
                </article>
                <article class="news-card">
                    <img src="https://images.unsplash.com/photo-1517404215738-15263e9f9178?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" alt="Documentary">
                    <span class="tag">Entertainment</span>
                    <a href="./entertainment/"><h3>Award-winning documentary sheds light on local history</h3></a>
                </article>
            </div>
        </div>
    """
    return archive_links_html

def generate_breaking_news_ticker(breaking_articles):
    if not breaking_articles:
        return ""
    ticker_items = ""
    for article in breaking_articles:
        ticker_items += f'<span>🔴 <a href="/{article["category"]}/{article["filename"]}" style="color: white; text-decoration: none;">{article["title"]}</a></span>'
    
    ticker_html = f"""
    <div class="breaking-news-ticker">
        <div class="breaking-label">BREAKING</div>
        <marquee class="breaking-marquee" behavior="scroll" direction="left" onmouseover="this.stop();" onmouseout="this.start();">
            {ticker_items}
        </marquee>
    </div>
    """
    return ticker_html

# ==========================================================
# Build Setup
# ==========================================================

clean_output_directory()
copy_static_files()

template = load_template(TEMPLATE_FILE)
index_template = load_template(INDEX_FILE)
md_parser = create_markdown_parser()

category_articles = {cat: [] for cat in DEFAULT_CATEGORIES}
all_articles = []
breaking_articles = []

# ==========================================================
# Markdown → HTML Conversion
# ==========================================================

print("\n📰 Processing articles...")

for root, dirs, files in os.walk(NEWS_DIR):
    for file in files:
        if not file.endswith(".md"):
            continue

        category = os.path.basename(root)
        if category not in category_articles:
            category_articles[category] = []

        category_output_dir = os.path.join(OUTPUT_DIR, category)
        os.makedirs(category_output_dir, exist_ok=True)

        markdown_path = os.path.join(root, file)
        html_filename = os.path.splitext(file)[0] + ".html"
        html_output_path = os.path.join(category_output_dir, html_filename)

        try:
            with open(markdown_path, "r", encoding="utf-8") as md_file:
                markdown_text = md_file.read()

            html_content = md_parser.convert(markdown_text)
            metadata = md_parser.Meta if hasattr(md_parser, 'Meta') else {}
            md_parser.reset()

            article_title = metadata['title'][0] if 'title' in metadata else (markdown_text.split("\n")[0].replace("# ", "").strip() if markdown_text.startswith("# ") else os.path.splitext(file)[0].replace("-", " ").title())
            is_breaking = metadata['breaking'][0].lower() == 'true' if 'breaking' in metadata else ('breaking: true' in markdown_text.lower())
            
            article_description = metadata.get('description', [""])[0]
            if not article_description:
                first_paragraph_match = re.search(r'\n\n([^#].*?)\n\n', markdown_text, re.DOTALL)
                if first_paragraph_match:
                    article_description = first_paragraph_match.group(1).strip()[:147] + "..." if len(first_paragraph_match.group(1)) > 150 else first_paragraph_match.group(1).strip()

            article_image = metadata.get('image', [f"{BASE_URL}default-social-image.jpg"])[0]
            if article_image == f"{BASE_URL}default-social-image.jpg":
                first_image_match = re.search(r'!\[.*?\]\((.*?)\)', markdown_text)
                if first_image_match:
                    article_image = first_image_match.group(1)

            article_date_published = datetime.now().isoformat()
            article_data = {
                "title": article_title,
                "filename": html_filename,
                "category": category,
                "description": article_description,
                "image": article_image,
                "date_published": article_date_published,
                "author": metadata.get('author', ["GenZ Frontier"])[0],
                "url": f"{BASE_URL}{category}/{html_filename}",
                "breaking": is_breaking
            }
            
            category_articles[category].append(article_data)
            all_articles.append(article_data)
            if is_breaking:
                breaking_articles.append(article_data)

            meta_tags = generate_meta_tags(article_data)
            json_ld_schema = generate_json_ld_schema(article_data)

            final_html = template.replace("{{ARTICLE_TITLE}}", article_title) \
                                 .replace("{{NEWS_CONTENT}}", html_content) \
                                 .replace("{{META_TAGS}}", meta_tags) \
                                 .replace("{{SCHEMA_DATA}}", json_ld_schema)

            with open(html_output_path, "w", encoding="utf-8") as output_file:
                output_file.write(final_html)

        except Exception as error:
            print(f"❌ Failed to process {category}/{file}: {error}")

all_articles.sort(key=lambda x: x['date_published'], reverse=True)
breaking_articles.sort(key=lambda x: x['date_published'], reverse=True)

# ==========================================================
# Generate Category Pages (NEW FEATURE ADDED)
# ==========================================================

print("\n📁 Generating category index pages...")
breaking_ticker_html = generate_breaking_news_ticker(breaking_articles)

for category, articles in category_articles.items():
    cat_dir = os.path.join(OUTPUT_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    
    articles.sort(key=lambda x: x['date_published'], reverse=True)
    
    cat_html = f'<div class="section-header"><h2>{category.title()} News</h2></div><div class="grid-4">'
    if articles:
        for article in articles:
            # Note: link uses just filename because we are already inside the category folder
            cat_html += f'''
            <article class="news-card">
                <img src="{article["image"]}" alt="{article["title"]}">
                <span class="tag">{category.title()}</span>
                <a href="./{article["filename"]}"><h3>{article["title"]}</h3></a>
                <p>{article["description"]}</p>
            </article>
            '''
    else:
        cat_html += f"<p>More updates coming soon in {category.title()}.</p>"
    cat_html += '</div>'
    
    # Create category page based on index template layout
    cat_page_html = index_template.replace("{{LATEST_NEWS_SECTION}}", cat_html) \
                                  .replace("{{CATEGORY_ARCHIVE_LINKS}}", "") \
                                  .replace("{{BREAKING_NEWS_TICKER}}", breaking_ticker_html)
    
    # Adjust relative paths so navigation menu and styles work from a sub-folder
    cat_page_html = cat_page_html.replace('href="./', 'href="../')
    
    with open(os.path.join(cat_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(cat_page_html)
    print(f"✅ Generated {category}/index.html")

# ==========================================================
# Generate Main index.html
# ==========================================================

print("\n🏠 Generating main index.html...")

latest_news_section_html = generate_latest_news_html(all_articles)
category_archive_links_html = generate_category_archive_links(category_articles)

final_index_html = index_template.replace("{{LATEST_NEWS_SECTION}}", latest_news_section_html) \
                                 .replace("{{CATEGORY_ARCHIVE_LINKS}}", category_archive_links_html) \
                                 .replace("{{BREAKING_NEWS_TICKER}}", breaking_ticker_html)

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as file:
    file.write(final_index_html)

print("🔄 Injecting ticker into template for future builds...")
ticker_placeholder = "{{BREAKING_NEWS_TICKER}}"
template = template.replace(ticker_placeholder, breaking_ticker_html)
with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
    f.write(template)

for root, dirs, files in os.walk(OUTPUT_DIR):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if ticker_placeholder in content:
                content = content.replace(ticker_placeholder, breaking_ticker_html)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

print(f"✅ Generated {INDEX_FILE} and all Category pages.")
print("\n🚀 Build Complete!")