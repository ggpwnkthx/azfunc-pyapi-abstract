from . import app
from libs.utils.threaded import current
from marshmallow import Schema
from uuid import uuid4
import azure.functions as func
import json


@app.thread_scope()  # current.request, current.response, current.azfunc
@app.session()  # current.session
@app.authenticate(enforce=False)  # current.subject
@app.jsonapi(
    route_prefix="v1/", methods=["GET", "POST", "PATCH", "DELETE"]
)  # current.jsonapi
def api_v1_jsonapi(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    match current.jsonapi["request"]["action"]["method"].upper():
        case "GET":
            if (
                "id" in current.jsonapi["request"]["resource"].keys()
                and "relation" not in current.jsonapi["request"]["resource"].keys()
            ):
                data, schema = {}, Schema.from_dict({})
                if data is not None:
                    return json.loads(schema().dumps(data))
            else:
                # cache_id = str(uuid4())
                filters = (
                    current.jsonapi["request"]["action"]["filters"]
                    if "filters" in current.jsonapi["request"]["action"].keys()
                    else None
                )

                page_size = 100
                page_num = 0
                if "page" in current.jsonapi["request"]["action"].keys():
                    page_size = (
                        int(current.jsonapi["request"]["action"]["page"]["size"])
                        if "size" in current.jsonapi["request"]["action"]["page"].keys()
                        else page_size
                    )
                    page_num = (
                        int(current.jsonapi["request"]["action"]["page"]["number"])
                        if "number"
                        in current.jsonapi["request"]["action"]["page"].keys()
                        else page_num
                    )
                return list(
                    map(
                        lambda data, schema: json.loads(schema().dumps(data)),
                        [({}, Schema.from_dict({})), ({}, Schema.from_dict({}))],
                    )
                )
    return None
