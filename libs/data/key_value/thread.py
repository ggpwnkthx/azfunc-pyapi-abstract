from libs.utils.decorators import staticproperty
from libs.utils.threaded import current
from typing import Any, Callable, List


class ThreadKeyValueProvider:
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> List[str]:
        return ["thread"]

    @staticproperty
    def scheme(self) -> str:
        self.SUPPORTED_SCHEMES[0]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(ThreadKeyValueProvider, cls).__new__(cls)
            return cls.instance

    def save(self, key: str, value: Any, encoder: Callable = None, **kwargs) -> None:
        current.__setattr__(key, encoder(value) if encoder else value)

    def load(self, key: str, decoder: Callable = None, **kwargs) -> Any:
        return (
            decoder(current.__getattribute__(key)._get_current_object())
            if decoder
            else current.__getattribute__(key)._get_current_object()
        )

    def drop(self, key: str) -> None:
        current.__delattr__(key)
