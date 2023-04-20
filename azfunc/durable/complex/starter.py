from ... import app
from libs.azure.functions import HttpRequest

# An HTTP-Triggered Function with a Durable Functions Client binding
@app.route(route="orchestrators/complex")
@app.durable_client_input(client_name="client")
async def complex_start(req: HttpRequest, client):
    instance_id = await client.start_new("complex_root")
    response = client.create_check_status_response(req, instance_id)
    return response