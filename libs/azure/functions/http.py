from marshmallow import Schema
from typing import Any
import azure.functions as func

class HttpRequest(func.HttpRequest):
    def __init__(self, *args, **kwargs) -> None:
        self.identity: dict = kwargs.pop("identity", None),
        self.jsonapi: dict = kwargs.pop("jsonapi", None),
        self.session: dict = kwargs.pop("session", None),
        super().__init__(*args, **kwargs)
        
class HttpResponse(func.HttpResponse):
    def __init__(self, *args, **kwargs) -> None:
        self.resource: Any = kwargs.pop("resource", None),
        super().__init__(*args, **kwargs)
        
    def set_body(self, *args, **kwargs):
        self.__set_body(*args, **kwargs)