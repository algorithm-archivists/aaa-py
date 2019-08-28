import os
import shutil
import re
import jinja2
import markdown
import pybtex.database
import json
from config import *
from ext import get_ext
from . import clone, utils


def build():
    md = markdown.Markdown(extensions=EXT)
    print("Detecting if contents present...")
    do_clone = clone.detect_if_contents_present(AAA_PATH, IMPORT_FILES)
    if do_clone:
        print("Creating the contents directory...")
        utils.create_dir_if_not_exists(AAA_PATH)
        print("No contents present, cloning...")
        clone.clone_contents(AAA_PATH, CONTENTS_ZIP, AAA_ORIGIN)
        print("Cloned, extracting...")
        clone.extract_contents(AAA_PATH, CONTENTS_ZIP, AAA_REPO_PATH, TMP_OUTPUT_DIRECTORY, OUTPUT_DIRECTORY)
        print("Extracted, moving files...")
        clone.move_from_contents(AAA_PATH, OUTPUT_DIRECTORY, IMPORT_FILES)
        print("Cleaning up...")
        utils.clean_up(AAA_PATH, CONTENTS_ZIP, TMP_OUTPUT_DIRECTORY, OUTPUT_DIRECTORY)
    else:
        print("Contents already exists.")

    try:
        print("Trying to create _book directory...")
        os.mkdir(O_NAME)
        print("Successfully created.")
    except FileExistsError:
        print("_book already exists. Removing...")
        shutil.rmtree(O_NAME)
        print("Making _book...")
        os.mkdir(O_NAME)

    print("Making contents folder...")
    os.mkdir(f"{O_NAME}/{CONTENTS_NAME}")

    print("Done making, looking for chapters...")
    chapters = filter(lambda a: re.match('^[a-zA-Z0-9_-]+$', a), os.listdir(os.path.join(CONTENTS_NAME, CONTENTS_NAME)))

    print("Looking for the template...")
    with open(TEMPLATE_PATH, 'r') as template_file:
        print("Reading...")
        template = jinja2.Template(template_file.read())
        print("Template ready!")

    print("Building Pygments...")
    os.system(f"pygmentize -S {PYGMENT_THEME} -f html -a .codehilite > {O_NAME}/pygments.css")

    print("Parsing SUMMARY.md...")
    summary = parse_summary()

    print("Opening bibtex...")
    bib_database = pybtex.database.parse_file("literature.bib")

    print("Opening book.json...")
    with open(os.path.join(CONTENTS_NAME, "book.json")) as bjs:
        book_json = json.load(bjs)

    print("Creating rendering pipeline...")
    renderer = get_ext(bib_database, PYGMENT_THEME, md)

    print("Rendering chapters...")
    for chapter in chapters:
        render_chapter(chapter, renderer, template, summary, book_json)

    print("Moving favicon.ico...")
    shutil.copy(FAVICON_PATH, f"{O_NAME}/favicon.ico")

    print("Moving styles...")
    shutil.copytree(STYLE_PATH, f"{O_NAME}/styles")

    print("Parsing redirects...")
    with open(f"{AAA_PATH}/redirects.json") as rjs_file:
        rjs = json.load(rjs_file)
    rjs = {i["from"]: i["to"] for i in rjs["redirects"]}
    with open(f"{O_NAME}/redirects.json", 'w') as rjs_file:
        json.dump(rjs, rjs_file)

    print("Rendering index...")
    with open(os.path.join(CONTENTS_NAME, INDEX_NAME), 'r') as readme, open(f"{O_NAME}/index.html", 'w') as index:
            index.write(render_one(readme, f"{O_NAME}/", 0, renderer, template, summary, book_json))
    print("Done!")


def parse_summary():
    with open(os.path.join(AAA_PATH, SUMMARY_NAME)) as s:
        summary = s.read()
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

    try:
        # dirty hack but it works
        shutil.copyfile(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}/CC-BY-SA_icon.svg", f"{O_NAME}/{CONTENTS_NAME}/{chapter}/CC-BY-SA_icon.svg") 
    except FileNotFoundError:
        pass
    try:
        shutil.copytree(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}/res", f"{O_NAME}/{CONTENTS_NAME}/{chapter}/res")
    except FileNotFoundError:
        pass
    try:
        shutil.copytree(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}/code", f"{O_NAME}/{CONTENTS_NAME}/{chapter}/code")
    except FileNotFoundError:
        pass

    try:
        md_file: str = next(filter(lambda a: a.endswith(".md"), os.listdir(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}")))
    except StopIteration:
        return
    out_file = f"{O_NAME}/{CONTENTS_NAME}/{chapter}/{md_file.replace('.md', '.html')}"
    with open(f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}/{md_file}", 'r') as r:
        try:
            index = [k[0] for k in filter(lambda x: out_file.split('/')[-1] in x[1],
                                          [(i, a[1]) for i, a in enumerate(summary)])][0]
        except IndexError:
            return
        contents: str = render_one(r, f"{CONTENTS_NAME}/{CONTENTS_NAME}/{chapter}", index, renderer, template, summary, book_json)
    with open(out_file, 'w') as f:
        f.write(contents)


def render_one(file_handle, code_dir, index, renderer, template, summary, book_json) -> str:
    text = file_handle.read()
    finalized = renderer(text, code_dir)
    rendered = template.render(md_text=finalized, summary=summary, index=index, enumerate=enumerate,
                               bjs=json.dumps(book_json))
    return rendered
