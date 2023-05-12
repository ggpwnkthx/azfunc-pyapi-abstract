# Init App
from azure.functions import AuthLevel
from libs.azure.functions import FunctionApp

app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)
app.register_blueprints(["libs/azure/functions/blueprints/jsonapi"])


# Data Bindings
import os
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
import libs.data

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
libs.data.register_binding(
    "some_azure_tables",
    "KeyValue",
    "azure_table",
    client=TableServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"]),
)
libs.data.register_binding(
    "an_sql_server",
    "Structured",
    "sql",
    url=os.environ["DATABIND_SQL_GENERAL"],
    schemas=["esquire", "dbo"],
)
