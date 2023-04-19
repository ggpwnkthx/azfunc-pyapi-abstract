from pathlib import Path
import importlib.util
import os
import sys


def load(path: str, file_mode: str = "init", depth: int = 0):
    parent = Path(path).parent
    modules = []
    for root, dirs, files in os.walk(parent):
        current_depth = root[len(path) + len(os.path.sep) :].count(os.path.sep)

        if depth != -1 and current_depth >= depth:
            dirs.clear()

        for file in files:
            if Path(root, file) != Path(path) and file.endswith(".py"):
                if (
                    (file_mode == "init" and file == "__init__.py")
                    or (file_mode == "non-init" and file != "__init__.py")
                    or (file_mode == "all")
                ):
                    module_name = ".".join(
                        Path(root, file).relative_to(Path.cwd()).parts
                    )[:-3]
                    if module_name not in sys.modules:
                        spec = importlib.util.spec_from_file_location(
                            module_name, os.path.join(root, file)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        modules.append(module)
                    else:
                        modules.append(sys.modules[module_name])
    return modules
