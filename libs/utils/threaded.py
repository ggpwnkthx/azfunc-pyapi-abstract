from contextvars import ContextVar
from typing import Any
from werkzeug.local import LocalProxy


class DynamicObject(object):
    pass


class GlobalThreadedVar(DynamicObject):
    def __init__(self):
        self._context = {}
        self._proxies = {}

    def __getattribute__(self, name) -> Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self._proxies[name]

    def __setattr__(self, name, value) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            if name not in self._context.keys():
                self._context[name] = ContextVar(name)
                self._proxies[name] = LocalProxy(self._context[name])
            self._context[name].set(value)
            
    def __delattr__(self, name: str) -> None:
        try:
            object.__delattr__(self, name)
        except AttributeError:
            del self._proxies[name]
        


current = GlobalThreadedVar()


import time
import random
import logging


def test(compare, sleep:float=random.random()):
    time.sleep(sleep)
    if not compare:
        logging.error("ERROR")
