from .authenticate import authenticate
from .jsonapi.parser import parse_request as parse_jsonapi_request
from .session import parse_request as parse_session_request
from .thread_scope import ThreadScope
from ..durable import DFApp
from azure.functions import AuthLevel
from azure.functions.decorators import FunctionApp
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.constants import HTTP_TRIGGER
from azure.functions.decorators.function_app import DecoratorApi
from functools import wraps
from typing import Any, Callable, Optional, Union
import os


class HttpDecoratorApi(DecoratorApi):
    @staticmethod
    def get_binding(wrap):
        for binding in wrap._function.get_bindings():
            if (
                binding._direction == BindingDirection.IN
                and binding.type == HTTP_TRIGGER
            ):
                return binding
        return None

    def _enhance_http_request(
        self,
        wrap: Callable,
        property_name: str,
        value: Any = None,
        func: Callable = None,
        **func_kwargs,
    ) -> None:
        if binding := self.get_binding(wrap):
            user_code = wrap._function._func

            @wraps(user_code)
            async def middleware(*args, **kwargs):
                setattr(
                    kwargs[binding.name],
                    property_name,
                    value or func(kwargs[binding.name], **func_kwargs),
                )
                return await user_code(*args, **kwargs)

            enchanced_user_code = middleware
            wrap._function._func = enchanced_user_code

    def authenticate(self, enforce: bool = True) -> Callable:
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                self._enhance_http_request(
                    fb, "identity", func=authenticate, enforce=enforce
                )
                return fb

            return decorator()

        return wrap

    def jsonapi(self) -> Callable:
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                self.get_binding(
                    fb
                ).route += (
                    "/{resource_type}/{resource_id?}/{relation_type?}/{relation_id?}"
                )
                self._enhance_http_request(fb, "jsonapi", func=parse_jsonapi_request)
                return fb

            return decorator()

        return wrap

    def session(
        self,
        secret: Optional[str] = os.environ.get("SESSION_SECRET"),
        max_age: Optional[int] = int(os.environ.get("SESSION_MAX_AGE")) or 3600,
        **kwargs,
    ):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                self._enhance_http_request(
                    fb,
                    "session",
                    func=parse_session_request,
                    secret=secret,
                    max_age=max_age,
                    **kwargs,
                )
                return fb

            return decorator()

        return wrap


class FunctionApp(DFApp, FunctionApp, ThreadScope, HttpDecoratorApi):
    def __init__(self, http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        super().__init__(http_auth_level)
