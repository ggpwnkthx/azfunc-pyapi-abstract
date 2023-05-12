from libs.azure.functions import Blueprint
from libs.azure.functions.http import HttpRequest, HttpResponse

import simplejson as json

bp = Blueprint()


@bp.route(route="whoami", methods=["GET"])
async def who_am_i(req: HttpRequest):
    return HttpResponse(
        json.dumps(
            {
                k: v
                for k, v in req.headers.items()
                if k.startswith("x-ms-client-principal-")
            }
        )
    )
