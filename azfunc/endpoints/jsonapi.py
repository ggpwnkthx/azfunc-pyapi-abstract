from .. import app
from libs.azure.functions.http import HttpRequest, HttpResponse
from libs.data import from_bind
from libs.data.structured import StructuredProvider

import logging
# @app.session()
# @app.authenticate(enforce=False)
@app.jsonapi()
@app.route("{binding}/jsonapi/v1")
async def api_v1_jsonapi(req: HttpRequest) -> HttpResponse:
    provider = from_bind(req.route_params.get("binding"))
    if provider and isinstance(provider, StructuredProvider):
        match req.method:
            case "GET":
                if req.jsonapi["type"] == "schema":
                    return HttpResponse(resource=provider.SCHEMA)
                elif not req.jsonapi.get("id"):
                    pass
                elif not req.jsonapi.get("relation"):
                    qf = provider[req.jsonapi["type"]]
                    logging.warn(qf)
                    column = qf["notes"]
                    logging.warn(column)
                    # logging.warn(qf[column != None])
                return HttpResponse(resource={})
    return HttpResponse(status_code=404)
