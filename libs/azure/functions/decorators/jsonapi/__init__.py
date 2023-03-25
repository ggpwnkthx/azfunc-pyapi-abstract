from ...http import HttpRequest, HttpResponse
from ...http.exceptions import abort
from abc import ABC
from azure.functions.decorators.core import AuthLevel
from azure.functions.decorators.function_app import DecoratorApi
from azure.functions.decorators.http import HttpMethod, HttpOutput, HttpTrigger
from azure.functions.decorators.utils import (
    parse_singular_param_to_enum,
    parse_iterable_param_to_enums,
)
from functools import wraps
from libs.utils.threaded import current
from typing import Callable, Dict, Optional, Union, Iterable
import copy


class JsonApi(DecoratorApi, ABC):
    """Interface to extend for using existing trigger decorator functions."""

    def jsonapi(
        self,
        route_prefix: str = "",
        trigger_arg_name: str = "req",
        binding_arg_name: str = "$return",
        methods: Optional[Union[Iterable[str], Iterable[HttpMethod]]] = None,
        auth_level: Optional[Union[AuthLevel, str]] = None,
        trigger_extra_fields: Dict = {},
        binding_extra_fields: Dict = {},
    ) -> Callable:
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=HttpTrigger(
                        name=trigger_arg_name,
                        methods=parse_iterable_param_to_enums(methods, HttpMethod),
                        auth_level=parse_singular_param_to_enum(auth_level, AuthLevel),
                        route=route_prefix
                        + "jsonapi/{resource_type}/{resource_id?}/{relation_type?}/{relation_id?}",
                        **trigger_extra_fields,
                    )
                )
                fb.add_binding(
                    binding=HttpOutput(name=binding_arg_name, **binding_extra_fields)
                )

                # Deep copy the original function so that we don't cause recursion
                inner = copy.deepcopy(fb._function._func)

                @wraps(fb._function._func)
                def outer(*function_args, **function_kwargs):
                    function_kwargs[trigger_arg_name] = HttpRequest(
                        method=function_kwargs[trigger_arg_name].method,
                        url=function_kwargs[trigger_arg_name].url,
                        headers=function_kwargs[trigger_arg_name].headers,
                        params=function_kwargs[trigger_arg_name].params,
                        route_params=function_kwargs[trigger_arg_name].route_params,
                        body=function_kwargs[trigger_arg_name].get_body(),
                    )
                    try:
                        current.jsonapi = {}
                        current.jsonapi["request"] = function_kwargs[
                            trigger_arg_name
                        ].get_jsonapi()
                    except Exception as e:
                        if hasattr(e,"status_code"):
                            abort(
                                headers={"Content-Type": "application/vnd.api+json"},
                                status_code=e.status_code,
                                body={"errors": e.errors},
                            )
                        else:
                            raise e
                    default: HttpResponse = inner(*function_args, **function_kwargs)
                    if isinstance(default, HttpResponse):
                        return default
                    elif "response" in current.jsonapi.keys():
                        return HttpResponse(
                            current.jsonapi["response"],
                            headers={"Content-Type": "application/vnd.api+json"},
                        )
                    else:
                        match function_kwargs[trigger_arg_name].method:
                            case "GET":
                                if default is None:
                                    return HttpResponse("", 404)
                                else:
                                    return HttpResponse(
                                        {
                                            "links": {
                                                "self": function_kwargs[
                                                    trigger_arg_name
                                                ].url
                                            },
                                            "data": default
                                        },
                                        headers={
                                            "Content-Type": "application/vnd.api+json"
                                        },
                                    )
                                    

                fb._function._func = outer
                return fb

            return decorator()

        return wrap
