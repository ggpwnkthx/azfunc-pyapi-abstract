from .__singletons__ import Galactus, auth_cache
from . import microsoft
from libs.utils.threaded import current
from urllib.parse import urlparse
import azure.functions as func
import jwt


NOONE = {}

class AuthenticationException(Exception):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)
        self.message = {}
        for key, value in kwargs.items():
            self.message[key] = value


def whoami():
    try:
        return current.subject
    except:
        return authenticate()


def authenticate(request: func.HttpRequest, enforce:bool = True):
    subject = None
    if request.headers.get("Authorization"):
        token = str(request.headers.get("Authorization")).removeprefix("Bearer ")
        if token:
            auth = jwt.decode(token, options={"verify_signature": False})
            if auth:
                if "iss" in auth.keys():
                    issuer = urlparse(auth["iss"]).hostname
                    subject = {
                        **Galactus[issuer](request, token, auth),
                        "issuer": issuer,
                    }
    if subject:
        if "error" in subject.keys():
            raise AuthenticationException(
                **subject["error"], issuer=subject["issuer"]
            )
        return subject
    else:
        if enforce:
            raise AuthenticationException(
                code="Unidentifiable", message="Unable to identify the requesting entity."
            )
