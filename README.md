# Peripatos
## Travels with Amy and Chris Blackwell

This repository contains a Python script (generate_site.py) that generates a static website for a travel blog. It processes a hierarchical directory of Markdown files (in the posts directory) and linked media, converting them into HTML pages with a table of contents (TOC) sidebar based on the directory structure. The TOC uses accordion-style nesting for categories and sections, with persistence across page loads. Media files (e.g., images) are copied to the output directory without modifying originals.The generated site is output to the docs directory, which can be served locally or deployed (e.g., to GitHub Pages).

## Prerequisites

- Python 3.6 or higher (tested with Python 3.12).
- Git (for cloning the repository).

## Setup and Installation

- Clone the Repository:
```
git clone https://github.com/Eumaeus/Peripatos.git
cd Peripatos
```
- **Create and Activate a Virtual Environment** (recommended to isolate dependencies):
	- On Unix/macOS:
```
python -m venv venv
source venv/bin/activate
```
- Install Dependencies:
	- The script requires the following Python packages:
`pip install markdown beautifulsoup4`

## Running the Script

Ensure your Markdown content and media files are in the posts directory (hierarchically organized, e.g., posts/Category/Subcategory/section.md).

Run the script:



