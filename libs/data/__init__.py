from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class StorageProvider(Protocol):
    def save(self, *args, **kwargs):
        pass

    def load(self, *args, **kwargs):
        pass


@runtime_checkable
class StorageProviderRegistry(Protocol):
    @classmethod
    def get_protocol(cls):
        pass

    @classmethod
    def register(cls, provider_class):
        pass

    @classmethod
    def get_instance(cls, schema, *args, **kwargs):
        pass

    @classmethod
    def get_schemes(cls):
        pass


import importlib
import inspect
from pathlib import Path

_REGISTRY = {}


current_directory = Path(__file__).parent
for subdir in [d for d in current_directory.iterdir() if d.is_dir()]:
    init_file = subdir / "__init__.py"
    if init_file.exists():
        relative_path = subdir.relative_to(Path.cwd())
        module_name = ".".join(relative_path.parts)
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and isinstance(obj, StorageProviderRegistry)
                and obj != StorageProviderRegistry
            ):
                _REGISTRY[name] = obj


def get_provider(protocol: str, scheme: str, *args, **kwargs) -> StorageProvider:
    global _REGISTRY
    for name, cls in _REGISTRY.items():
        if protocol == cls.get_protocol() or protocol == cls.get_protocol().__name__:
            if scheme in cls.get_schemes():
                return cls.get_instance(scheme, *args, **kwargs)
    raise ValueError(
        f"Storage provider for the '{protocol}' protocol and '{scheme}' schema is not supported."
    )


def get_supported():
    global _REGISTRY
    return {
        cls.get_protocol().__name__: cls.get_schemes()
        for name, cls in _REGISTRY.items()
    }


_BINDINGS = {}


def register_binding(handle: str, protocol: str, scheme: str, *args, **kwargs):
    global _BINDINGS
    if handle not in _BINDINGS:
        _BINDINGS[handle] = get_provider(protocol, scheme, *args, **kwargs)


def from_bind(handle: str) -> StorageProvider:
    if handle in _BINDINGS:
        return _BINDINGS[handle]
    return None
