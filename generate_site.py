#!/usr/bin/env python3

import os
import shutil
import re
import markdown
from bs4 import BeautifulSoup
import subprocess
from pathlib import Path
from collections import defaultdict

# Configuration
POSTS_DIR = "posts"
OUTPUT_DIR = "docs"

def slugify(text):
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '-')

def get_section_title(sec_md):
    for line in sec_md.splitlines():
        stripped = line.strip()
        if stripped.startswith('## '):
            return stripped[3:].strip()
    return 'Introduction'

# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create assets directory and CSS if not exists
assets_dir = os.path.join(OUTPUT_DIR, "assets")
css_dir = os.path.join(assets_dir, "css")
os.makedirs(css_dir, exist_ok=True)
css_path = os.path.join(css_dir, "style.css")
if not os.path.exists(css_path):
    with open(css_path, "w") as f:
        f.write("""
body {
    display: flex;
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}
#sidebar {
    width: 250px;
    background-color: #f0f0f0;
    padding: 40px;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #ddd;
}
#sidebar h2 {
    margin-top: 0;
}
#content {
    margin-left: 330px;
    padding: 40px;
    max-width: 80ch;
    font-size: 1.1em; /* Larger main text */
}
.navigation {
    margin-top: 40px;
    display: flex;
    justify-content: space-between;
}
.navigation a {
    text-decoration: none;
    color: #007bff;
    font-weight: bold;
}
details {
    margin-bottom: 20px; /* More vertical whitespace */
}
summary {
    cursor: pointer;
    font-weight: bold;
}
ul {
    list-style: none;
    padding-left: 20px;
    margin: 0;
}
a {
    text-decoration: none;
    color: #007bff; /* Shade of blue, no underline */
}
a:hover {
    text-decoration: underline; /* Optional hover underline */
}
""")

# Create JS for accordion persistence if not exists
js_dir = os.path.join(assets_dir, "js")
os.makedirs(js_dir, exist_ok=True)
js_path = os.path.join(js_dir, "script.js")
if not os.path.exists(js_path):
    with open(js_path, "w") as f:
        f.write("""
document.addEventListener('DOMContentLoaded', () => {
    const details = document.querySelectorAll('details');
    const storageKey = 'accordionState';

    // Restore state
    const savedState = JSON.parse(localStorage.getItem(storageKey)) || {};
    details.forEach((detail, index) => {
        const key = `detail-${index}`;
        if (savedState[key] !== undefined) {
            detail.open = savedState[key];
        }
        detail.addEventListener('toggle', () => {
            savedState[key] = detail.open;
            localStorage.setItem(storageKey, JSON.stringify(savedState));
        });
    });
});
""")

# Clear old content except assets
for item in os.listdir(OUTPUT_DIR):
    item_path = os.path.join(OUTPUT_DIR, item)
    if os.path.isdir(item_path) and item != 'assets':
        shutil.rmtree(item_path)
    elif item == 'index.html':
        os.remove(item_path)

# Find all .md files recursively
post_list = []
for md_path in Path(POSTS_DIR).rglob('*.md'):
    post_dir = md_path.parent
    post_name = str(post_dir.relative_to(POSTS_DIR)).replace('\\', '/')
    if post_name == '.' or 'docs' in post_name.lower() or 'venv' in post_name.lower():
        continue  # Skip root .md or non-content dirs
    post_list.append((post_name, md_path))

# Sort by post_name
post_list.sort(key=lambda x: x[0])

# Collect category data with sections
category_data = defaultdict(list)
for post_name, md_path in post_list:
    category = post_name.split('/')[0]
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    # Extract post_title
    html_temp = markdown.markdown(md_content)
    soup_temp = BeautifulSoup(html_temp, 'html.parser')
    h1s = soup_temp.find_all('h1')
    post_title = h1s[0].text.strip() if h1s else post_name.replace('/', ' ').replace('_', ' ').replace('-', ' ').title()
    # Split MD into sections
    sections = []
    current_section_lines = []
    current_slug = 'index'
    for line in md_content.splitlines(keepends=True):
        if line.strip().startswith('## '):
            if current_section_lines:
                sections.append((current_slug, ''.join(current_section_lines).strip()))
            current_slug = slugify(line.strip()[3:].strip())
            current_section_lines = [line]
        else:
            current_section_lines.append(line)
    if current_section_lines:
        sections.append((current_slug, ''.join(current_section_lines).strip()))
    # Merge if index has only # followed by empty lines
    if len(sections) > 1:
        index_md = sections[0][1]
        index_lines = index_md.splitlines(keepends=True)
        h1_index = next((i for i, line in enumerate(index_lines) if line.strip().startswith('# ')), -1)
        if h1_index != -1:
            after_h1 = index_lines[h1_index + 1:]
            if all(line.strip() == '' for line in after_h1):
                # Merge first ## into index
                first_sub_md = sections[1][1]
                new_index_md = index_md + first_sub_md
                sections = [('index', new_index_md)] + sections[2:]
    # Collect section titles and store sections_md
    section_list = []
    for slug, sec_md in sections:
        sec_title = get_section_title(sec_md)
        section_list.append((slug, sec_title))
    category_data[category].append({
        'post_name': post_name,
        'post_title': post_title,
        'sections': section_list,
        'sections_md': sections
    })

# Sort categories and posts within
sorted_categories = sorted(category_data.keys())
for cat in sorted_categories:
    category_data[cat].sort(key=lambda x: x['post_name'])

# Generate sidebar HTML
sidebar_html = '''
<nav id="sidebar">
    <h2>Table of Contents</h2>
'''
for cat in sorted_categories:
    sidebar_html += f'<details><summary>{cat}</summary><ul>\n'
    for post in category_data[cat]:
        if len(post['sections']) == 1:
            url = f"/{post['post_name']}/index.html"
            sidebar_html += f'    <li><a href="{url}">{post["post_title"]}</a></li>\n'
        else:
            sidebar_html += f'    <li><details><summary>{post["post_title"]}</summary><ul>\n'
            for slug, sec_title in post['sections']:
                url = f"/{post['post_name']}/{slug}.html"
                sidebar_html += f'        <li><a href="{url}">{sec_title}</a></li>\n'
            sidebar_html += '    </ul></details></li>\n'
    sidebar_html += '</ul></details>\n'
sidebar_html += '</nav>\n'

# Process each post
for cat in sorted_categories:
    for post in category_data[cat]:
        post_name = post['post_name']
        post_title = post['post_title']
        sections = post['sections_md']

        # Create post output dir
        post_out_dir = Path(OUTPUT_DIR) / post_name
        post_out_dir.mkdir(parents=True, exist_ok=True)

        # Copy images to global assets/images/post_name/ (contents only)
        post_dir = Path(POSTS_DIR) / post_name
        images_src = post_dir / 'images'
        if images_src.is_dir():
            assets_images_dir = Path(OUTPUT_DIR) / 'assets' / 'images' / post_name
            assets_images_dir.mkdir(parents=True, exist_ok=True)
            for item in os.listdir(images_src):
                s = images_src / item
                d = assets_images_dir / item
                if s.is_dir():
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        # Generate HTML for each section
        for idx, (sec_slug, sec_md) in enumerate(sections):
            # Convert section MD to HTML fragment using pandoc
            proc = subprocess.run(
                ['pandoc', '-f', 'markdown', '-t', 'html'],
                input=sec_md.encode('utf-8'),
                capture_output=True,
                text=False
            )
            html_fragment = proc.stdout.decode('utf-8')

            # Modify media paths to point to global assets
            soup = BeautifulSoup(html_fragment, 'html.parser')
            media_tags = soup.find_all(['img', 'video', 'source'])
            for tag in media_tags:
                for attr in ['src', 'poster']:
                    if attr in tag.attrs:
                        val = tag[attr]
                        if val.startswith('images/'):
                            tag[attr] = f"/assets/images/{post_name}/{val[7:]}"
            html_fragment = str(soup)

            # Navigation links (within post)
            prev_link = ''
            next_link = ''
            if idx > 0:
                prev_slug = sections[idx-1][0]
                prev_link = f'<a href="{prev_slug}.html">Previous</a>'
            if idx < len(sections) - 1:
                next_slug = sections[idx+1][0]
                next_link = f'<a href="{next_slug}.html">Next</a>'
            nav_html = f'<div class="navigation">{prev_link} {next_link}</div>' if prev_link or next_link else ''

            # Full page HTML with JS link
            page_title = f"{post_title} - {sec_slug.capitalize().replace('-', ' ')}" if sec_slug != 'index' else post_title
            full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <link rel="stylesheet" href="/assets/css/style.css">
    <script src="/assets/js/script.js" defer></script>
</head>
<body>
    {sidebar_html}
    <div id="content">
        {html_fragment}
        {nav_html}
    </div>
</body>
</html>
'''

            sec_path = post_out_dir / f"{sec_slug}.html"
            with open(sec_path, 'w', encoding='utf-8') as f:
                f.write(full_html)

# Generate home index.html
home_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Blogs</title>
    <link rel="stylesheet" href="/assets/css/style.css">
    <script src="/assets/js/script.js" defer></script>
</head>
<body>
    {sidebar_html}
    <div id="content">
        <h1>περίπᾰτος (<i>Peripatos</i>)</h1>
        <h2>“Walking and Talking” with Amy and Chris Blackwell</h2>
        <p>Select a post from the sidebar to begin reading.</p>
    </div>
</body>
</html>
'''
with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(home_html)

print("Site generated successfully in '{}'. Added JS for accordion persistence, updated CSS for whitespace, links, and text size. To update CSS/JS, delete the files in docs/assets/ and re-run.".format(OUTPUT_DIR))