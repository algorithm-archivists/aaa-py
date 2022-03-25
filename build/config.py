""" Default configuration file for aaa-py. """
from pathlib import Path

O_NAME = Path("website")
CONTENTS_NAME = Path("contents")
INDEX_NAME = Path("README.md")
SUMMARY_NAME = Path("SUMMARY.md")
AAA_CLONE_PATH = Path("contents")
AAA_PATH = Path("contents")
AAA_ORIGIN = "http://github.com/algorithm-archivists/algorithm-archive.git"
CONTENTS_PATH = Path("contents")
AAA_README = Path("README.md")
AAA_SUMMARY = Path("SUMMARY.md")
AAA_REPO_PATH = "algorithm-archive-master"
IMPORT_FILES = {
    "SUMMARY.md": "SUMMARY.md",
    "README.md": "README.md",
    "contents": "contents",
    "literature.bib": "literature.bib",
    "book.json": "book.json",
    "redirects.json": "redirects.json"
}
EXT = [
    "fenced_code",
    "codehilite",
    "tables",
    "ext.mdx_links"
]
TEMPLATE_PATH = Path("templates/index.html")
PYGMENT_THEME = "friendly"
SUMMARY_INDENT_LEVEL = 4
STYLE_PATH = Path("styles")
FAVICON_PATH = "favicon.ico"
EXTENSIONS = [
    ("handle_languages", "HandleLanguages"),
    ("mdify", "MDfier"),
    ("mathjaxify", "MathJax"),
    ("creative", "Creativize"),
    ("bibtexivize", "Bibtex"),
    ("importize", "Importize"),
    ("self_link", "SelfLink")
]
