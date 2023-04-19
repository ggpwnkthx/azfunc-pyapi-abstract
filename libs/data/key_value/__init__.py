from libs.utils.decorators import staticproperty, immutable_arguments
from typing import Any, Callable, List, Protocol, runtime_checkable
from libs.utils.pluginloader import load
import functools
import inspect

_REGISTRY = {}

@runtime_checkable
class KeyValueProvider(Protocol):
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> List[str]:
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
    def get_protocol(cls) -> Protocol:
        return KeyValueProvider

    @classmethod
    def register(cls, provider_class) -> None:
        if (not inspect.isclass(provider_class) or not isinstance(
            provider_class, KeyValueProvider
        )):
            raise TypeError(
                "Only KeyValueProviders can be registered."
            )
        if provider_class not in cls._providers:
            cls._providers.append(provider_class)

    @classmethod
    @immutable_arguments
    @functools.cache
    def get_instance(cls, scheme, *args, **kwargs) -> KeyValueProvider:
        provider_class = None
        for provider in cls._providers:
            if scheme in provider.SUPPORTED_SCHEMES:
                provider_class = provider
                break
        if not provider_class:
            raise ValueError(f"Storage provider for the '{scheme}' scheme is not supported.")
        return provider_class(scheme=scheme, *args, **kwargs)

    @classmethod
    def get_schemes(cls) -> List[str]:
        return [
            scheme
            for provider in cls._providers
            for scheme in provider.SUPPORTED_SCHEMES
        ]
        
    @classmethod
    def load_modules(cls) -> None:
        for module in load(path=__file__,file_mode="all",depth=-1):
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and isinstance(obj, KeyValueProvider)
                    and obj != KeyValueProvider
                ):
                    KeyValueRegistry.register(obj)
