from abc import ABC
from azure.functions.decorators.function_app import DecoratorApi
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
from libs.utils.threaded import current
from urllib.parse import urlparse
import copy
import os
import uuid


SERIALIZER = URLSafeTimedSerializer(os.environ["session_secret"])


class SessionApi(DecoratorApi, ABC):
    def session(self):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                # Deep copy the original function so that we don't cause recursion
                inner = copy.deepcopy(fb._function._func)

                @wraps(fb._function._func)
                def outer(*function_args, **function_kwargs):
                    cookies = {}
                    if header := current.request.headers.get("Cookie"):
                        cookies = {
                            kv[0]: kv[1]
                            for cookie in header.split("; ")
                            if (kv := cookie.split("="))
                        }
                    current.session = {
                        "id":uuid.uuid4().hex
                    }
                    if token := cookies.get("SessionToken"):
                        try:
                            current.session = SERIALIZER.loads(
                                token, max_age=int(os.environ["session_max_age"])
                            )
                        except:
                            pass

                    default = inner(*function_args, **function_kwargs)

                    current.response.add_cookie(
                        "SessionToken",
                        SERIALIZER.dumps(current.session._get_current_object()),
                        domain = urlparse(current.request.url).netloc
                    )

                    return default

                fb._function._func = outer
                return fb

            return decorator()

        return wrap
