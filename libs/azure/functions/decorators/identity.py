from ..http.exceptions import abort
from ..http.trigger.authenticate import authenticate as do_auth, AuthenticationException, NOONE
from abc import ABC
from azure.functions.decorators.function_app import DecoratorApi
from functools import wraps
from libs.utils.threaded import current
import copy


class Idenity(DecoratorApi, ABC):
    def authenticate(self, enforce: bool = False):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                # Deep copy the original function so that we don't cause recursion
                inner = copy.deepcopy(fb._function._func)
                
                @wraps(fb._function._func)
                def outer(*function_args, **function_kwargs):
                    try:
                        current.subject = do_auth()
                    except AuthenticationException as e:
                        if enforce:
                            abort(e.message, status_code=403)
                        else:
                            current.subject = NOONE
                    return inner(*function_args, **function_kwargs)

                fb._function._func = outer
                return fb

            return decorator()

        return wrap