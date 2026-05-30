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
BASE_URL = "https://genzfrontier.com/" # Replace with your actual base URL
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
]

# Default news categories (Added ads folder so it doesn't crash)
DEFAULT_CATEGORIES = [
    "world",
    "politics",
    "business",
    "tech",
    "science",
    "health",
    "sports",
    "entertainment",
    ADS_DIR 
]

print("🚀 Starting GenZ Frontier Build Process...")

# ==========================================================
# Helper Functions
# ==========================================================

def clean_output_directory():
    """Remove old build and create fresh output directory."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"✅ Created fresh '{OUTPUT_DIR}' directory")

    # Ensure ads directory exists in output
    os.makedirs(os.path.join(OUTPUT_DIR, ADS_DIR), exist_ok=True)


def copy_static_files():
    """Copy all required static files to public/."""
    print("\n📦 Copying static files...")

    for filename in STATIC_FILES:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(OUTPUT_DIR, filename))
            print(f"✅ Copied {filename}")
        else:
            print(f"⚠️ Skipped missing file: {filename}")
    
    # Copy ads images/assets if any (Skip .md files so they don't leak)
    if os.path.exists(ADS_DIR):
        for item in os.listdir(ADS_DIR):
            s = os.path.join(ADS_DIR, item)
            d = os.path.join(OUTPUT_DIR, ADS_DIR, item)
            if os.path.isfile(s) and not s.endswith(".md"):
                shutil.copy2(s, d)
        print(f"✅ Copied static assets from {ADS_DIR}")


def load_template(template_path):
    """Load article template and fail gracefully if missing."""
    if not os.path.exists(template_path):
        print(
            "\n❌ BUILD FAILED\n"
            f"Required template file '{template_path}' was not found.\n"
            "Please ensure template.html exists in the repository root."
        )
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as file:
        print(f"✅ Loaded {template_path}")
        return file.read()


def create_markdown_parser():
    """Return configured markdown parser."""
    return markdown.Markdown(
        extensions=[
            "meta",
            "tables",
            "fenced_code",
            "toc",
            "attr_list",
        ]
    )


def generate_meta_tags(article_data, page_type="article"):
    """Generates SEO meta tags for an article or a general page."""
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
    """Generates JSON-LD NewsArticle schema for an article."""
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
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        },
        "headline": headline,
        "image": [
            image
        ],
        "datePublished": date_published,
        "dateModified": datetime.now().isoformat(),
        "author": {
            "@type": "Person",
            "name": article_data.get("author", "GenZ Frontier")
        },
        "publisher": {
            "@type": "Organization",
            "name": "GenZ Frontier",
            "logo": {
                "@type": "ImageObject",
                "url": f"{BASE_URL}logo.png"
            }
        },
        "description": description
    }
    return f"<script type=\"application/ld+json\">{json.dumps(schema, indent=4)}</script>"

def generate_latest_news_html(articles):
    """Generates the HTML for the latest news section."""
    latest_news_html = """
        <div class="section-header">
            <h2>Latest News</h2>
            <a href="./world/" class="see-all">See all →</a>
        </div>
        <div class="grid-4" id="newsGrid">
    """
    # Only show actual news in the latest news grid, ignore ads
    real_news = [a for a in articles if a["category"] != ADS_DIR]
    
    for article in real_news[:4]:
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
    """Generates HTML for category archive links."""
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
    """
    archive_links_html += """
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
    """Generates HTML for the breaking news ticker."""
    if not breaking_articles:
        return ""
    
    ticker_items = ""
    for article in breaking_articles:
        # Use custom URL if provided (perfect for Ads), else use the generated news link
        ticker_items += f'<span class="ticker-item"><a href="{article["ticker_url"]}">{article["title"]}</a></span>'
    
    ticker_html = f"""
    <div class="breaking-news-ticker">
        <div class="ticker-label">BREAKING</div>
        <div class="ticker-wrap">
            <div class="ticker-move">
                {ticker_items}
                {ticker_items} </div>
        </div>
    </div>
    """
    return ticker_html

# ==========================================================
# Build Setup
# ==========================================================

clean_output_directory()
copy_static_files()

# Load templates
template = load_template(TEMPLATE_FILE)
index_template = load_template(INDEX_FILE)
md_parser = create_markdown_parser()

# Track category articles
category_articles = {cat: [] for cat in DEFAULT_CATEGORIES}
all_articles = []
breaking_articles = []

# ==========================================================
# Markdown → HTML Conversion
# ==========================================================

print("\n📰 Processing articles and ads...")

# We only need to scan NEWS_DIR because ads is inside it (news/ads/)
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

            # Parse with metadata
            html_content = md_parser.convert(markdown_text)
            metadata = md_parser.Meta if hasattr(md_parser, 'Meta') else {}
            md_parser.reset()

            # Extract title
            article_title = "Untitled"
            if 'title' in metadata:
                article_title = metadata['title'][0]
            elif markdown_text.startswith("# "):
                article_title = markdown_text.split("\n")[0].replace("# ", "").strip()
            else:
                article_title = os.path.splitext(file)[0].replace("-", " ").title()
            
            # Check for breaking news tag
            is_breaking = False
            if 'breaking' in metadata:
                is_breaking = metadata['breaking'][0].lower() == 'true'
            elif 'breaking: true' in markdown_text.lower():
                is_breaking = True

            # Extract description
            article_description = metadata.get('description', [""])[0]
            if not article_description:
                first_paragraph_match = re.search(r'\n\n([^#].*?)\n\n', markdown_text, re.DOTALL)
                if first_paragraph_match:
                    article_description = first_paragraph_match.group(1).strip()
                    if len(article_description) > 150:
                        article_description = article_description[:147] + "..."

            # Extract image
            article_image = metadata.get('image', [f"{BASE_URL}default-social-image.jpg"])[0]
            
            # Setup custom URL for ads
            custom_url = metadata.get('url', [""])[0]
            ticker_url = custom_url if custom_url else f"/{category}/{html_filename}"

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
                "ticker_url": ticker_url,
                "breaking": is_breaking
            }
            
            category_articles[category].append(article_data)
            all_articles.append(article_data)
            if is_breaking:
                breaking_articles.append(article_data)

            # Generate SEO meta tags and JSON-LD schema
            meta_tags = generate_meta_tags(article_data)
            json_ld_schema = generate_json_ld_schema(article_data)

            final_html = template.replace("{{ARTICLE_TITLE}}", article_title) \
                                 .replace("{{NEWS_CONTENT}}", html_content) \
                                 .replace("{{META_TAGS}}", meta_tags) \
                                 .replace("{{SCHEMA_DATA}}", json_ld_schema)

            with open(html_output_path, "w", encoding="utf-8") as output_file:
                output_file.write(final_html)

            print(f"📝 Converted: {category}/{file} {'[BREAKING/AD]' if is_breaking else ''}")

        except Exception as error:
            print(f"❌ Failed to process {category}/{file}: {error}")

# Sort all articles
all_articles.sort(key=lambda x: x['date_published'], reverse=True)
breaking_articles.sort(key=lambda x: x['date_published'], reverse=True)

# ==========================================================
# Generate index.html
# ==========================================================

print("\n🏠 Generating index.html...")

latest_news_section_html = generate_latest_news_html(all_articles)
category_archive_links_html = generate_category_archive_links(category_articles)
breaking_ticker_html = generate_breaking_news_ticker(breaking_articles)

final_index_html = index_template.replace("{{LATEST_NEWS_SECTION}}", latest_news_section_html) \
                                 .replace("{{CATEGORY_ARCHIVE_LINKS}}", category_archive_links_html) \
                                 .replace("{{BREAKING_NEWS_TICKER}}", breaking_ticker_html)

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as file:
    file.write(final_index_html)

# ==========================================================
# Inject Ticker Into Public HTML Files ONLY
# ==========================================================

print("🔄 Injecting ticker into all output pages...")
ticker_placeholder = "{{BREAKING_NEWS_TICKER}}"

# Update all files inside the OUTPUT_DIR (public folder)
for root, dirs, files in os.walk(OUTPUT_DIR):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # শুধুমাত্র আউটপুট ফাইলেই রিপ্লেস হবে, সোর্স ফাইলে নয়
            if ticker_placeholder in content:
                content = content.replace(ticker_placeholder, breaking_ticker_html)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

print(f"✅ Generated {INDEX_FILE} and updated all pages with ticker.")
print("\n🚀 Build Complete!")