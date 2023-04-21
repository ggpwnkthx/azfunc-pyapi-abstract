from pathlib import Path
from typing import Any
import inspect
import logging


def get(name: str, level=logging.DEBUG) -> logging.Logger:
    # init logger object
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create file handler if it doesn't exist
    if not len(logger.handlers):
        path = Path(f"logs/{name}.txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(str(path))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    return logger


def WARNING(message: Any, name: str = None, *args, **kwargs):
    if not name:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = str(Path(module.__file__).relative_to(Path.cwd()))
    if not len(args) and not len(kwargs):
        get(name).warning(message)
    else:
        get(name).warning((message, *args, kwargs))
