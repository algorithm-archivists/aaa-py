import os
from .extension import Extension


class Bibtex(Extension):
    def run(self, code, path):
        return bibtex(code, self.bib, path)[0]


def bibtex(code, bib_database, path, use_path=False):
    if use_path:
        with open(path) as f:
            code = f.read()
    halves = code.replace('" | cite}}', '" | cite }}').split("\" | cite }}")
    if len(halves) < 2:
        return code, []
    references = []
    for index, ref in enumerate(halves[:-1]):
        to_ref = ref.split('"')[-1]
        halves[index] = ref.split('{{')[0].rstrip()
        references.append(to_ref)
        halves[index] += f'<a href="#ref-{index + 1}">[{index + 1}]</a>'
    code = "".join(halves)
    formatted = []
    count = 1
    for i in references:
        if "/" in i:
            cd, form = bibtex("", bib_database, os.path.join(path, i), True)
            for index, e in enumerate(form):
                a, b, *c = e.split('"')
                form[index] = a + '"' + "ref-" + str(count + index) + '"' + '"'.join(c)
            formatted += form
            count += len(form)
        else:
            entry = bib_database.entries[i]
            authors = entry.persons.get('author')
            if authors is not None:
                authors = ', '.join(map(str, authors))
            title = entry.fields['title']
            publisher = entry.fields.get('publisher', "No Publisher Specified")
            year = entry.fields.get('year')
            jumper = f"<a name=\"ref-{count}\" class=bib-link></a>"
            string = f"{f'{authors}: ' if authors is not None else ''}<i>{title}</i>, {publisher}{f', {year}' if year is not None else ''}"
            formatted.append(jumper + string)
            count += 1
    formatted = '<ol><li>' + "</li>\n<li>".join(formatted) + '</li></ol>'
    code = formatted.join(code.split('{% references %} {% endreferences %}'))
    return code, formatted
