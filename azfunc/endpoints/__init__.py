import importlib
from pathlib import Path

current_directory = Path(__file__).parent
for f in [f for f in current_directory.iterdir() if f.is_file()]:
    if f.exists() and f.name != "__init__.py" and f.name.endswith(".py"):
        relative_path = f.relative_to(Path.cwd())
        module_name = ".".join(relative_path.parts)[:-3]
        module = importlib.import_module(module_name)
