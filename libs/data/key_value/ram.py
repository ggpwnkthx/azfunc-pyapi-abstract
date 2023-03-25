from typing import Any


class MemoryStorageProvider():
    SUPPORTED_SCHEMES = [
        "ram"
    ]
    
    def __init__(self) -> None:
        self.store = {}

    def save(self, key: str, value: Any) -> None:
        self.store[key] = value

    def load(self, key: str) -> Any:
        return self.store[key]

    def drop(self, key: str) -> None:
        del self.store[key]