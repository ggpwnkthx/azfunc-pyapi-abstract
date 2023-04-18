from .. import app
import azure.functions as func
import libs.data
import logging


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    general_sql = libs.data.from_bind("general_sql")
    table = general_sql.get_table(schema="esquire", name="locations")
    logging.warn(general_sql.connect().query(table.notes).first())
    return func.HttpResponse(f"OK")
