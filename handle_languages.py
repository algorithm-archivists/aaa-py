import re
import os
import markdown


def handle_section(section: str, code_dir):
    code = section.split('{% endmethod %}')
    if len(code) == 1:
        return code[0]
    code = code[0]
    result = ''
    for language in code.split('{% sample lang="')[1:]:
        language = language[language.find('"') + 5:]
        res = ''
        for line in language.split('\n'):
            if line.startswith("[import"):
                lang = line.split('lang')[1][2:].split('"')[0]
                result += f'<div class={lang}>\n'
                res += markdown.markdown(line) + '\n\n'
            else:
                res += markdown.markdown(line) + '\n\n'
        result += res
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