# Bootstrap Stuff Goes Here
import bindings


# Create App Instance
import libs.azure.functions as func

app = func.FunctionApp()

# Setup Standard Extensions
from . import jsonapi


from datetime import datetime
import pickle


# Testing
@app.function_name(name="HttpTrigger_Test")
@app.route(route="test")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    current_thread = bindings.get("current_thread")
    current_thread.save(
        "general/test.pickle",
        {"data": "this is a test", "time": datetime.utcnow()}
    )
    print(
        current_thread.load(
            "general/test.pickle"
        )
    )
    return func.HttpResponse(f"OK")
