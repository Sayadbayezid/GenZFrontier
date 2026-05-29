import os
import markdown
import shutil

# ডিরেক্টরি পাথ সেটআপ
NEWS_DIR = 'news'
OUTPUT_DIR = 'public'

print("🚀 Starting GenZ Frontier Build Process...")

# আগের আউটপুট ফোল্ডার থাকলে সেটি ক্লিয়ার করে নতুন করে তৈরি করা
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# মেইন হোমপেজ (index.html) পাবলিক ফোল্ডারে কপি করা
if os.path.exists('index.html'):
    shutil.copy('index.html', os.path.join(OUTPUT_DIR, 'index.html'))
    print("✅ Copied root index.html")
else:
    print("❌ Warning: index.html not found in root directory!")

# আর্টিকেল টেমপ্লেট লোড করা
if os.path.exists('template.html'):
    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    print("✅ Loaded template.html")
else:
    print("❌ Error: template.html not found!")
    exit(1)

# Markdown কনভার্টার সেটআপ
md = markdown.Markdown(extensions=['meta', 'tables', 'fenced_code'])

# news ফোল্ডারের ভেতরের সব ফাইল স্ক্যান করা
for root, dirs, files in os.walk(NEWS_DIR):
    for file in files:
        if file.endswith('.md'):
            # কোন ক্যাটাগরির ফোল্ডার (যেমন: tech, politics) সেটি বের করা
            category = os.path.basename(root)
            
            # পাবলিক ফোল্ডারে সেই ক্যাটাগরির ফোল্ডার তৈরি করা (যেমন: public/tech)
            out_category_dir = os.path.join(OUTPUT_DIR, category)
            os.makedirs(out_category_dir, exist_ok=True)
            
            # ফাইলের পাথগুলো সেট করা
            md_path = os.path.join(root, file)
            html_filename = file.replace('.md', '.html')
            out_html_path = os.path.join(out_category_dir, html_filename)
            
            # Markdown ফাইল রিড করা
            with open(md_path, 'r', encoding='utf-8') as mf:
                text = mf.read()
                # Markdown থেকে HTML-এ কনভার্ট
                html_content = md.convert(text)
                md.reset()  # পরবর্তী ফাইলের জন্য কনভার্টার রিসেট
            
            # টেমপ্লেটের {{NEWS_CONTENT}} এর জায়গায় HTML বসানো
            final_html = template.replace('{{NEWS_CONTENT}}', html_content)
            
            # কনভার্ট হওয়া HTML ফাইলটি সেভ করা
            with open(out_html_path, 'w', encoding='utf-8') as hf:
                hf.write(final_html)
            
            print(f"📝 Converted: {category}/{file} -> {category}/{html_filename}")

print("🎉 Build Successful! All files are ready in the 'public' folder.")