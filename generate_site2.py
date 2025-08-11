#!/usr/bin/env python3
import os
import shutil
import re
import markdown
from bs4 import BeautifulSoup

# Configuration
POSTS_DIR = "posts"
OUTPUT_DIR = "docs"

skipped_dirs = ['Markdown', '01 Greenville', '00 Introductions']

def slugify(text):
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '-')

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
.local-toc {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 5px;
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

def build_tree(directory):
    tree = {}
    for entry in sorted(os.listdir(directory)):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            subtree = build_tree(full_path)
            if subtree:
                if entry in skipped_dirs:
                    tree.update(subtree)
                else:
                    tree[entry] = subtree
        elif entry.endswith('.md'):
            tree['md_file'] = full_path
        # Non-MD files (media) will be copied later
    return tree

def generate_toc_html(node, current_path=''):
    html = ''
    subdirs = [k for k in node if k != 'md_file']
    subdirs.sort()  # Sort subdirectories by name (leveraging two-digit prefixes)
    for subdir in subdirs:
        sub_path = os.path.join(current_path, subdir) if current_path else subdir
        summary_text = subdir  # Keep full directory name, including prefix
        html += f'<details><summary>{summary_text}</summary><ul>'
        html += generate_toc_html(node[subdir], sub_path)
        html += '</ul></details>'
    if 'md_file' in node:
        # Extract post_title from H1
        md_path = node['md_file']
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        post_title = soup.find('h1').text.strip() if soup.find('h1') else os.path.basename(current_path)
        post_slug = current_path.replace(os.sep, '/') if current_path else ''
        html += f'<li><a href="{post_slug}/index.html">{post_title}</a></li>'
    return html

def get_post_list(node, current_path='', post_list=[]):
    subdirs = [k for k in node if k != 'md_file']
    subdirs.sort()
    for subdir in subdirs:
        sub_path = os.path.join(current_path, subdir) if current_path else subdir
        get_post_list(node[subdir], sub_path, post_list)
    if 'md_file' in node:
        post_list.append(current_path)
    return post_list

def generate_pages(node, current_path='', sidebar_html='', post_paths=[]):
    output_post_dir = os.path.join(OUTPUT_DIR, current_path)
    os.makedirs(output_post_dir, exist_ok=True)
    if 'md_file' in node:
        md_path = node['md_file']
        # Copy media files and directories recursively
        source_dir = os.path.dirname(md_path)
        for item in os.listdir(source_dir):
            if item.endswith('.md'):
                continue
            src = os.path.join(source_dir, item)
            dst = os.path.join(output_post_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy(src, dst)
        # Generate content HTML
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=['extra'])
        soup = BeautifulSoup(html_content, 'html.parser')
        page_title = soup.find('h1').text.strip() if soup.find('h1') else 'Untitled'
        # Add IDs to H2 for local TOC
        local_toc = '<div class="local-toc"><h3>Contents</h3><ul>'
        has_sections = False
        for h2 in soup.find_all('h2'):
            has_sections = True
            title = h2.text.strip()
            id_ = slugify(title)
            h2['id'] = id_
            local_toc += f'<li><a href="#{id_}">{title}</a></li>'
        local_toc += '</ul></div>'
        if not has_sections:
            local_toc = ''
        content_html = local_toc + str(soup)
        # Navigation
        i = post_paths.index(current_path)
        prev_path = post_paths[i-1] + '/index.html' if i > 0 else None
        next_path = post_paths[i+1] + '/index.html' if i < len(post_paths) - 1 else None
        navigation = '<div class="navigation">'
        if prev_path:
            navigation += f'<a href="/{prev_path}">Previous</a>'
        else:
            navigation += '<span></span>'  # Placeholder for spacing
        if next_path:
            navigation += f'<a href="/{next_path}">Next</a>'
        navigation += '</div>'
        content_html += navigation
        # Full page HTML
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{page_title}</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    {sidebar_html}
    <div id="content">
        {content_html}
    </div>
    <script src="/assets/js/script.js"></script>
</body>
</html>"""
        html_path = os.path.join(output_post_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
    # Recurse into subdirectories
    subdirs = [k for k in node if k != 'md_file']
    subdirs.sort()
    for subdir in subdirs:
        sub_path = os.path.join(current_path, subdir) if current_path else subdir
        generate_pages(node[subdir], sub_path, sidebar_html, post_paths)

# Build the tree
tree = build_tree(POSTS_DIR)

# Generate sidebar HTML
toc_html = generate_toc_html(tree)
sidebar_html = f'<div id="sidebar"><h2>Table of Contents</h2><ul>{toc_html}</ul></div>'

# Get ordered list of post paths
post_paths = get_post_list(tree)

# Generate pages
generate_pages(tree, '', sidebar_html, post_paths)

# Create root index.html if needed (redirect to first post)
if post_paths:
    first_post = post_paths[0] + '/index.html'
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w') as f:
        f.write(f'<meta http-equiv="refresh" content="0; url=/{first_post}" />')