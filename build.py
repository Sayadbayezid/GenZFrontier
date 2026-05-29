import os
import markdown
import shutil

NEWS_DIR = 'news'
OUTPUT_DIR = 'public'

print("🚀 Starting GenZ Frontier Build Process...")

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

if os.path.exists('index.html'):
    shutil.copy('index.html', os.path.join(OUTPUT_DIR, 'index.html'))
    print("✅ Copied root index.html")

if os.path.exists('template.html'):
    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    print("✅ Loaded template.html")
else:
    print("❌ Error: template.html not found!")
    exit(1)

md = markdown.Markdown(extensions=['meta', 'tables', 'fenced_code'])

# সব ক্যাটাগরির লিস্ট তৈরি
categories = ['world', 'politics', 'business', 'tech', 'science', 'health', 'sports', 'entertainment']
category_articles = {cat: [] for cat in categories}

# Markdown ফাইল স্ক্যান এবং কনভার্ট
for root, dirs, files in os.walk(NEWS_DIR):
    for file in files:
        if file.endswith('.md'):
            category = os.path.basename(root)
            if category not in category_articles:
                category_articles[category] = []
            
            out_category_dir = os.path.join(OUTPUT_DIR, category)
            os.makedirs(out_category_dir, exist_ok=True)
            
            md_path = os.path.join(root, file)
            html_filename = file.replace('.md', '.html')
            out_html_path = os.path.join(out_category_dir, html_filename)
            
            with open(md_path, 'r', encoding='utf-8') as mf:
                text = mf.read()
                html_content = md.convert(text)
                md.reset()
            
            # ফাইলের নাম থেকে নিউজের টাইটেল তৈরি
            title = file.replace('.md', '').replace('-', ' ').title()
            category_articles[category].append({'title': title, 'filename': html_filename})
            
            final_html = template.replace('{{NEWS_CONTENT}}', html_content)
            
            with open(out_html_path, 'w', encoding='utf-8') as hf:
                hf.write(final_html)
            print(f"📝 Converted: {category}/{file}")

# ক্যাটাগরি ফোল্ডারগুলোর জন্য অটোমেটিক index.html তৈরি করা
for cat, articles in category_articles.items():
    cat_dir = os.path.join(OUTPUT_DIR, cat)
    os.makedirs(cat_dir, exist_ok=True)
    cat_index_path = os.path.join(cat_dir, 'index.html')
    
    # ক্যাটাগরি পেজের লিংক লিস্ট তৈরি
    links_html = ""
    if articles:
        for article in articles:
            links_html += f"<li style='margin-bottom:15px;'><a href='{article['filename']}' style='color:#CC0000; font-size:20px; font-weight:bold; text-decoration:none;'>{article['title']} &rarr;</a></li>"
    else:
        links_html = "<p style='font-size:18px; color:#666;'>No news published in this category yet. Stay tuned!</p>"

    # ক্যাটাগরি পেজের ডিজাইন
    category_page_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GenZ Frontier | {cat.title()} News</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #F4F4F4; margin: 0; padding: 0; }}
            header {{ background-color: #000; color: #FFF; padding: 15px 20px; border-bottom: 4px solid #CC0000; }}
            .container {{ max-width: 900px; margin: 40px auto; background: #FFF; padding: 40px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        </style>
    </head>
    <body>
        <header>
            <div style="max-width: 900px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
                <a href="../" style="font-size: 28px; font-weight: 900; color: #CC0000; text-decoration: none;">GenZ <span style="color: #FFF; font-weight: 400;">Frontier</span></a>
                <a href="../" style="color: #CCC; font-weight: bold; text-decoration: none;">&larr; Back to Home</a>
            </div>
        </header>
        <div class="container">
            <h1 style="text-transform: uppercase; border-bottom: 2px solid #CC0000; padding-bottom: 10px; color:#222; margin-top:0;">{cat.title()} NEWS</h1>
            <ul style="list-style: none; padding: 0; margin-top: 30px;">
                {links_html}
            </ul>
        </div>
    </body>
    </html>
    """
    with open(cat_index_path, 'w', encoding='utf-8') as hf:
        hf.write(category_page_html)

print("🎉 Build Successful! Categories and index pages are ready.")