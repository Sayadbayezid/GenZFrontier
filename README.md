# 🚀 GenZ Frontier News Portal

![GitHub Pages](https://img.shields.io/badge/Hosted_on-GitHub_Pages-181717?style=flat-square&logo=github)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)
![Automation](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?style=flat-square&logo=github-actions)
![Python](https://img.shields.io/badge/Script-Python_3.10-3776AB?style=flat-square&logo=python)

GenZ Frontier is a modern, automated, and serverless news publishing platform built entirely with **Markdown**, **Python**, and **GitHub Actions**.

The project is designed for ultra-fast publishing workflows where contributors can create articles using simple `.md` files without touching HTML or backend infrastructure.

A custom Python build system automatically converts Markdown articles into responsive HTML pages and deploys them directly to GitHub Pages.

---

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

# 📄 License

This project is open-source and available for educational and personal use.

Feel free to fork, customize, and improve it.