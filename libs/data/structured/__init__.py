import functools
from libs.utils.decorators import staticproperty, immutable_arguments
from libs.utils.pluginloader import load
from typing import Any, List, Protocol, runtime_checkable
import inspect


@runtime_checkable
class StructuredProvider(Protocol):
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> list:
        pass

    @property
    def SCHEMA(self) -> dict:
        """Returns a dictionary representing the structure's schema."""
        pass

    def save(self, key: str, value: Any, **kwargs) -> None:
        """Store the given value with the specified key in the storage provider."""
        pass

    def load(self, key: str, **kwargs) -> Any:
        """Retrieve the value associated with the specified key from the storage provider."""
        pass

    def drop(self, key: str, **kwargs) -> None:
        """"""
        pass


class StructuredRegistry:
    _providers = []

    @classmethod
    def get_protocol(cls) -> Protocol:
        return StructuredProvider

    @classmethod
    def register(cls, provider_class) -> None:
        if not inspect.isclass(provider_class) or not isinstance(
            provider_class, StructuredProvider
        ):
            raise TypeError("Only KeyValue StorageProviders can be registered.")
        if provider_class not in cls._providers:
            cls._providers.append(provider_class)

    @classmethod
    @immutable_arguments
    @functools.cache
    def get_instance(cls, scheme: str, *args, **kwargs) -> StructuredProvider:
        provider_class = None
        for provider in cls._providers:
            if scheme in provider.SUPPORTED_SCHEMES:
                provider_class = provider
                break
            if cls.regex_schemes(scheme):
                provider_class = provider
                break
        if not provider_class:
            raise ValueError(
                f"Storage provider for the '{scheme}' scheme is not supported."
            )
        return provider_class(scheme=scheme, *args, **kwargs)

    @classmethod
    def get_schemes(cls) -> List[str]:
        return [
            scheme
            for provider in cls._providers
            for scheme in provider.SUPPORTED_SCHEMES
        ]

    @classmethod
    def regex_schemes(cls, scheme: str) -> bool:
        for provider in cls._providers:
            if hasattr(provider, "SUPPORTED_SCHEMES_REGEX"):
                if provider.SUPPORTED_SCHEMES_REGEX(scheme):
                    return True
        return False

    @classmethod
    def load_modules(cls) -> None:
        for module in load(path=__file__, file_mode="all", depth=-1):
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and isinstance(obj, StructuredProvider)
                    and obj != StructuredProvider
                ):
                    StructuredRegistry.register(obj)
