from .. import app
import azure.functions as func
import libs.data
import logging


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    general_sql = libs.data.from_bind("general_sql")
    logging.warn(general_sql["esquire"]["geoframes"])
    return func.HttpResponse(f"OK")
