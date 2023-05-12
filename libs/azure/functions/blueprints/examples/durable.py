from libs.azure.functions import Blueprint
from libs.azure.functions.http import HttpRequest

bp = Blueprint()


# An HTTP-Triggered Function with a Durable Functions Client binding
@bp.route(route="orchestrators/simple")
@bp.durable_client_input(client_name="client")
async def example_start(req: HttpRequest, client):
    instance_id = await client.start_new("simple_root")
    response = client.create_check_status_response(req, instance_id)
    return response


# Orchestrator
@bp.orchestration_trigger(context_name="context")
def example_orch(context):
    result1 = yield context.call_activity("simple_hello", "Seattle")
    result2 = yield context.call_activity("simple_hello", "Tokyo")
    result3 = yield context.call_activity("simple_hello", "London")

    return [result1, result2, result3]


# Activity
@bp.activity_trigger(input_name="city")
def example_act(city: str):
    return "Hello " + city
