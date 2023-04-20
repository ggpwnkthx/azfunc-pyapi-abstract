from .identity import Idenity
from .jsonapi import JsonApi
from .session import SessionApi
from .thread_scope import ThreadScope
from ..durable import DFApp
from azure.functions import AuthLevel
from azure.functions.decorators import FunctionApp
from typing import Union


class FunctionApp(FunctionApp, DFApp, ThreadScope, Idenity, SessionApi, JsonApi):
    def __init__(self, http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        super().__init__(http_auth_level)