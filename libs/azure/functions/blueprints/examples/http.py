from azure.durable_functions import DurableOrchestrationClient
from libs.azure.functions import Blueprint
from libs.azure.functions.http import HttpRequest, HttpResponse

bp = Blueprint()


@bp.route(route="example_http", methods=["GET"])
async def example_http(req: HttpRequest, client: DurableOrchestrationClient):
    return HttpResponse("OK")
