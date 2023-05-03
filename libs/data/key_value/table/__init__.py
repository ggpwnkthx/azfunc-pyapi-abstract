from libs.utils.decorators import staticproperty
from typing import Any, Callable, List


class TableKeyValueProvider:
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> List[str]:
        return ["azure_table"]

    @staticproperty
    def RESOURCE_TYPE_DELIMITER(self) -> str:
        return "."

    def __init__(self, *args, **kwargs) -> None:
        if len(args):
            self.scheme = args[0]
        if "scheme" in kwargs:
            self.scheme = kwargs.pop("scheme")
        self.config = {**kwargs}

    def __getitem__(self, handle: str) -> Any:
        match self.scheme:
            case "azure_table":
                handle = handle.split(self.RESOURCE_TYPE_DELIMITER)
                conn = self.connect(
                    table_name=handle[0],
                    partition_key=handle[1] if len(handle) > 1 else None,
                    key_split_char=self.RESOURCE_TYPE_DELIMITER
                )
                return conn

    def connect(self, table_name: str, **kwargs) -> Any:
        match self.scheme:
            case "azure_table":
                from .azure_table import Client as AzureTableClient

                return AzureTableClient.from_service_client(
                    service_client=self.config["client"],
                    table_name=table_name,
                    **kwargs,
                )

    def save(self, key: str, value: Any, encoder: Callable = None, **kwargs) -> None:
        if encoder:
            value = encoder(value, **kwargs)
        match self.scheme:
            case "azure_table":
                table_name, partition_key, row_key = self.parse_key(key)
                conn = self.connect(table_name)
                if not hasattr(value, "keys"):
                    value = {"value": value}
                conn.upsert_entity(
                    {"PartitionKey": partition_key, "RowKey": row_key, **value}
                )

    def load(self, key: str, decoder: Callable = None, **kwargs) -> Any:
        match self.scheme:
            case "azure_table":
                table_name, partition_key, row_key = self.parse_key(key)
                conn = self.connect(table_name)
                value = conn.get_entity(partition_key=partition_key, row_key=row_key)
        return decoder(value) if decoder else value

    def drop(self, key: str, **kwargs) -> None:
        match self.scheme:
            case "azure_table":
                table_name, partition_key, row_key = self.parse_key(key)
                conn = self.connect(table_name)
                conn.delete_entity(partition_key=partition_key, row_key=row_key)

    def parse_key(self, key: str):
        match self.scheme:
            case "azure_table":
                key = key.split(self.RESOURCE_TYPE_DELIMITER)
                table_name = key[0]
                partition_key = key[1]
                row_key = ""
                if len(key) > 2:
                    row_key = key[2]
                return table_name, partition_key, row_key
