import libs.data
get = libs.data.from_bind

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