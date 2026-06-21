# 🚀 GenZ Frontier News Portal
![GitHub Pages](https://img.shields.io/badge/Hosted_on-GitHub_Pages-181717?style=flat-square&logo=github)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)
![Automation](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?style=flat-square&logo=github-actions)
![Python](https://img.shields.io/badge/Script-Python_3.10-3776AB?style=flat-square&logo=python)
![genzfrontier logo](https://i.ibb.co/LXZv7DjY/IMG-4776.jpg)

GenZ Frontier is a modern, automated, and serverless news publishing platform built entirely with **Markdown**, **Python**, and **GitHub Actions**. This guide provides a complete overview of the system architecture, build logic, and critical guardrails to maintain the platform.
---
[![Broken Link Checker](https://github.com/Sayadbayezid/GenZFrontier/actions/workflows/link-checker.yml/badge.svg)](https://github.com/Sayadbayezid/GenZFrontier/actions/workflows/link-checker.yml)

---

## 🏗️ System Architecture & Build Logic

The core of GenZ Frontier is the `build.py` script. It transforms raw content into a high-performance, SEO-optimized news portal using a **BBC-style layout**.

### 1. Dynamic Layout Engine
The homepage (`index.html`) is generated using five main dynamic blocks:
- **Global Hero:** Automatically picks the **latest 1 post** globally to feature as the main story.
- **Breaking News Ticker:** A right-to-left scrolling bar featuring the **latest 15 posts** globally.
- **Live Updates Section:** A sidebar next to the hero displaying a scrollable list of the **latest 15 posts** with thumbnails.
- **Latest Mix (BBC Style):** A large section featuring **1 main story** and a list of **19 recent titles**, totaling 20 posts.
- **Category Blocks:** 10 specific categories (*World, Politics, Business, Tech, Science, Health, Sports, Entertainment, Careers, Legacy Archives*). Each block shows **1 featured post** with an image and **4 titles** as a list.

### 2. Automated SEO & Sitemap
- **Valid ISO Dates:** The sitemap generator extracts dates from Git history or markdown metadata and converts them to valid ISO 8601 format (`YYYY-MM-DD`).
- **Dynamic Metadata:** The system automatically generates Meta descriptions, Open Graph tags, and Twitter cards for every article.
- **JSON-LD Schema:** Automated schema injection for every article to improve Google Search visibility and Adsense approval.
- **llms.txt:** A dedicated file for AI crawlers is generated in the root directory.

### 3. Video Auto-Popup System
The system scans markdown files for `<iframe>` tags (YouTube, Facebook, Vimeo), `<video>` tags, or direct video links. If a video is detected, a floating popup is automatically enabled for that article.

---

## ⚠️ CRITICAL GUARDRAILS (Must Read Before Updating)

To prevent the website architecture from breaking, you **MUST** follow these rules strictly:

### 1. Visual Design & CSS
- **DO NOT** modify the existing Tailwind CSS classes, glassmorphism effects, or color palettes.
- **DO NOT** change the DOM structure of the header, navigation, or footer.
- **ABSOLUTE PATHS ONLY:** All links in `template.html` and `index.html` must use absolute paths (e.g., `<a href="/tech/">` instead of `../tech/`). This ensures styling works on sub-pages.

### 2. Category Management
- **The "Ads" Rule:** The `news/ads` folder is for local monetization. It is processed by the build script but **MUST NOT** be added to the public navigation menu or the sitemap.
- **Folder Structure:** Every category folder inside `/news/` must have a corresponding logic in `build.py` to generate its `index.html`.

### 3. Template Placeholders
The `template.html` relies on specific placeholders. **DO NOT** remove these:
- `{{TITLE}}`, `{{DESCRIPTION}}`, `{{IMAGE}}`, `{{AUTHOR}}`, `{{DATE}}`
- `{{CONTENT}}` — Main article body.
- `{{RELATED_POSTS}}` — The "Suggested For You" grid.
- `{{VIDEO_URL}}` — The URL for the auto-popup system.
- `{{META_TAGS}}`, `{{SCHEMA_DATA}}` — SEO and Schema injection points.

---

## 🛠️ How to Use & Update

### Publishing a New Article
1. Create a `.md` file in the appropriate category folder (e.g., `/news/tech/my-article.md`).
2. Use the **GenZ Frontier Markdown Style** (see the Bonus Tips section below).
3. Commit and push. GitHub Actions will handle the rest.

### Manually Triggering a Build
If you want to update the sitemap or rebuild without adding a new post:
1. Go to the **Actions** tab in your GitHub repository.
2. Select **Deploy GenZ Frontier News**.
3. Click **Run workflow**.

---

## 👨‍💻 Developed & Maintained By

### Sayad Md Bayezid Hosan
🌐 Website: [sayadbayezid.com](https://www.sayadbayezid.com)

---

## 🎁 Bonus: AI Article Prompt Pipeline
Use this format to generate news articles perfectly formatted for this system:

```markdown
Title: [Bengali title]
description: [1-2 sentence summary]
image: [Image URL]
date: [e.g., June 20, 2026]
author: Sayad Md Bayezid Hosan
breaking: [true/false]

![GenZ Frontier News Header]([Image URL])

# [Title]

**[নিজস্ব প্রতিবেদক] | [তারিখ]**

[Article Content with ### subheadings]

SEO-Friendly File Name: [slug].md
```

---

## 📄 License
This project is open-source for educational and personal use. Feel free to fork and customize!
