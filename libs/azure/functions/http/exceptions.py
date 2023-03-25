from ..http import HttpResponse
import json


class HttpAbort(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.response = args[0]


def abort(*args, **kwargs):
    args = list(args)
    kwargs = dict(kwargs)
    if len(args):
        if not isinstance(args[0], str):
            args[0] = json.dumps(args[0])
    if "body" in kwargs.keys():
        if not isinstance(kwargs["body"], str):
            kwargs["body"] = json.dumps(kwargs["body"])
    raise HttpAbort(
        HttpResponse(
            *args,
            **{
                "headers": {"Content-Type": "application/json"},
                **kwargs,
            }
        )
    )
