def mathjaxify(code):
    splitted = code.split("$$")
    result = ""
    for i, section in enumerate(splitted):
        if i % 2:
            section = section.replace('<em>', '*').replace('</em>', '*')
            result += "<script type='math/tex'>"
            result += section
            result += "</script>"
        else:
            result += section
    return result