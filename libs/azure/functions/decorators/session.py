from azure.functions.http import HttpRequest
from itsdangerous import URLSafeTimedSerializer
import uuid


def parse_request(request: HttpRequest, secret: str, max_age: int, **kwargs):
    cookies = {}
    if header := request.headers.get("Cookie"):
        cookies = {
            kv[0]: kv[1] for cookie in header.split("; ") if (kv := cookie.split("="))
        }
    session = {"id": uuid.uuid4().hex}
    if token := cookies.get("SessionToken"):
        try:
            session = URLSafeTimedSerializer(secret, **kwargs).loads(
                token,
                max_age=max_age,
                salt=kwargs.get("salt") or None,
            )
        except:
            pass

    return session
