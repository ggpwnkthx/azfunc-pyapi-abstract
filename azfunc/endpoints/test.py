from .. import app
import azure.functions as func
import libs.data


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    qf = libs.data.from_bind("an_sql_server")["schema.table"]
    qf = qf[
        (
            (qf["column_1"] != None) & (qf["column_2"] != None)
        ) | (qf["column_3"] == None)
    ][qf[
        "id", "owner"
    ]]

    return func.HttpResponse(f"OK")
