from libs.utils.threaded import current
from typing import Any


class ThreadMemoryStorageProvider():
    SUPPORTED_SCHEMES = [
        "thread"
    ]
    
    def __init__(self, *args, **kwargs) -> None:
        self.scheme = self.SUPPORTED_SCHEMES[0]
    
    def save(self, key: str, value: Any) -> None:
        current.__setattr__(key, value)

    def load(self, key: str) -> Any:
        return current.__getattribute__(key)

    def drop(self, key: str) -> None:
        current.__delattr__(key)