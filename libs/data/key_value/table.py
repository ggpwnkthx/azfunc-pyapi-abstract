from libs.utils.decorators import staticproperty
from typing import Any, Callable

from azure.data.tables import TableClient


_RENAME = {}


class TableKeyValueProvider:
    @staticproperty
    def SUPPORTED_SCHEMES(self):
        return ["azure_table"]

    def __init__(self, *args, **kwargs) -> None:
        if len(args):
            self.scheme = args[0]
        if "scheme" in kwargs:
            self.scheme = kwargs.pop("scheme")
        for key, value in _RENAME.items():
            if self.scheme == value:
                self.scheme = key
        self.config = {**kwargs}

    def connect(self, key: str, **kwargs) -> Any:
        match self.scheme:
            case "azure_table":
                return self.config["client"].get_table_client(key.split("/")[0])

    def save(self, key: str, value: Any, encoder: Callable = None, **kwargs) -> None:
        if encoder:
            value = encoder(value, **kwargs)
        conn = self.connect(key)
        key = key.split("/")
        match self.scheme:
            case "azure_table":
                if not hasattr(value, "keys"):
                    value = {"value": value}
                conn.upsert_entity({"PartitionKey": key[1], "RowKey": key[2], **value})

    def load(self, key: str, decoder: Callable = None, **kwargs) -> Any:
        conn = self.connect(key)
        key = key.split("/")
        match self.scheme:
            case "azure_table":
                value = conn.get_entity(partition_key = key[1], row_key = key[2])
                
        return decoder(value) if decoder else value

    def drop(self, key: str, **kwargs) -> None:
        conn = self.connect(key)
        key = key.split("/")
        match self.scheme:
            case "azure_table":
                conn.delete_entity(partition_key = key[1], row_key = key[2])
        pass
