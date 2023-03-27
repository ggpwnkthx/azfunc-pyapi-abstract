from libs.utils.decorators import staticproperty
from typing import Any, Callable, Protocol, runtime_checkable
import inspect


@runtime_checkable
class KeyValue(Protocol):
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> list:
        pass

    def save(self, key: str, value: Any, encoder: Callable = None, **kwargs) -> None:
        """Store the given value with the specified key in the storage provider."""
        pass

    def load(self, key: str, decoder: Callable = None, **kwargs) -> Any:
        """Retrieve the value associated with the specified key from the storage provider."""
        pass


class KeyValueRegistry:
    _providers = []
    
    @classmethod
    def get_protocol(cls):
        return KeyValue

    @classmethod
    def register(cls, provider_class):
        if (not inspect.isclass(provider_class) or not isinstance(
            provider_class, KeyValue
        )):
            raise TypeError(
                "Only KeyValue StorageProviders can be registered."
            )
        if provider_class not in cls._providers:
            cls._providers.append(provider_class)

    @classmethod
    def get_instance(cls, scheme, *args, **kwargs):
        provider_class = None
        for provider in cls._providers:
            if scheme in provider.SUPPORTED_SCHEMES:
                provider_class = provider
                break
        if not provider_class:
            raise ValueError(f"Storage provider for the '{scheme}' scheme is not supported.")
        return provider_class(scheme=scheme, *args, **kwargs)

    @classmethod
    def get_schemes(cls):
        return [
            schema
            for provider in cls._providers
            for schema in provider.SUPPORTED_SCHEMES
        ]


import importlib
import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
base_path = current_file_path.parent
sys.path.insert(0, str(base_path.parent))

for py_file in base_path.glob("**/*.py"):
    if py_file.name.startswith("__"):
        continue

    relative_path = py_file.relative_to(Path.cwd()).with_suffix("")
    module_name = ".".join(relative_path.parts)

    module = importlib.import_module(module_name)

    for name, obj in inspect.getmembers(module):
        if (
            inspect.isclass(obj)
            and isinstance(obj, KeyValue)
            and obj != KeyValue
        ):
            KeyValueRegistry.register(obj)

sys.path.pop(0)
