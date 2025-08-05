# Peripatos: Static Travel Blog Generator

This repository contains a Python script (`generate_site.py`) that generates a static website for a travel blog. It processes a hierarchical directory of Markdown files (in the `posts` directory) and linked media, converting them into HTML pages with a table of contents (TOC) sidebar based on the directory structure. The TOC uses accordion-style nesting for categories and sections, with persistence across page loads. Media files (e.g., images) are copied to the output directory without modifying originals.

The generated site is output to the `docs` directory, which can be served locally or deployed (e.g., to GitHub Pages).

## Prerequisites

- Python 3.6 or higher (tested with Python 3.12).
- Git (for cloning the repository).

## Setup and Installation

1. **Clone the Repository**:

```
   git clone https://github.com/Eumaeus/Peripatos.git
   cd Peripatos
```


2. **Create and Activate a Virtual Environment** (recommended to isolate dependencies):
- On Unix/macOS:
  ```
  python -m venv venv
  source venv/bin/activate
  ```
- On Windows:
  ```
  python -m venv venv
  venv\Scripts\activate
  ```

3. **Install Dependencies**:
The script requires the following Python packages:

`pip install markdown beautifulsoup4`


## Running the Script

1. Ensure your Markdown content and media files are in the `posts` directory (hierarchically organized, e.g., `posts/Category/Subcategory/section.md`).

2. Run the script:

`python generate_site.py`


- This will:
  - Read Markdown files from `posts` (without modifying them).
  - Convert them to HTML.
  - Generate a sidebar TOC with nested accordions.
  - Copy linked media files to the output directory.
  - Create necessary CSS and JS files in `docs/assets` for styling and functionality.
  - Output the static site to the `docs` directory.

3. **Preview the Site Locally**:
From the repository root:

`python -m http.server --directory docs`

Open a browser and navigate to `http://localhost:8000` (or the port shown). The homepage is `index.html`.

## Customization

- **Content Structure**: Organize your `posts` directory with categories as top-level folders, subcategories as subfolders, and Markdown files for sections. The script automatically builds the TOC from this hierarchy.
- **Styling**: Edit `docs/assets/css/style.css` after generation for custom styles.
- **Media**: Place images/videos in the same directory as their linking Markdown files; the script will copy them.
- **Deployment**: Push the `docs` directory to a GitHub Pages branch or host it on any static site server.

## Troubleshooting

- If media files are missing in output, ensure they are referenced correctly in Markdown (e.g., `![alt](image.jpg)` where `image.jpg` is in the same folder).
- The script clears previous builds in `docs` (except assets) to avoid stale files—back up custom changes if needed.
- For errors related to dependencies, reactivate the virtual environment and reinstall packages.

If you encounter issues or want to add features (e.g., search functionality), feel free to open an issue or contribute!







