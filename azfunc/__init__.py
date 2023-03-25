# Bootstrap Stuff Goes Here
import libs.data
import os
from azure.storage.blob import BlobServiceClient

libs.data.register_binding(
    "general_blobs",
    "KeyValue",
    "azure_blob",
    transport_params={
        "client": BlobServiceClient.from_connection_string(
            os.environ["AzureWebJobsStorage"]
        )
    },
)

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
    libs.data.from_bind("general_blobs").save("general/test.pickle", pickle.dumps({"data": "this is a test", "time": datetime.utcnow()}))
    print(libs.data.from_bind("general_blobs").load("general/test.pickle", decoder=pickle.load))
    return func.HttpResponse(f"OK")
