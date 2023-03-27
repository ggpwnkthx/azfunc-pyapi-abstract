from libs.utils.decorators import staticproperty
from typing import Any, Callable


class MemoryStorageProvider():
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> list:
        return [
            "ram"
        ]
    
    @staticproperty
    def scheme(self) -> str:
        self.SUPPORTED_SCHEMES[0]
        
    def __init__(self, *args, **kwargs) -> None:
        self.store = {}

    def save(self, key: str, value: Any, encoder: Callable = None, **kwargs) -> None:
        self.store[key] = encoder(value, **kwargs) if encoder else value

    def load(self, key: str, decoder: Callable = None, **kwargs) -> Any:
        return decoder(self.store[key], **kwargs) if decoder else self.store[key]

    def drop(self, key: str) -> None:
        del self.store[key]