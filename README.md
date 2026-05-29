# GenZ Frontier News Portal

![GitHub Pages](https://img.shields.io/badge/Hosted_on-GitHub_Pages-181717?style=flat-square&logo=github)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)
![Automation](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?style=flat-square&logo=github-actions)
![Python](https://img.shields.io/badge/Script-Python_3.10-3776AB?style=flat-square&logo=python)

GenZ Frontier is a modern, dynamic, and automated news portal designed for fast content delivery. The platform operates on a completely serverless architecture using **Markdown (.md)** files, allowing authors to publish news seamlessly without writing HTML.

The backend relies on **GitHub Actions** and a custom **Python Build Script** that automatically converts Markdown articles into responsive HTML pages and deploys them to GitHub Pages.

---

## 🏗️ Architecture & Features

- **Automated Deployment:** GitHub Actions automatically builds and deploys the site upon every commit.
- **Markdown to HTML Conversion:** A custom `build.py` script parses Markdown files and injects them into the UI template.
- **Dynamic Category Indexing:** Automatically generates index pages (`index.html`) for every news category.
- **CNN-Style Dark UI:** Premium dark header and white content area for optimal reading experience.
- **Integrated Live TV:** Floating video popup player integrated with news articles and the main header.
- **Local Storage Auth:** Lightweight client-side authentication mock-up for user login simulation.

---

## 📂 Repository Structure

```text
GenZFrontier/
│
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions automation script
│
├── news/                    # 📝 Add all your Markdown (.md) news here
│   ├── business/
│   ├── entertainment/
│   ├── health/
│   ├── politics/
│   ├── science/
│   ├── sports/
│   ├── tech/
│   └── world/
│
├── index.html               # Main website homepage
├── template.html            # Article layout template
├── 404.html                 # Custom 404 Error Page
├── build.py                 # Core Python script for MD -> HTML generation
└── README.md                # Project documentation
✍️ How to Publish a News Article
Publishing a new article is incredibly simple. You do not need to edit any HTML files.
1 Navigate to the ⁠news/⁠ directory.
2 Select the appropriate category folder (e.g., ⁠tech/⁠).
3 Create a new Markdown file (e.g., ⁠meta-ai-update.md⁠). Use hyphens instead of spaces in the filename.
4 Write your news content using standard Markdown syntax.
5 Commit the changes.
GitHub Actions will automatically trigger the build process, and your article will be live within 2-3 minutes!
##Example Markdown Format
# Main Headline Goes Here

Your news content starts here. You can use **bold text**, *italics*, and lists.

## Subheading

To add a video to your article (which triggers the Live TV popup), just paste the YouTube iframe:

<iframe width="560" height="315" src="[https://www.youtube.com/embed/YOUR_VIDEO_ID](https://www.youtube.com/embed/YOUR_VIDEO_ID)" frameborder="0" allowfullscreen></iframe>
⚙️ Technical Build Process (build.py)
The custom Python script handles the core logic of the site generation:
1 Cleans the existing ⁠public⁠ directory.
2 Copies ⁠index.html⁠ and ⁠404.html⁠ to the output folder.
3 Scans all ⁠.md⁠ files inside the ⁠news/⁠ subdirectories.
4 Converts Markdown to HTML using the ⁠markdown⁠ library.
5 Injects the converted HTML into the ⁠{{NEWS_CONTENT}}⁠ placeholder inside ⁠template.html⁠.
6 Generates dynamic category index pages containing links to all articles within that category.
🌐 Live Preview
The site is currently hosted on GitHub Pages and can be accessed here:
Visit GenZ Frontier
Developed & Maintained by Sayad Md Bayezid Hosan for Connect With Bayezid (CWB Agency).

