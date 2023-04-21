from ...http.exceptions import abort
from .parser import parse_request
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.constants import HTTP_TRIGGER
from azure.functions.decorators.function_app import DecoratorApi
from functools import wraps
from typing import Callable

from libs.utils.logger import get as Logger

logger = Logger("jsonapi")


class JsonApi(DecoratorApi):
    """Interface to extend for using existing trigger decorator functions."""

    def _jsonapi(self, fb, parameter_name) -> None:
        user_code = fb._function._func

        @wraps(user_code)
        async def middleware(*args, **kwargs):
            setattr(
                kwargs[parameter_name],
                "jsonapi",
                parse_request(kwargs[parameter_name]),
            )
            return await user_code(*args, **kwargs)

        enchanced_user_code = middleware
        fb._function._func = enchanced_user_code

    def jsonapi(self) -> Callable:
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                for binding in fb._function.get_bindings():
                    if (
                        binding._direction == BindingDirection.IN
                        and binding.type == HTTP_TRIGGER
                    ):
                        binding.route += "/{resource_type}/{resource_id?}/{relation_type?}/{relation_id?}"
                        self._jsonapi(fb, binding.name)
                        break
                return fb

            return decorator()

        return wrap

    # def jsonapi(
    #     self,
    #     route: str = "",
    #     trigger_arg_name: str = "req",
    #     binding_arg_name: str = "$return",
    #     methods: Optional[Union[Iterable[str], Iterable[HttpMethod]]] = [
    #         "GET",
    #         "POST",
    #         "PATCH",
    #         "DELETE",
    #     ],
    #     auth_level: Optional[Union[AuthLevel, str]] = AuthLevel.FUNCTION,
    #     trigger_extra_fields: Dict = {},
    #     binding_extra_fields: Dict = {},
    # ) -> Callable:
    #     @self._configure_function_builder
    #     def wrap(fb):
    #         def decorator():
    #             fb.add_trigger(
    #                 trigger=HttpTrigger(
    #                     name=trigger_arg_name,
    #                     methods=parse_iterable_param_to_enums(methods, HttpMethod),
    #                     auth_level=parse_singular_param_to_enum(auth_level, AuthLevel),
    #                     route=route
    #                     + ("/" if route[-1] != "/" else "")
    #                     + "{resource_type}/{resource_id?}/{relation_type?}/{relation_id?}",
    #                     **trigger_extra_fields,
    #                 )
    #             )
    #             fb.add_binding(
    #                 binding=HttpOutput(name=binding_arg_name, **binding_extra_fields)
    #             )

    #             # Deep copy the original function so that we don't cause recursion
    #             inner = copy.deepcopy(fb._function._func)

    #             @wraps(fb._function._func)
    #             def outer(*function_args, **function_kwargs):
    #                 function_kwargs[trigger_arg_name] = HttpRequest(
    #                     method=function_kwargs[trigger_arg_name].method,
    #                     url=function_kwargs[trigger_arg_name].url,
    #                     headers=function_kwargs[trigger_arg_name].headers,
    #                     params=function_kwargs[trigger_arg_name].params,
    #                     route_params=function_kwargs[trigger_arg_name].route_params,
    #                     body=function_kwargs[trigger_arg_name].get_body(),
    #                 )
    #                 try:
    #                     setattr(
    #                         function_kwargs[trigger_arg_name],
    #                         "jsonapi",
    #                         parse_request(function_kwargs[trigger_arg_name]),
    #                     )
    #                 except Exception as e:
    #                     if hasattr(e, "status_code"):
    #                         abort(
    #                             headers={"Content-Type": "application/vnd.api+json"},
    #                             status_code=e.status_code,
    #                             body={"errors": e.errors},
    #                         )
    #                     else:
    #                         raise e
    #                 return inner(*function_args, **function_kwargs)