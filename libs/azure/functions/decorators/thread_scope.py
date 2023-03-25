from ..http.exceptions import HttpAbort
from ..http import HttpResponse
from abc import ABC
from azure.functions.decorators.function_app import DecoratorApi
from azure.functions.decorators.http import HttpOutput, HttpTrigger
from functools import wraps
from libs.utils.threaded import current
import copy
import inspect


class ThreadScope(DecoratorApi, ABC):
    """Interface to extend for using existing trigger decorator functions."""

    def thread_scope(self, *decorator_args, **decorator_kwargs):
        @self._configure_function_builder
        def wrap(fb):
            self.function_name(fb._function._func.__name__)

            def decorator():
                # Deep copy the original function so that we don't cause recursion
                inner = copy.deepcopy(fb._function._func)

                @wraps(fb._function._func)
                def outer(*function_args, **function_kwargs):
                    for arg in function_kwargs.values():
                        match inspect.getmodule(arg).__name__:
                            case "azure_functions_worker.bindings.context":
                                current.azfunc = arg

                    for binding in fb._function.get_bindings():
                        match type(binding):
                            case HttpOutput:
                                current.response = HttpResponse()

                    trigger = fb._function.get_trigger()
                    match type(trigger):
                        case HttpTrigger:
                            # this pattern is convenient for catching aborts
                            try:
                                current.request = function_kwargs[trigger.name]
                                default: HttpResponse = inner(
                                    *function_args, **function_kwargs
                                )
                                if current.response.altered() and default:
                                    combined = HttpResponse.combine(
                                        default,
                                        current.response,
                                    )
                                    return combined
                                if current.response != {} and not default:
                                    return HttpResponse(**current.response)
                                if current.response == {} and not default:
                                    return HttpResponse(status_code=204)
                                return default
                            except HttpAbort as abortion:
                                return abortion.response

                    # default behavior
                    return inner(*function_args, **function_kwargs)

                fb._function._func = outer
                return fb

            return decorator()

        return wrap
