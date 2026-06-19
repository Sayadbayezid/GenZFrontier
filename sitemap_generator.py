import os
import subprocess
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

BASE_URL = "https://www.genzfrontir.com/"
SCAN_DIR = "." 

def get_seo_date(file_path):
    """
    Fetches the exact last modification date from Git history.
    This prevents GitHub Actions from applying 'today's date' to old files.
    """
    try:
        # Ask Git for the last commit date of this specific file
        git_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cI', file_path],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        if git_date:
            return git_date
    except Exception:
        pass
    
    # Absolute fallback (Only applies if a file is brand new and not yet committed to Git)
    ts = os.path.getmtime(file_path)
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S+00:00')

def generate_sitemap():
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # A Python set strictly prevents any duplicate entries
    added_links = set()

    # Walk through the directory looking for HTML files
    for root, dirs, files in os.walk(SCAN_DIR):
        # Ignore hidden directories (.git, .github) to save time and prevent errors
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith(".html"):
                
                # 1. Ignore the 404 page
                if file == "404.html":
                    continue
                
                # Determine relative path from the root
                if root == ".":
                    rel_path = file
                else:
                    rel_path = os.path.relpath(os.path.join(root, file), SCAN_DIR)
                
                # Normalize slashes for Windows/Linux compatibility
                rel_path = rel_path.replace("\\", "/")
                
                # 2. Strict URL Normalization (Removes index.html to prevent duplicates)
                if rel_path == "index.html":
                    url_path = ""
                elif rel_path.endswith("/index.html"):
                    url_path = rel_path[:-10] # Removes "index.html" but keeps trailing slash
                else:
                    url_path = rel_path
                
                # Construct final URL
                full_url = f"{BASE_URL}{url_path}"
                
                # 3. The Duplicate Checker
                if full_url in added_links:
                    continue # Skip this loop iteration if URL is already processed
                
                added_links.add(full_url)
                
                # 4. XML Element Creation
                url_elem = ET.SubElement(urlset, "url")
                
                loc = ET.SubElement(url_elem, "loc")
                loc.text = full_url
                
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = get_seo_date(os.path.join(root, file))
                
                priority = ET.SubElement(url_elem, "priority")
                if url_path == "":
                    priority.text = "1.0"
                elif "/" not in url_path.strip("/"):
                    priority.text = "0.8"
                else:
                    priority.text = "0.6"

    # Convert XML tree to a formatted string
    xml_str = ET.tostring(urlset, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # Output single sitemap to the root directory
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    print(f"✅ Root sitemap.xml successfully generated with {len(added_links)} unique HTML links.")

if __name__ == "__main__":
    generate_sitemap()
