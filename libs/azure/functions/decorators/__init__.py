from .identity import Idenity
from .jsonapi import JsonApi
from .session import SessionApi
from .thread_scope import ThreadScope
from azure.functions.decorators import FunctionApp


class FunctionApp(FunctionApp, ThreadScope, Idenity, SessionApi, JsonApi):
    pass