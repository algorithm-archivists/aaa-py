O_NAME = "_book"
CONTENTS_NAME = "contents"
INDEX_NAME = "README.md"
SUMMARY_NAME = "SUMMARY.md"
AAA_ORIGIN = "https://github.com/algorithm-archivists/algorithm-archive/archive/master.zip"
AAA_PATH = "contents"
CONTENTS_ZIP = "aaa-book.zip"
TMP_OUTPUT_DIRECTORY = "aaa-repo-all"
OUTPUT_DIRECTORY = "aaa-repo"
AAA_README = "README.md"
AAA_SUMMARY = "SUMMARY.md"
AAA_REPO_PATH = "algorithm-archive-master"
EXT = [
    "fenced_code",
    "codehilite",
    "tables",
    "ext.mdx_links"
]
TEMPLATE_PATH = "templates/index.html"
PYGMENT_THEME = "friendly"
SUMMARY_INDENT_LEVEL = 4
STYLE_PATH = "styles"
IMPORT_FILES = {
    "SUMMARY.md": "SUMMARY.md",
    "README.md": "README.md",
    "contents": "contents",
    "literature.bib": "literature.bib",
    "book.json": "book.json",
    "redirects.json": "redirects.json"
}
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
