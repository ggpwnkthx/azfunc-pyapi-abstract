from azure.functions._http import HttpResponse
from azure.functions.http import HttpRequest
from itsdangerous import URLSafeTimedSerializer
from typing import Any
from urllib.parse import urlparse
from http.cookies import SimpleCookie
import uuid


def parse_request(request: HttpRequest, secret: str, max_age: int, **kwargs) -> dict:
    cookies = SimpleCookie()
    cookies.load(request.headers.get("Cookie", ""))
    try:
        return URLSafeTimedSerializer(secret_key=secret).loads(
            getattr(cookies.get("SessionToken", None), "value", ""),
            max_age=max_age,
        )
    except:
        return {"id": uuid.uuid4().hex}


def _generate_session_cookie(
    session: Any,
    secret: str,
    **kwargs,
) -> SimpleCookie:
    cookies = SimpleCookie()
    cookies["SessionToken"] = URLSafeTimedSerializer(secret_key=secret).dumps(session)
    for key, value in kwargs.items():
        cookies["SessionToken"][key.replace("_", "-")] = value
    return cookies


def alter_response(response: HttpResponse, request: HttpRequest, **kwargs):
    cookies = _generate_session_cookie(
        session=getattr(request, "session", {"id": uuid.uuid4().hex}),
        secret=kwargs["secret"],
        domain=urlparse(request.url).netloc,
        path=kwargs.get("path", "/"),
        max_age=kwargs["max_age"],
        secure=kwargs.get("secure", True),
        httponly=kwargs.get("httponly", False),
    )
    for morsel in cookies.values():
        response.headers.add("Set-Cookie", morsel.OutputString())
    return response
