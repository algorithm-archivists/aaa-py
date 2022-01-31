import os
import shutil
import re
import jinja2
import markdown
import pybtex.database
import json
from contextlib import suppress
from config import *
from ext import get_ext
from .pull import pull
from pathlib import Path
import pygit2
import subprocess
import shlex


def build(local=False):
    md = markdown.Markdown(extensions=EXT)
    print("Detecting if contents present...")
    do_clone = not AAA_CLONE_PATH.exists()
    if do_clone and not local:
        print("No contents present, cloning...")
        pygit2.clone_repository(AAA_ORIGIN, str(AAA_CLONE_PATH))
    elif do_clone and local:
        raise FileNotFoundError('Contents must be present to build them in local mode')
    elif not local:
        print("Contents already exists.")
        print("Updating...")
        pull(pygit2.Repository(AAA_CLONE_PATH))
    else:
        print('Found contents.')
        
    try:
        print("Trying to create _book directory...")
        O_NAME.mkdir()
        print("Successfully created.")
    except FileExistsError:
        print("_book already exists. Removing...")
        shutil.rmtree(O_NAME)
        print("Making _book...")
        O_NAME.mkdir()

    print("Making contents folder...")
    (O_NAME/CONTENTS_NAME).mkdir()

    print("Copying res folder...")
    with suppress(FileNotFoundError):
        shutil.copytree(f"{AAA_CLONE_PATH}/rest", f"{O_NAME}/res")

    print("Done making, looking for chapters...")
    chapters = filter(lambda a: re.match('^[a-zA-Z0-9_-]+$', a),
                      map(lambda p: p.stem,
                          (AAA_CLONE_PATH / CONTENTS_NAME).iterdir()
                         )
                     )

    print("Looking for the template...")

    print("Reading...")
    template = jinja2.Template(TEMPLATE_PATH.read_text())
    print("Template ready!")

    print("Building Pygments...")
    os.system(f"pygmentize -S {PYGMENT_THEME} -f html -a .codehilite > {O_NAME}/pygments.css")

    print("Parsing SUMMARY.md...")
    summary = parse_summary((AAA_PATH / SUMMARY_NAME).read_text())

    print("Opening bibtex...")
    bib_database = pybtex.database.parse_file(AAA_CLONE_PATH / "literature.bib")

    print("Opening book.json...")
    with open(os.path.join(CONTENTS_NAME, "book.json")) as bjs:
        book_json = json.load(bjs)

    print("Creating rendering pipeline...")
    renderer = get_ext(bib_database, PYGMENT_THEME, md)

    print("Rendering chapters...")
    for chapter in chapters:
        render_chapter(chapter, renderer, template, summary, book_json)

    print("Moving favicon.ico...")
    shutil.copy(FAVICON_PATH, O_NAME / "favicon.ico")

    print("Moving styles...")
    shutil.copytree(STYLE_PATH, O_NAME / "styles")

    print("Parsing redirects...")
    with open(f"{AAA_PATH}/redirects.json") as rjs_file:
        rjs = json.load(rjs_file)
    rjs = {i["from"]: i["to"] for i in rjs["redirects"]}
    with open(f"{O_NAME}/redirects.json", 'w') as rjs_file:
        json.dump(rjs, rjs_file)

    print("Rendering index...")
    with open(os.path.join(CONTENTS_NAME, INDEX_NAME), 'r') as readme, open(f"{O_NAME}/index.html", 'w') as index:
        index.write(render_one(readme.read(), f"{O_NAME}/", 0, renderer, template, summary, book_json))
    print("Done!")


def parse_summary(summary):
    summary = summary.replace(".md", ".html") \
        .replace("(contents", "(/contents") \
        .replace('* ', '') \
        .replace('README', '/index')
    summary_parsed = []
    for index, line in enumerate(summary.split('\n')[2:-1]):
        indent, rest = line.split('[')
        name, link = rest.split('](')
        link = link[:-1]
        current_indent = len(indent) // SUMMARY_INDENT_LEVEL
        summary_parsed.append((name, link, current_indent))
    return summary_parsed


def render_chapter(chapter, renderer, template, summary, book_json):
    os.mkdir(f"{O_NAME}/{CONTENTS_NAME}/{chapter}")

    with suppress(FileNotFoundError):
        # dirty hack but it works
        shutil.copyfile(f"{AAA_CLONE_PATH}/{CONTENTS_NAME}/{chapter}/CC-BY-SA_icon.svg",
                        f"{O_NAME}/{CONTENTS_NAME}/{chapter}/CC-BY-SA_icon.svg")
    
    with suppress(FileNotFoundError):
        shutil.copytree(f"{AAA_CLONE_PATH}/{CONTENTS_NAME}/{chapter}/res", f"{O_NAME}/{CONTENTS_NAME}/{chapter}/res")
    
    with suppress(FileNotFoundError):
        shutil.copytree(f"{AAA_CLONE_PATH}/{CONTENTS_NAME}/{chapter}/code", f"{O_NAME}/{CONTENTS_NAME}/{chapter}/code")

    try:
        md_file: str = next(filter(lambda a: a.endswith(".md"),
                                   os.listdir(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}")))
    except StopIteration:
        return
    out_file = f"{O_NAME}/{CONTENTS_NAME}/{chapter}/{md_file.replace('.md', '.html')}"
    with open(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}/{md_file}", 'r') as r:
        try:
            index = [k[0] for k in filter(lambda x: out_file.split('/')[-1] in x[1],
                                          ((i, a[1]) for i, a in enumerate(summary)))][0]
        except IndexError:
            return
        contents: str = render_one(r.read(), f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}",
                                   index, renderer, template, summary, book_json)
    with open(out_file, 'w') as f:
        f.write(contents)


def render_one(text, code_dir, index, renderer, template, summary, book_json) -> str:
    finalized = renderer(text, code_dir)
    rendered = template.render(md_text=finalized, summary=summary, index=index, enumerate=enumerate,
                               bjs=json.dumps(book_json))
    return rendered
