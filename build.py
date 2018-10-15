import os
import shutil
import re
import jinja2
import markdown
import requests
import zipfile
import pybtex.database
import json
import sys
from config import *
from ext import get_ext
from multiprocessing import Pool


md = markdown.Markdown(extensions=ext)
renderer = None


def render_one(file_handle, code_dir, index) -> str:
    text = file_handle.read()
    finalized = renderer(text, code_dir)

    rendered = template.render(md_text=finalized, summary=summary, index=index, enumerate=enumerate,
                               bjs=json.dumps(book_json))
    return rendered


def render_chapter(chapter):
    os.mkdir(f"{o_name}/{contents_name}/{chapter}")
    md_file: str = next(filter(lambda a: a.endswith(".md"), os.listdir(f"{contents_name}/{chapter}")))
    out_file = f"{o_name}/{contents_name}/{chapter}/{md_file.replace('.md', '.html')}"
    with open(f"{contents_name}/{chapter}/{md_file}", 'r') as r:
        try:
            index = [k[0] for k in filter(lambda x: out_file.split('/')[-1] in x[1],
                                          [(i, a[1]) for i, a in enumerate(summary)])][0]
        except IndexError:
            return
        contents: str = render_one(r, f"{contents_name}/{chapter}", index)
    with open(out_file, 'w') as f:
        f.write(contents)
    try:
        shutil.copytree(f"{contents_name}/{chapter}/res", f"{o_name}/{contents_name}/{chapter}/res")
    except FileNotFoundError:
        pass
    try:
        shutil.copytree(f"{contents_name}/{chapter}/code", f"{o_name}/{contents_name}/{chapter}/code")
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    print("Detecting if contents present...")
    do_clone = False
    for file in import_files:
        if file not in os.listdir("."):
            do_clone = True
    if do_clone:
        print("No contents present, cloning...")
        with open("aaa-repo.zip", "wb") as f:
            response = requests.get(aaa_origin, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()

        print("Cloned, extracting...")
        with zipfile.ZipFile("aaa-repo.zip", 'r') as origin_zip:
            origin_zip.extractall("aaa-repo-all")
        shutil.move(f"aaa-repo-all/{aaa_repo_path}", "aaa-repo")

        print("Cleanup...")
        shutil.rmtree("aaa-repo-all")
        os.remove("aaa-repo.zip")

        print("Cleaned up, moving...")

        for file, name in import_files.items():
            print(f"Moving {file}...")
            shutil.move(os.path.join("aaa-repo", file), name)

        print("Cleanup...")
        shutil.rmtree("aaa-repo")

        print("Cleanup successful, building...")
    else:
        print("Contents exists, building...")
    try:
        print("Trying to create _book directory...")
        os.mkdir(o_name)
        print("Successfully created.")
    except FileExistsError:
        print("_book already exists. Removing...")
        shutil.rmtree(o_name)
        print("Making _book...")
        os.mkdir(o_name)

    print("Making contents folder...")
    os.mkdir(f"{o_name}/{contents_name}")

    print("Done making, looking for chapters...")
    chapters = filter(lambda a: re.match('^[a-zA-Z0-9_-]+$', a), os.listdir(contents_name))

    print("Looking for the template...")
    with open(template_path, 'r') as template_file:
        print("Reading...")
        template = jinja2.Template(template_file.read())
        print("Template ready!")

    print("Building Pygments...")
    os.system(f"pygmentize -S {pygment_theme} -f html -a .codehilite > {o_name}/pygments.css")

    print("Parsing SUMMARY.md...")
    with open(summary_name) as s:
        summary = s.read()
    summary = summary.replace(".md", ".html")\
                     .replace("(contents", "(/contents")\
                     .replace('* ', '')\
                     .replace('README', '/index')
    summary_parsed = []
    for index, line in enumerate(summary.split('\n')[2:-1]):
        indent, rest = line.split('[')
        name, link = rest.split('](')
        link = link[:-1]
        current_indent = len(indent) // summary_indent_level
        summary_parsed.append((name, link, current_indent))
    summary = summary_parsed

    print("Opening bibtex...")
    bib_database = pybtex.database.parse_file("literature.bib")

    print("Opening book.json...")
    with open("book.json") as bjs:
        book_json = json.load(bjs)

    print("Creating rendering pipeline...")
    renderer = get_ext(bib_database, pygment_theme, md)

    print("Rendering chapters...")
    Pool(num_workers).map(render_chapter, chapters)

    print("Moving favicon.ico...")
    shutil.copy(favicon_path, f"{o_name}/favicon.ico")

    print("Moving styles...")
    shutil.copytree(style_path, f"{o_name}/styles")

    print("Parsing redirects...")
    with open("redirects.json") as rjs_file:
        rjs = json.load(rjs_file)
    rjs = {i["from"]:i["to"] for i in rjs["redirects"]}
    with open(f"{o_name}/redirects.json", 'w') as rjs_file:
        json.dump(rjs, rjs_file)

    print("Rendering index...")
    with open(index_name, 'r') as readme:
        with open(f"{o_name}/index.html", 'w') as index:
            index.write(render_one(readme, f"{o_name}/", 0))
    print("Done!")
