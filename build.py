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

# Static pages that must always be copied
STATIC_FILES = [
    "index.html",
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
    print(f"✅ Created fresh '{OUTPUT_DIR}' directory")


def copy_static_files():
    """Copy all required static files to public/."""
    print("\n📦 Copying static files...")

    for filename in STATIC_FILES:
        if os.path.exists(filename):
            shutil.copy2(filename, os.path.join(OUTPUT_DIR, filename))
            print(f"✅ Copied {filename}")
        else:
            print(f"⚠️ Skipped missing file: {filename}")


def load_template():
    """Load article template and fail gracefully if missing."""
    if not os.path.exists(TEMPLATE_FILE):
        print(
            "\n❌ BUILD FAILED\n"
            f"Required template file '{TEMPLATE_FILE}' was not found.\n"
            "Please ensure template.html exists in the repository root."
        )
        sys.exit(1)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as file:
        print("✅ Loaded template.html")
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


# ==========================================================
# Build Setup
# ==========================================================

clean_output_directory()
copy_static_files()

template = load_template()
md = create_markdown_parser()

# Track category articles
category_articles = {cat: [] for cat in DEFAULT_CATEGORIES}

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

            article_title = (
                os.path.splitext(file)[0]
                .replace("-", " ")
                .title()
            )

            category_articles[category].append(
                {
                    "title": article_title,
                    "filename": html_filename,
                }
            )

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
                    f"<a href='{article['filename']}'>"
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