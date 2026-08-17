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
import hashlib
import html
from pathlib import Path

# === GA4 Imports (Optional) ===
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
except ImportError:
    BetaAnalyticsDataClient = None
    DateRange = Dimension = Metric = RunReportRequest = None
# =================================

def get_git_date(file_path):
    """Fetches the last commit date for a given file from Git history."""
    try:
        git_date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", file_path],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        if git_date:
            return git_date
    except Exception:
        pass
    return None

def sanitize_url(url):
    return url.replace(' ', '-').replace('#', '').replace('"', '').replace("'", "")

def absolute_url(path):
    """Convert a site-relative asset path into a stable absolute URL."""
    if not path:
        return f"{BASE_URL}default.webp"
    if path.startswith(("http://", "https://")):
        return path
    return urllib.parse.urljoin(BASE_URL, path.lstrip("/"))

def published_image_url(path):
    """Use WebP for local SVG article art when the optimized asset exists."""
    if path and not path.startswith(("http://", "https://")) and path.lower().endswith(".svg"):
        path = path[:-4] + ".webp"
    return absolute_url(path)

# Article video media is intentionally scoped to the news tree. The builder
# copies these files verbatim, validates that local references exist, and keeps
# the browser-friendly source order WebM -> MP4 with an optional VTT track.
VIDEO_MEDIA_EXTENSIONS = (".webm", ".mp4", ".m4v", ".vtt", ".ogv", ".ogg")
VIDEO_MIME_TYPES = {
    ".webm": "video/webm",
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".ogv": "video/ogg",
    ".ogg": "video/ogg",
}
FIRST_PARTY_MEDIA_PREFIXES = ("/news/", "/mind-manipulation/")
FIRST_PARTY_MEDIA_HOSTS = {"genzfrontir.com", "www.genzfrontir.com"}


def is_first_party_media_url(value):
    """Allow only same-domain or site-relative article media URLs."""
    normalized = str(value or "").strip()
    if not normalized or normalized.startswith(("#", "data:")):
        return False
    if normalized.startswith("/"):
        return normalized.startswith(FIRST_PARTY_MEDIA_PREFIXES)
    parsed = urllib.parse.urlparse(normalized)
    return parsed.scheme in ("http", "https") and parsed.netloc.lower() in FIRST_PARTY_MEDIA_HOSTS and parsed.path.startswith(FIRST_PARTY_MEDIA_PREFIXES)


def validate_first_party_video_markup(markdown_text):
    """Reject third-party native video sources, captions, and posters at build time."""
    video_blocks = re.findall(r"<video\b[^>]*>.*?</video>", markdown_text, flags=re.IGNORECASE | re.DOTALL)
    media_values = []
    for block in video_blocks:
        media_values.extend(re.findall(r'(?:src|poster)=["\']([^"\']+)["\']', block, flags=re.IGNORECASE))
    media_values.extend(re.findall(r'\[[^\]]*\]\(([^)]+?\.(?:webm|mp4|m4v|ogv|ogg|vtt))(?:\?[^)]*)?\)', markdown_text, flags=re.IGNORECASE))
    violations = [value for value in media_values if not is_first_party_media_url(value)]
    if violations:
        unique = sorted(set(violations))
        raise ValueError("Third-party video media is not allowed; use GenZ Frontier URLs only: " + ", ".join(unique))


def copy_news_media():
    """Copy supported news media to public/news and report invalid video assets."""
    copied = 0
    warnings = []
    for root, _, files in os.walk(NEWS_DIR):
        for file in files:
            suffix = os.path.splitext(file)[1].lower()
            if not (suffix in VIDEO_MEDIA_EXTENSIONS or suffix in (".svg", ".webp", ".avif", ".jpg", ".jpeg", ".png", ".gif")):
                continue
            src_file = os.path.join(root, file)
            if suffix in VIDEO_MEDIA_EXTENSIONS and os.path.getsize(src_file) == 0:
                warnings.append(f"empty video media skipped: {src_file}")
                continue
            dest_dir = os.path.join(OUTPUT_DIR, root)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(src_file, os.path.join(dest_dir, file))
            copied += 1
    for warning in warnings:
        print(f"VIDEO WARNING: {warning}")
    print(f"Copied {copied} supported news media assets, including local video files.")


def local_video_reference(path):
    """Return a normalized site-relative media path for local video references."""
    value = str(path or "").strip()
    if not value or value.startswith(("http://", "https://", "//", "data:")):
        return value
    value = value.split("#", 1)[0].split("?", 1)[0]
    if value.startswith("public/"):
        value = "/" + value[len("public/"):]
    elif not value.startswith("/"):
        value = "/" + value
    return value


def validate_local_video_references(markdown_text):
    """Warn about missing local video, poster, and caption files referenced by an article."""
    validate_first_party_video_markup(markdown_text)
    references = re.findall(r'(?:src|poster)=["\']([^"\']+)["\']', markdown_text, flags=re.IGNORECASE)
    references += re.findall(r'\[[^\]]*\]\(([^)]+)\)', markdown_text, flags=re.IGNORECASE)
    for reference in references:
        normalized = local_video_reference(reference)
        if not normalized or normalized.startswith(("http://", "https://", "//", "data:")):
            continue
        suffix = os.path.splitext(normalized.split("?", 1)[0])[1].lower()
        if suffix not in VIDEO_MEDIA_EXTENSIONS:
            continue
        source_path = os.path.join(os.getcwd(), normalized.lstrip("/"))
        if not os.path.exists(source_path):
            print(f"VIDEO WARNING: missing local media reference: {normalized}")


def ensure_image_alt_attributes(article_html, fallback_alt):
    """Add meaningful fallback alt text to article images that omit it."""
    fallback = html.escape(re.sub(r"\s+", " ", str(fallback_alt or "Article image")).strip(), quote=True)
    def add_alt(match):
        tag = match.group(0)
        if re.search(r"\balt\s*=\s*[\"\']\s*[\"\']", tag, flags=re.IGNORECASE):
            return re.sub(r"\balt\s*=\s*[\"\']\s*[\"\']", f'alt="{fallback}"', tag, count=1, flags=re.IGNORECASE)
        if re.search(r"\balt\s*=", tag, flags=re.IGNORECASE):
            return tag
        return tag[:-1] + f' alt="{fallback}">'
    return re.sub(r"<img\b[^>]*>", add_alt, article_html, flags=re.IGNORECASE)


def normalize_article_headings(article_html, title):
    """Ensure a mind-manipulation article has exactly one H1."""
    h1_count = len(re.findall(r"<h1\b", article_html, flags=re.IGNORECASE))
    if h1_count == 0:
        article_html = f'<h1>{html.escape(title)}</h1>\n' + article_html
    elif h1_count > 1:
        seen = 0
        def demote(match):
            nonlocal seen
            seen += 1
            return match.group(0) if seen == 1 else match.group(0).replace("h1", "h2").replace("H1", "H2")
        article_html = re.sub(r"<h1\b[^>]*>.*?</h1>", demote, article_html, flags=re.IGNORECASE | re.DOTALL)
    return article_html


def shorten_seo_title(title, max_prefix=42):
    """Keep the rendered title tag under common search-display limits."""
    value = re.sub(r"\s+", " ", str(title or "")).strip()
    if len(value) <= max_prefix:
        return value
    if ":" in value:
        prefix = value.split(":", 1)[0].strip()
        if len(prefix) <= max_prefix:
            return prefix
    shortened = value[:max_prefix].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return shortened + "…"


def enhance_video_markup(article_html):
    """Make inline article videos responsive and keyboard/mobile friendly."""
    def enhance_opening(match):
        tag = match.group(0)
        if "playsinline" not in tag.lower():
            tag = tag[:-1] + " playsinline>"
        if "preload=" not in tag.lower():
            tag = tag[:-1] + ' preload="metadata">'
        if "aria-label=" not in tag.lower():
            tag = tag[:-1] + ' aria-label="Article explainer video">'
        return tag

    article_html = re.sub(r"<video\b[^>]*>", enhance_opening, article_html, flags=re.IGNORECASE)
    return article_html

STATIC_PAGE_DESCRIPTIONS = {
    "index.html": "GenZ Frontier delivers breaking news, explainers, analysis, and practical guides across global categories.",
    "404.html": "The requested GenZ Frontier page could not be found. Return to the homepage or browse the latest categories.",
    "about.html": "Learn about GenZ Frontier, our editorial purpose, and the news, explainers, and practical guides we publish.",
    "contact.html": "Contact GenZ Frontier for editorial questions, corrections, guest-post inquiries, and general communication.",
    "cookie-policy.html": "Read how GenZ Frontier uses cookies and related technologies to support site functionality and measurement.",
    "privacy-policy.html": "Read the GenZ Frontier privacy policy and learn how information is handled on this website.",
    "terms.html": "Read the GenZ Frontier terms of use, publishing expectations, and website policies.",
    "disclaimer.html": "Read the GenZ Frontier disclaimer covering editorial information, links, and general educational content.",
}


def normalize_html_links(content):
    """Normalize malformed external URLs and remove unsupported placeholder links."""
    content = re.sub(r'(?P<prefix>\b(?:href|src)=["\'])Https://', r'\g<prefix>https://', content, flags=re.IGNORECASE)
    content = re.sub(r'(?P<prefix>\b(?:href|src)=["\'])www\.', r'\g<prefix>https://www.', content, flags=re.IGNORECASE)
    content = re.sub(r'<a\s+href=["\']chatgpt://[^"\']+["\']>(?P<label>.*?)</a>', r'\g<label>', content, flags=re.IGNORECASE | re.DOTALL)
    return content


def normalize_static_page(path):
    """Add baseline SEO metadata and heading structure to copied static pages."""
    filename = os.path.basename(path)
    if not os.path.exists(path):
        return
    content = open(path, "r", encoding="utf-8").read()
    default_description = f"Read this GenZ Frontier page for site information, editorial context, or archived content."
    description = html.escape(STATIC_PAGE_DESCRIPTIONS.get(filename, default_description), quote=True)
    if not re.search(r'<meta\s+[^>]*name=["\']description["\']', content, flags=re.IGNORECASE):
        content = re.sub(r'(<meta\s+charset=["\'][^>]+>)', r'\1\n    <meta name="description" content="' + description + '">', content, count=1, flags=re.IGNORECASE)
    content = re.sub(r'<title>(.*?)</title>', lambda m: f'<title>{html.escape(shorten_seo_title(re.sub(r"\s+", " ", m.group(1)).strip()), quote=False)}</title>', content, count=1, flags=re.IGNORECASE | re.DOTALL)
    if not re.search(r'<h1\b', content, flags=re.IGNORECASE):
        heading = html.escape(Path(filename).stem.replace("-", " ").title())
        content = content.replace("<body>", f'<body>\n<main><h1>{heading}</h1></main>', 1)
    content = ensure_image_alt_attributes(content, Path(filename).stem.replace("-", " ").title())
    content = normalize_html_links(content)
    open(path, "w", encoding="utf-8").write(content)


ENTITY_ALIASES = {
    "Sheikh Hasina": ["sheikh hasina", "hasina", "শেখ হাসিনা"],
    "Tarique Rahman": ["tarique rahman", "tarique", "তারেক রহমান"],
    "Sayad Md Bayezid Hosan": ["sayad md bayezid hosan", "sayad bayezid", "bayezid hosan"],
    "Abdul Latif Siddiqui": ["abdul latif siddiqui", "latif siddiqui", "লতিফ সিদ্দিকী"],
    "Murad Siddiqui": ["murad siddiqui", "মুরাদ সিদ্দিকী"],
    "Mirza Fakhrul Islam Alamgir": ["mirza fakhrul", "mirza fakhrul islam alamgir", "মির্জা ফখরুল"],
    "Obaidul Quader": ["obaidul quader", "obaidul kader", "ওবায়দুল কাদের"],
}
ENTITY_STOPWORDS = {"the", "and", "for", "with", "from", "after", "before", "news", "today", "update", "bangladesh", "article", "guide", "latest", "breaking"}

def normalize_text(value):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", str(value or "").lower())).strip()

def legacy_slug_from_filename(filename):
    """Return the previous filename-derived slug for backward-compatible redirects."""
    return sanitize_url(os.path.splitext(os.path.basename(filename))[0]).lower()

def slug_from_filename(filename, fallback_text=""):
    """Create a deterministic ASCII English slug from a filename or English metadata."""
    raw = os.path.splitext(os.path.basename(filename))[0]
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()
    if slug:
        return slug
    words = re.findall(r"[a-zA-Z0-9]+", str(fallback_text or ""))
    slug = "-".join(words[:10]).lower()
    if slug:
        return slug
    digest = hashlib.sha1(str(filename).encode("utf-8")).hexdigest()[:8]
    return f"article-{digest}"

def article_href(category, slug):
    """Return the canonical clean URL path for a generated article."""
    return f"/{category}/{slug}/"

def entity_keys_for_article(meta, title, description, body_text=""):
    """Infer stable entity keys from explicit metadata, aliases, and repeated title phrases."""
    raw_explicit = []
    for key in ("entity", "person", "people", "tags", "topic"):
        for value in meta.get(key, []):
            raw_explicit.extend(re.split(r"[,|]", str(value)))
    haystack = normalize_text(" ".join([title, description, body_text, " ".join(raw_explicit)]))
    found = []
    for canonical, aliases in ENTITY_ALIASES.items():
        if any(normalize_text(alias) in haystack for alias in aliases):
            found.append(canonical)
    for value in raw_explicit:
        candidate = normalize_text(value)
        if candidate and len(candidate.split()) >= 2 and not set(candidate.split()).issubset(ENTITY_STOPWORDS):
            found.append(value.strip())
    unique = {}
    for value in found:
        key = normalize_text(value)
        if key:
            unique[key] = value.strip()
    return sorted(unique.keys())

def entity_display_name(entity_key):
    for canonical, aliases in ENTITY_ALIASES.items():
        if normalize_text(canonical) == entity_key or entity_key in {normalize_text(alias) for alias in aliases}:
            return canonical
    return entity_key.title()

def article_fingerprint(article):
    """Return a normalized title/description fingerprint used only for duplicate suppression."""
    return normalize_text(f"{article.get('title', '')} {article.get('desc', '')}")

def dedupe_articles(articles, exclude_url=""):
    seen_urls, seen_fingerprints, result = set(), set(), []
    for article in articles:
        if article.get("url") == exclude_url:
            continue
        url = article.get("url", "")
        fingerprint = article_fingerprint(article)
        if url in seen_urls or (fingerprint and fingerprint in seen_fingerprints):
            continue
        seen_urls.add(url)
        if fingerprint:
            seen_fingerprints.add(fingerprint)
        result.append(article)
    return result

def primary_entity_key(article):
    """Return an entity only when it is explicitly named in title-level metadata."""
    haystack = normalize_text(f"{article.get('title', '')} {article.get('desc', '')}")
    keys = article.get("entity_keys", [])
    ranked = sorted(
        [key for key in keys if key in haystack],
        key=lambda key: (-haystack.count(key), key)
    )
    return ranked[0] if ranked else ""

def topic_tokens(article):
    words = set(normalize_text(f"{article.get('title', '')} {article.get('desc', '')}").split())
    return words - ENTITY_STOPWORDS - {"vs", "what", "how", "when", "does", "become", "becomes"}

def topic_label_for_article(article):
    title = article.get("title", "").strip()
    if len(title) > 62:
        title = title[:59].rstrip() + "…"
    return title or article.get("slug", "this topic").replace("-", " ").title()

def related_topic_score(current, candidate):
    overlap = topic_tokens(current).intersection(topic_tokens(candidate))
    if not overlap:
        return 0
    score = len(overlap) * 12
    if current.get("cat") == candidate.get("cat"):
        score += 8
    return score

def related_entity_score(current, candidate):
    """Score only when both articles share the same primary title-level entity."""
    current_primary = primary_entity_key(current)
    candidate_primary = primary_entity_key(candidate)
    if not current_primary or current_primary != candidate_primary:
        return 0
    score = 100
    if current.get("cat") == candidate.get("cat"):
        score += 8
    current_words = set(normalize_text(current.get("title", "")).split()) - ENTITY_STOPWORDS
    candidate_words = set(normalize_text(candidate.get("title", "")).split()) - ENTITY_STOPWORDS
    score += min(12, len(current_words.intersection(candidate_words)) * 2)
    return score

def render_related_cards(items, relation_label="Related article"):
    cards = ""
    for item in items:
        cards += f'''
        <article class="news-card related-card">
            <img src="{html.escape(item["img"], quote=True)}" alt="{html.escape(item["title"], quote=True)}" loading="lazy" width="400" height="225" decoding="async">
            <span class="related-card-category">{html.escape(item["cat"].replace("-", " ").title())}</span>
            <span class="related-card-label">{html.escape(relation_label)}</span>
            <a href="{html.escape(item["href"], quote=True)}"><h3>{html.escape(item["title"])}</h3></a>
            <a class="related-card-open" href="{html.escape(item["href"], quote=True)}">Open article <span aria-hidden="true">→</span></a>
        </article>'''
    return cards

AD_PROFILES = (
    {"name": "native", "class_name": "ad-slot-native", "min_words": 0},
    {"name": "tall-160x600", "class_name": "ad-slot-tall desktop-only-ad", "min_words": 900},
    {"name": "medium-160x300", "class_name": "ad-slot-medium desktop-only-ad", "min_words": 650},
    {"name": "banner-320x50", "class_name": "ad-slot-banner-small", "min_words": 0},
    {"name": "banner-728x90", "class_name": "ad-slot-banner-wide desktop-only-ad", "min_words": 700},
    {"name": "rectangle-300x250", "class_name": "ad-slot-rectangle", "min_words": 0},
    {"name": "banner-468x60", "class_name": "ad-slot-banner-medium desktop-only-ad", "min_words": 500},
)

def ad_slot_html(profile_name, placement="article"):
    """Return exactly one user-provided ad unit in a labeled, scoped slot."""
    wrappers = {
        "native": '''<aside class="article-ad-slot article-middle-ad ad-slot-native" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script async="async" data-cfasync="false" src="https://pl30308054.effectivecpmnetwork.com/ec56a821de60d9845e8059349f970dbf/invoke.js"></script><div id="container-ec56a821de60d9845e8059349f970dbf"></div></div></aside>''',
        "tall-160x600": '''<aside class="article-ad-slot article-middle-ad ad-slot-tall desktop-only-ad" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script>atOptions = {'key' : 'b9782458d33b2a813bcaf2fe42023033','format' : 'iframe','height' : 600,'width' : 160,'params' : {}};</script><script src="https://www.highperformanceformat.com/b9782458d33b2a813bcaf2fe42023033/invoke.js"></script></div></aside>''',
        "medium-160x300": '''<aside class="article-ad-slot article-middle-ad ad-slot-medium desktop-only-ad" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script>atOptions = {'key' : '67ca660e991495fefe1690d338feda7c','format' : 'iframe','height' : 300,'width' : 160,'params' : {}};</script><script src="https://www.highperformanceformat.com/67ca660e991495fefe1690d338feda7c/invoke.js"></script></div></aside>''',
        "banner-320x50": '''<aside class="article-ad-slot article-middle-ad ad-slot-banner-small" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script>atOptions = {'key' : '63306a6b6bacb1c08864039cf7a2415e','format' : 'iframe','height' : 50,'width' : 320,'params' : {}};</script><script src="https://www.highperformanceformat.com/63306a6b6bacb1c08864039cf7a2415e/invoke.js"></script></div></aside>''',
        "banner-728x90": '''<aside class="article-ad-slot article-middle-ad ad-slot-banner-wide desktop-only-ad" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script>atOptions = {'key' : '408a580368a45b8ea139e174fa740252','format' : 'iframe','height' : 90,'width' : 728,'params' : {}};</script><script src="https://www.highperformanceformat.com/408a580368a45b8ea139e174fa740252/invoke.js"></script></div></aside>''',
        "rectangle-300x250": '''<aside class="article-ad-slot article-middle-ad ad-slot-rectangle" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script>atOptions = {'key' : 'f6e57b56ca931a8024e4741fa8b443ea','format' : 'iframe','height' : 250,'width' : 300,'params' : {}};</script><script src="https://www.highperformanceformat.com/f6e57b56ca931a8024e4741fa8b443ea/invoke.js"></script></div></aside>''',
        "banner-468x60": '''<aside class="article-ad-slot article-middle-ad ad-slot-banner-medium desktop-only-ad" aria-label="Advertisement"><span class="article-ad-label">ADVERTISEMENT</span><div class="ad-slot-content"><script>atOptions = {'key' : 'f6678c6f84bf003f94564ce757f58307','format' : 'iframe','height' : 60,'width' : 468,'params' : {}};</script><script src="https://www.highperformanceformat.com/f6678c6f84bf003f94564ce757f58307/invoke.js"></script></div></aside>''',
    }
    return wrappers.get(profile_name, wrappers["native"])

def choose_article_ad_profile(article, word_count):
    """Choose one format per article; long articles can receive desktop-only formats."""
    digest = int(hashlib.sha1(article["slug"].encode("utf-8")).hexdigest()[:8], 16)
    eligible = [profile for profile in AD_PROFILES if word_count >= profile["min_words"]]
    return eligible[digest % len(eligible)]["name"]

CATEGORY_AD_PROFILES = {
    "world": "rectangle-300x250",
    "politics": "banner-728x90",
    "business": "banner-320x50",
    "tech": "banner-468x60",
    "science": "medium-160x300",
    "health": "banner-320x50",
    "sports": "rectangle-300x250",
    "entertainment": "banner-468x60",
    "careers": "medium-160x300",
    "legacy-archives": "banner-728x90",
    "mind-manipulation": "native",
}

def category_ad_slot_html(category):
    return ad_slot_html(CATEGORY_AD_PROFILES.get(category, "native"), placement="category")

def clean_canonical_reference(html_content, canonical_url):
    """Render the publication canonical as a readable action link, not a raw URL."""
    pattern = r'(<p><strong>Canonical URL:</strong>\s*)(https?://[^<\s]+)(\s*</p>)'
    replacement = r'\1<a class="canonical-reference-link" href="' + html.escape(canonical_url, quote=True) + r'" rel="canonical">Open the canonical article page</a>\3'
    return re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)

def add_avif_picture(html_content):
    """Wrap the first local WebP article image with an AVIF source and WebP fallback."""
    pattern = r'<p><img alt="([^"]*)" src="([^" ]+\.webp)" /></p>'

    def replacement(match):
        alt_text = html.escape(match.group(1), quote=True)
        webp_url = html.escape(match.group(2), quote=True)
        avif_url = html.escape(match.group(2)[:-5] + ".avif", quote=True)
        return (
            '<p><picture>'
            f'<source type="image/avif" srcset="{avif_url}">'
            f'<img alt="{alt_text}" src="{webp_url}" loading="eager" fetchpriority="high" decoding="async">'
            '</picture></p>'
        )

    return re.sub(pattern, replacement, html_content, count=1, flags=re.IGNORECASE)

def normalize_date(date_str):
    if not date_str: return datetime.now().strftime("%Y-%m-%d")
    try:
        if "T" in date_str: return date_str.split("T")[0]
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y", "%d %B %Y"):
            try: return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except: continue
        return date_str
    except: return datetime.now().strftime("%Y-%m-%d")

# ==========================================================
# GA4 Data Fetch Function (New)
# ==========================================================
def get_ga4_pageviews(property_id):
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if BetaAnalyticsDataClient is None:
        print("⚠️ google-analytics-data package not found! Skipping analytics data.")
        return {}
    if not creds_json:
        print("⚠️ GA4 Credentials not found! Skipping analytics data.")
        return {}

    with open("temp_ga_key.json", "w", encoding="utf-8") as f:
        f.write(creds_json)
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_ga_key.json"
    
    try:
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")],
            date_ranges=[DateRange(start_date="2026-01-01", end_date="today")],
        )
        response = client.run_report(request)
        views_data = {row.dimension_values[0].value: row.metric_values[0].value for row in response.rows}
        return views_data
    except Exception as e:
        print(f"Error fetching GA4 data: {e}")
        return {}
    finally:
        if os.path.exists("temp_ga_key.json"):
            os.remove("temp_ga_key.json")

# ==========================================================
# GenZ Frontier Build Configuration
# ==========================================================
NEWS_DIR = "news"
BASE_URL = "https://www.genzfrontir.com/"
OUTPUT_DIR = "public"
TEMPLATE_FILE = "template.html"
INDEX_FILE = "index.html"
ADS_DIR = "ads"

# ⚠️ GA4 Property ID (Updated) ⚠️
GA4_PROPERTY_ID = "524639425"

# ==========================================================
# 🔴 LIVE TV CONFIGURATION (NEW)
# ==========================================================
IS_LIVE = False
LIVE_VIDEO_URL = "https://www.youtube.com/embed/h7tqrdSOkog"

LIVE_SCRIPT_HTML = f"""
<script>
    window.LIVE_STATUS = {'true' if IS_LIVE else 'false'};
    window.LIVE_URL = '{LIVE_VIDEO_URL}';
</script>
"""
# ==========================================================

DEFAULT_CATEGORIES = ["world", "politics", "business", "tech", "science", "health", "sports", "entertainment", "careers", "legacy-archives","mind-manipulation"]

def clean_and_prepare():
    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, ADS_DIR), exist_ok=True)
    
    # Copy basic files
    for f in ["index.html", "404.html", "contact.html", "about.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html", "CNAME", "sitemap.xml", "robots.txt", "style.css", "favicon.ico", "2f91fd414fbc449ba9072df8cca9804a.txt"]:
        if os.path.exists(f):
            destination = os.path.join(OUTPUT_DIR, f)
            shutil.copy2(f, destination)
            if f.endswith(".html"):
                normalize_static_page(destination)
    
    # Copy optimized images and article video media through one scoped path.
    copy_news_media()

    # Handle Legacy Archives
    legacy_src = "legacy-archives"
    if os.path.exists(legacy_src):
        shutil.copytree(legacy_src, os.path.join(OUTPUT_DIR, "legacy-archives"), dirs_exist_ok=True)
        for legacy_html in Path(os.path.join(OUTPUT_DIR, "legacy-archives")).rglob("*.html"):
            normalize_static_page(str(legacy_html))

def generate_sitemap(articles):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    added_links = set()
    static_pages = ["", "about.html", "contact.html", "privacy-policy.html", "terms.html", "disclaimer.html", "cookie-policy.html", "submit-guest-post.html"]
    for page in static_pages:
        full_url = f"{BASE_URL}{page}"
        url_elem = ET.SubElement(urlset, "url")
        ET.SubElement(url_elem, "loc").text = full_url
        ET.SubElement(url_elem, "lastmod").text = normalize_date(get_git_date(page))
        ET.SubElement(url_elem, "priority").text = "1.0" if page == "" else "0.8"
        added_links.add(full_url)
    for art in all_arts:
        if art["cat"] == "ads": continue
        if art["url"] not in added_links:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = art["url"]
            ET.SubElement(url_elem, "lastmod").text = normalize_date(art["date"])
            ET.SubElement(url_elem, "priority").text = "0.6"
            added_links.add(art["url"])
    xml_str = ET.tostring(urlset, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f: f.write(pretty_xml)
    shutil.copy2(os.path.join(OUTPUT_DIR, "sitemap.xml"), "sitemap.xml")

# ==========================================================
# Main Execution
# ==========================================================
clean_and_prepare()

# === Fetch GA4 Data Before Building HTML (New) ===
print("Fetching GA4 Page Views...")
all_page_views = get_ga4_pageviews(GA4_PROPERTY_ID)
# =================================================

md_parser = markdown.Markdown(extensions=["meta", "tables"])
template = open(TEMPLATE_FILE, "r", encoding="utf-8").read()
index_template = open(INDEX_FILE, "r", encoding="utf-8").read()

cat_arts = {cat: [] for cat in DEFAULT_CATEGORIES}
all_arts = []

for root, _, files in os.walk(NEWS_DIR):
    for file in files:
        if not file.endswith(".md"): continue
        cat = os.path.basename(root)
        if cat not in cat_arts: continue
        with open(os.path.join(root, file), "r", encoding="utf-8") as f: txt = f.read()
        md_parser.convert(txt)
        meta = md_parser.Meta; md_parser.reset()
        output_file = file.replace(".md", ".html")
        title = meta.get("title", [file.replace(".md", "").title()])[0]
        description = meta.get("description", [""])[0]
        canonical_slug = slug_from_filename(output_file, f"{title} {description}")
        art = {
            "title": title,
            "file": output_file,
            "slug": canonical_slug,
            "legacy_slug": legacy_slug_from_filename(output_file),
            "href": article_href(cat, canonical_slug),
            "cat": cat,
            "desc": description,
            "img": published_image_url(meta.get("image", ["/default.webp"])[0]),
            "date": meta.get("date", [get_git_date(os.path.join(root, file)) or datetime.now().isoformat()])[0],
            "entity_keys": entity_keys_for_article(meta, title, description, txt[:10000]),
            "url": urllib.parse.urljoin(BASE_URL, article_href(cat, canonical_slug).lstrip("/"))
        }
        cat_arts[cat].append(art)
        all_arts.append(art)

all_arts.sort(key=lambda x: x["date"], reverse=True)

# Finalize unique canonical slugs per category. Collisions receive a deterministic
# short suffix so two articles can never silently overwrite one another.
used_slugs = {}
for art in all_arts:
    base_slug = art["slug"]
    key = (art["cat"], base_slug)
    if key in used_slugs:
        suffix = hashlib.sha1(f"{art['cat']}/{art['file']}".encode("utf-8")).hexdigest()[:8]
        candidate = f"{base_slug}-{suffix}"
        while (art["cat"], candidate) in used_slugs:
            suffix = hashlib.sha1(f"{art['cat']}/{art['file']}/{candidate}".encode("utf-8")).hexdigest()[:8]
            candidate = f"{base_slug}-{suffix}"
        art["slug"] = candidate
    used_slugs[(art["cat"], art["slug"])] = art["file"]
    art["href"] = article_href(art["cat"], art["slug"])
    art["url"] = urllib.parse.urljoin(BASE_URL, art["href"].lstrip("/"))

# 1. Hero Section & 3. Live Update Section
hero_post = all_arts[0] if all_arts else None
live_updates_posts = all_arts[:15]
hero_html = ""
if hero_post:
    hero_html = f'''
<section class="hero-section">
    <div class="hero-container">
        <div class="hero-main">
            <span class="red-tag">LATEST NEWS</span>
            <a href="{hero_post["href"]}">
                <h1>{hero_post["title"]}</h1>
            </a>
            <p>{hero_post["desc"]}</p>
            <a href="{hero_post["href"]}">
                <img src="{hero_post["img"]}" alt="{hero_post["title"]}" loading="eager" fetchpriority="high" width="1069" height="713" decoding="async">
            </a>
        </div>
        <div class="hero-sidebar hero-sidebar-scroll">
            <div class="section-header"><h2>LIVE UPDATES</h2></div>
'''
    for a in live_updates_posts:
        hero_html += f'''
            <div class="hero-side-item">
                <a href="{a["href"]}">
                    <img src="{a["img"]}" alt="{a["title"]}" loading="lazy" width="80" height="80" decoding="async">
                </a>
                <div>
                    <h3><a href="{a["href"]}">{a["title"]}</a></h3>
                </div>
            </div>
'''
    hero_html += '</div></div></section>'

# 2. Breaking News Ticker
ticker_posts = all_arts[:15]
ticker_items = "".join([f'<span>🔴 <a href="{a["href"]}" class="ticker-link">{a["title"]}</a></span>' for a in ticker_posts])
ticker = f'<div class="breaking-news-ticker"><div class="breaking-label">BREAKING</div><marquee class="breaking-marquee" behavior="scroll" direction="left" onmouseover="this.stop();" onmouseout="this.start();">{ticker_items}</marquee></div>'

# 4. Latest Mix Section (BBC Style)
mix_posts = all_arts[:20]
dyn_html = ""
if mix_posts:
    featured_mix = mix_posts[0]
    dyn_html += f'''
<div class="section-header"><h2>Latest Mix</h2></div>
<div class="grid-featured">
    <div class="featured-large">
        <a href="{featured_mix["href"]}">
            <img src="{featured_mix["img"]}" alt="{featured_mix["title"]}" loading="lazy" width="800" height="450" decoding="async">
            <div class="overlay">
                <h3>{featured_mix["title"]}</h3>
            </div>
        </a>
    </div>
    <div class="hero-sidebar hero-sidebar-scroll">
'''
    for a in mix_posts[1:]:
        dyn_html += f'''
        <div class="hero-side-item">
            <div>
                <h3><a href="{a["href"]}">{a["title"]}</a></h3>
            </div>
        </div>
'''
    dyn_html += '</div></div>'

# 5. Category Sections (10 Blocks)
for cat in DEFAULT_CATEGORIES:
    if cat in ["ads"]: continue
    c_posts = sorted(cat_arts[cat], key=lambda x: x["date"], reverse=True)
    if not c_posts: continue
    
    cat_block_html = f'<div class="section-header"><h2>{cat.title()}</h2><a href="/{cat}/" class="see-all">See All →</a></div><div class="grid-featured">'
    featured = c_posts[0]
    cat_block_html += f'''
    <div class="featured-large">
        <a href="{featured["href"]}">
            <img src="{featured["img"]}" alt="{featured["title"]}" loading="lazy" width="800" height="450" decoding="async">
            <div class="overlay">
                <h3>{featured["title"]}</h3>
            </div>
        </a>
    </div>
    <div class="hero-sidebar hero-sidebar-scroll">
'''
    for a in c_posts[1:5]:
        cat_block_html += f'''
        <div class="hero-side-item">
            <div>
                <h3><a href="{a["href"]}">{a["title"]}</a></h3>
            </div>
        </div>
'''
    cat_block_html += '</div></div>'
    dyn_html += cat_block_html

    # Generate Category Index Page
    os.makedirs(os.path.join(OUTPUT_DIR, cat), exist_ok=True)
    category_title = "Mind Manipulation" if cat == "mind-manipulation" else cat.title()
    category_description = f"Latest {category_title} articles, explainers, analysis, and practical guidance from GenZ Frontier."
    heading_html = f'<div class="section-header"><h1>{html.escape(category_title)}</h1></div>'
    cat_grid_html = heading_html + '<div class="grid-4">'
    for a in c_posts:
        cat_grid_html += f'''
        <article class="news-card">
            <img src="{a["img"]}" alt="{a["title"]}" loading="lazy" width="400" height="225" decoding="async">
            <a href="{a["href"]}"><h3>{a["title"]}</h3></a>
        </article>'''
    cat_grid_html += '</div>'
    cat_index_content = index_template.replace("{{HERO_SECTION}}", "").replace("{{DYNAMIC_CONTENT}}", cat_grid_html).replace("{{BREAKING_NEWS_TICKER}}", ticker)
    cat_index_content = cat_index_content.replace("{{META_TAGS}}", "").replace("{{SCHEMA_DATA}}", "").replace("{{LIVE_STATUS_SCRIPT}}", LIVE_SCRIPT_HTML).replace("{{INDEX_AD_SLOT}}", category_ad_slot_html(cat))
    category_meta = f'<meta name="description" content="{html.escape(category_description, quote=True)}"><meta property="og:title" content="{html.escape(category_title, quote=True)} | GenZ Frontier"><meta property="og:description" content="{html.escape(category_description, quote=True)}">'
    cat_index_content = cat_index_content.replace('<title>GenZ Frontier | Breaking News, Latest News and Videos</title>', f'<title>{html.escape(category_title)} | GenZ Frontier</title>' + category_meta)
    cat_index_content = ensure_image_alt_attributes(normalize_html_links(cat_index_content), category_title)
    with open(os.path.join(OUTPUT_DIR, cat, "index.html"), "w", encoding="utf-8") as f: f.write(cat_index_content)

# Generate Article Pages
for art in all_arts:
    with open(os.path.join(NEWS_DIR, art["cat"], art["file"].replace(".html", ".md")), "r", encoding="utf-8") as f:
        md_content = f.read()
    
    all_candidates = [candidate for candidate in all_arts if candidate["url"] != art["url"]]
    entity_pool = sorted(
        [candidate for candidate in all_candidates if related_entity_score(art, candidate) > 0],
        key=lambda candidate: (related_entity_score(art, candidate), candidate.get("date", "")),
        reverse=True
    )
    topic_pool = sorted(
        [candidate for candidate in all_candidates if related_topic_score(art, candidate) > 0],
        key=lambda candidate: (related_topic_score(art, candidate), candidate.get("date", "")),
        reverse=True
    )
    fallback_candidates = sorted(
        [candidate for candidate in cat_arts[art["cat"]] if candidate["url"] != art["url"]],
        key=lambda candidate: candidate.get("date", ""),
        reverse=True
    ) + all_candidates
    related_pool = dedupe_articles(entity_pool or topic_pool or fallback_candidates, exclude_url=art["url"])
    related_cards = related_pool[:3]
    next_related = related_pool[3] if len(related_pool) > 3 else (related_pool[0] if related_pool else None)
    matched_entity = primary_entity_key(art)
    if matched_entity:
        related_heading = f"More from {entity_display_name(matched_entity)}"
        related_intro = f"Explore other GenZ Frontier articles connected to {entity_display_name(matched_entity)}."
        relation_label = "Same person or entity"
    elif topic_pool:
        related_heading = "More on This Topic"
        related_intro = "Continue with closely related explainers and reporting from this topic cluster."
        relation_label = "Related topic"
    else:
        related_heading = "Suggested For You"
        related_intro = "Continue reading with carefully selected coverage from the same section."
        relation_label = "From this section"
    related_html = f'<div class="related-section"><div class="section-header"><h2>{html.escape(related_heading)}</h2></div><p class="related-intro">{html.escape(related_intro)}</p><div class="grid-3">'
    related_html += render_related_cards(related_cards, relation_label)
    related_html += '</div>'
    if next_related:
        related_html += f'''<div class="next-related-wrap"><span class="next-related-label">Next related article</span><a class="next-related-button" href="{html.escape(next_related["href"], quote=True)}"><span>{html.escape(topic_label_for_article(next_related))}</span><strong>Read next <span aria-hidden="true">→</span></strong></a></div>'''
    related_html += '</div>'

    video_url = ""
    iframe_match = re.search(r'<iframe.*?src=["\'](.*?)["\']', md_content, re.IGNORECASE)
    video_tag_match = re.search(r'<video.*?src=["\'](.*?)["\']', md_content, re.IGNORECASE)
    source_video_match = re.search(r'<source.*?src=["\'](.*?\.(?:mp4|webm|m4v|ogv|ogg))["\']', md_content, re.IGNORECASE)
    direct_video_match = re.search(r'\[.*?\]\((.*?\.(mp4|webm|m4v|ogv|ogg))\)', md_content, re.IGNORECASE)

    if iframe_match: video_url = iframe_match.group(1)
    elif video_tag_match: video_url = video_tag_match.group(1)
    elif source_video_match: video_url = source_video_match.group(1)
    elif direct_video_match: video_url = direct_video_match.group(1)

    if video_url and video_url.startswith("//"): video_url = "https:" + video_url
    elif video_url and not video_url.startswith(("http://", "https://", "/")):
        video_url = "/" + video_url

    seo_title = shorten_seo_title(art["title"])
    safe_title = html.escape(seo_title, quote=True)
    safe_desc = html.escape(art["desc"] or f"{art['title']}. Evidence-based guidance from GenZ Frontier.", quote=True)
    safe_img = html.escape(art["img"], quote=True)
    safe_url = html.escape(art["url"], quote=True)
    meta_tags = f'''
    <meta name="description" content="{safe_desc}">
    <meta property="og:title" content="{safe_title} - GenZ Frontier">
    <meta property="og:description" content="{safe_desc}">
    <meta property="og:image" content="{safe_img}">
    <meta property="og:url" content="{safe_url}">
    <meta name="twitter:card" content="summary_large_image">
    '''
    # Build JSON-LD as a Python object instead of interpolating fragments into a
    # hand-written JSON string. This prevents malformed commas/braces and safely
    # escapes characters that could terminate the script element.
    schema_object = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": art["title"],
        "image": [art["img"]],
        "datePublished": normalize_date(art["date"]),
        "dateModified": normalize_date(art["date"]),
        "author": {"@type": "Organization", "name": "GenZ Frontier"},
        "publisher": {
            "@type": "Organization",
            "name": "GenZ Frontier",
            "url": BASE_URL
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": art["url"]}
    }
    schema_json = json.dumps(schema_object, ensure_ascii=False, separators=(",", ":"))
    schema_json = (schema_json.replace("<", "\\u003c")
                             .replace(">", "\\u003e")
                             .replace("&", "\\u0026"))
    schema_data = f'<script type="application/ld+json">{schema_json}</script>'

    # Convert markdown to HTML
    validate_local_video_references(md_content)
    article_html = md_parser.convert(md_content)
    article_html = clean_canonical_reference(article_html, art["url"])
    article_html = normalize_article_headings(article_html, art["title"])
    article_html = ensure_image_alt_attributes(article_html, art["title"])
    article_html = normalize_html_links(article_html)
    article_html = enhance_video_markup(article_html)
    # Source Markdown may retain historical SVG references; render optimized WebP instead.
    article_html = re.sub(r'(?P<prefix>/news/mind-manipulation/images/[^"\']+)\.svg(?P<suffix>["\'])', r'\g<prefix>.webp\g<suffix>', article_html, flags=re.IGNORECASE)
    article_html = add_avif_picture(article_html)
    # Keep wide tables readable on phones without changing their semantic HTML.
    article_html = re.sub(
        r'(?s)<table(?:\s[^>]*)?>.*?</table>',
        lambda match: '<div class="article-table-wrap" role="region" aria-label="Scrollable data table" tabindex="0">' + match.group(0) + '</div>',
        article_html
    )
    
    # User-approved ad policy: exclude Social Bar and choose exactly one banner
    # profile per substantive article. No header, footer, or stacked ad injection.
    ads_enabled = True
    word_count = len(re.findall(r"\b\w+\b", md_content, flags=re.UNICODE))
    selected_profile = choose_article_ad_profile(art, word_count) if ads_enabled else ""
    article_ad_html = ad_slot_html(selected_profile) if selected_profile else ""
    article_desktop_ad_html = ""
    social_bar_html = ""
    paragraph_ends = list(re.finditer(r"</p>", article_html, flags=re.IGNORECASE))
    # Every non-empty article receives one selected unit, but never before the
    # title. Longer articles get a midpoint slot; short articles get the slot
    # after their body so the header and opening remain uncluttered.
    if article_ad_html:
        if len(paragraph_ends) >= 4:
            midpoint = paragraph_ends[max(1, (len(paragraph_ends) // 2) - 1)].end()
            article_html = article_html[:midpoint] + article_ad_html + article_html[midpoint:]
        elif len(paragraph_ends) >= 2:
            insertion = paragraph_ends[0].end()
            article_html = article_html[:insertion] + article_ad_html + article_html[insertion:]
        elif article_html.strip():
            article_html += article_ad_html

    # === Map Views to Article (New) ===
    article_path = art["href"]
    total_views = all_page_views.get(article_path, "0")
    # ==================================

    final_html = template.replace("{{NEWS_CONTENT}}", article_html).replace("{{ARTICLE_TITLE}}", seo_title) \
                         .replace("{{BREAKING_NEWS_TICKER}}", ticker).replace("{{VIDEO_URL}}", video_url) \
                         .replace("{{RELATED_POSTS}}", related_html).replace("{{META_TAGS}}", meta_tags).replace("{{SCHEMA_DATA}}", schema_data) \
                         .replace("{{CANONICAL_URL}}", art["url"]) \
                         .replace("{{ARTICLE_DESKTOP_AD}}", article_desktop_ad_html) \
                         .replace("{{SOCIAL_BAR_SCRIPT}}", social_bar_html) \
                         .replace('id="total-views">--', f'id="total-views">{total_views}') \
                         .replace("{{LIVE_STATUS_SCRIPT}}", LIVE_SCRIPT_HTML) # === Inject Live Script ===
    
    article_output_dir = os.path.join(OUTPUT_DIR, art["cat"], art["slug"])
    os.makedirs(article_output_dir, exist_ok=True)
    with open(os.path.join(article_output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(final_html)

    # Preserve old .html URLs while consolidating SEO signals on the clean URL.
    legacy_path = os.path.join(OUTPUT_DIR, art["cat"], art["file"])
    moved_description = html.escape(f"{seo_title} has moved to its clean GenZ Frontier URL.", quote=True)
    legacy_redirect = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><link rel="canonical" href="{art["url"]}"><meta name="robots" content="noindex,follow"><meta name="description" content="{moved_description}"><title>{html.escape(seo_title)} | GenZ Frontier</title></head><body><main><h1>Article moved</h1><p>This article moved to <a rel="canonical" href="{art["href"]}">{html.escape(art["url"])}</a>.</p></main></body></html>'''
    with open(legacy_path, "w", encoding="utf-8") as f:
        f.write(legacy_redirect)

with open(os.path.join(OUTPUT_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
    home_html = index_template.replace("{{HERO_SECTION}}", hero_html).replace("{{DYNAMIC_CONTENT}}", dyn_html).replace("{{BREAKING_NEWS_TICKER}}", ticker)
    home_html = ensure_image_alt_attributes(normalize_html_links(home_html), "GenZ Frontier")
    home_description = html.escape(STATIC_PAGE_DESCRIPTIONS["index.html"], quote=True)
    home_html = home_html.replace('<title>GenZ Frontier | Breaking News, Latest News and Videos</title>', '<title>GenZ Frontier | Breaking News, Latest News and Videos</title><meta name="description" content="' + home_description + '">')
    home_html = home_html.replace("{{META_TAGS}}", "").replace("{{SCHEMA_DATA}}", "").replace("{{LIVE_STATUS_SCRIPT}}", LIVE_SCRIPT_HTML).replace("{{INDEX_AD_SLOT}}", ad_slot_html("native", placement="home"))
    f.write(home_html)

generate_sitemap(all_arts)
print("✅ Build Complete with GA4 Data!")