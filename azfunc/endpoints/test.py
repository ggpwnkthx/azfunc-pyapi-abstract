from .. import app
import azure.functions as func
import libs.data
import logging


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    sql = libs.data.from_bind("general_sql")
    
    row = sql["esquire"]["locations"]["f4d76819-0031-4da2-802e-00045d6f3833"]
    logging.warn(row["notes"])
    
    row["notes"] = "testing"
        
    row = sql["esquire"]["locations"]["f4d76819-0031-4da2-802e-00045d6f3833"]
    logging.warn(row["notes"])
    
    return func.HttpResponse(f"OK")
