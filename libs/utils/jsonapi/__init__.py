from .exceptions import *

# from ..odata import build as build_odata_query
from querystring_parser import parser
from urllib.parse import urlparse, ParseResult
import simplejson as json


JSONAPI_VERSION = "1.1"


def validate_jsonapi_request(
    method: str,
    headers: dict,
    body: bytes = None,
):
    # Validate the request method
    if method not in ["GET", "POST", "PATCH", "DELETE"]:
        raise JsonApiMethodException()

    # Validate the Accept header
    if headers.get("Accept") != "application/vnd.api+json":
        raise JsonApiHeaderAcceptException

    # Validate the JSONAPI version
    if method in ["POST", "PATCH", "DELETE"]:
        # Validate the content type
        if "application/vnd.api+json" not in headers.get("Content-Type"):
            raise JsonApiHeaderContentTypeException
        try:
            body = json.loads(body)
            if method in ["POST", "PATCH"]:
                if body.get("jsonapi") != {"version": JSONAPI_VERSION}:
                    raise JsonApiInvalidVersionException(JSONAPI_VERSION)
                else:
                    if body != {}:
                        raise JsonApiInvalidEmptyPayloadException()
                if any([key not in body for key in ["data", "type", "id"]]):
                    raise JsonApiInvalidRequestException()
            return body
        except:
            raise JsonApiInvalidPayloadException()
    return None


def parse_query(query_string: str):
    query = {}
    for key, value in parser.parse(query_string).items():
        key = key.lower()
        match key:
            case "include":
                query["include"] = value.split(",")
            case "fields":
                query["fields"] = [
                    {"type": k, "fields": v.split(",")} for k, v in value.items()
                ]
            case "sort":
                query["sort"] = [
                    {"field": f[-1], "dir": "DESC" if len(f) > 1 else "ASC"}
                    for field in value.split(",")
                    if (f := field.split("-"))
                ]
            case "filters":
                query[key] = {k: json.loads(v) for k, v in value.items()}
            case _:
                query[key] = value

    return query

def parse_request(
    url: str,
    method: str,
    headers: dict,
    body: bytes = None,
    prefix: str = "/",
):
    method = method.upper()
    body = validate_jsonapi_request(method=method, headers=headers, body=body)

    # parse resource location
    url: ParseResult = urlparse(url)
    prefix += "/" if prefix[-1] != "/" else ""
    path = url.path.split(prefix)[1].split("/")
    match len(path):
        case 4:
            if path[2] == "relationships":
                resource = {
                    "type": path[0],
                    "id": path[1],
                    "relation": path[3],
                }
            else:
                resource = {"type": path[2], "id": path[3]}

        case 3:
            resource = {
                "type": path[0],
                "id": path[1],
                "relation": path[2],
            }
        case 2:
            resource = {"type": path[0], "id": path[1]}
        case 1:
            resource = {"type": path[0]}

    request = {
        "resource": resource,
        "action": {"method": method, **parse_query(url.query)},
    }

    if method in ["POST", "PATCH"]:
        request["data"] = body

    return request
