from .. import app
from libs.data import from_bind
from libs.utils.threaded import current
from marshmallow import Schema
import azure.functions as func
import logging


@app.thread_scope()  # current.request, current.response, current.azfunc
@app.session()  # current.session
@app.authenticate(enforce=False)  # current.subject
@app.jsonapi(
    route_prefix="{binding}/jsonapi/v1", methods=["GET", "POST", "PATCH", "DELETE"]
)  # current.jsonapi
def api_v1_jsonapi(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    provider = from_bind(req.route_params.get("binding"))
    if provider:
        match current.jsonapi["request"]["action"]["method"].upper():
            case "GET":
                if (
                    "id" in current.jsonapi["request"]["resource"].keys()
                    and "relation" not in current.jsonapi["request"]["resource"].keys()
                ):  
                    resource = provider.load(
                        key=current.jsonapi["request"]["resource"]["type"]
                        + "."
                        + current.jsonapi["request"]["resource"]["id"]
                    )
                    logging.warn(resource)
                    return resource
                # else:
                #     # cache_id = str(uuid4())
                #     filters = (
                #         current.jsonapi["request"]["action"]["filters"]
                #         if "filters" in current.jsonapi["request"]["action"].keys()
                #         else None
                #     )

                #     page_size = os.environ.get("DEFAULT_JSONAPI_PAGE_SIZE") or 100
                #     page_num = 0
                #     if "page" in current.jsonapi["request"]["action"].keys():
                #         page_size = (
                #             int(current.jsonapi["request"]["action"]["page"]["size"])
                #             if "size" in current.jsonapi["request"]["action"]["page"].keys()
                #             else page_size
                #         )
                #         page_num = (
                #             int(current.jsonapi["request"]["action"]["page"]["number"])
                #             if "number"
                #             in current.jsonapi["request"]["action"]["page"].keys()
                #             else page_num
                #         )
                #     return list(
                #         map(
                #             lambda data, schema: json.loads(schema().dumps(data)),
                #             [({}, Schema.from_dict({})), ({}, Schema.from_dict({}))],
                #         )
                #     )
    return None
