import re
import os
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import pygments


def handle_section(section: str, code_dir):
    code = section.split('{% endmethod %}')
    if len(code) == 1:
        return code[0]
    code = code[0]
    result = '<div class="code-section">\n'
    for language in code.split('{% sample lang="')[1:]:
        language = language[language.find('"') + 5:]
        lang = None
        res = ''
        for line in language.split('\n'):
            if line.startswith("[import"):
                lang = line.split('lang')[1][2:].split('"')[0]
                lnk = line.split('](')[1].split(')')[0]
                with open(os.path.join(code_dir, lnk)) as source:
                    source_code = source.read()
                try:
                    lexer = get_lexer_by_name(lang)
                except pygments.util.ClassNotFound:
                    if lang == "c_cpp":
                        lexer = get_lexer_by_name("c")
                    else:
                        lexer = get_lexer_by_name("python")
                res += highlight(source_code, lexer, HtmlFormatter())
            else:
                res += markdown.markdown(line) + '\n\n'
        result += f'<div class="{lang} codehilite">\n'
        result += res
        result += '\n</div>'
    result += '\n</div>'
    return section.replace(code, result).replace("{% endmethod %}", '')


def handle_languages(code: str, code_dir):
    result = ''
    for section in code.split("{% method %}"):
        result += handle_section(section, code_dir)
        result += '\n'
    return result


def handle_after_md(code:str):
    return code