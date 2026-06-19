# How to Manage Legacy Archives

This guide explains how to add and update legacy archives in the GenZ Frontier repository.

## 1. Where to Place Your Files
You can manage your legacy archives in one of two places:
- **Option A (Recommended):** Place your folder in the root directory: `/legacy-archives/`
- **Option B:** Place your folder inside the news directory: `/news/legacy-archives/`

The build script will automatically find the folder and copy it to the `public/` directory for deployment.

## 2. Adding a New Archive Page
1. Create a new HTML file inside the `legacy-archives` folder (e.g., `new-hero-legacy.html`).
2. Open `legacy-archives/index.html`.
3. Find the "Grid Cards" section (around line 137).
4. Copy an existing card block and update the `href`, `img src`, title, and description.

Example Card:
```html
<a href="https://www.genzfrontir.com/legacy-archives/new-hero-legacy" class="archive-card group block bg-[#0f172a] border border-slate-800 rounded-2xl overflow-hidden relative">
    <div class="card-img-wrapper h-64 w-full bg-slate-900 relative">
        <img src="YOUR_IMAGE_URL" alt="New Hero" class="card-img w-full h-full object-cover opacity-70 group-hover:opacity-100 grayscale group-hover:grayscale-0">
        <div class="absolute inset-0 bg-gradient-to-t from-[#0f172a] to-transparent"></div>
        <span class="absolute top-4 left-4 bg-blue-600/80 text-white text-xs font-bold px-3 py-1 rounded-full bangla-font backdrop-blur-sm">Category</span>
    </div>
    <div class="p-8">
        <h3 class="text-2xl font-bold bangla-font text-white mb-3 group-hover:text-cyan-400 transition-colors">New Hero Name</h3>
        <p class="text-slate-400 bangla-font text-sm leading-relaxed mb-6">Description of the legacy.</p>
        <div class="flex items-center text-cyan-500 font-bold bangla-font text-sm">
            আর্কাইভ দেখুন <span class="ml-2 transition-transform group-hover:translate-x-2">→</span>
        </div>
    </div>
</a>
```

## 3. Deployment
Once you have added your files:
1. Run `python3 build.py` (if you are working locally).
2. Commit and push your changes to GitHub.
3. The GitHub Actions will automatically deploy the updated `public/` folder.

**Note:** Never manually edit files inside the `public/` folder, as they will be overwritten by the build script. Always edit the source files in the root or `news/` directory.
