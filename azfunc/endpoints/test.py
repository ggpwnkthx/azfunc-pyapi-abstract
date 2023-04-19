from .. import app
import azure.functions as func
import libs.data
import logging


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    general_sql = libs.data.from_bind("general_sql")
    logging.warn(dir(general_sql.models["esquire"]["geoframes"]))
    logging.warn(general_sql.models["esquire"]["geoframes"].__marshmallow__)
    return func.HttpResponse(f"OK")
