import os
import subprocess
import urllib.parse
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

BASE_URL = "https://www.genzfrontir.com/"
SCAN_DIR = "." 

def get_seo_date(file_path):
    """Fetches the exact last modification date from Git history."""
    try:
        git_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cI', file_path],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        if git_date:
            return git_date
    except Exception:
        pass
    
    ts = os.path.getmtime(file_path)
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S+00:00')

def generate_sitemap():
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    added_links = set()

    for root, dirs, files in os.walk(SCAN_DIR):
        # Ignore hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if file.endswith(".html"):
                
                # 1. Ignore the 404 page
                if file == "404.html":
                    continue
                
                if root == ".":
                    rel_path = file
                else:
                    rel_path = os.path.relpath(os.path.join(root, file), SCAN_DIR)
                
                rel_path = rel_path.replace("\\", "/")
                
                # Remove 'public/' prefix from the URL
                if rel_path.startswith("public/"):
                    rel_path = rel_path[7:]
                
                # 2. Strict URL Normalization
                if rel_path == "index.html":
                    url_path = ""
                elif rel_path.endswith("/index.html"):
                    url_path = rel_path[:-10]
                else:
                    url_path = rel_path
                
                # NEW FIX: Encode spaces and special characters for a valid URL
                url_path = urllib.parse.quote(url_path, safe='/')
                
                full_url = f"{BASE_URL}{url_path}"
                
                # 3. Duplicate Checker
                if full_url in added_links:
                    continue 
                
                added_links.add(full_url)
                
                # 4. XML Element Creation (Matches your exact format)
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

    # Convert to standard XML and pretty print
    xml_str = ET.tostring(urlset, encoding='utf-8')
    # Use minidom to format exactly like your example
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # Remove the extra blank line minidom sometimes adds at the top
    pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines() if s.strip()])
    
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    print(f"✅ Root sitemap.xml successfully generated in the exact requested format with {len(added_links)} links.")

if __name__ == "__main__":
    generate_sitemap()
