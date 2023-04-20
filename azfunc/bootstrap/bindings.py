import libs.data

libs.data.register_binding("current_thread", "KeyValue", "thread")


import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.WARNING)

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

from azure.data.tables import TableServiceClient

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
