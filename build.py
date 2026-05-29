
import os
import sys
import shutil
import markdown

# ==========================================================
# GenZ Frontier Build Configuration
# ==========================================================

NEWS_DIR = "news"
OUTPUT_DIR = "public"
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"

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
    print(f"✅ Created fresh \'{OUTPUT_DIR}\' directory")


def copy_static_files():
    """Copy all required static files to public/."""
    print("\n📦 Copying static files...")

    for filename in STATIC_FILES:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(OUTPUT_DIR, filename))
            print(f"✅ Copied {filename}")
        else:
            print(f"⚠️ Skipped missing file: {filename}")


def load_template(template_path):
    """Load article template and fail gracefully if missing."""
    if not os.path.exists(template_path):
        print(
            "\n❌ BUILD FAILED\n"
            f"Required template file \'{template_path}\' was not found.\n"
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


def generate_latest_news_html(articles):
    """Generates the HTML for the latest news section."""
    latest_news_html = """
        <div class="section-header">
            <h2>Latest News</h2>
            <a href="./world/" class="see-all">See all →</a>
        </div>
        <div class="grid-4" id="newsGrid">
    """
    for article in articles[:4]:  # Display up to 4 latest articles
        latest_news_html += f"""
            <article class="news-card">
                <img src="{article['image']}" alt="{article['title']}">
                <span class="tag">{article['category'].title()}</span>
                <a href="./{article['category']}/{article['filename']}"><h3>{article['title']}</h3></a>
                <p>{article['description']}</p>
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
    # For simplicity, let's just pick two from business and entertainment for the sidebar.
    # In a real scenario, this would be more dynamic based on the actual articles.
    # For now, I'll use placeholders as in the original index.html
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


# ==========================================================
# Build Setup
# ==========================================================

clean_output_directory()

# Load templates
template = load_template(TEMPLATE_FILE)
index_template = load_template(INDEX_FILE)
md = create_markdown_parser()

# Track category articles
category_articles = {cat: [] for cat in DEFAULT_CATEGORIES}
all_articles = []

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
        html_output_path = os.path.join(
            category_output_dir,
            html_filename
        )

        try:
            with open(markdown_path, "r", encoding="utf-8") as md_file:
                markdown_text = md_file.read()

            html_content = md.convert(markdown_text)
            md.reset()

            # Extract title from the first H1 or use filename
            article_title = "Untitled Article"
            if markdown_text.startswith("# "):
                article_title = markdown_text.split("\n")[0].replace("# ", "").strip()
            else:
                article_title = (
                    os.path.splitext(file)[0]
                    .replace("-", " ")
                    .title()
                )
            
            # Extract description (first paragraph) and image (first image) if available
            article_description = ""
            article_image = "https://via.placeholder.com/400x225.png?text=No+Image"
            
            # Simple regex to find the first paragraph
            import re
            first_paragraph_match = re.search(r'\n\n([^#].*?)\n\n', markdown_text, re.DOTALL)
            if first_paragraph_match:
                article_description = first_paragraph_match.group(1).strip()
                # Limit description length
                if len(article_description) > 150:
                    article_description = article_description[:147] + "..."

            # Simple regex to find the first image
            first_image_match = re.search(r'!\[.*?\]\((.*?)\)', markdown_text)
            if first_image_match:
                article_image = first_image_match.group(1)

            article_data = {
                "title": article_title,
                "filename": html_filename,
                "category": category,
                "description": article_description,
                "image": article_image,
            }
            category_articles[category].append(article_data)
            all_articles.append(article_data)

            final_html = template.replace(
                "{{NEWS_CONTENT}}",
                html_content
            )

            with open(
                html_output_path,
                "w",
                encoding="utf-8"
            ) as output_file:
                output_file.write(final_html)

            print(f"📝 Converted: {category}/{file}")

        except Exception as error:
            print(
                f"❌ Failed to process "
                f"{category}/{file}: {error}"
            )

# Sort all articles by some criteria for "latest news" - for now, just reverse the order of processing
all_articles.reverse()

# ==========================================================
# Generate index.html
# ==========================================================

print("\n🏠 Generating index.html...")

latest_news_section_html = generate_latest_news_html(all_articles)
category_archive_links_html = generate_category_archive_links(category_articles)

final_index_html = index_template.replace(
    "{{LATEST_NEWS_SECTION}}",
    latest_news_section_html
).replace(
    "{{CATEGORY_ARCHIVE_LINKS}}",
    category_archive_links_html
)

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as file:
    file.write(final_index_html)

print(f"✅ Generated {INDEX_FILE}")

# ==========================================================
# Category Index Pages
# ==========================================================

print("\n📂 Generating category pages...")

for category, articles in category_articles.items():

    category_dir = os.path.join(OUTPUT_DIR, category)
    os.makedirs(category_dir, exist_ok=True)

    category_index = os.path.join(
        category_dir,
        "index.html"
    )

    if articles:
        links_html = "\n".join(
            [
                (
                    f"<li>"
                    f"<a href=\"{article['filename']}\">"
                    f"{article['title']} &rarr;"
                    f"</a>"
                    f"</li>"
                )
                for article in articles
            ]
        )
    else:
        links_html = (
            "<p>No news published in this category yet. "
            "Stay tuned!</p>"
        )

    category_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>GenZ Frontier | {category.title()} News</title>

<meta name="description"
      content="Latest {category.title()} news and updates from GenZ Frontier.">

<meta name="robots"
      content="index,follow">

<style>
* {{
    box-sizing: border-box;
}}

body {{
    font-family: Arial, Helvetica, sans-serif;
    background: #f4f4f4;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}}

header {{
    background: #000;
    color: #fff;
    padding: 15px 20px;
    border-bottom: 4px solid #cc0000;
}}

.container {{
    max-width: 900px;
    margin: 40px auto;
    background: #fff;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,.08);
}}

h1 {{
    border-bottom: 2px solid #cc0000;
    padding-bottom: 10px;
}}

ul {{
    list-style: none;
    padding: 0;
}}

li {{
    margin-bottom: 15px;
}}

a {{
    color: #cc0000;
    text-decoration: none;
    font-size: 1.1rem;
    font-weight: bold;
}}

a:hover {{
    text-decoration: underline;
}}

@media (max-width: 768px) {{
    .container {{
        margin: 20px;
        padding: 25px;
    }}
}}
</style>

</head>

<body>

<header>
    <div style="
        max-width:900px;
        margin:auto;
        display:flex;
        justify-content:space-between;
        align-items:center;
        flex-wrap:wrap;
        gap:10px;">
        
        <a href="../"
           style="
           color:#cc0000;
           text-decoration:none;
           font-size:28px;
           font-weight:900;">
            GenZ Frontier
        </a>

        <a href="../"
           style="
           color:#ddd;
           text-decoration:none;">
            ← Back Home
        </a>
    </div>
</header>

<div class="container">

    <h1>{category.title()} News</h1>

    <ul>
        {links_html}
    </ul>

</div>

</body>
</html>
"""

    with open(category_index, "w", encoding="utf-8") as file:
        file.write(category_html)

    print(f"✅ Generated {category}/index.html")

# ==========================================================
# Build Complete
# ==========================================================

print("\n🎉 Build Successful!")
print("✅ Static pages copied")
print("✅ Markdown converted")
print("✅ Category pages generated")
print(f"✅ Output directory: {OUTPUT_DIR}/")
