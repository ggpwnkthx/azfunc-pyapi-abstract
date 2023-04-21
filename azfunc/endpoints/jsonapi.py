from .. import app
from libs.data import from_bind
from libs.data.structured import StructuredProvider
import azure.functions as func
import logging
import simplejson as json

@app.session()
@app.authenticate(enforce=False)
@app.jsonapi()
@app.route("{binding}/jsonapi/v1")
async def api_v1_jsonapi(req: func.HttpRequest) -> func.HttpResponse:
    logging.warn(dir(req))
    provider = from_bind(req.route_params.get("binding"))
    if provider:
        match req.method:
            case "GET":
                if req.jsonapi["type"] == "schema":
                    if isinstance(provider, StructuredProvider):
                        return func.HttpResponse(json.dumps(provider.SCHEMA))

                # if (
                #     "id" in current.jsonapi["request"]["resource"].keys()
                #     and "relation" not in current.jsonapi["request"]["resource"].keys()
                # ):
                #     resource = provider.load(
                #         key=current.jsonapi["request"]["resource"]["type"]
                #         + "."
                #         + current.jsonapi["request"]["resource"]["id"]
                #     )
                #     logging.warn(resource)
                #     return resource
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
    return func.HttpResponse(status_code=404)
