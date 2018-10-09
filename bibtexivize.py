import os


def bibtex(code, bib_database, path, use_path=False):
    if use_path:
        with open(path) as f:
            code = f.read()
    halves = code.split("\" | cite }}")
    if len(halves) < 2:
        return code, []
    references = []
    for index, ref in enumerate(halves[:-1]):
        to_ref = ref.split('"')[1]
        halves[index] = ref.split('{{ ')[0]
        references.append(to_ref)
        halves[index] += f'<a href="#ref-{to_ref}">[{index + 1}]</a>'
    code = "".join(halves)
    formatted = []
    for i in references:
        if "/" in i:
            cd, form = bibtex("", bib_database, os.path.join(path, i), True)
        else:
            entry = bib_database.entries[i]
            author = entry.fields['author']
            title = entry.fields['title']
            publisher = entry.fields['publisher']
            year = entry.fields['year']
            formatted.append(f"{author}: {title}, <i>{publisher}</i>, {year}")
    code = ("\n".join(formatted)).join(code.split('{% references %} {% endreferences %}'))
    return code, formatted