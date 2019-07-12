import importlib
from .extension import Extension
from typing import List
from config import extensions


def get_ext(*args):
    ext: List[Extension] = []
    for module, cls in extensions:
        extension: type = getattr(importlib.import_module('.' + module, 'ext'), cls)
        inst: Extension = extension(*args)
        ext.append(inst)

    def run(code, path):
        for i in ext:
            code = i.run(code, path)
        return code

    return run
