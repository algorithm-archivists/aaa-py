import os
import shutil
from pprint import pprint
import pygments
import re
import jinja2
import markdown
import requests
import zipfile
from handle_languages import handle_languages
from creative import creativize


o_name = "_book"
contents_name = "contents"
index_name = "README.md"
summary_name = "SUMMARY.md"
aaa_origin = "https://github.com/algorithm-archivists/algorithm-archive/archive/master.zip"
aaa_path = "contents"
aaa_readme = "README.md"
aaa_summary = "SUMMARY.md"
aaa_repo_path = "algorithm-archive-master"
ext = [
    "fenced_code",
    "codehilite",
    "tables"
]
md = markdown.Markdown(extensions=ext)
template = None
template_path = "index.html"
pygment_theme = "default"
summary = ""
summary_indent_level = 4
style_path = "styles"


def render_one(file_handle, code_dir) -> str:
    text = file_handle.read()
    text = handle_languages(text, code_dir)
    mathjaxed = text.replace('$$', '$')
    mdified = md.convert(mathjaxed)
    creativized = creativize(mdified)

    rendered = template.render(md_text=creativized, summary=summary)
    print("Finished rendering the chapter. Reading next...")
    return rendered


def render_chapter(chapter):
    os.mkdir(f"{o_name}/{contents_name}/{chapter}")
    md_file: str = next(filter(lambda a: a.endswith(".md"), os.listdir(f"{contents_name}/{chapter}")))
    with open(f"{contents_name}/{chapter}/{md_file}", 'r') as r:
        print(f"Rendering {md_file}...")
        contents: str = render_one(r, f"{contents_name}/{chapter}")
    with open(f"{o_name}/{contents_name}/{chapter}/{md_file.replace('.md', '.html')}", 'w') as f:
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
    if contents_name not in os.listdir("."):
        print("No contents present, cloning...")
        origin = requests.get(aaa_origin)
        with open("/tmp/aaa-repo.zip", 'wb') as origin_zip:
            origin_zip.write(origin.content)

        print("Cloned, extracting...")
        with zipfile.ZipFile("/tmp/aaa-repo.zip", 'r') as origin_zip:
            origin_zip.extractall("/tmp/aaa-repo-all")
        os.rename(f"/tmp/aaa-repo-all/{aaa_repo_path}", "/tmp/aaa-repo")

        print("Cleanup...")
        shutil.rmtree("/tmp/aaa-repo-all")
        os.remove("/tmp/aaa-repo.zip")

        print("Extracted, moving...")
        os.rename(os.path.join("/tmp/aaa-repo", aaa_path), contents_name)

        print("Moving README.md...")
        os.rename(os.path.join("/tmp/aaa-repo", aaa_readme), index_name)

        print("Moving SUMMARY.md...")
        os.rename(os.path.join("/tmp/aaa-repo", aaa_summary), summary_name)

        print("Cleanup...")
        shutil.rmtree("/tmp/aaa-repo")

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
    chapters = filter(lambda a: re.match('^[a-zA-Z0-9_]+$', a), os.listdir(contents_name))

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

    print("Rendering chapters...")
    for chapter in chapters:
        render_chapter(chapter)

    print("Moving styles...")
    shutil.copytree(style_path, f"{o_name}/styles")

    print("Rendering index...")
    with open(index_name, 'r') as readme:
        with open(f"{o_name}/index.html", 'w') as index:
            index.write(render_one(readme, None))
    print("Done!")
