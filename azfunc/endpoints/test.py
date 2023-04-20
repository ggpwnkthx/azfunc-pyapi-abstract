from .. import app
import azure.functions as func
import libs.data


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    sql = libs.data.from_bind("general_sql")
    print(sql["esquire"]["locations"]["f4d76819-0031-4da2-802e-00045d6f3833"])

    return func.HttpResponse(f"OK")
