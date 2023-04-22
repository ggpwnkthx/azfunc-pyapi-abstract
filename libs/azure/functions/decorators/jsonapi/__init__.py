from .exceptions import *
from libs.azure.functions.http import HttpRequest, HttpResponse
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
                "action": parse_query(request.url),
            }
        else:
            return {
                "type": request.route_params.get("resource_id"),
                "id": request.route_params.get("relation_id"),
                "relation": None,
                "action": parse_query(request.url),
            }
    else:
        return {
            "type": request.route_params.get("resource_type"),
            "id": request.route_params.get("resource_id"),
            "relation": request.route_params.get("relation_type"),
            "action": parse_query(request.url),
        }

from libs.utils.jsonapi.marshmallow import Responder
def alter_response(response: HttpResponse, request: HttpRequest, **kwargs):
    response.headers.add("Content-Type", "application/vnd.api+json")
    if isinstance(response.resource, tuple):
        for resource in response.resource:
            # responder = type(
            #     f"{resource.__name__}Responder", 
            #     (Responder,), 
            #     {
            #         "TYPE": resource.__name__,
            #         "SERIALIZER": resource.__marshmallow__
            #     }
            # )
            if hasattr(resource, "__repr__"):
                response.set_body(str(resource))
            else:
                response.set_body(json.dumps(resource))
    return response
