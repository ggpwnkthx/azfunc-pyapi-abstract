import libs.data

libs.data.register_binding("current_thread", "KeyValue", "thread")

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

libs.data.register_binding(
    "general_sql",
    "Structured",
    "sql",
    url=os.environ["data_sql_general"],
    schemas=["dbo","esquire"]
)