from .. import app
from libs.azure.functions.http import HttpRequest, HttpResponse
from libs.data import from_bind

# @app.session()
@app.jsonapi()
@app.route("{binding}/jsonapi/v1")
async def api_v1_jsonapi(req: HttpRequest) -> HttpResponse:
    provider = from_bind(req.route_params.get("binding"))
    match req.method:
        case "GET":
            if req.jsonapi["type"] == "schema":
                resources = provider.SCHEMA
            elif not req.jsonapi.get("id"):
                resources = provider[req.jsonapi["type"]]
            elif not req.jsonapi.get("relation"):
                resources = provider[req.jsonapi["type"]](req.jsonapi["id"])
            return HttpResponse(resources=resources)
    return HttpResponse(status_code=404)
