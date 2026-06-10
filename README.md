# 🚀 GenZ Frontier News Portal
genzFrontier logo(https://i.ibb.co/LXZv7DjY/IMG-4776.jpg)
![GitHub Pages](https://img.shields.io/badge/Hosted_on-GitHub_Pages-181717?style=flat-square&logo=github)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)
![Automation](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?style=flat-square&logo=github-actions)
![Python](https://img.shields.io/badge/Script-Python_3.10-3776AB?style=flat-square&logo=python)

GenZ Frontier is a modern, automated, and serverless news publishing platform built entirely with **Markdown**, **Python**, and **GitHub Actions**.

The project is designed for ultra-fast publishing workflows where contributors can create articles using simple `.md` files without touching HTML or backend infrastructure.

A custom Python build system automatically converts Markdown articles into responsive HTML pages and deploys them directly to GitHub Pages.

---
<!-- START_LINK_CHECKER -->

### ⏳ Loading link status...

The automated system will update this section daily.

<!-- END_LINK_CHECKER -->
# 🌐 Live Demo

👉 **Visit the Website:**  
https://sayadbayezid.github.io/GenZFrontier/

---

# ✨ Core Features

## ⚡ Fully Automated Deployment

Every push to the repository automatically triggers a GitHub Actions workflow that builds and deploys the website.

## 📝 Markdown-Based Publishing

Writers only need to create Markdown files inside category folders. No HTML knowledge required.


## 🧠 Custom Python Build System

The `build.py` script dynamically:

- Parses Markdown articles
- Converts Markdown to HTML
- Injects content into templates
- Generates category index pages
- Creates SEO-friendly article structures

## 🎨 Modern CNN-Style UI

The interface features:

- Premium dark navigation header
- Clean white reading layout
- Responsive mobile-first design
- Optimized typography for readability

## 📺 Integrated Live TV Popup

Articles support embedded YouTube videos that automatically trigger a floating live TV player.

## 🔐 Lightweight Client-Side Authentication

LocalStorage-based login simulation for lightweight authentication demos.

## 📂 Dynamic Category Indexing

Each news category automatically receives its own generated `index.html` page listing all related articles.

---

# 🏗️ Project Architecture

```text
GenZFrontier/
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── news/
│   ├── business/
│   ├── entertainment/
│   ├── health/
│   ├── politics/
│   ├── science/
│   ├── sports/
│   ├── tech/
│   └── world/
│
├── index.html
├── template.html
├── 404.html
├── build.py
└── README.md
```

---

# ✍️ Publishing a News Article

Publishing content is extremely simple.

## Step 1 — Open the News Directory

Navigate to:

```text
/news/
```

## Step 2 — Choose a Category

Example:

```text
/news/tech/
```

## Step 3 — Create a Markdown File

Example filename:

```text
meta-ai-update.md
```

> Use hyphens (`-`) instead of spaces in filenames.

## Step 4 — Write Your Article

Use standard Markdown syntax.

Example:

```markdown
# Main Headline

Your article content goes here.

## Subheading

More article details...
```

## Step 5 — Commit & Push

Once pushed to GitHub:

- GitHub Actions automatically starts the build process
- HTML pages are generated
- Deployment happens automatically
- The article becomes live within minutes

---

# 🎥 Embedding Videos

To embed YouTube videos inside an article, simply paste a standard iframe:

```html
<iframe
  width="560"
  height="315"
  src="https://www.youtube.com/embed/YOUR_VIDEO_ID"
  frameborder="0"
  allowfullscreen>
</iframe>
```

This automatically activates the integrated floating Live TV popup system.

---

# ⚙️ Technical Build Process

The custom `build.py` script performs the following tasks:

1. Cleans the existing output directory
2. Copies static assets and base pages
3. Scans all Markdown files inside `/news/`
4. Converts Markdown into HTML using the Python `markdown` library
5. Injects generated content into `template.html`
6. Builds dynamic category pages
7. Generates internal article links automatically
8. Prepares the final static site for deployment

---

# 🚀 Deployment Workflow

The project uses GitHub Actions for CI/CD automation.

## Workflow Overview

```text
Push Commit
     ↓
GitHub Actions Triggered
     ↓
Python Build Script Executes
     ↓
Static HTML Generated
     ↓
GitHub Pages Deployment
     ↓
Website Updated Live
```

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| HTML5 | Frontend Structure |
| CSS3 | Styling & Responsive UI |
| JavaScript | Client-side Interactions |
| Python 3.10 | Build Automation |
| Markdown | Content Authoring |
| GitHub Actions | CI/CD Automation |
| GitHub Pages | Hosting Platform |

---

# 📌 Example Markdown Article

```markdown
# Apple Announces New AI Features

Apple has officially introduced its latest AI-powered ecosystem updates.

## Highlights

- Smarter Siri
- AI-assisted productivity
- Improved on-device processing

Stay tuned for more updates.
```

---

# 💖 Support the Project

If you find this project useful, consider supporting its development.

Your support helps maintain the project and keep it free for everyone.

<div align="left">

<a href="https://www.paypal.me/connectwithbayezid" target="_blank">
  <img src="https://raw.githubusercontent.com/bayzed123/sayadbayezid-portfolio-/main/assets/images/paypal_logo.png" width="150" alt="Support via PayPal">
</a>

&nbsp;&nbsp;&nbsp;&nbsp;

<a href="https://www.payoneer.com/" target="_blank">
  <img src="https://raw.githubusercontent.com/bayzed123/sayadbayezid-portfolio-/main/assets/images/payoneer_logo.png" width="150" alt="Support via Payoneer">
</a>

</div>

## Donation Methods

- **PayPal:** https://www.paypal.me/connectwithbayezid
- **Payoneer:** `cwb.agency@outlook.com`

---

# 👨‍💻 Developed & Maintained By

## Sayad Md Bayezid Hosan

🌐 Website:  
https://www.sayadbayezid.com

---
# Bunas tips use this format Write News 
# GenZ Frontier News - AI Prompt Pipeline

Whenever I want to generate a news article for GenZ Frontier, I will provide you with a raw text, draft, or some context along with image links. Your task is to process that raw input and format it EXACTLY according to the "GenZ Frontier Markdown Style" described below. 

### ⚠️ STRICT RULES FOR AI:
1. **No Conversational Filler:** DO NOT say "Here is your article" or "Let me know if you need changes." ONLY output the final markdown code block.
2. **Strict Structure:** You must follow the exact YAML-like metadata frontmatter, header image, title, and body structure provided in the template.
3. **Author Name:** Always use "Sayad Md Bayezid Hosan" as the default author unless I specify another name in the prompt.
4. **Subheadings:** Use `###` for subheadings inside the article. Make them catchy and relevant.
5. **SEO Slug:** Always generate an SEO-friendly URL slug (in Roman Bengali or English) at the end of the output.
6. **Date:** Use the current date or the date provided in the raw text.

---

### 📋 THE EXACT FORMAT TEMPLATE (Copy this structure exactly):

```markdown
Title: [Generate a strong, click-worthy Bengali title]
description: [Write a 1-2 sentence meta description summarizing the news]
image: [Insert provided Image URL here]
date: [e.g., June 2, 2026]
author: Sayad Md Bayezid Hosan
breaking: [true/false based on news urgency]

![GenZ Frontier News Header]([Insert provided Image URL here])

# [Same as Title]

**[নিজস্ব প্রতিবেদক / স্পেশাল করেসপন্ডেন্ট / স্থান] | [তারিখ, যেমন: ০২ জুন ২০২৬]**

[Write the first introduction paragraph here. It should be engaging and summarize the core event.]

### [Catchy Subheading 1]
[Elaborate the first part of the news/raw text here.]

### [Catchy Subheading 2]
[Elaborate the second part of the news/raw text here.]

*(Continue with more subheadings if the text is long)*
SEO-Friendly File Name / URL Slug:
⁠[generate-seo-friendly-slug-with-hyphens].md⁠
📥 HOW TO USE THIS PIPELINE:
When I am ready, I will send you a prompt like this:
"Please write a GenZ Frontier news using the following raw text and image: [My Raw Text] [Image Link]"
You will immediately apply the rules and output the formatted markdown.
# 📄 License

This project is open-source and available for educational and personal use.

Feel free to fork, customize, and improve it.
