from .exceptions import *
from azure.functions.http import HttpRequest
from querystring_parser import parser
import simplejson as json


JSONAPI_VERSION = "1.1"


def validate_jsonapi_request(request: HttpRequest):
    # Validate the request method
    if request.method not in ["GET", "POST", "PATCH", "DELETE"]:
        raise JsonApiMethodException()

    # Validate the Accept header
    if request.headers.get("Accept") != "application/vnd.api+json":
        raise JsonApiHeaderAcceptException

    # Validate the JSONAPI version
    if request.method in ["POST", "PATCH", "DELETE"]:
        # Validate the content type
        if "application/vnd.api+json" not in request.headers.get("Content-Type"):
            raise JsonApiHeaderContentTypeException
        try:
            if request.method in ["POST", "PATCH"]:
                body = request.get_json()
                if body.get("jsonapi") != {"version": JSONAPI_VERSION}:
                    raise JsonApiInvalidVersionException(JSONAPI_VERSION)
                else:
                    if body != {}:
                        raise JsonApiInvalidEmptyPayloadException()
                if any([key not in body for key in ["data", "type", "id"]]):
                    raise JsonApiInvalidRequestException()
        except:
            raise JsonApiInvalidPayloadException()
    return None


def parse_query(url: str):
    query = {}
    query_string = url.split("?")
    if len(query_string) > 1:
        for key, value in parser.parse(query_string[1]).items():
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


def parse_request(request: HttpRequest):
    validate_jsonapi_request(request)
    if request.route_params.get("relation_id"):
        if request.route_params.get("relation_type") == "relationships":
            return {
                "type": request.route_params.get("resource_type"),
                "id": request.route_params.get("resource_id"),
                "relation": request.route_params.get("relation_id"),
                "action": parse_query(request.url)
            }
        else:
            return {
                "type": request.route_params.get("resource_id"),
                "id": request.route_params.get("relation_id"),
                "relation": None,
                "action": parse_query(request.url)
            }
    else:
        return {
            "type": request.route_params.get("resource_type"),
            "id": request.route_params.get("resource_id"),
            "relation": request.route_params.get("relation_type"),
            "action": parse_query(request.url)
        }
