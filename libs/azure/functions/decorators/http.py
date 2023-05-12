from ..http import HttpResponse
from .jsonapi import (
    parse_request as parse_request_jsonapi,
    alter_response as alter_response_jsonapi,
)
from .session import (
    parse_request as parse_request_session,
    alter_response as alter_response_session,
)
from asyncio import iscoroutinefunction
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.constants import HTTP_TRIGGER, HTTP_OUTPUT
from azure.functions.decorators.function_app import DecoratorApi
from functools import wraps
from typing import Any, Callable, Optional
import os

class HttpDecoratorApi(DecoratorApi):
    @staticmethod
    def get_request_binding(wrap):
        for binding in wrap._function.get_bindings():
            if (
                binding._direction == BindingDirection.IN
                and binding.type == HTTP_TRIGGER
            ):
                return binding
        return None

    @staticmethod
    def get_response_binding(wrap):
        for binding in wrap._function.get_bindings():
            if (
                binding._direction == BindingDirection.OUT
                and binding.type == HTTP_OUTPUT
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
        if binding := self.get_request_binding(wrap):
            user_code = wrap._function._func

            if iscoroutinefunction(user_code):

                @wraps(user_code)
                async def middleware(*args, **kwargs):
                    setattr(
                        kwargs[binding.name],
                        property_name,
                        value or func(kwargs[binding.name], **func_kwargs),
                    )
                    return await user_code(*args, **kwargs)

            else:

                @wraps(user_code)
                def middleware(*args, **kwargs):
                    setattr(
                        kwargs[binding.name],
                        property_name,
                        value or func(kwargs[binding.name], **func_kwargs),
                    )
                    return user_code(*args, **kwargs)

            enchanced_user_code = middleware
            wrap._function._func = enchanced_user_code

    def _enhance_http_response(
        self,
        wrap: Callable,
        property_name: str = None,
        value: Any = None,
        func: Callable = None,
        **func_kwargs,
    ):
        if binding := self.get_response_binding(wrap):
            user_code = wrap._function._func

            if iscoroutinefunction(user_code):

                @wraps(user_code)
                async def middleware(*args, **kwargs):
                    func_kwargs["request"] = kwargs[self.get_request_binding(wrap).name]
                    if binding.name == "$return":
                        response: HttpResponse = await user_code(*args, **kwargs)
                        if property_name:
                            setattr(
                                response,
                                property_name,
                                value or func(response, **func_kwargs),
                            )
                        else:
                            response: HttpResponse = value or func(
                                response, **func_kwargs
                            )
                        return response

            else:

                @wraps(user_code)
                def middleware(*args, **kwargs):
                    func_kwargs["request"] = kwargs[self.get_request_binding(wrap).name]
                    if binding.name == "$return":
                        results = user_code(*args, **kwargs)
                    if property_name:
                        setattr(
                            results,
                            property_name,
                            value or func(results, **func_kwargs),
                        )
                    else:
                        results = value or func(results, **func_kwargs)
                    return results

            enchanced_user_code = middleware
            wrap._function._func = enchanced_user_code

    def jsonapi(self) -> Callable:
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                # Append the JSONAPI route parameters
                self.get_request_binding(
                    fb
                ).route += (
                    "/{resource_type}/{resource_id?}/{relation_type?}/{relation_id?}"
                )
                self._enhance_http_request(
                    wrap=fb, property_name="jsonapi", func=parse_request_jsonapi
                )
                self._enhance_http_response(wrap=fb, func=alter_response_jsonapi)
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
                    wrap=fb,
                    property_name="session",
                    func=parse_request_session,
                    secret=secret,
                    max_age=max_age,
                    **kwargs,
                )
                self._enhance_http_response(
                    wrap=fb,
                    func=alter_response_session,
                    secret=secret,
                    max_age=max_age,
                )
                return fb

            return decorator()

        return wrap
