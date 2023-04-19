from typing import List, Protocol, runtime_checkable


@runtime_checkable
class StorageProvider(Protocol):
    def save(self, *args, **kwargs):
        pass

    def load(self, *args, **kwargs):
        pass


@runtime_checkable
class StorageProviderRegistry(Protocol):
    @classmethod
    def get_protocol(cls) -> Protocol:
        pass

    @classmethod
    def register(cls, provider_class) -> None:
        pass

    @classmethod
    def get_instance(cls, schema, *args, **kwargs) -> StorageProvider:
        pass

    @classmethod
    def get_schemes(cls) -> List[str]:
        pass

    @classmethod
    def load_modules(cls) -> None:
        pass


from libs.utils.pluginloader import load
import inspect

_REGISTRY = {}
for module in load(path=__file__, depth=1):
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, StorageProviderRegistry):
            _REGISTRY[name] = obj
            obj.load_modules()


def get_provider(protocol: str, scheme: str, *args, **kwargs) -> StorageProvider:
    global _REGISTRY
    cls = _REGISTRY.get(protocol) or _REGISTRY.get(protocol + "Registry")
    if scheme in cls.get_schemes():
        return cls.get_instance(scheme, *args, **kwargs)
    if hasattr(cls, "regex_schemes"):
        if cls.regex_schemes(scheme):
            return cls.get_instance(scheme, *args, **kwargs)


def get_supported() -> dict:
    global _REGISTRY
    return {
        cls.get_protocol().__name__: cls.get_schemes() for _, cls in _REGISTRY.items()
    }


_BINDINGS = {}


def register_binding(handle: str, protocol: str, scheme: str, *args, **kwargs) -> None:
    global _BINDINGS
    if handle not in _BINDINGS:
        _BINDINGS[handle] = get_provider(protocol, scheme, *args, **kwargs)


def from_bind(handle: str) -> StorageProvider:
    global _BINDINGS
    if handle in _BINDINGS:
        return _BINDINGS[handle]
    return None
