from ....utils.jsonapi import parse_request
from azure.functions import HttpRequest, HttpResponse
from datetime import datetime
from werkzeug.local import LocalProxy
import simplejson as json
import typing


class HttpRequest(HttpRequest):
    def get_jsonapi(self, prefix: str = "jsonapi/"):
        return parse_request(
            url=self.url,
            method=self.method,
            headers=self.headers,
            body=self.get_body(),
            prefix=prefix,
        )


class HttpResponse(HttpResponse):
    def __init__(
        self,
        body=None,
        status_code: typing.Optional[int] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None,
        mimetype: typing.Optional[str] = None,
        charset: typing.Optional[str] = None,
    ) -> None:
        self.__altered = False
        if not isinstance(body, str) and not isinstance(body, bytes):
            if isinstance(body, LocalProxy):
                body = json.dumps(body._get_current_object())
            elif body is not None:
                body = json.dumps(body)
        super().__init__(
            body=body,
            status_code=status_code,
            headers=headers,
            mimetype=mimetype,
            charset=charset,
        )

    @staticmethod
    def combine(*args: typing.List[HttpResponse]):
        combined = HttpResponse()
        for response in args:
            if response.get_body() != b"":
                combined.set_body(response.get_body())
            if response.status_code:
                combined.set_status_code(response.status_code)
            if response.mimetype:
                combined.set_mimetype(response.mimetype)
            if response.charset:
                combined.set_charset(response.charset)
            for header in response.headers:
                combined.add_header(*header)
        return combined

    def altered(self):
        return self.__altered

    def set_body(self, body):
        self.__altered = True
        if not isinstance(body, str) and not isinstance(body, bytes):
            if isinstance(body, LocalProxy):
                self.__body = json.dumps(body._get_current_object())
            else:
                self.__body = json.dumps(body)
        else:
            self.__body = body

    def set_status_code(self, status_code: int):
        self.__altered = True
        if not isinstance(status_code, int):
            self.__status_code = int(status_code)
        else:
            self.__status_code = status_code

    def set_mimetype(self, mimetype: str):
        self.__altered = True
        self.__mimetype = mimetype

    def set_charset(self, charset: str):
        self.__altered = True
        self.__charset = charset

    def add_header(self, key, value, **kwargs):
        self.__altered = True
        self.headers.add(_key=key, _value=value, *kwargs)

    def add_cookie(
        self,
        key: str,
        value: str,
        domain: str = None,
        path: str = "/",
        expires: datetime = None,
        max_age: int = None,
        secure: bool = True,
        httponly: bool = False,
    ):
        self.__altered = True
        if " " in value and (value[0] != '"' or value[0] != "'"):
            if '"' in value:
                value = f"'{value}'"
            else:
                value = f'"{value}"'
        cookie = f"{key}={value}"
        if domain:
            cookie += f"; Domain={domain}"
        if path:
            cookie += f"; Path={path}"
        if expires:
            cookie += f"; Expires={expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
        if max_age:
            cookie += f"; Max-Age={max_age}"
        if secure:
            cookie += f"; Secure"
        if httponly:
            cookie += f"; HttpOnly"
        self.headers.add("Set-Cookie", cookie)

    def __dict__(self):
        d = {}
        if self.__body:
            d["body"] = self.__body
        if self.__status_code:
            d["status_code"] = self.__status_code
        if self.__headers:
            d["headers"] = self.__headers
        if self.__mimetype:
            d["mimetype"] = self.__mimetype
        if self.__charset:
            d["charset"] = self.__charset
        return d
