import os
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

BASE_URL = "https://www.genzfrontir.com/"
PUBLIC_DIR = "public"

def parse_date(date_str):
    """Parse various date formats from markdown metadata."""
    try:
        # Example: "June 2, 2026"
        return datetime.strptime(date_str.strip(), '%B %d, %Y').strftime('%Y-%m-%dT%H:%M:%S+00:00')
    except:
        try:
            # Example: "2026-06-02"
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S+00:00')
        except:
            return None

def get_article_date(rel_path):
    """Try to find the original date from the markdown source."""
    # rel_path like "tech/article.html" -> "news/tech/article.md"
    if '/' in rel_path and not rel_path.endswith('index.html'):
        md_path = os.path.join("news", rel_path.replace('.html', '.md'))
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.lower().startswith('date:'):
                        date_val = line.split(':', 1)[1].strip()
                        parsed = parse_date(date_val)
                        if parsed:
                            return parsed
    return None

def get_last_mod(file_path, rel_path=None):
    """Get the modification time, prioritizing article metadata date."""
    if rel_path:
        article_date = get_article_date(rel_path)
        if article_date:
            return article_date
            
    ts = os.path.getmtime(file_path)
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S+00:00')

def generate_sitemap():
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Track added links to avoid duplicates
    added_links = set()

    # Walk through the public directory to find all .html files
    for root, _, files in os.walk(PUBLIC_DIR):
        for file in files:
            if file.endswith(".html"):
                # Construct the relative path
                rel_path = os.path.relpath(os.path.join(root, file), PUBLIC_DIR)
                
                # Normalize URL
                if rel_path == "index.html":
                    url_path = ""
                elif rel_path.endswith("index.html"):
                    url_path = rel_path[:-10] # Remove index.html
                else:
                    url_path = rel_path
                
                full_url = f"{BASE_URL}{url_path}"
                
                # Avoid duplicates (e.g., /tech/ and /tech/index.html)
                if full_url in added_links:
                    continue
                
                added_links.add(full_url)
                
                url_elem = ET.SubElement(urlset, "url")
                loc = ET.SubElement(url_elem, "loc")
                loc.text = full_url
                
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = get_last_mod(os.path.join(root, file), rel_path)
                
                priority = ET.SubElement(url_elem, "priority")
                if url_path == "":
                    priority.text = "1.0"
                elif "/" not in url_path.strip("/"):
                    priority.text = "0.8"
                else:
                    priority.text = "0.6"

    # Convert to pretty-printed XML string
    xml_str = ET.tostring(urlset, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # Save to both root and public (for immediate use and persistence)
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    with open(os.path.join(PUBLIC_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    print(f"✅ Sitemap generated with {len(added_links)} links.")

if __name__ == "__main__":
    if not os.path.exists(PUBLIC_DIR):
        print(f"❌ Error: {PUBLIC_DIR} directory not found. Run build.py first.")
    else:
        generate_sitemap()
