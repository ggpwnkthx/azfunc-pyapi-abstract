from .utils import extend_model
from libs.utils.decorators import staticproperty

from marshmallow import Schema
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.automap import automap_base, AutomapBase
from sqlalchemy.orm import Session
from typing import Any, Callable, List, Tuple
import uuid


class SQLAlchemyStructuredProvider:
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> list:
        return ["sql"]

    @staticproperty
    def RESOURCE_TYPE_DELIMITER(self) -> str:
        return "."

    @staticproperty
    def DEFAULT_SCHEMA(self) -> str:
        return "default"

    @property
    def SCHEMA(self) -> dict:
        return {
            f"{schema}.{table}": {
                field.name: {
                    "type": field.__class__.__name__,
                    "read_only": field.dump_only,
                    "write_only": field.load_only,
                    "required": field.required,
                    "allow_none": field.allow_none,
                }
                for field in model.__marshmallow__().fields.values()
            }
            for schema, tables in self.models.items()
            for table, model in tables.items()
        }

    def __init__(self, *args, **kwargs) -> None:
        kw = kwargs.keys()
        kwargs.pop("scheme")
        self.id: str = uuid.uuid4().hex
        self.schemas: List[str] = (
            kwargs.pop("schemas")
            if "schemas" in kw
            else [kwargs.pop("schema")]
            if "schema" in kw
            else []
        )
        self.engine: Engine = (
            kwargs.pop("engine")
            if "engine" in kw
            else create_engine(kwargs.pop("url"), **kwargs)
            if "url" in kw
            else None
        )
        if not self.engine:
            raise Exception("No engine configuration values specified.")

        self.base: AutomapBase = automap_base()
        self.session: Callable = lambda: Session(self.engine)

        for schema in self.schemas:
            self.base.prepare(
                autoload_with=self.engine,
                schema=schema,
                modulename_for_table=self.modulename_for_table,
            )
        self.models = self.base.by_module.get(self.id)
        for schema in self.models.keys():
            for model in self.models[schema].keys():
                extend_model(model=self.models[schema][model], session=self.session)

    def __getitem__(self, handle):
        selected = self.models
        for selector in handle.split(self.RESOURCE_TYPE_DELIMITER):
            selected = selected[selector]
        return selected

    def connect(self) -> Session:
        return self.session()

    def save(
        self,
        key: str,
        value: Any,
        schema_name: str = None,
        table_name: str = None,
        model: Any = None,
    ) -> None:
        session = self.session()
        if not model:
            if not table_name and not schema_name:
                schema_name, table_name, primary_key = self.parse_key(key)
            model = self.models[schema_name or self.DEFAULT_SCHEMA][table_name]
        record = session.query(model).get(primary_key)
        if record:
            for k, v in value.items():
                setattr(record, k, v)
        else:
            session.add(model(**value))
        session.commit()

    def load(
        self,
        key: str,
        schema_name: str = None,
        table_name: str = None,
        model: Any = None,
    ) -> Any:
        session = self.session()
        if not model:
            if not table_name and not schema_name:
                schema_name, table_name, primary_key = self.parse_key(key)
            model = self.models[schema_name or self.DEFAULT_SCHEMA][table_name]
        return session.query(model).get(primary_key)

    def filter(
        self, filters: List[str], decoder: Callable = None, **kwargs
    ) -> List[Any]:
        pass

    def drop(
        self,
        key: str,
        schema_name: str = None,
        table_name: str = None,
        model: Any = None,
    ) -> None:
        session = self.session()
        if not model:
            if not table_name and not schema_name:
                schema_name, table_name, primary_key = self.parse_key(key)
            model = self.models[schema_name or self.DEFAULT_SCHEMA][table_name]
        session.delete(session.query(model).get(primary_key))
        session.commit()

    def parse_key(self, key: str):
        key = key.split(self.RESOURCE_TYPE_DELIMITER)
        schema_name = key[0]
        table_name = key[1]
        primary_key = ""
        if len(key) > 2:
            primary_key = key[2]
        return schema_name, table_name, primary_key

    def modulename_for_table(self, cls, tablename, table) -> str:
        return (
            f"{self.id}.{table.schema}"
            if getattr(table, "schema", None)
            else f"{self.id}.{self.DEFAULT_SCHEMA}"
        )
